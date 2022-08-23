#!/usr/bin/env python
import os
from datetime import datetime
from etcd import Lock as EtcdLock
from kombu.mixins import ConsumerMixin
from kombu.log import get_logger
from kombu import Connection
from kombu.utils.debug import setup_logging
from kombu import Exchange, Queue
from metroculus_worker.migrator import Migrator
from metroculus_worker.processor import MetricsProcessor

from config_client.client import Client as ConfigClient


EXCHANGE_NAME = 'metroculus-tasks'
QUEUE_NAME = 'metroculus-task'
LOG = get_logger(__name__)
TASK_EXCHANGE = Exchange(EXCHANGE_NAME, type='direct')
TASK_QUEUE = Queue(QUEUE_NAME, TASK_EXCHANGE, routing_key=QUEUE_NAME)


class MetroculusWorker(ConsumerMixin):
    def __init__(self, connection, config_cl):
        self.connection = connection
        self.config_cl = config_cl

    def get_consumers(self, consumer, channel):
        return [consumer(queues=[TASK_QUEUE], accept=['json'],
                         callbacks=[self.process_task])]

    def _process_task(self, task):
        start_process_time = datetime.utcnow()
        cloud_account_id = task.get('cloud_account_id')
        processor = MetricsProcessor(self.config_cl, cloud_account_id)
        result = processor.start()
        LOG.info(
            'Metrics received for cloud_account %s (%s resources). '
            'The processing took %s seconds' % (
                cloud_account_id, len(result),
                (datetime.utcnow() - start_process_time).total_seconds()))

    def process_task(self, body, message):
        try:
            self._process_task(body)
        except Exception as exc:
            LOG.exception('Metrics processing failed: %s', str(exc))
        message.ack()


if __name__ == '__main__':
    debug = os.environ.get('DEBUG', False)
    log_level = 'INFO' if not debug else 'DEBUG'
    setup_logging(loglevel=log_level, loggers=[''])

    config_cl = ConfigClient(
        host=os.environ.get('HX_ETCD_HOST'),
        port=int(os.environ.get('HX_ETCD_PORT')),
    )
    config_cl.wait_configured()
    conn_str = 'amqp://{user}:{pass}@{host}:{port}'.format(
        **config_cl.read_branch('/rabbit'))
    with Connection(conn_str) as conn:
        try:
            migrator = Migrator(config_cl)
            with EtcdLock(config_cl, 'metroculus_migrations'):
                migrator.migrate()
            worker = MetroculusWorker(conn, config_cl)
            worker.run()
        except KeyboardInterrupt:
            LOG.info('Shutdown received')
