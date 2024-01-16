""""fixed_power_schedule_index"

Revision ID: a84e2b6e2053
Revises: 8837a7d17bba
Create Date: 2024-01-16 11:12:32.232728

"""
import os
from pymongo import MongoClient
from optscale_client.config_client.client import Client as EtcdClient

# revision identifiers, used by Alembic.
revision = 'a84e2b6e2053'
down_revision = '8837a7d17bba'
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
    return {x['name']: x['key'] for x in resources_collection.list_indexes()}


def upgrade():
    resources_collection = _get_restapi_resources_mongo()
    indexes = _list_indexes(resources_collection)
    created_index = indexes.get(POWER_SCHEDULE_INDEX_NAME)
    if created_index:
        if 'power_schedule' in created_index:
            return
        resources_collection.drop_index(POWER_SCHEDULE_INDEX_NAME)
    resources_collection.create_index(
        [('power_schedule', 1)],
        name=POWER_SCHEDULE_INDEX_NAME,
        partialFilterExpression={
            'power_schedule': {'$exists': True},
        }, background=True)


def downgrade():
    resources_collection = _get_restapi_resources_mongo()
    indexes = _list_indexes(resources_collection)
    created_index = indexes.get(POWER_SCHEDULE_INDEX_NAME)
    if created_index:
        if 'power_schedule_id' in created_index:
            return
        resources_collection.drop_index(POWER_SCHEDULE_INDEX_NAME)
    resources_collection.create_index(
        [('power_schedule_id', 1)],
        name=POWER_SCHEDULE_INDEX_NAME, background=True)
