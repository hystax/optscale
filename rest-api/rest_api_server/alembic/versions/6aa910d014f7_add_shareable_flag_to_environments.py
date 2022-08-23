""""add_shareable_flag_to_environment"

Revision ID: 6aa910d014f7
Revises: 91979a9bd827
Create Date: 2021-08-25 09:15:23.601265

"""
import os
from pymongo import MongoClient, UpdateMany
from config_client.client import Client as EtcdClient

# revision identifiers, used by Alembic.
revision = '6aa910d014f7'
down_revision = '91979a9bd827'
branch_labels = None
depends_on = None
DEFAULT_ETCD_HOST = 'etcd-client'
DEFAULT_ETCD_PORT = 80
CHUNK_UPDATE_SIZE = 200


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
    res_filters = {
        'deleted_at': 0,
        'is_environment': True,
        '$or': [
            {'shareable': {'$exists': False}},
            {'shareable': {'$in': [False, None]}},
        ]
    }
    environment_resources = list(
        {res['_id'] for res in resources_collection.find(res_filters, ['_id'])}
    )
    for i in range(0, len(environment_resources), CHUNK_UPDATE_SIZE):
        env_res_ids_chunk = environment_resources[i:i + CHUNK_UPDATE_SIZE]
        update_filter = {'_id': {'$in': env_res_ids_chunk}}
        update_cmd = {'$set': {'shareable': True}}
        resources_collection.bulk_write([
            UpdateMany(
                filter=update_filter,
                update=update_cmd
            )
        ])


def downgrade():
    pass
