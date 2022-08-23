""""rename_cloud_create_at"

Revision ID: 29cd5af93e61
Revises: 6ce6170a7898
Create Date: 2022-06-06 17:14:28.077666

"""
import os
import logging
from config_client.client import Client as EtcdClient
from pymongo import MongoClient

# revision identifiers, used by Alembic.
revision = '29cd5af93e61'
down_revision = '6ce6170a7898'
branch_labels = None
depends_on = None

DEFAULT_ETCD_HOST = 'etcd-client'
DEFAULT_ETCD_PORT = 80
LOG = logging.getLogger(__name__)
RDS_INSTANCE = 'RDS Instance'


def _get_etcd_config_client():
    etcd_host = os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST)
    etcd_port = os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT)
    config_cl = EtcdClient(host=etcd_host, port=int(etcd_port))
    return config_cl


def get_mongo_resources():
    config_cl = _get_etcd_config_client()
    mongo_params = config_cl.mongo_params()
    mongo_conn_string = "mongodb://%s:%s@%s:%s" % mongo_params[:-1]
    mongo_client = MongoClient(mongo_conn_string)
    return mongo_client.restapi.resources


def upgrade():
    mongo_resources = get_mongo_resources()
    results = mongo_resources.update_many(
        filter={'resource_type': RDS_INSTANCE,
                'deleted_at': 0},
        update={'$rename': {'cloud_create_at': 'cloud_created_at'}}
    )
    LOG.info(f'Updated {results.modified_count} rows')


def downgrade():
    mongo_resources = get_mongo_resources()
    results = mongo_resources.update_many(
        filter={'resource_type': RDS_INSTANCE,
                'deleted_at': 0},
        update={'$rename': {'cloud_created_at': 'cloud_create_at'}}
    )
    LOG.info(f'Updated {results.modified_count} rows')

