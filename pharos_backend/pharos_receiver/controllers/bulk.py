import base64
import boto3
import gzip
import logging
import os
from kombu import Connection as QConnection, Exchange
from kombu.pools import producers
from boto3.session import Config as BotoConfig
from pharos_receiver.controllers.base import (BaseController,
                                              BaseAsyncControllerWrapper)

LOG = logging.getLogger(__name__)
SPARK_LOGS_BUCKET_NAME = 'spark-logs'


class LogsBulkController(BaseController):
    QUEUE_NAME = 'process-logs'
    EXCHANGE_NAME = 'pharos-tasks'
    RETRY_POLICY = {'max_retries': 15, 'interval_start': 0,
                    'interval_step': 1, 'interval_max': 3}

    def __init__(self, config=None):
        super().__init__(config=config)
        self._s3_client = None

    @property
    def s3_client(self):
        if self._s3_client is None:
            s3_params = self.config_cl.read_branch('/minio')
            self._s3_client = boto3.client(
                's3',
                endpoint_url='http://{}:{}'.format(
                    s3_params['host'], s3_params['port']),
                aws_access_key_id=s3_params['access'],
                aws_secret_access_key=s3_params['secret'],
                config=BotoConfig(s3={'addressing_style': 'path'})
            )
            try:
                self._s3_client.create_bucket(Bucket=SPARK_LOGS_BUCKET_NAME)
            except self._s3_client.exceptions.BucketAlreadyOwnedByYou:
                pass
        return self._s3_client

    @staticmethod
    def parse_logs(data):
        """Convert logs from delight agent to list of json strings"""
        # data -> base64 -> gzip -> utf-8 str -> list of json str
        enc = base64.b64decode(data.encode('utf-8'))
        res = gzip.decompress(enc)
        res_str = res.decode('utf-8')
        # string looks like '{"Event": ...}{"Event": ...}...'
        d = res_str.split('}{')
        last = len(d)
        json_list = []
        for i, x in enumerate(d):
            if i == 0:
                x += '}'
            elif i + 1 == last:
                x = '{' + x
            elif i == last:
                continue
            else:
                x = x[1:]
                x = x + '}'
            json_list.append(x)
        return json_list

    def save_logs_to_file(self, data, app_id=None):
        logs_list = self.parse_logs(data)
        filename = str(app_id)
        with open(filename, 'a+') as f:
            for x in logs_list:
                f.write(x)
        return filename

    def upload_to_minio(self, organization_id, filename):
        self.s3_client.upload_file(
            filename, SPARK_LOGS_BUCKET_NAME,
            os.path.join(str(organization_id), filename))

    def get_organization_id(self, app_id):
        # TODO: some logic to get organization id by app_id or by delight agent
        return None

    def save(self, body):
        """Parse spark logs from agent, save them as file, upload file
        to minio"""
        # TODO: rename 'dmAppId' to 'paAppId' for pharos agent
        app_id = body['dmAppId']
        data = body['data']
        organization_id = self.get_organization_id(app_id)
        filename = self.save_logs_to_file(data, app_id)
        self.upload_to_minio(organization_id, filename)
        self.publish_task({
            'organization_id': organization_id,
            'app_id': app_id
        })

    def publish_task(self, task_params):
        queue_conn = QConnection('amqp://{user}:{pass}@{host}:{port}'.format(
            **self.config_cl.read_branch('/rabbit')),
            transport_options=self.RETRY_POLICY)

        task_exchange = Exchange(self.EXCHANGE_NAME, type='direct')
        with producers[queue_conn].acquire(block=True) as producer:
            producer.publish(
                task_params,
                serializer='json',
                exchange=task_exchange,
                declare=[task_exchange],
                routing_key=self.QUEUE_NAME,
                retry=True,
                retry_policy=self.RETRY_POLICY
            )


class LogsBulkAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return LogsBulkController
