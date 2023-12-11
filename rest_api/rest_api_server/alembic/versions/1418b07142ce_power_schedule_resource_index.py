""""power_schedule_resource_index"

Revision ID: 1418b07142ce
Revises: 9fd932293995
Create Date: 2023-10-30 12:50:33.015513

"""
import os
from pymongo import MongoClient
from optscale_client.config_client.client import Client as EtcdClient

# revision identifiers, used by Alembic.
revision = '1418b07142ce'
down_revision = '9fd932293995'
branch_labels = None
depends_on = None

DEFAULT_ETCD_HOST = 'etcd-client'
DEFAULT_ETCD_PORT = 80
POWER_SCHEDULE_INDEX_NAME = 'PowerScheduleId'


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
    if POWER_SCHEDULE_INDEX_NAME not in indexes:
        resources_collection.create_index(
            [('power_schedule_id', 1)],
            name=POWER_SCHEDULE_INDEX_NAME, background=True)


def downgrade():
    resources_collection = _get_restapi_resources_mongo()
    indexes = _list_indexes(resources_collection)
    if POWER_SCHEDULE_INDEX_NAME in indexes:
        resources_collection.drop_index(POWER_SCHEDULE_INDEX_NAME)
    resources_collection.update_many({'power_schedule': {'$exists': True}},
                                     {'$unset': {'power_schedule': 1}})
