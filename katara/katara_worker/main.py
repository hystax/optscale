#!/usr/bin/env python
import os
import requests

from requests.packages.urllib3.exceptions import InsecureRequestWarning
from kombu import Connection, Exchange, Queue
from kombu.log import get_logger
from kombu.mixins import ConsumerProducerMixin
from kombu.pools import producers
from kombu.utils.debug import setup_logging

from katara_worker.transitions import TASKS_TRANSITIONS

from config_client.client import Client as ConfigClient
from katara_client.client import Client as KataraClient


EXCHANGE_NAME = 'katara-tasks'
QUEUE_NAME = 'katara-task'
task_exchange = Exchange(EXCHANGE_NAME, type='direct')
task_queue = Queue(QUEUE_NAME, task_exchange, routing_key=QUEUE_NAME)
LOG = get_logger(__name__)
DEFAULT_ETCD_HOST = 'etcd'
DEFAULT_ETCD_PORT = 80


class Worker(ConsumerProducerMixin):
    def __init__(self, connection, config_cl):
        self.connection = connection
        self.config_cl = config_cl
        self._auth_cl = None
        self._rest_cl = None
        self._katara_cl = None
        self._herald_routing_key = None

    @property
    def katara_cl(self):
        if self._katara_cl is None:
            self._katara_cl = KataraClient(
                url=self.config_cl.katara_url(), verify=False)
            self._katara_cl.secret = self.config_cl.cluster_secret()
        return self._katara_cl

    @property
    def herald_routing_key(self):
        if not self._herald_routing_key:
            self._herald_routing_key = self.config_cl.events_queue()
        return self._herald_routing_key

    def get_consumers(self, Consumer, channel):
        return [Consumer(queues=[task_queue], accept=['json'],
                         callbacks=[self.process_task])]

    def put_herald_task(self, task_params):
        task_exchange = Exchange(type='direct')
        with producers[self.connection].acquire(block=True) as producer:
            producer.publish(
                task_params,
                serializer='json',
                exchange=task_exchange,
                declare=[task_exchange],
                routing_key=self.herald_routing_key,
                retry=True
            )

    def put_task(self, task_params):
        self.producer.publish(
            task_params,
            serializer='json',
            exchange=task_exchange,
            declare=[task_exchange],
            routing_key=QUEUE_NAME,
            retry=True,
        )

    def process_task(self, body, message):
        try:
            _, katara_task = self.katara_cl.task_get(body['task_id'])
            task = TASKS_TRANSITIONS[katara_task['state']]
        except Exception as ex:
            LOG.exception('Failed to get task %s: %s', body['task_id'], str(ex))
            message.ack()
            return

        try:
            task(body=body, message=message,
                 config_cl=self.config_cl,
                 on_continue_cb=self.put_task,
                 on_complete_cb=self.put_herald_task).run()
        except Exception as exc:
            LOG.exception('Task execution failed: %s', str(exc))


if __name__ == '__main__':
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    setup_logging(loglevel='INFO', loggers=[''])

    config_cl = ConfigClient(
        host=os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST),
        port=int(os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT)),
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
