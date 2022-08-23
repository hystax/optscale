""""gb_to_bytes_size"

Revision ID: 69b78adf3fdc
Revises: bd1ca74c5343
Create Date: 2022-03-30 14:39:11.517238

"""
import os
import logging
import sqlalchemy as sa
from alembic import op
from config_client.client import Client as EtcdClient
from pymongo import MongoClient, UpdateOne
from sqlalchemy.orm import Session

# revision identifiers, used by Alembic.
revision = '69b78adf3fdc'
down_revision = 'bd1ca74c5343'
branch_labels = None
depends_on = None


LOG = logging.getLogger(__name__)
BULK_SIZE = 100
BYTES_IN_GB = 1024 * 1024 * 1024
GB_IN_BYTES = 1 / BYTES_IN_GB
RESOURCE_TYPES = ['Snapshot', 'Volume']
SKIPPED_CLOUD_TYPE = 'kubernetes_cnr'
DEFAULT_ETCD_HOST = 'etcd-client'
DEFAULT_ETCD_PORT = 80


def _get_etcd_config_client():
    etcd_host = os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST)
    etcd_port = os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT)
    config_cl = EtcdClient(host=etcd_host, port=int(etcd_port))
    return config_cl


def get_mongo_resources():
    config_cl = _get_etcd_config_client()
    mongo_params = config_cl.mongo_params()
    mongo_conn_string = "mongodb://%s:%s@%s:%s" % mongo_params[:-1]
    mongo_client = MongoClient(mongo_conn_string)
    return mongo_client.restapi.resources


def get_cloud_accounts(session):
    organization_t = sa.table("organization",
                              sa.Column('id', sa.String()),
                              sa.Column('is_demo', sa.Boolean()),
                              sa.Column('deleted_at', sa.Integer()))
    cloud_account_t = sa.table("cloudaccount",
                               sa.Column('id', sa.String()),
                               sa.Column('organization_id', sa.String()),
                               sa.Column('type', sa.String()),
                               sa.Column('deleted_at', sa.Integer()))
    organizations = session.execute(
        sa.select([organization_t.c.id]).where(sa.and_(
            organization_t.c.deleted_at == 0,
            organization_t.c.is_demo.is_(False))))
    cloud_accounts = session.execute(sa.select([cloud_account_t.c.id]).where(
        sa.and_(
            cloud_account_t.c.organization_id.in_([x[0] for x in organizations]),
            cloud_account_t.c.type != SKIPPED_CLOUD_TYPE,
            cloud_account_t.c.deleted_at == 0)))
    return [x[0] for x in cloud_accounts]


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        cloud_accounts = get_cloud_accounts(session)
        LOG.info(cloud_accounts)
    finally:
        session.close()
    mongo_resources = get_mongo_resources()
    resources = mongo_resources.find(
            {'cloud_account_id': {'$in': cloud_accounts},
             'size': {'$exists': True, '$ne': None, '$lte': BYTES_IN_GB},
             'resource_type': {'$in': RESOURCE_TYPES}}, ['_id', 'size'])
    updates = []
    for r in resources:
        updates.extend([UpdateOne(
            filter={'_id': r['_id']},
            update={'$set': {'size': r['size'] * BYTES_IN_GB}})])
    modified = 0
    for i in range(0, len(updates), BULK_SIZE):
        results = mongo_resources.bulk_write(updates[i: i + BULK_SIZE])
        modified += results.modified_count
    LOG.info(f'Updated {modified} rows')


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        cloud_accounts = get_cloud_accounts(session)
    finally:
        session.close()
    mongo_resources = get_mongo_resources()
    resources = mongo_resources.find(
            {'cloud_account_id': {'$in': cloud_accounts},
             'size': {'$exists': True, '$ne': None, '$gte': BYTES_IN_GB},
             'resource_type': {'$in': RESOURCE_TYPES}}, ['_id', 'size'])
    updates = []
    for r in resources:
        updates.extend([UpdateOne(
            filter={'_id': r['_id']},
            update={'$set': {'size': r['size'] * GB_IN_BYTES}})])
    modified = 0
    for i in range(0, len(updates), BULK_SIZE):
        results = mongo_resources.bulk_write(updates[i: i + BULK_SIZE])
        modified += results.modified_count
    LOG.info(f'Updated {modified} rows')
