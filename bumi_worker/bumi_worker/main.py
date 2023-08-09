#!/usr/bin/env python
import os
import requests

from kombu import Connection, Exchange, Queue, Consumer
from kombu.log import get_logger
from kombu.mixins import ConsumerProducerMixin
from kombu.utils.debug import setup_logging

from requests.packages.urllib3.exceptions import InsecureRequestWarning

from bumi_worker.transitions import (
    TASKS_TRANSITIONS, GROUP_TASKS_TRANSITIONS)

from config_client.client import Client as ConfigClient


EXCHANGE_NAME = 'bumi-tasks'
DLX_EXCHANGE_NAME = '%s-dlx' % EXCHANGE_NAME
QUEUE_NAME = 'bumi-task'
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
LOG = get_logger(__name__)
DEFAULT_ETCD_HOST = 'etcd'
DEFAULT_ETCD_PORT = 80


class Worker(ConsumerProducerMixin):
    def __init__(self, connection, config_cl):
        self.connection = connection
        self.config_cl = config_cl
        self._rest_cl = None

    def get_consumers(self, Consumer, channel):
        return [Consumer(queues=[task_queue], accept=['json'],
                         callbacks=[self.process_task], prefetch_count=50)]

    def on_connection_revived(self):
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

    def create_children(self, tasks_params):
        for task_params in tasks_params:
            self.put_task(task_params)

    def process_task(self, body, message):
        try:
            transitions_map = TASKS_TRANSITIONS
            if body.get('module') is not None:
                transitions_map = GROUP_TASKS_TRANSITIONS
            task = transitions_map[body['state']]
        except Exception as ex:
            LOG.exception(
                'Failed to get task %s(%s), state %s: %s',
                body.get('created_at'), body.get('organization_id'),
                body.get('state'), str(ex))
            message.ack()
            return

        try:
            task(body=body, message=message,
                 config_cl=self.config_cl,
                 on_continue_cb=self.put_task,
                 create_children_cb=self.create_children).execute()
        except Exception as exc:
            LOG.exception('Task execution failed: %s - %s', type(exc), str(exc))
            raising_exceptions = tuple(
                [BrokenPipeError, ConnectionResetError, TimeoutError])
            if isinstance(exc, raising_exceptions):
                raise


if __name__ == '__main__':
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    setup_logging(loglevel='INFO', loggers=[''])

    config_cl = ConfigClient(
        host=os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST),
        port=int(os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT)),
    )
    config_cl.wait_configured()
    conn_str = 'amqp://localhost'
    with Connection(conn_str) as conn:
        try:
            worker = Worker(conn, config_cl)
            worker.run()
        except KeyboardInterrupt:
            print('bye bye')
