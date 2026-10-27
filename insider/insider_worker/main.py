#!/usr/bin/env python
import os
from datetime import datetime, timezone

import urllib3
from etcd import Lock as EtcdLock
from pymongo import MongoClient
from kombu.mixins import ConsumerMixin
from kombu.log import get_logger
from kombu import Connection
from kombu.utils.debug import setup_logging
from kombu import Exchange, Queue

from optscale_client.config_client.client import Client as ConfigClient
from insider.insider_worker.migrator import Migrator
from insider.insider_worker.processors.factory import get_processor_class


EXCHANGE_NAME = 'insider-tasks'
QUEUE_NAME = 'insider-task'
LOG = get_logger(__name__)
TASK_EXCHANGE = Exchange(EXCHANGE_NAME, type='direct')
TASK_QUEUE = Queue(QUEUE_NAME, TASK_EXCHANGE, routing_key=QUEUE_NAME)
DISCOVERIES_THRESHOLD = 43200  # 12 hours in seconds


class InsiderWorker(ConsumerMixin):
    def __init__(self, connection, config_cl):
        self.connection = connection
        self.config_cl = config_cl
        self._mongo_client = None

    @property
    def mongo_client(self):
        if not self._mongo_client:
            mongo_params = self.config_cl.mongo_params()
            self._mongo_client = MongoClient(mongo_params[0])
        return self._mongo_client

    @property
    def discoveries(self):
        return self.mongo_client.insider.discoveries

    def get_consumers(self, consumer, channel):
        return [consumer(queues=[TASK_QUEUE], accept=['json'],
                         callbacks=[self.process_task], prefetch_count=1)]

    def get_last_discovery_ts(self, cloud_type):
        discoveries = self.discoveries.find(
            {'cloud_type': cloud_type, 'completed_at': {'$ne': 0}}
        ).sort(
            [('completed_at', -1)]).limit(1)
        try:
            discovery = next(discoveries)
            return discovery.get('started_at', 0)
        except StopIteration:
            return 0

    def _process_task(self, task):
        start_process_time = int(datetime.now(tz=timezone.utc).timestamp())
        cloud_type = task.get('cloud_type')
        if not cloud_type:
            raise Exception('Invalid task received: {}'.format(task))
        last_discovery_ts = self.get_last_discovery_ts(cloud_type)
        if last_discovery_ts + DISCOVERIES_THRESHOLD >= start_process_time:
            LOG.info('Skipping task for %s by threshold', cloud_type)
            return
        discovery_id = self.discoveries.insert_one({
            'cloud_type': cloud_type,
            'started_at': start_process_time,
            'completed_at': 0
        }).inserted_id

        get_processor_class(cloud_type)(
            self.mongo_client, self.config_cl).process_prices(last_discovery_ts)

        end_process_time = int(datetime.now(tz=timezone.utc).timestamp())
        self.discoveries.update_one(
            filter={'_id': discovery_id},
            update={'$set': {'completed_at': end_process_time}}
        )
        LOG.info('Prices received for cloud_type %s with discovery_id %s. '
                 'Completed at %s, price processing was provided during %s seconds.',
                 cloud_type, discovery_id, end_process_time,
                 end_process_time - start_process_time)

    def process_task(self, body, message):
        try:
            LOG.info('Started processing for task: %s', body)
            self._process_task(body)
        except Exception as exc:
            LOG.exception('Prices discovery failed: %s', str(exc))
        message.ack()


if __name__ == '__main__':
    urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)
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
            migrator = Migrator(
                config_cl, 'insider', 'insider/insider_worker/migrations')
            with EtcdLock(config_cl, 'insider_migrations'):
                migrator.migrate()
            worker = InsiderWorker(conn, config_cl)
            worker.run()
        except KeyboardInterrupt:
            LOG.info('Shutdown received')
