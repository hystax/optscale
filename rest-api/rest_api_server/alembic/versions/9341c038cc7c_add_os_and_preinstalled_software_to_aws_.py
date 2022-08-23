"""Add os and preinstalled software to AWS resources

Revision ID: 9341c038cc7c
Revises: cada5a6777ec
Create Date: 2021-07-30 08:53:13.599646

"""
import logging

from alembic import op
import sqlalchemy as sa
import os
from config_client.client import Client as EtcdClient
from pymongo import MongoClient, UpdateOne
from sqlalchemy import select, Integer, and_
from sqlalchemy.orm import Session
from sqlalchemy.sql import table, column


# revision identifiers, used by Alembic.
revision = '9341c038cc7c'
down_revision = 'cada5a6777ec'
branch_labels = None
depends_on = None

LOG = logging.getLogger(__name__)
CHUNK_SIZE = 1000
DEFAULT_ETCD_HOST = 'etcd-client'
DEFAULT_ETCD_PORT = 80
CURRENT_CLOUD_TYPES = ('openstack', 'openstack_cnr', 'openstack_huawei_cnr',
                       'aws_cnr', 'alibaba_cnr', 'vmware_cnr', 'azure_cnr',
                       'fake', 'kubernetes_cnr')


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


def _get_raw_exp_collection():
    config_cl = _get_etcd_config_client()
    mongo_params = config_cl.mongo_params()
    mongo_conn_string = "mongodb://%s:%s@%s:%s" % mongo_params[:-1]
    mongo_client = MongoClient(mongo_conn_string)
    return mongo_client.restapi.raw_expenses


def _get_active_aws_cloud_accounts():
    ca_table = table(
        'cloudaccount',
        column('id', sa.String(36)),
        column('type', sa.Enum(CURRENT_CLOUD_TYPES)),
        column('deleted_at', Integer())
    )
    active_cloud_accounts_stmt = select([ca_table.c.id]).where(and_(
        ca_table.c.deleted_at == 0, ca_table.c.type == 'aws_cnr'))
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        active_cloud_accounts = session.execute(active_cloud_accounts_stmt)
    finally:
        session.close()
    active_cloud_account_ids = [
        cloud_info['id'] for cloud_info in active_cloud_accounts]
    return active_cloud_account_ids


def upgrade():
    ca_ids = _get_active_aws_cloud_accounts()
    res_collection = _get_resources_collection()
    raw_collection = _get_raw_exp_collection()
    for ca_id in ca_ids:
        res_ids = res_collection.distinct('cloud_resource_id', {
            'cloud_account_id': ca_id,
            'resource_type': 'Instance',
            'deleted_at': 0
        })
        for i in range(0, len(res_ids), CHUNK_SIZE):
            chunk = res_ids[i:i + CHUNK_SIZE]
            pipeline = [
                {
                    '$match': {
                        '$and': [
                            {'product/operatingSystem': {'$exists': True}},
                            {'product/preInstalledSw': {'$exists': True}},
                            {'cloud_account_id': ca_id},
                            {'resource_id': {'$in': chunk}}
                        ]
                    }
                },
                {
                    '$group': {
                        '_id': '$resource_id',
                        'os': {'$last': '$product/operatingSystem'},
                        'preinstalled': {'$last': '$product/preInstalledSw'}
                    }
                }
            ]
            resources_info = raw_collection.aggregate(pipeline)
            updates = []
            for row in resources_info:
                updates.append(UpdateOne(
                    filter={
                        'cloud_account_id': ca_id,
                        'cloud_resource_id': row.pop('_id')
                    },
                    update={'$set': row}
                ))
            if updates:
                result = res_collection.bulk_write(updates)
                if len(updates) != result.bulk_api_result.get('nModified'):
                    LOG.warning('Updates (%d) are not fully applied: %s' % (
                        len(updates), result.bulk_api_result))


def downgrade():
    res_collection = _get_resources_collection()
    res_ids = res_collection.distinct('_id', {
        '$or': [
            {'os': {'$exists': True}},
            {'preinstalled': {'$exists': True}}
        ]})
    found = len(res_ids)
    updated = 0
    for i in range(0, found, CHUNK_SIZE):
        result = res_collection.update_many(
            {'_id': {'$in': res_ids[i:i + CHUNK_SIZE]}},
            {'$unset': {'os': '', 'preinstalled': ''}})
        updated += result.modified_count
    if found != updated:
        LOG.warning('Downgrade - found %d, updated %d' % (found, updated))
