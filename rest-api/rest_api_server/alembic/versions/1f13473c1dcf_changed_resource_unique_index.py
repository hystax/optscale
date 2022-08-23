""""changed_resource_unique_index"

Revision ID: 1f13473c1dcf
Revises: 352d40bbe882
Create Date: 2021-05-11 14:45:49.283294

"""
import os

from config_client.client import Client as EtcdClient
from pymongo import MongoClient


# revision identifiers, used by Alembic.
revision = '1f13473c1dcf'
down_revision = '352d40bbe882'
branch_labels = None
depends_on = None

DEFAULT_ETCD_HOST = 'etcd-client'
DEFAULT_ETCD_PORT = 80
RESOURCE_UNIQUE_INDEX = 'OptResourceUnique'


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
    mongo_resources = _get_resources_collection()
    resource_indices = {x['name'] for x in mongo_resources.list_indexes()}
    if RESOURCE_UNIQUE_INDEX in resource_indices:
        mongo_resources.drop_index(RESOURCE_UNIQUE_INDEX)
    mongo_resources.create_index(
        [
            ('cloud_resource_id', 1), ('deleted_at', 1),
            ('cloud_account_id', 1), ('organization_id', 1)
        ],
        name=RESOURCE_UNIQUE_INDEX,
        unique=True
    )


def downgrade():
    mongo_resources = _get_resources_collection()
    resource_indices = {x['name'] for x in mongo_resources.list_indexes()}
    if RESOURCE_UNIQUE_INDEX in resource_indices:
        mongo_resources.drop_index(RESOURCE_UNIQUE_INDEX)
    mongo_resources.create_index(
        [
            ('cloud_resource_id', 1), ('deleted_at', 1),
            ('cloud_account_id', 1)
        ],
        name=RESOURCE_UNIQUE_INDEX,
        unique=True
    )
