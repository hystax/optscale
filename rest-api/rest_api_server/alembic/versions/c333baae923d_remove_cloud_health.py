"""remove_cloud_health

Revision ID: c333baae923d
Revises: 3575a7a8b8dd
Create Date: 2022-10-10 15:30:54.852161

"""
import os
from alembic import op
import sqlalchemy as sa

from config_client.client import Client as EtcdClient
from pymongo import MongoClient
from kombu import Connection as QConnection, Exchange, Queue


# revision identifiers, used by Alembic.
revision = 'c333baae923d'
down_revision = '3575a7a8b8dd'
branch_labels = None
depends_on = None


DEFAULT_ETCD_HOST = 'etcd-client'
DEFAULT_ETCD_PORT = 80
HEALTH_QUEUE = 'health'
RETRY_POLICY = {'max_retries': 15, 'interval_start': 0,
                'interval_step': 1, 'interval_max': 3}
HEALTH_INDEX_FIELDS = [
    'created_at',
    'organization_id',
]


def _get_etcd_config_client():
    etcd_host = os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST)
    etcd_port = os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT)
    config_cl = EtcdClient(host=etcd_host, port=int(etcd_port))
    return config_cl


def _get_health_collection(config_cl):
    mongo_params = config_cl.mongo_params()
    mongo_conn_string = "mongodb://%s:%s@%s:%s" % mongo_params[:-1]
    mongo_client = MongoClient(mongo_conn_string)
    return mongo_client.restapi.health


def upgrade():
    config_client = _get_etcd_config_client()
    _get_health_collection(config_client).drop()
    queue_conn = QConnection(
            'amqp://{user}:{pass}@{host}:{port}'.format(
                **config_client.read_branch('/rabbit')),
            transport_options=RETRY_POLICY)
    queue_conn.connect()
    task_exchange = Exchange('health', type='direct')
    bound_task_exchange = task_exchange(queue_conn.channel())
    task_queue = Queue(HEALTH_QUEUE, task_exchange, routing_key=HEALTH_QUEUE)
    bound_task_queue = task_queue(queue_conn.channel())
    bound_task_queue.delete()
    bound_task_exchange.delete()


def downgrade():
    config_cl = _get_etcd_config_client()
    health = _get_health_collection(config_cl)
    existing_indexes = [x['name'] for x in health.list_indexes()]
    for field in HEALTH_INDEX_FIELDS:
        if field not in existing_indexes:
            health.create_index([(field, 1)], name=field)
