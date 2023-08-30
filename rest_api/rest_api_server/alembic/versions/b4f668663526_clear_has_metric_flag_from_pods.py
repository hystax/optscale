""""clear_has_metric_flag_from_pods"

Revision ID: b4f668663526
Revises: e63b63d4d484
Create Date: 2022-08-12 11:07:05.431745

"""
import os
import sqlalchemy as sa
from alembic import op
from sqlalchemy.orm import Session
from optscale_client.config_client.client import Client as EtcdClient
from pymongo import MongoClient, UpdateMany


# revision identifiers, used by Alembic.
revision = 'b4f668663526'
down_revision = 'e63b63d4d484'
branch_labels = None
depends_on = None

ORGANIZATION_TABLE = sa.table(
    'organization',
    sa.Column('id', sa.String()),
    sa.Column('deleted_at', sa.Integer()),
)

CLOUD_ACCOUNT_TABLE = sa.table(
    'cloudaccount',
    sa.Column('id', sa.String()),
    sa.Column('organization_id', sa.String()),
    sa.Column('type', sa.String()),
    sa.Column('deleted_at', sa.Integer()),
)

KUBERNETES_CLOUD_TYPE = 'KUBERNETES_CNR'
DEFAULT_ETCD_HOST = 'etcd'
DEFAULT_ETCD_PORT = 80


def get_etcd_config_client():
    etcd_host = os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST)
    etcd_port = os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT)
    config_cl = EtcdClient(host=etcd_host, port=int(etcd_port))
    return config_cl


def get_resources_collection():
    config_cl = get_etcd_config_client()
    mongo_params = config_cl.mongo_params()
    mongo_conn_string = "mongodb://%s:%s@%s:%s" % mongo_params[:-1]
    mongo_client = MongoClient(mongo_conn_string)
    return mongo_client.restapi.resources


def get_organization_ids(session):
    orgs_q = sa.select([
        ORGANIZATION_TABLE.c.id
    ]).where(ORGANIZATION_TABLE.c.deleted_at == 0)
    return [x[0] for x in session.execute(orgs_q)]


def get_k8s_cloud_account_ids(session, organization_ids):
    cloud_accs_q = sa.select([
        CLOUD_ACCOUNT_TABLE.c.id
    ]).where(sa.and_(
        CLOUD_ACCOUNT_TABLE.c.organization_id.in_(organization_ids),
        CLOUD_ACCOUNT_TABLE.c.type == KUBERNETES_CLOUD_TYPE,
        CLOUD_ACCOUNT_TABLE.c.deleted_at == 0
    ))
    return [x[0] for x in session.execute(cloud_accs_q)]


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        org_ids = get_organization_ids(session)
        ca_ids = get_k8s_cloud_account_ids(session, org_ids)
        if ca_ids:
            resources_collection = get_resources_collection()
            resources_collection.bulk_write([UpdateMany(
                filter={
                    'cloud_account_id': ca_id
                },
                update={
                    '$unset': {'has_metrics': 1}
                }
            ) for ca_id in ca_ids])
    finally:
        session.close()


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        org_ids = get_organization_ids(session)
        ca_ids = get_k8s_cloud_account_ids(session, org_ids)
        if ca_ids:
            resources_collection = get_resources_collection()
            resources_collection.bulk_write([UpdateMany(
                filter={
                    'cloud_account_id': ca_id
                },
                update={
                    '$set': {'has_metrics': True}
                }
            ) for ca_id in ca_ids])
    finally:
        session.close()
