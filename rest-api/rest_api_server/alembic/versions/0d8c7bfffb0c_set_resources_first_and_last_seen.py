""""set_resources_first_and_last_seen"

Revision ID: 0d8c7bfffb0c
Revises: 1f13473c1dcf
Create Date: 2021-05-24 13:29:33.091810

"""
import os
from config_client.client import Client as EtcdClient
from pymongo import MongoClient, UpdateOne

# revision identifiers, used by Alembic.
revision = '0d8c7bfffb0c'
down_revision = '1f13473c1dcf'
branch_labels = None
depends_on = None
DEFAULT_ETCD_HOST = 'etcd-client'
DEFAULT_ETCD_PORT = 80
BULK_SIZE = 1000
FIELD_OP_MAP = {
    'first_seen': '$min',
    'last_seen': '$max'
}


def _get_etcd_config_client():
    etcd_host = os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST)
    etcd_port = os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT)
    config_cl = EtcdClient(host=etcd_host, port=int(etcd_port))
    return config_cl


def _get_mongo_client():
    config_cl = _get_etcd_config_client()
    mongo_params = config_cl.mongo_params()
    mongo_conn_string = "mongodb://%s:%s@%s:%s" % mongo_params[:-1]
    mongo_client = MongoClient(mongo_conn_string)
    return mongo_client


def _get_expenses_threshold(resource_ids, expenses_collection):
    pipeline = [
        {
            '$match': {
                'resource_id': {'$in': resource_ids}
            }
        },
        {
            '$group': {
                '_id': {
                    'resource_id': '$resource_id',
                },
                'first_seen': {'$min': '$date'},
                'last_seen': {'$max': '$date'},
            }
        }
    ]
    return {
        e['_id']['resource_id']: {
            'first_seen': int(e['first_seen'].timestamp()),
            'last_seen': int(e['last_seen'].timestamp())
        } for e in expenses_collection.aggregate(pipeline)}


def _get_changes(resource_map, expenses_collection):
    op_bulk = []
    threshold_map = _get_expenses_threshold(
        list(resource_map.keys()), expenses_collection)
    for r_id, r in resource_map.items():
        threshold = threshold_map.get(r_id, {})
        changes = {}
        for field in FIELD_OP_MAP.keys():
            if not r.get(field):
                changes[field] = threshold.get(field, r.get('created_at'))
        if changes:
            op_bulk.append(UpdateOne(
                filter={'_id': r_id},
                update={'$set': changes}))
            if r.get('cluster_id'):
                op_bulk.append(UpdateOne(
                    filter={'_id': r['cluster_id']},
                    update={
                        op: {field: changes[field]}
                        for field, op in FIELD_OP_MAP.items()
                        if changes.get(field) is not None
                    }
                ))
    return op_bulk


def upgrade():
    mongo_client = _get_mongo_client()
    expenses_collection = mongo_client.restapi.expenses
    resources_collection = mongo_client.restapi.resources

    incomplete_resources = resources_collection.find({
        'cluster_type_id': {'$exists': False},
        'deleted_at': 0,
        '$or': [
            {'first_seen': None},
            {'last_seen': None}
        ]
    })

    op_bulk = []
    resource_map = {}
    for incomplete_resource in incomplete_resources:
        resource_map[incomplete_resource['_id']] = incomplete_resource
        if len(resource_map) == BULK_SIZE:
            op_bulk.extend(
                _get_changes(resource_map, expenses_collection))
            resource_map.clear()
    if resource_map:
        op_bulk.extend(
            _get_changes(resource_map, expenses_collection))
        resource_map.clear()

    for i in range(0, len(op_bulk), BULK_SIZE):
        resources_collection.bulk_write(op_bulk[i:i + BULK_SIZE])


def downgrade():
    pass
