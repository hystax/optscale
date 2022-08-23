import os
import requests
import time
from threading import Thread
from kombu.mixins import ConsumerMixin
from kombu.log import get_logger
from kombu import Connection
from kombu.utils.debug import setup_logging
from kombu import Exchange, Queue
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from config_client.client import Client as ConfigClient
from rest_api_client.client_v2 import Client as RestClient
from trapper_worker.processor import ProcessorFactory

EXCHANGE_NAME = 'trapper-tasks'
QUEUE_NAME = 'traffic-processing'
LOG = get_logger(__name__)
TASK_EXCHANGE = Exchange(EXCHANGE_NAME, type='direct')
TASK_QUEUE = Queue(QUEUE_NAME, TASK_EXCHANGE, routing_key=QUEUE_NAME)


class TrafficProcessingWorker(ConsumerMixin):
    def __init__(self, connection, config_cl):
        self.connection = connection
        self.config_cl = config_cl
        self._rest_cl = None
        self.running = True
        self.thread = Thread(target=self.heartbeat)
        self.thread.start()

    @property
    def rest_cl(self):
        if self._rest_cl is None:
            self._rest_cl = RestClient(
                url=self.config_cl.restapi_url(),
                secret=self.config_cl.cluster_secret(),
                verify=False)
        return self._rest_cl

    def get_consumers(self, consumer, channel):
        return [consumer(queues=[TASK_QUEUE], accept=['json'],
                         callbacks=[self.process_task])]

    def process_traffic(self, cloud_account_id, cloud_type):
        module = ProcessorFactory.get_module(cloud_type, self.config_cl)
        if not module:
            return
        _, resp = self.rest_cl.traffic_processing_task_list(cloud_account_id)
        tasks = resp['traffic_processing_tasks']
        if tasks:
            module.process(cloud_account_id, tasks)
        for task in tasks:
            self.rest_cl.traffic_processing_task_delete(task['id'])

    def _process_task(self, task):
        cloud_account_id = task.get('cloud_account_id')
        cloud_type = task.get('cloud_type')
        if not cloud_account_id or not cloud_type:
            raise Exception('Invalid task received: {}'.format(task))
        start_time = time.time()
        self.process_traffic(cloud_account_id, cloud_type)
        LOG.info('Traffic processing task for cloud account %s completed in %s',
                 cloud_account_id, time.time() - start_time)

    def process_task(self, body, message):
        try:
            self._process_task(body)
        except Exception as exc:
            LOG.exception('Traffic processing task failed: %s', str(exc))
        message.ack()

    def heartbeat(self):
        while self.running:
            self.connection.heartbeat_check()
            time.sleep(1)


if __name__ == '__main__':
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
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
            worker = TrafficProcessingWorker(conn, config_cl)
            worker.run()
        except KeyboardInterrupt:
            worker.running = False
            worker.thread.join()
            LOG.info('Shutdown received')
