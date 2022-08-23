""""cluster_resources_indices"

Revision ID: 352d40bbe882
Revises: c5bd60bf041c
Create Date: 2021-05-05 17:27:34.221305

"""
import os

from config_client.client import Client as EtcdClient
from pymongo import MongoClient


# revision identifiers, used by Alembic.
revision = '352d40bbe882'
down_revision = 'c5bd60bf041c'
branch_labels = None
depends_on = None

DEFAULT_ETCD_HOST = 'etcd-client'
DEFAULT_ETCD_PORT = 80
CLUSTER_RELATED_INDICES = [
    ('ClusterId', 'cluster_id', {'cluster_id': {'$exists': True}}),
    ('ClusterTypeId', 'cluster_type_id', {'cluster_type_id': {'$exists': True}})
]


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
    for name, column, partial_exp in CLUSTER_RELATED_INDICES:
        if name in resource_indices:
            continue
        mongo_resources.create_index(
            [(column, 1)],
            name=name,
            partialFilterExpression=partial_exp
        )


def downgrade():
    mongo_resources = _get_resources_collection()
    resource_indices = {x['name'] for x in mongo_resources.list_indexes()}
    for name, _, _ in CLUSTER_RELATED_INDICES:
        if name not in resource_indices:
            continue
        mongo_resources.drop_index(name)
