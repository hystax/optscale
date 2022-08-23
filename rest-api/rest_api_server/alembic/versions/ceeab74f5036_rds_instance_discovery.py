"""RDS instance discovery

This migration adds a new discovery type for RDS instances into our MySQL DB.
It also updates existing resource-related MongoDB entries with new type name.

Revision ID: ceeab74f5036
Revises: 28199397c343
Create Date: 2021-06-30 16:11:44.994050

"""
import datetime
import logging
import os
import uuid

import sqlalchemy as sa
from alembic import op
from config_client.client import Client as EtcdClient
from pymongo import MongoClient, UpdateMany, DeleteMany
from sqlalchemy import insert, select, String, Integer
from sqlalchemy.orm import Session
from sqlalchemy.sql import table, column

# revision identifiers, used by Alembic.
revision = 'ceeab74f5036'
down_revision = '28199397c343'
branch_labels = None
depends_on = None

LOG = logging.getLogger(__name__)
DEFAULT_ETCD_HOST = 'etcd-client'
DEFAULT_ETCD_PORT = 80
CHUNK_SIZE = 1000
RDS_INSTANCE_SQL_TYPE = 'rds_instance'
RDS_INSTANCE_MONGO_TYPE = 'RDS Instance'
CURRENT_DISCOVERY_TYPES = ('instance', 'volume', 'snapshot', 'bucket',
                           'k8s_pod', 'snapshot_chain')
CURRENT_CLOUD_TYPES = ('openstack', 'openstack_cnr', 'openstack_huawei_cnr',
                       'aws_cnr', 'alibaba_cnr', 'vmware_cnr', 'azure_cnr',
                       'fake', 'kubernetes_cnr')

old_discovery_info_types = sa.Enum(*CURRENT_DISCOVERY_TYPES)
new_discovery_info_types = sa.Enum(
    *CURRENT_DISCOVERY_TYPES, RDS_INSTANCE_SQL_TYPE)


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


def _get_active_cloud_account_ids(cloud_type=None):
    bind = op.get_bind()
    session = Session(bind=bind)
    cloud_acc_table = table(
        'cloudaccount',
        column('id', sa.String(36)),
        column('type', sa.Enum(CURRENT_CLOUD_TYPES)),
        column('deleted_at', Integer())
    )
    active_cloud_accounts_stmt = select([cloud_acc_table.c.id]).where(
        cloud_acc_table.c.deleted_at == 0)
    if cloud_type is not None:
        active_cloud_accounts_stmt = active_cloud_accounts_stmt.where(
            cloud_acc_table.c.type == cloud_type)
    active_cloud_accounts = session.execute(active_cloud_accounts_stmt)
    session.close()
    active_cloud_account_ids = [
        cloud_info['id'] for cloud_info in active_cloud_accounts]
    return active_cloud_account_ids


def _upgrade_discovery_info():
    op.alter_column('discovery_info', 'resource_type',
                    existing_type=old_discovery_info_types,
                    type_=new_discovery_info_types, nullable=False)
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        active_cloud_account_ids = _get_active_cloud_account_ids()
        d_info_table = table(
            'discovery_info',
            column('id', String(36)),
            column('cloud_account_id', String(36)),
            column('resource_type', String(36)),
            column('created_at', Integer()),
            column('deleted_at', Integer()),
            column('last_discovery_at', sa.Integer()),
        )
        for active_cloud_account_id in active_cloud_account_ids:
            dt = datetime.datetime.utcnow().timestamp()
            ins_stmt = insert(d_info_table).values(
                id=str(uuid.uuid4()),
                cloud_account_id=active_cloud_account_id,
                resource_type=RDS_INSTANCE_SQL_TYPE,
                created_at=dt,
                deleted_at=0,
                last_discovery_at=0,
            )
            session.execute(ins_stmt)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def _downgrade_discovery_info():
    ct = sa.sql.table('discovery_info',
                      sa.sql.column('resource_type', new_discovery_info_types))
    op.execute(
        ct.delete().where(ct.c.resource_type.in_([RDS_INSTANCE_SQL_TYPE])))
    op.alter_column('discovery_info', 'resource_type',
                    existing_type=new_discovery_info_types,
                    type_=old_discovery_info_types, nullable=False)


