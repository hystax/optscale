import os
import logging
import requests

import boto3
from boto3.session import Config as BotoConfig

from kombu import Connection, Exchange, Queue, Consumer
from kombu.mixins import ConsumerProducerMixin
from requests.packages.urllib3.exceptions import InsecureRequestWarning


from transitions import TRANSITIONS

from config_client.client import Client as ConfigClient
from rest_api_client.client_v2 import Client as RestClient
from bulldozer_client.client import Client as BulldozerClient
from arcee_client.client import Client as ArceeClient


LOG = logging.getLogger(__name__)

EXCHANGE_NAME = 'bulldozer-tasks'
DLX_EXCHANGE_NAME = '%s-dlx' % EXCHANGE_NAME
QUEUE_NAME = 'bulldozer-task'
DLX_QUEUE_NAME = '%s-delayed' % QUEUE_NAME
DLX_ARGUMENTS = {'x-dead-letter-exchange': EXCHANGE_NAME,
                 'x-dead-letter-routing-key': QUEUE_NAME}
task_exchange = Exchange(EXCHANGE_NAME, type='direct')
dlx_task_exchange = Exchange(DLX_EXCHANGE_NAME, type='direct')
task_queue = Queue(QUEUE_NAME, task_exchange, routing_key=QUEUE_NAME,
                   durable=True)
dlx_task_queue = Queue(DLX_EXCHANGE_NAME, dlx_task_exchange,
                       routing_key=QUEUE_NAME, message_ttl=2.0,
                       queue_arguments=DLX_ARGUMENTS, durable=True)
RETRY_POLICY = {'max_retries': 15, 'interval_start': 0,
                'interval_step': 1, 'interval_max': 3}
WORKDIR = '/var/lib/bulldozer/'

BUCKET_NAME = "bulldozer-states"


class BulldozerWorker(ConsumerProducerMixin):
    def __init__(self, workdir, connection, config_cl):
        self.workdir = workdir
        self.connection = connection
        self.config_cl = config_cl
        self._rest_cl = None
        self._bulldozer_client = None
        self._arcee_client = None
        self._minio_cl = None

    @property
    def rest_cl(self):
        if self._rest_cl is None:
            self._rest_cl = RestClient(
                url=self.config_cl.restapi_url(), verify=False)
            self._rest_cl.secret = self.config_cl.cluster_secret()
        return self._rest_cl

    @property
    def arcee_cl(self):
        if self._arcee_client is None:
            self._arcee_client = ArceeClient(
                url=self.config_cl.arcee_url())
            self._arcee_client.secret = self.config_cl.cluster_secret()
        return self._arcee_client

    @property
    def bulldozer_cl(self):
        if self._bulldozer_client is None:
            self._bulldozer_client = BulldozerClient(
                url=self.config_cl.bulldozer_url())
            self._bulldozer_client.secret = self.config_cl.cluster_secret()
        return self._bulldozer_client

    @property
    def minio_cl(self):
        if self._minio_cl is None:
            s3_params = self.config_cl.read_branch('/minio')
            self._minio_cl = boto3.client(
                's3',
                endpoint_url='http://{}:{}'.format(
                    s3_params['host'], s3_params['port']),
                aws_access_key_id=s3_params['access'],
                aws_secret_access_key=s3_params['secret'],
                config=BotoConfig(s3={'addressing_style': 'path'})
            )
            try:
                # trying to create bucket for state
                self._minio_cl.create_bucket(Bucket=BUCKET_NAME)
            except self._minio_cl.exceptions.BucketAlreadyOwnedByYou:
                pass
        return self._minio_cl

    def get_consumers(self, Consumer, channel):
        return [Consumer(
            queues=[task_queue],
            accept=['json'],
            callbacks=[self.process_task],
            prefetch_count=1,
        )]

    @staticmethod
    def on_connection_revived():
        LOG.info('Recovering delayed queue')
        try:
            with Connection(conn_str) as connection:
                with connection.channel() as channel:
                    delayed_consumer = Consumer(channel, dlx_task_queue)
                    delayed_consumer.close()
        except Exception as ex:
            LOG.exception('Error on delayed queue recover - %s', str(ex))
            raise

    def put_task(self, task_params, delayed=False):
        self.producer.publish(
            task_params,
            serializer='json',
            exchange=dlx_task_exchange if delayed else task_exchange,
            declare=[dlx_task_exchange] if delayed else [task_exchange],
            routing_key=QUEUE_NAME,
            retry=True,
            retry_policy=RETRY_POLICY,
            delivery_mode=2,
        )

    def process_task(self, body, message):
        try:
            runner_id = body.get("runner_id")
        except AttributeError:
            LOG.error("Failed to get runner id")
            message.ack()
            return
        try:
            transition_map = TRANSITIONS
            task = transition_map[body["state"]]
        except Exception as exc:
            LOG.exception(
                'Processing task for runner %s failed: %s',
                runner_id, (str(exc)))
            message.ack()
            return

        LOG.info("processing runner %s:", runner_id)
        try:
            task(body=body,
                 message=message,
                 config_cl=self.config_cl,
                 rest_cl=self.rest_cl,
                 arcee_cl=self.arcee_cl,
                 bulldozer_cl=self.bulldozer_cl,
                 minio_cl=self.minio_cl,
                 bucket_name=BUCKET_NAME,
                 workdir=self.workdir,
                 on_continue=self.put_task,
                 ).execute()
        except Exception as exc:
            LOG.exception(
                "Task for runner %s execution failed: %s %s",
                runner_id,
                type(exc),
                str(exc))
            message.ack()


if __name__ == '__main__':
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    logging.basicConfig(level=logging.INFO)
    os.makedirs(WORKDIR, exist_ok=True)
    config_cl = ConfigClient(
        host=os.environ.get('HX_ETCD_HOST'),
        port=int(os.environ.get('HX_ETCD_PORT')))
    config_cl.wait_configured()
    conn_str = 'amqp://{user}:{pass}@{host}:{port}'.format(
        **config_cl.read_branch('/rabbit'))
    with Connection(conn_str) as conn:
        try:
            worker = BulldozerWorker(WORKDIR, conn, config_cl)
            worker.run()
        except KeyboardInterrupt:
            print('sayonara')
