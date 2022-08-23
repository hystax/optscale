""""checklists_collection_indexes"

Revision ID: 2ff7e59fffef
Revises: a9eb1e7f82d9
Create Date: 2021-02-19 16:44:30.025735

"""
import os

from config_client.client import Client as EtcdClient


# revision identifiers, used by Alembic.
from pymongo import MongoClient

revision = '2ff7e59fffef'
down_revision = '0c99b4c498d5'
branch_labels = None
depends_on = None
DEFAULT_ETCD_HOST = 'etcd-client'
DEFAULT_ETCD_PORT = 2379
COMBINED_INDEX = 'OrgCreatedAtIndex'
MODULE_INDEX = 'ModuleIndex'


def _get_etcd_config_client():
    etcd_host = os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST)
    etcd_port = os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT)
    config_cl = EtcdClient(host=etcd_host, port=int(etcd_port))
    return config_cl


def _get_checklists_collection():
    config_cl = _get_etcd_config_client()
    mongo_params = config_cl.mongo_params()
    mongo_conn_string = "mongodb://%s:%s@%s:%s" % mongo_params[:-1]
    mongo_client = MongoClient(mongo_conn_string)
    return mongo_client.restapi.checklists


def upgrade():
    checklists = _get_checklists_collection()
    checklists.create_index([('organization_id', 1), ('created_at', 1)],
                            name=COMBINED_INDEX)
    checklists.create_index([('module', 1)], name=MODULE_INDEX)


def downgrade():
    checklists = _get_checklists_collection()
    index_list = [x['name'] for x in checklists.list_indexes()]
    for index_name in [MODULE_INDEX, COMBINED_INDEX]:
        if index_name in index_list:
            checklists.drop_index(index_name)
