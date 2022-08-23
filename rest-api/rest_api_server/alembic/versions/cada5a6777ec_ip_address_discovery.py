"""IP address discovery

This migration adds a new discovery type for IP addresses into our MySQL DB.
It also updates existing resource-related MongoDB entries with new type name.

Revision ID: cada5a6777ec
Revises: 20c5be16bc87
Create Date: 2021-07-12 09:10:22.994050

"""
import datetime
import logging
import os
import uuid

import sqlalchemy as sa
from alembic import op
from config_client.client import Client as EtcdClient
from pymongo import MongoClient
from sqlalchemy import insert, select, String, Integer
from sqlalchemy.orm import Session
from sqlalchemy.sql import table, column

# revision identifiers, used by Alembic.
revision = 'cada5a6777ec'
down_revision = '20c5be16bc87'
branch_labels = None
depends_on = None

LOG = logging.getLogger(__name__)
DEFAULT_ETCD_HOST = 'etcd-client'
DEFAULT_ETCD_PORT = 80
CHUNK_SIZE = 1000
IP_ADDRESS_SQL_TYPE = 'ip_address'
IP_ADDRESS_MONGO_TYPE = 'IP Address'
CURRENT_DISCOVERY_TYPES = ('instance', 'volume', 'snapshot', 'bucket',
                           'k8s_pod', 'snapshot_chain', 'rds_instance')
CURRENT_CLOUD_TYPES = ('openstack', 'openstack_cnr', 'openstack_huawei_cnr',
                       'aws_cnr', 'alibaba_cnr', 'vmware_cnr', 'azure_cnr',
                       'fake', 'kubernetes_cnr')
# aws ip resource type name is already set to 'IP Address',
# so need to set expenses and resources for azure and alibaba
CLOUD_RESOURCE_TYPE_MAP = {
    'azure_cnr': 'Public IP',
    'alibaba_cnr': 'Elastic IP'
}

old_discovery_info_types = sa.Enum(*CURRENT_DISCOVERY_TYPES)
new_discovery_info_types = sa.Enum(
    *CURRENT_DISCOVERY_TYPES, IP_ADDRESS_SQL_TYPE)


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


def _get_active_cloud_account_ids(session, cloud_type=None):
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
    active_cloud_account_ids = [
        cloud_info['id'] for cloud_info in active_cloud_accounts]
    return active_cloud_account_ids


def _upgrade_discovery_info(session):
    op.alter_column('discovery_info', 'resource_type',
                    existing_type=old_discovery_info_types,
                    type_=new_discovery_info_types, nullable=False)
    active_cloud_account_ids = _get_active_cloud_account_ids(session)
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
            resource_type=IP_ADDRESS_SQL_TYPE,
            created_at=dt,
            deleted_at=0,
            last_discovery_at=0,
        )
        session.execute(ins_stmt)
    session.commit()


def _downgrade_discovery_info():
    ct = sa.sql.table('discovery_info',
                      sa.sql.column('resource_type', new_discovery_info_types))
    op.execute(
        ct.delete().where(ct.c.resource_type.in_([IP_ADDRESS_SQL_TYPE])))
    op.alter_column('discovery_info', 'resource_type',
                    existing_type=new_discovery_info_types,
                    type_=old_discovery_info_types, nullable=False)


def _upgrade_resource_types(session):
    mongo_client = _get_mongo_client()
    expenses_collection = mongo_client.restapi.expenses
    group_collection = mongo_client.restapi.expenses_group_month_resource
    resources_collection = mongo_client.restapi.resources

    for cloud_type, source_resource_type in CLOUD_RESOURCE_TYPE_MAP.items():
        active_cloud_account_ids = _get_active_cloud_account_ids(session,
                                                                 cloud_type=cloud_type)
        for cloud_account_id in active_cloud_account_ids:
            cloud_resource_ids = list(x['cloud_resource_id'] for x in
                                      resources_collection.find({'resource_type': source_resource_type,
                                                                 'cloud_account_id': cloud_account_id},
                                                                ['cloud_resource_id']))
            for i in range(0, len(cloud_resource_ids), CHUNK_SIZE):
                update_filter = {
                    'cloud_account_id': cloud_account_id,
                    'cloud_resource_id': {'$in': cloud_resource_ids[i:i + CHUNK_SIZE]},
                }
                update_cmd = {'$set': {'resource_type': IP_ADDRESS_MONGO_TYPE}}
                expenses_collection.update_many(update_filter, update_cmd)
                group_collection.update_many(update_filter, update_cmd)
                resources_collection.update_many(update_filter, update_cmd)


def _downgrade_resource_types(session):
    mongo_client = _get_mongo_client()
    expenses_collection = mongo_client.restapi.expenses
    group_collection = mongo_client.restapi.expenses_group_month_resource
    resources_collection = mongo_client.restapi.resources
    for cloud_type, source_resource_type in CLOUD_RESOURCE_TYPE_MAP.items():
        active_cloud_account_ids = _get_active_cloud_account_ids(session,
                                                                 cloud_type=cloud_type)
        for cloud_account_id in active_cloud_account_ids:
            cloud_resource_ids = list(x['cloud_resource_id'] for x in
                                      resources_collection.find({'resource_type': IP_ADDRESS_MONGO_TYPE,
                                                                 'cloud_account_id': cloud_account_id},
                                                                ['cloud_resource_id']))
            for i in range(0, len(cloud_resource_ids), CHUNK_SIZE):
                update_filter = {
                    'cloud_account_id': cloud_account_id,
                    'cloud_resource_id': {'$in': cloud_resource_ids[i:i + CHUNK_SIZE]},
                }
                update_cmd = {'$set': {'resource_type': source_resource_type}}
                expenses_collection.update_many(update_filter, update_cmd)
                group_collection.update_many(update_filter, update_cmd)
                resources_collection.update_many(update_filter, update_cmd)


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        LOG.info('Upgrading discovery info...')
        _upgrade_discovery_info(session)
        LOG.info('Upgrading resource types...')
        _upgrade_resource_types(session)
        LOG.info('Done!')
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        LOG.info('Downgrading discovery info...')
        _downgrade_discovery_info()
        LOG.info('Downgrading resource types...')
        _downgrade_resource_types(session)
        LOG.info('Done!')
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
