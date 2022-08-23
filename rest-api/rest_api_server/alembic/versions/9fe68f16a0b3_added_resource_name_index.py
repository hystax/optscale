""""added_resource_name_index"

Revision ID: 9fe68f16a0b3
Revises: 9c6bfcfb79b3
Create Date: 2021-09-07 15:17:07.903631

"""
import os
from pymongo import MongoClient
from config_client.client import Client as EtcdClient

# revision identifiers, used by Alembic.
revision = '9fe68f16a0b3'
down_revision = '9c6bfcfb79b3'
branch_labels = None
depends_on = None
DEFAULT_ETCD_HOST = 'etcd-client'
DEFAULT_ETCD_PORT = 80
INDEX_NAME = 'Name'


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


def upgrade():
    resources_collection = _get_resources_collection()
    resources_collection.create_index([('name', 1)], name=INDEX_NAME)


def downgrade():
    resources_collection = _get_resources_collection()
    indexes = [x['name'] for x in resources_collection.list_indexes()]
    if INDEX_NAME in indexes:
        resources_collection.drop_index(INDEX_NAME)
