#!/usr/bin/env python
import os
import time

from threading import Thread
from pymongo import MongoClient
from kombu.mixins import ConsumerMixin
from kombu.log import get_logger
from kombu import Connection
from kombu.utils.debug import setup_logging
from kombu import Exchange, Queue
import urllib3
from datetime import datetime

from optscale_client.config_client.client import Client as ConfigClient
from optscale_client.rest_api_client.client_v2 import Client as RestClient

EXCHANGE_NAME = 'live-demo-generations'
QUEUE_NAME = 'live-demo-generation'
task_exchange = Exchange(EXCHANGE_NAME, type='direct')
task_queue = Queue(QUEUE_NAME, task_exchange, routing_key=QUEUE_NAME)
LOG = get_logger(__name__)


class LiveDemoGenerator(ConsumerMixin):
    def __init__(self, connection, config_client):
        self.connection = connection
        self.config_cl = config_client
        self._rest_cl = None
        self.running = True
        self.thread = Thread(target=self.heartbeat)
        self.thread.start()
        self._mongo_cl = None

    @property
    def rest_cl(self):
        if self._rest_cl is None:
            self._rest_cl = RestClient(
                url=self.config_cl.restapi_url(),
                secret=self.config_cl.cluster_secret()
            )
        return self._rest_cl

    @property
    def mongo_cl(self):
        if not self._mongo_cl:
            mongo_params = self.config_cl.mongo_params()
            mongo_conn_string = "mongodb://%s:%s@%s:%s" % mongo_params[:-1]
            self._mongo_cl = MongoClient(mongo_conn_string)
        return self._mongo_cl

    def get_consumers(self, Consumer, channel):
        return [Consumer(queues=[task_queue], accept=['json'],
                         callbacks=[self.process_task], prefetch_count=1)]

    def process_task(self, body, message):
        try:
            self.generate_live_demo()
        except Exception as exc:
            LOG.exception('Live demo generation failed: %s', str(exc))
        message.ack()

    def heartbeat(self):
        while self.running:
            self.connection.heartbeat_check()
            time.sleep(1)

    def generate_live_demo(self):
        d_start = datetime.utcnow()
        _, response = self.rest_cl.live_demo_create()
        response['created_at'] = int(d_start.timestamp())
        self.mongo_cl.restapi.live_demos.insert_one(response)
        LOG.info('Live demo generated in %s seconds',
                 (datetime.utcnow() - d_start).total_seconds())


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
            worker = LiveDemoGenerator(conn, config_cl)
            worker.run()
        except KeyboardInterrupt:
            worker.running = False
            worker.thread.join()
            LOG.info('Shutdown received')
