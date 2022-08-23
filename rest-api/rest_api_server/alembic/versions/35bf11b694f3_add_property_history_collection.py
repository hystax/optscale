"""Add property_history collection

Revision ID: 35bf11b694f3
Revises: 9fe68f16a0b3
Create Date: 2021-08-27 14:18:58.399059

"""
import os
from config_client.client import Client as EtcdClient
from pymongo import MongoClient
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '35bf11b694f3'
down_revision = 'f6250c19a6c3'
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


def _create_unique_index(collection):
    collection.create_index([('resource_id', 1), ('time', 1)],
                            name='PropHistoryUnique', unique=True)


def _create_search_indexes(collection):
    search_indexes = {
        'ResourceID': 'resource_id',
        'Time': 'time'
    }
    for index_name, field_name in search_indexes.items():
        collection.create_index([(field_name, 1)], name=index_name)


def upgrade():
    property_history = _get_property_history_collection()
    # The collection is created when the first record is inserted
    property_history.insert_one({'resource_id': 'Create_collection', 'time': 0})
    _create_unique_index(property_history)
    _create_search_indexes(property_history)
    property_history.delete_many({})


def downgrade():
    property_history = _get_property_history_collection()
    property_history.drop()
