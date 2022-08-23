import logging
import os
from kombu import Connection as QConnection, Exchange
from kombu.pools import producers
from config_client.client import Client as ConfigClient

LOG = logging.getLogger(__name__)
DEFAULT_ETCD_HOST = 'etcd'
DEFAULT_ETCD_PORT = 80
RETRY_POLICY = {'max_retries': 15, 'interval_start': 0,
                'interval_step': 1, 'interval_max': 3}
SUPPORTED_CLOUD_TYPES = ['azure_cnr']


def publish_tasks(config_cl):
    queue_conn = QConnection('amqp://{user}:{pass}@{host}:{port}'.format(
        **config_cl.read_branch('/rabbit')),
        transport_options=RETRY_POLICY)

    task_exchange = Exchange('insider-tasks', type='direct')
    with producers[queue_conn].acquire(block=True) as producer:
        for cloud_type in SUPPORTED_CLOUD_TYPES:
            producer.publish(
                {'cloud_type': cloud_type},
                serializer='json',
                exchange=task_exchange,
                declare=[task_exchange],
                routing_key='insider-task',
                retry=True,
                retry_policy=RETRY_POLICY
            )
            LOG.info('Task published for cloud_type %s', cloud_type)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    etcd_host = os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST)
    etcd_port = int(os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT))

    config_cl = ConfigClient(host=etcd_host, port=etcd_port)
    config_cl.wait_configured()
    publish_tasks(config_cl)
