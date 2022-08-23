"""Rename sls_intl to Log Storage

Revision ID: 9c6bfcfb79b3
Revises: a5e00bf5ea0a
Create Date: 2021-09-10 10:22:57.256102

"""
import logging
import os
from config_client.client import Client as EtcdClient
from pymongo import MongoClient
from alembic import op
import sqlalchemy as sa
from sqlalchemy import table, column, select, Integer
from sqlalchemy.orm import Session

# revision identifiers, used by Alembic.
revision = '9c6bfcfb79b3'
down_revision = 'a5e00bf5ea0a'
branch_labels = None
depends_on = None
DEFAULT_ETCD_HOST = 'etcd-client'
DEFAULT_ETCD_PORT = 80
BULK_SIZE = 1000
LOG = logging.getLogger(__name__)
REPLACED_RESOURCES_TYPES = ('sls_intl', 'Log Storage')


def _get_etcd_config_client():
    etcd_host = os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST)
    etcd_port = os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT)
    config_cl = EtcdClient(host=etcd_host, port=int(etcd_port))
    return config_cl


def _get_mongo_client():
    config_cl = _get_etcd_config_client()
    mongo_params = config_cl.mongo_params()
    mongo_conn_string = "mongodb://%s:%s@%s:%s" % mongo_params[:-1]
    mongo_client = MongoClient(mongo_conn_string)
    return mongo_client


def get_alibaba_ca_ids():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        ca_table = table('cloudaccount',
                         column('id', sa.String(36)),
                         column('type', sa.String(36)),
                         column('deleted_at', Integer()))
        alibaba_ids_stmt = select(
            [ca_table.c.id]).where(
            sa.and_(ca_table.c.type == 'ALIBABA_CNR',
                    ca_table.c.deleted_at == 0))
        alibaba_ids_raw = session.execute(alibaba_ids_stmt)
        alibaba_ids = [x['id'] for x in alibaba_ids_raw]
    finally:
        session.close()
    return alibaba_ids


def update_chunk(collection, bulk_ids, new_type):
    res = collection.update_many({'_id': {'$in': bulk_ids}},
                                 {'$set': {'resource_type': new_type}})
    if res.modified_count != len(bulk_ids):
        LOG.warning('Update cloud resources failed - updated %d of %d;'
                    ' result: %s' %
                    (res.modified_count, len(bulk_ids), res.raw_result))


def upgrade():
    old_type = REPLACED_RESOURCES_TYPES[0]
    new_type = REPLACED_RESOURCES_TYPES[1]
    ca_ids = get_alibaba_ca_ids()
    mongo_client = _get_mongo_client()
    resources_collection = mongo_client.restapi.resources
    expenses_collection = mongo_client.restapi.expenses
    expenses_group = mongo_client.restapi.expenses_group_month_resource
    for collection in [resources_collection, expenses_collection, expenses_group]:
        records = collection.find({'cloud_account_id': {'$in': ca_ids},
                                   'resource_type': old_type}, {'_id': True})
        bulk_ids = []
        for record in records:
            bulk_ids.append(record['_id'])
            if len(bulk_ids) == BULK_SIZE:
                update_chunk(collection, bulk_ids, new_type)
                bulk_ids = []
        if bulk_ids:
            update_chunk(collection, bulk_ids, new_type)



def downgrade():
    old_type = REPLACED_RESOURCES_TYPES[1]
    new_type = REPLACED_RESOURCES_TYPES[0]
    ca_ids = get_alibaba_ca_ids()
    mongo_client = _get_mongo_client()
    resources_collection = mongo_client.restapi.resources
    expenses_collection = mongo_client.restapi.expenses
    expenses_group = mongo_client.restapi.expenses_group_month_resource
    for collection in [resources_collection, expenses_collection, expenses_group]:
        records = collection.find({'cloud_account_id': {'$in': ca_ids},
                                   'resource_type': old_type}, {'_id': True})
        bulk_ids = []
        for record in records:
            bulk_ids.append(record['_id'])
            if len(bulk_ids) == BULK_SIZE:
                update_chunk(collection, bulk_ids, new_type)
                bulk_ids = []
        if bulk_ids:
            update_chunk(collection, bulk_ids, new_type)
