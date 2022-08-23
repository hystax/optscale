""""health_indexes_and_tasks_in_q"

Revision ID: b0ffdb5aefef
Revises: 88b1b34c77ce
Create Date: 2021-01-21 16:57:47.151995

"""
import os

from alembic import op
import sqlalchemy as sa
from config_client.client import Client as EtcdClient


# revision identifiers, used by Alembic.
from pymongo import MongoClient
from sqlalchemy import false, and_
from sqlalchemy.orm import Session
from kombu import Connection as QConnection, Exchange, Queue
from kombu.pools import producers

revision = 'b0ffdb5aefef'
down_revision = '88b1b34c77ce'
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
    config_cl = _get_etcd_config_client()
    health = _get_health_collection(config_cl)
    existing_indexes = [x['name'] for x in health.list_indexes()]
    for field in HEALTH_INDEX_FIELDS:
        if field not in existing_indexes:
            health.create_index([(field, 1)], name=field)

    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        org_table = sa.table('organization',
                             sa.Column('deleted_at', sa.Integer()),
                             sa.Column('id', sa.String(36)),
                             sa.Column('is_demo', sa.Boolean()))
        stmt = sa.select([org_table]).where(
            and_(
                org_table.c.deleted_at == 0,
                org_table.c.is_demo == false(),
            )
        )
        orgs = session.execute(stmt)

        queue_conn = QConnection(
            'amqp://{user}:{pass}@{host}:{port}'.format(
                **config_cl.read_branch('/rabbit')),
            transport_options=RETRY_POLICY)
        task_exchange = Exchange('health', type='direct')
        task_queue = Queue(HEALTH_QUEUE, task_exchange, routing_key=HEALTH_QUEUE)
        with producers[queue_conn].acquire(block=True) as producer:
            for org in orgs:
                producer.publish(
                    {'organization_id': org['id']},
                    serializer='json',
                    exchange=task_exchange,
                    declare=[task_exchange, task_queue],
                    routing_key=HEALTH_QUEUE,
                    retry=True,
                    retry_policy=RETRY_POLICY
                )
    finally:
        session.close()


def downgrade():
    config_cl = _get_etcd_config_client()
    health = _get_health_collection(config_cl)
    existing_indexes = [x['name'] for x in health.list_indexes()]
    for field in HEALTH_INDEX_FIELDS:
        if field in existing_indexes:
            health.drop_index(field)
