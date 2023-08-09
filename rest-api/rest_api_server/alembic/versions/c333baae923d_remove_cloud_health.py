"""remove_cloud_health

Revision ID: c333baae923d
Revises: 3575a7a8b8dd
Create Date: 2022-10-10 15:30:54.852161

"""
import os
from alembic import op
import sqlalchemy as sa

from pymongo import MongoClient
from kombu import Connection as QConnection, Exchange, Queue


# revision identifiers, used by Alembic.
revision = 'c333baae923d'
down_revision = '3575a7a8b8dd'
branch_labels = None
depends_on = None


HEALTH_QUEUE = 'health'
RETRY_POLICY = {'max_retries': 15, 'interval_start': 0,
                'interval_step': 1, 'interval_max': 3}
HEALTH_INDEX_FIELDS = [
    'created_at',
    'organization_id',
]


def _get_health_collection(config_cl):
    mongo_params = config_cl.mongo_params()
    mongo_conn_string = "mongodb://localhost:27017/humalect-local-main"
    mongo_client = MongoClient(mongo_conn_string)
    return mongo_client.restapi.health


def upgrade():
    queue_conn = QConnection(
            'amqp://localhost',
            transport_options=RETRY_POLICY)
    queue_conn.connect()
    task_exchange = Exchange('health', type='direct')
    bound_task_exchange = task_exchange(queue_conn.channel())
    task_queue = Queue(HEALTH_QUEUE, task_exchange, routing_key=HEALTH_QUEUE)
    bound_task_queue = task_queue(queue_conn.channel())
    bound_task_queue.delete()
    bound_task_exchange.delete()


def downgrade():
    return True
