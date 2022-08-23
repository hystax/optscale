""""delete_expenses_for_deleted_clouds"

Revision ID: 145b4c9cc308
Revises: 865bb21cc4a4
Create Date: 2020-09-28 11:43:10.790540

"""
import os

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session
from config_client.client import Client as EtcdClient
from pymongo import MongoClient


# revision identifiers, used by Alembic.
revision = '145b4c9cc308'
down_revision = '01a187c9482f'
branch_labels = None
depends_on = None
DEFAULT_ETCD_HOST = 'etcd-client'
DEFAULT_ETCD_PORT = 80


def _get_etcd_config_client():
    etcd_host = os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST)
    etcd_port = os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT)
    config_cl = EtcdClient(host=etcd_host, port=int(etcd_port))
    return config_cl


def _get_expenses_collection():
    config_cl = _get_etcd_config_client()
    mongo_params = config_cl.mongo_params()
    mongo_conn_string = "mongodb://%s:%s@%s:%s" % mongo_params[:-1]
    mongo_client = MongoClient(mongo_conn_string)
    return mongo_client.restapi.expenses


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        cloud_table = sa.table('cloudcredentials',
                               sa.Column('deleted_at', sa.Integer()),
                               sa.Column('id', sa.String(36)))
        stmt = sa.select([cloud_table]).where(cloud_table.c.deleted_at != 0)
        creds = session.execute(stmt)
        expenses = _get_expenses_collection()
        for cc in creds:
            expenses.delete_many({'cloud_credentials_id': cc['id']})
    finally:
        session.close()


def downgrade():
    # downgrade is not necessary and not possible from rest,
    # regenerator in diworker can do this (but only for non-deleted cloud
    # credentials, so if you need to restore expenses for creds, you should
    # undelete them first)
    pass
