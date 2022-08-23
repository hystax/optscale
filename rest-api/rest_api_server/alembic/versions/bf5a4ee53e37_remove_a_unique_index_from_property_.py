"""Remove a unique index from property_history

Revision ID: bf5a4ee53e37
Revises: 56140dd30553
Create Date: 2021-09-28 10:34:01.456967

"""
import os
from config_client.client import Client as EtcdClient
from pymongo import MongoClient
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bf5a4ee53e37'
down_revision = '7095b8f9663d'
branch_labels = None
depends_on = None
DEFAULT_ETCD_HOST = 'etcd-client'
DEFAULT_ETCD_PORT = 80


def _get_etcd_config_client():
    etcd_host = os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST)
    etcd_port = os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT)
    config_cl = EtcdClient(host=etcd_host, port=int(etcd_port))
    return config_cl


def _get_property_history_collection():
    config_cl = _get_etcd_config_client()
    mongo_params = config_cl.mongo_params()
    mongo_conn_string = "mongodb://%s:%s@%s:%s" % mongo_params[:-1]
    mongo_client = MongoClient(mongo_conn_string)
    return mongo_client.restapi.property_history


def upgrade():
    property_history = _get_property_history_collection()
    property_history.drop_index('PropHistoryUnique')


def downgrade():
    property_history = _get_property_history_collection()
    property_history.create_index([('resource_id', 1), ('time', 1)],
                                  name='PropHistoryUnique', unique=True)
