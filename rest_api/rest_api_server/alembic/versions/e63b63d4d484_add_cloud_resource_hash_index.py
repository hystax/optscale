""""add_cloud_resource_hash_to_unique_index"

Revision ID: e63b63d4d484
Revises: 32b34ca9b0d9
Create Date: 2022-05-18 17:14:20.769743

"""
import os
from pymongo import MongoClient
from optscale_client.config_client.client import Client as EtcdClient


# revision identifiers, used by Alembic.
revision = 'e63b63d4d484'
down_revision = '32b34ca9b0d9'
branch_labels = None
depends_on = None

DEFAULT_ETCD_HOST = 'etcd-client'
DEFAULT_ETCD_PORT = 80
UNIQUE_INDEX_NAME = 'OptResourceUnique'
RESOURCE_HASH_INDEX_NAME = 'CloudResourceHash'


def _get_etcd_config_client():
    etcd_host = os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST)
    etcd_port = os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT)
    config_cl = EtcdClient(host=etcd_host, port=int(etcd_port))
    return config_cl


def _get_restapi_resources_mongo():
    config_cl = _get_etcd_config_client()
    mongo_params = config_cl.mongo_params()
    mongo_conn_string = "mongodb://%s:%s@%s:%s" % mongo_params[:-1]
    mongo_client = MongoClient(mongo_conn_string)
    return mongo_client.restapi.resources


def _list_indexes(resources_collection):
    return [x['name'] for x in resources_collection.list_indexes()]


def upgrade():
    resources_collection = _get_restapi_resources_mongo()
    indexes = _list_indexes(resources_collection)
    if UNIQUE_INDEX_NAME in indexes:
        resources_collection.drop_index(UNIQUE_INDEX_NAME)
    resources_collection.create_index([
        ('cloud_resource_id', 1), ('cloud_resource_hash', 1),
        ('cloud_account_id', 1), ('organization_id', 1), ('deleted_at', 1)],
        name=UNIQUE_INDEX_NAME, unique=True, background=True)
    resources_collection.create_index(
        [('cloud_resource_hash', 1)], name=RESOURCE_HASH_INDEX_NAME,
        background=True)


def downgrade():
    resources_collection = _get_restapi_resources_mongo()
    indexes = _list_indexes(resources_collection)
    for index_ in [UNIQUE_INDEX_NAME, RESOURCE_HASH_INDEX_NAME]:
        if index_ in indexes:
            resources_collection.drop_index(index_)
    resources_collection.create_index([
        ('cloud_resource_id', 1), ('cloud_account_id', 1),
        ('organization_id', 1), ('deleted_at', 1)],
        name=UNIQUE_INDEX_NAME, unique=True, background=True)
