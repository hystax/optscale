"""remove_organization_id_for_cloud_resources

Revision ID: c8777666e641
Revises: 29cd5af93e61
Create Date: 2022-06-06 16:16:06.981448

"""
import logging
import os
import sqlalchemy as sa
from alembic import op
from config_client.client import Client as EtcdClient
from pymongo import MongoClient
from sqlalchemy.orm import Session

# revision identifiers, used by Alembic.
revision = 'c8777666e641'
down_revision = '29cd5af93e61'
branch_labels = None
depends_on = None


LOG = logging.getLogger(__name__)
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
            cloud_account_t.c.deleted_at == 0)))
    return [x[0] for x in cloud_accounts]


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        cloud_accounts_ids = get_cloud_accounts(session)
    finally:
        session.close()
    mongo_resources = get_mongo_resources()
    results = mongo_resources.update_many(
        filter={'cloud_account_id': {'$in': cloud_accounts_ids},
                'organization_id': {'$exists': True},
                'deleted_at': 0},
        update={'$unset': {'organization_id': 1}}
    )
    LOG.info(f'Updated {results.modified_count} rows')


def downgrade():
    pass
