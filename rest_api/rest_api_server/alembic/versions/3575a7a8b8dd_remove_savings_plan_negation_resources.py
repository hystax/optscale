""""remove_savings_plan_negation_resources"

Revision ID: 3575a7a8b8dd
Revises: 8992bafc1505
Create Date: 2022-12-01 10:51:58.489729

"""
from alembic import op
import sqlalchemy as sa
import os
import logging
from alembic import op
from sqlalchemy.orm import Session
from sqlalchemy.sql import table, column
from optscale_client.config_client.client import Client as EtcdClient
from pymongo import MongoClient
from sqlalchemy import Integer, select, String, and_
from clickhouse_driver import Client as ClickHouseClient


# revision identifiers, used by Alembic.
revision = '3575a7a8b8dd'
down_revision = '8992bafc1505'
branch_labels = None
depends_on = None


DEFAULT_ETCD_HOST = 'etcd-client'
DEFAULT_ETCD_PORT = 80
LOG = logging.getLogger(__name__)


def _get_etcd_config_client():
    etcd_host = os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST)
    etcd_port = os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT)
    config_cl = EtcdClient(host=etcd_host, port=int(etcd_port))
    return config_cl


def get_mongo_client():
    config_cl = _get_etcd_config_client()
    mongo_params = config_cl.mongo_params()
    mongo_conn_string = "mongodb://%s:%s@%s:%s" % mongo_params[:-1]
    return MongoClient(mongo_conn_string)


def _get_clickhouse_client():
    config_cl = _get_etcd_config_client()
    user, password, host, db_name = config_cl.clickhouse_params()
    return ClickHouseClient(
        host=host, password=password, database=db_name, user=user)


def get_cloud_account_ids():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        org_t = table('organization',
                      column('id', String(36)),
                      column('deleted_at', Integer()),
                      column('is_demo', Integer()))
        c_acc_t = table('cloudaccount',
                        column('id', String(36)),
                        column('deleted_at', Integer()),
                        column('organization_id', String(36)),
                        column('type', String(36)))
        cmd = select([c_acc_t.c.id]).where(
            and_(c_acc_t.c.organization_id.in_(
                select([org_t.c.id]).where(
                    and_(org_t.c.deleted_at == 0,
                         org_t.c.is_demo.is_(False)))),
                 c_acc_t.c.type == 'AWS_CNR',
                 c_acc_t.c.deleted_at == 0))
        cloud_accounts = session.execute(cmd)
    finally:
        session.close()
    return cloud_accounts


def upgrade():
    mongo_cl = get_mongo_client()
    cloud_accounts = list(get_cloud_account_ids())
    clickhouse_cl = _get_clickhouse_client()
    table_exists = clickhouse_cl.execute("SHOW TABLES LIKE 'expenses'")
    for i, cloud_account in enumerate(cloud_accounts):
        LOG.info('Started deleting resources for '
                 'cloud account {0} ({1}/{2})'.format(
                     cloud_account['id'], i + 1, len(cloud_accounts)))
        cloud_account_id = cloud_account['id']
        resources = mongo_cl.restapi.resources.find({
            'cloud_account_id': cloud_account_id,
            'cloud_resource_id': {'$regex': 'SavingsPlanNegation'}
        }, [])
        resource_ids = list(map(lambda x: x['_id'], resources))
        if not resource_ids:
            continue
        if table_exists:
            clickhouse_cl.execute(
                'ALTER TABLE expenses DELETE WHERE cloud_account_id=%(ca)s AND resource_id IN %(ids)s',
                params={
                    'ca': cloud_account_id,
                    'ids': resource_ids
                })
        mongo_cl.restapi.resources.delete_many({
            'cloud_account_id': cloud_account_id,
            'cloud_resource_id': {'$regex': 'SavingsPlanNegation'}
        })
    if table_exists:
        clickhouse_cl.execute('OPTIMIZE TABLE expenses FINAL')


def downgrade():
    pass
