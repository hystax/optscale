""""fix_clean_expenses_resource_types"

Revision ID: 30ca937baee2
Revises: b0ffdb5aefef
Create Date: 2021-02-04 15:08:27.151995

"""
import os
from pymongo import MongoClient, UpdateOne
from config_client.client import Client as EtcdClient

# revision identifiers, used by Alembic.
revision = '30ca937baee2'
down_revision = 'b0ffdb5aefef'
branch_labels = None
depends_on = None
DEFAULT_ETCD_HOST = 'etcd-client'
DEFAULT_ETCD_PORT = 80

resource_type_map = {
        'snapshot': 'Snapshot',
        'volume': 'Volume',
        'instance': 'Instance',
        'bucket': 'Bucket'
    }
CHUNK_UPDATE_SIZE = 200


def _get_etcd_config_client():
    etcd_host = os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST)
    etcd_port = os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT)
    config_cl = EtcdClient(host=etcd_host, port=int(etcd_port))
    return config_cl


def _get_clean_expenses_collection():
    config_cl = _get_etcd_config_client()
    mongo_params = config_cl.mongo_params()
    mongo_conn_string = "mongodb://%s:%s@%s:%s" % mongo_params[:-1]
    mongo_client = MongoClient(mongo_conn_string)
    return mongo_client.restapi.expenses


def upgrade():
    expenses_collection = _get_clean_expenses_collection()
    filters = {'resource_type': {'$in': list(resource_type_map.keys())}}
    expenses_id_res_type = [(x['_id'], x['resource_type']) for x in
                            expenses_collection.find(filters, ['resource_type'])]
    for i in range(0, len(expenses_id_res_type), CHUNK_UPDATE_SIZE):
        expenses_id_res_chunk = expenses_id_res_type[i:i + CHUNK_UPDATE_SIZE]
        updates = []
        for expense_id, expense_res_type in expenses_id_res_chunk:
            valid_resource_type = resource_type_map.get(expense_res_type)
            if valid_resource_type:
                updates.append(
                    UpdateOne(
                        filter={
                            '_id': expense_id
                        },
                        update={'$set': {
                            'resource_type': valid_resource_type
                        }}
                    )
                )
        if updates:
            expenses_collection.bulk_write(updates)


def downgrade():
    pass
