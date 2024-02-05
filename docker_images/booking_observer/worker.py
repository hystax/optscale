#!/usr/bin/env python
import os
import time
from datetime import datetime
from threading import Thread
from pymongo import MongoClient, UpdateOne
from kombu.mixins import ConsumerMixin
from kombu.log import get_logger
from kombu import Connection
from kombu.utils.debug import setup_logging
from kombu import Connection as QConnection, Exchange, Queue
from kombu.pools import producers
import urllib3

from optscale_client.config_client.client import Client as ConfigClient
from optscale_client.rest_api_client.client_v2 import Client as RestClient

BOOKING_OBSERVER_EXCHANGE_NAME = 'booking-activities'
BOOKING_OBSERVER_QUEUE_NAME = 'booking-activity'
ACTIVITIES_EXCHANGE_NAME = 'activities-tasks'
LOG = get_logger(__name__)
BOOKING_OBSERVER_TASK_EXCHANGE = Exchange(
    BOOKING_OBSERVER_EXCHANGE_NAME, type='direct')
BOOKING_OBSERVER_TASK_QUEUE = Queue(
    BOOKING_OBSERVER_QUEUE_NAME, BOOKING_OBSERVER_TASK_EXCHANGE,
    routing_key=BOOKING_OBSERVER_QUEUE_NAME)
RETRY_POLICY = {'max_retries': 15, 'interval_start': 0,
                'interval_step': 1, 'interval_max': 3}


class BookingObserverWorker(ConsumerMixin):
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
                secret=self.config_cl.cluster_secret(),
                verify=False)
        return self._rest_cl

    @property
    def mongo_cl(self):
        if not self._mongo_cl:
            mongo_params = self.config_cl.mongo_params()
            mongo_conn_string = "mongodb://%s:%s@%s:%s" % mongo_params[:-1]
            self._mongo_cl = MongoClient(mongo_conn_string)
        return self._mongo_cl

    def get_consumers(self, consumer, channel):
        return [consumer(queues=[BOOKING_OBSERVER_TASK_QUEUE], accept=['json'],
                         callbacks=[self.process_task], prefetch_count=10)]

    def process_booking_activities(self, task):
        org_id = task.get('organization_id')
        observe_time = task.get('observe_time')
        if not org_id or not observe_time:
            raise Exception('Invalid task received: {}'.format(task))

        start_time = datetime.utcnow()
        self._process(org_id, observe_time)
        LOG.info('Booking observer process for org %s completed in %s seconds',
                 org_id, (datetime.utcnow() - start_time).total_seconds())

    def get_start_date(self, organization_id):
        try:
            observe = next(self.mongo_cl.restapi.webhook_observer.find(
                {'organization_id': organization_id}, ['observe_time']
            ).sort('observe_time', -1).limit(1))
            start_date = observe.get('observe_time', 0)
        except StopIteration:
            start_date = 0
        LOG.info('Last observe time for %s: %s', organization_id, start_date)
        return start_date

    def _update_observe_time(self, observe_time, org_id):
        self.mongo_cl.restapi.webhook_observer.bulk_write([
            UpdateOne(
                filter={'organization_id': org_id},
                update={
                    '$set': {'observe_time': observe_time}
                },
                upsert=True
            )
        ])

    def _process(self, organization_id, observe_time):
        end_date = int(datetime.utcnow().timestamp())
        start_date = self.get_start_date(organization_id)
        _, bookings = self.rest_cl.shareable_book_list(
            organization_id, start_date, end_date)

        tasks = []
        field_action_map = {'acquired_since': 'booking_acquire',
                            'released_at': 'booking_release'}
        for b in bookings['data']:
            for key, action in field_action_map.items():
                value = b[key]
                if value and start_date < value <= end_date:
                    tasks.append({
                        'organization_id': organization_id,
                        'object_type': 'booking',
                        'action': action,
                        'object_id': b['id']
                    })
        self._publish_activities_tasks(tasks)
        self._update_observe_time(observe_time, organization_id)
        LOG.info('%s tasks published for org: %s', len(tasks), organization_id)

    def _publish_activities_tasks(self, tasks):
        queue_conn = QConnection('amqp://{user}:{pass}@{host}:{port}'.format(
            **self.config_cl.read_branch('/rabbit')),
            transport_options=RETRY_POLICY)
        task_exchange = Exchange(ACTIVITIES_EXCHANGE_NAME, type='topic')
        with producers[queue_conn].acquire(block=True) as producer:
            for task_params in tasks:
                producer.publish(
                    task_params,
                    serializer='json',
                    exchange=task_exchange,
                    declare=[task_exchange],
                    routing_key='booking.action.{}'.format(
                        task_params.get('action')),
                    retry=True,
                    retry_policy=RETRY_POLICY
                )

    def process_task(self, body, message):
        try:
            self.process_booking_activities(body)
        except Exception as exc:
            LOG.exception('Booking observe failed: %s', str(exc))
        message.ack()

    def heartbeat(self):
        while self.running:
            self.connection.heartbeat_check()
            time.sleep(1)


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
            worker = BookingObserverWorker(conn, config_cl)
            worker.run()
        except KeyboardInterrupt:
            worker.running = False
            worker.thread.join()
            LOG.info('Shutdown received')
