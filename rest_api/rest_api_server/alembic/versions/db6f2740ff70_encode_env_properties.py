"""encode env properties

Revision ID: db6f2740ff70
Revises: 7b5354bbb05b
Create Date: 2022-09-28 13:16:11.643446

"""
import os
import base64
from alembic import op
import sqlalchemy as sa
from pymongo import MongoClient, UpdateOne
from optscale_client.config_client.client import Client as EtcdClient


# revision identifiers, used by Alembic.
revision = 'db6f2740ff70'
down_revision = '7b5354bbb05b'
branch_labels = None
depends_on = None


DEFAULT_ETCD_HOST = 'etcd'
DEFAULT_ETCD_PORT = 80
CHUNK_SIZE = 200


def encode_string(val, decode=False):
    if len(val) == 0:
        return val
    method = base64.b64decode if decode else base64.b64encode
    return method(val.encode('utf-8')).decode('utf-8')


def encoded_map(map, decode=False):
    if not map:
        return {}
    new_map = {}
    for k, v in map.items():
        new_key = encode_string(k, decode)
        new_map[new_key] = v
    return new_map


def get_etcd_config_client():
    etcd_host = os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST)
    etcd_port = os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT)
    config_cl = EtcdClient(host=etcd_host, port=int(etcd_port))
    return config_cl


def get_mongo_client():
    config_cl = get_etcd_config_client()
    mongo_params = config_cl.mongo_params()
    mongo_conn_string = "mongodb://%s:%s@%s:%s" % mongo_params[:-1]
    mongo_client = MongoClient(mongo_conn_string)
    return mongo_client


def get_resources_collection():
    return get_mongo_client().restapi.resources


def get_property_history_collection():
    return get_mongo_client().restapi.property_history


def resources_with_env_properties():
    resources_collection = get_resources_collection()
    res_filters = {
        'deleted_at': 0,
        'shareable': True,
        'env_properties': {'$exists': True}
    }
    return resources_collection.find(res_filters, ['_id', 'env_properties'])


def process_resources(decode: bool):
    resources_collection = get_resources_collection()
    update_requests = []
    for res in resources_with_env_properties():
        env_properties = res.get('env_properties')
        env_properties = encoded_map(env_properties, decode)
        update_reqest = UpdateOne(
                filter={'_id': res['_id']},
                update={'$set': {'env_properties': env_properties}},
            )
        update_requests.append(update_reqest)
        if len(update_requests) == CHUNK_SIZE:
            resources_collection.bulk_write(update_requests)
            update_requests = []
    if len(update_requests) > 0:
        resources_collection.bulk_write(update_requests)


def process_properties_history(decode: bool):
    collection = get_property_history_collection()
    update_requests = []
    for property in collection.find({}):
        changes = property.get('changes')
        changes = encoded_map(changes, decode)
        update_reqest = UpdateOne(
                filter={'_id': property['_id']},
                update={'$set': {'changes': changes}},
            )
        update_requests.append(update_reqest)
        if len(update_requests) == CHUNK_SIZE:
            collection.bulk_write(update_requests)
            update_requests = []
    if len(update_requests) > 0:
        collection.bulk_write(update_requests)


def upgrade():
    process_resources(decode=False)
    process_properties_history(decode=False)


def downgrade():
    process_resources(decode=True)
    process_properties_history(decode=True)
