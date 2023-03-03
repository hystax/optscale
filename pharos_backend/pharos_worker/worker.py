#!/usr/bin/env python
import os
import config_client.client
from kombu import Connection, Exchange, Queue
from kombu.log import get_logger
from kombu.mixins import ConsumerProducerMixin
from kombu.utils.debug import setup_logging


EXCHANGE_NAME = 'pharos-tasks'
QUEUE_NAME = 'process-logs'
task_exchange = Exchange(EXCHANGE_NAME, type='direct')
task_queue = Queue(QUEUE_NAME, task_exchange, routing_key=QUEUE_NAME)
LOG = get_logger(__name__)
DEFAULT_ETCD_HOST = 'etcd'
DEFAULT_ETCD_PORT = 80


class Worker(ConsumerProducerMixin):
    def __init__(self, connection, config_cl):
        self.connection = connection
        self.config_cl = config_cl

    def get_consumers(self, Consumer, channel):
        return [Consumer(queues=[task_queue], accept=['json'],
                         callbacks=[self.process_task])]

    def _process_task(self, body):
        pass

    def process_task(self, body, message):
        try:
            LOG.info('Started processing for task: %s' % body)
            self._process_task(body)
        except Exception as exc:
            LOG.exception('Task execution failed: %s', str(exc))
        message.ack()


if __name__ == '__main__':
    setup_logging(loglevel='INFO', loggers=[''])
    config_cl = config_client.client.Client(
        host=os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST),
        port=int(os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT))
    )
    config_cl.wait_configured()
    conn_str = 'amqp://{user}:{pass}@{host}:{port}'.format(
        **config_cl.read_branch('/rabbit'))
    with Connection(conn_str) as conn:
        try:
            worker = Worker(conn, config_cl)
            worker.run()
        except KeyboardInterrupt:
            print('bye bye')