def _upgrade_resource_types():
    mongo_client = _get_mongo_client()
    expenses_collection = mongo_client.restapi.expenses
    raw_expenses_collection = mongo_client.restapi.raw_expenses
    group_collection = mongo_client.restapi.expenses_group_month_resource
    resources_collection = mongo_client.restapi.resources
    active_cloud_account_ids = _get_active_cloud_account_ids(
        cloud_type='alibaba_cnr')

    cloud_account_count = len(active_cloud_account_ids)
    for cloud_account_num, cloud_account_id in enumerate(
            active_cloud_account_ids):
        LOG.info(f'[{cloud_account_num + 1}/{cloud_account_count}] '
                 f'Processing Cloud Account ID {cloud_account_id}')
        instance_ids = list(raw_expenses_collection.distinct('resource_id', {
            'cloud_account_id': cloud_account_id, 'ProductCode': 'rds'}))
        for i in range(0, len(instance_ids), CHUNK_SIZE):
            update_filter = {
                'cloud_account_id': cloud_account_id,
                'cloud_resource_id': {'$in': instance_ids[i:i + CHUNK_SIZE]},
            }
            update_cmd = {'$set': {'resource_type': RDS_INSTANCE_MONGO_TYPE}}
            expenses_collection.update_many(update_filter, update_cmd)
            group_collection.update_many(update_filter, update_cmd)
            resources_collection.update_many(update_filter, update_cmd)


def _downgrade_resource_types():
    mongo_client = _get_mongo_client()
    expenses_collection = mongo_client.restapi.expenses
    raw_expenses_collection = mongo_client.restapi.raw_expenses
    group_collection = mongo_client.restapi.expenses_group_month_resource
    resources_collection = mongo_client.restapi.resources
    active_cloud_account_ids = _get_active_cloud_account_ids(
        cloud_type='alibaba_cnr')

    cloud_account_count = len(active_cloud_account_ids)
    for cloud_account_num, cloud_account_id in enumerate(
            active_cloud_account_ids):
        LOG.info(f'[{cloud_account_num + 1}/{cloud_account_count}] '
                 f'Processing Cloud Account ID {cloud_account_id}')

        raw_product_details_map = {
            x['_id']: x['product_detail']
            for x in raw_expenses_collection.aggregate([
                {'$match': {
                    'cloud_account_id': cloud_account_id,
                    'ProductCode': 'rds'
                }},
                {'$group': {
                    '_id': '$resource_id',
                    'product_detail': {'$last': '$ProductDetail'}
                }}
            ])}

        instance_ids = list(resources_collection.distinct(
            'cloud_resource_id', {
                'cloud_account_id': cloud_account_id,
                'resource_type': RDS_INSTANCE_MONGO_TYPE
            }))

        for i in range(0, len(instance_ids), CHUNK_SIZE):
            update_requests = []
            for instance_id in instance_ids[i:i + CHUNK_SIZE]:
                operation_filter = {
                    'cloud_account_id': cloud_account_id,
                    'cloud_resource_id': instance_id,
                }
                downgrade_type = raw_product_details_map.get(instance_id)
                if downgrade_type:
                    update_cmd = {'$set': {'resource_type': downgrade_type}}
                    update_requests.append(UpdateMany(
                        filter=operation_filter, update=update_cmd))
                else:
                    # Resource was created by discovery and has no raw expenses.
                    # Let's delete it.
                    update_requests.append(DeleteMany(filter=operation_filter))
            expenses_collection.bulk_write(update_requests)
            group_collection.bulk_write(update_requests)
            resources_collection.bulk_write(update_requests)


def upgrade():
    LOG.info('Upgrading discovery info...')
    _upgrade_discovery_info()
    LOG.info('Upgrading resource types...')
    _upgrade_resource_types()
    LOG.info('Done!')


def downgrade():
    LOG.info('Downgrading discovery info...')
    _downgrade_discovery_info()
    LOG.info('Downgrading resource types...')
    _downgrade_resource_types()
    LOG.info('Done!')
