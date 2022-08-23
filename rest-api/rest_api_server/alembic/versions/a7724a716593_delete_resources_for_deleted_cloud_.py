"""Delete resources for deleted cloud accounts

Revision ID: a7724a716593
Revises: cada5a6777ec
Create Date: 2021-08-02 09:59:31.333684

"""
from alembic import op
import sqlalchemy as sa
import logging
import os
from datetime import datetime
from config_client.client import Client as EtcdClient
from pymongo import MongoClient
from sqlalchemy import select, Integer
from sqlalchemy.orm import Session
from sqlalchemy.sql import table, column

# revision identifiers, used by Alembic.
revision = 'a7724a716593'
down_revision = 'b8b16ddb0aab'
branch_labels = None
depends_on = None

CHUNK_SIZE = 10000
LOG = logging.getLogger(__name__)
DEFAULT_ETCD_HOST = 'etcd-client'
DEFAULT_ETCD_PORT = 80


def _get_etcd_config_client():
    etcd_host = os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST)
    etcd_port = os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT)
    config_cl = EtcdClient(host=etcd_host, port=int(etcd_port))
    return config_cl


def _get_resources_collection():
    config_cl = _get_etcd_config_client()
    mongo_params = config_cl.mongo_params()
    mongo_conn_string = "mongodb://%s:%s@%s:%s" % mongo_params[:-1]
    mongo_client = MongoClient(mongo_conn_string)
    return mongo_client.restapi.resources



def _get_inactive_cloud_accounts():
    ca_table = table(
        'cloudaccount',
        column('id', sa.String(36)),
        column('deleted_at', Integer())
    )
    inactive_cloud_accounts_stmt = select([ca_table.c.id]).where(
        ca_table.c.deleted_at != 0)
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        inactive_cloud_accounts = session.execute(inactive_cloud_accounts_stmt)
    finally:
        session.close()
    inactive_cloud_account_ids = [
        cloud_info['id'] for cloud_info in inactive_cloud_accounts]
    return inactive_cloud_account_ids


def _delete_cloud_resources(collection, cloud_account_id, new_deleted_at):
    old_deleted_at = 0 if new_deleted_at else {'$ne': 0}
    update = {'$set': {'deleted_at': new_deleted_at}}
    if new_deleted_at:
        update['$unset'] = {'cluster_id': ''}
    found = collection.find({
        'cloud_account_id': cloud_account_id,
        'deleted_at': old_deleted_at
    }).count()
    for i in range(0, found, CHUNK_SIZE):
        resources = collection.find({
            'cloud_account_id': cloud_account_id,
            'deleted_at': old_deleted_at
        }, {'_id': True}).limit(CHUNK_SIZE)
        res_ids = [x['_id'] for x in resources]
        r = collection.update_many(
            filter={
                '_id': {'$in': res_ids}
            },
            update=update
        )
        if r.modified_count != len(res_ids):
            LOG.warning('Delete cloud resources failed - deleted %d of %d;'
                        ' result: %s' %
                        (r.modified_count, len(res_ids), r.raw_result))

def upgrade():
    ca_ids = _get_inactive_cloud_accounts()
    now = int(datetime.utcnow().timestamp())
    res_collection = _get_resources_collection()
    for ca_id in ca_ids:
        _delete_cloud_resources(res_collection, ca_id, now)


def downgrade():
    ca_ids = _get_inactive_cloud_accounts()
    res_collection = _get_resources_collection()
    for ca_id in ca_ids:
        _delete_cloud_resources(res_collection, ca_id, 0)
