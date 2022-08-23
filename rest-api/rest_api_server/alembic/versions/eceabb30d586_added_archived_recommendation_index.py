""""added_archived_recommendation_index"

Revision ID: eceabb30d586
Revises: a3cb068fe60f
Create Date: 2022-05-18 17:35:04.662623

"""
import os
from pymongo import MongoClient
from config_client.client import Client as EtcdClient


# revision identifiers, used by Alembic.
revision = 'eceabb30d586'
down_revision = 'a3cb068fe60f'
branch_labels = None
depends_on = None
DEFAULT_ETCD_HOST = 'etcd'
DEFAULT_ETCD_PORT = 80
INDEX_NAME = 'OrgArchivedAtModule'


def _get_etcd_config_client():
    etcd_host = os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST)
    etcd_port = os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT)
    config_cl = EtcdClient(host=etcd_host, port=int(etcd_port))
    return config_cl


def _get_archived_recommendations_collection():
    config_cl = _get_etcd_config_client()
    mongo_params = config_cl.mongo_params()
    mongo_conn_string = "mongodb://%s:%s@%s:%s" % mongo_params[:-1]
    mongo_client = MongoClient(mongo_conn_string)
    return mongo_client.restapi.archived_recommendations


def upgrade():
    archived_recommendations = _get_archived_recommendations_collection()
    archived_recommendations.create_index([
        ('organization_id', 1), ('archived_at', 1), ('module', 1)
    ], name=INDEX_NAME)


def downgrade():
    archived_recommendations = _get_archived_recommendations_collection()
    indexes = [x['name'] for x in archived_recommendations.list_indexes()]
    if INDEX_NAME in indexes:
        archived_recommendations.drop_index(INDEX_NAME)
