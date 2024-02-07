import logging
import os
from datetime import datetime, timedelta
from kombu import Connection as QConnection, Exchange
from kombu.pools import producers
from pymongo import MongoClient
from optscale_client.config_client.client import Client as ConfigClient

LOG = logging.getLogger(__name__)
DEMO_LIFETIME_DAYS = 2
DEMO_COUNT = 5
RETRY_POLICY = {'max_retries': 15, 'interval_start': 0,
                'interval_step': 1, 'interval_max': 3}
ROUTING_KEY = 'live-demo-generation'
EXCHANGE_NAME = 'live-demo-generations'


def publish_tasks(config_client, count):
    queue_conn = QConnection('amqp://{user}:{pass}@{host}:{port}'.format(
        **config_client.read_branch('/rabbit')),
        transport_options=RETRY_POLICY)
    task_exchange = Exchange(EXCHANGE_NAME, type='direct')
    with producers[queue_conn].acquire(block=True) as producer:
        for _ in range(0, count):
            producer.publish(
                {},
                serializer='json',
                exchange=task_exchange,
                declare=[task_exchange],
                routing_key=ROUTING_KEY,
                retry=True,
                retry_policy=RETRY_POLICY
            )


def main(config_client):
    mongo_params = config_client.mongo_params()
    mongo_conn_string = "mongodb://%s:%s@%s:%s" % mongo_params[:-1]
    mongo_cl = MongoClient(mongo_conn_string)
    live_demos_collection = mongo_cl.restapi.live_demos
    dt = datetime.utcnow() - timedelta(days=DEMO_LIFETIME_DAYS)
    count = DEMO_COUNT - live_demos_collection.count_documents({
        'created_at': {'$gte': int(dt.timestamp())}
    })
    if count > 0:
        publish_tasks(config_client, count)
        LOG.info('Published %s tasks', count)
    deleted = live_demos_collection.delete_many({
        'created_at': {'$lt': int(dt.timestamp())}
    }).deleted_count
    if deleted:
        LOG.info('Deleted %s old live demos', deleted)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    config_cl = ConfigClient(
        host=os.environ.get('HX_ETCD_HOST'),
        port=int(os.environ.get('HX_ETCD_PORT')),
    )
    config_cl.wait_configured()
    main(config_cl)
