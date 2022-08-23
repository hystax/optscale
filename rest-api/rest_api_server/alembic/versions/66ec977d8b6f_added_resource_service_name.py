""""added_resource_service_name"

Revision ID: 66ec977d8b6f
Revises: 3efd73867797
Create Date: 2021-10-21 15:28:52.718008

"""
import os
import sqlalchemy as sa

from alembic import op
from config_client.client import Client as ConfigClient
from pymongo import MongoClient, UpdateMany, UpdateOne
from sqlalchemy import and_
from sqlalchemy import select, String
from sqlalchemy.orm import Session
from sqlalchemy.sql import table, column

# revision identifiers, used by Alembic.
revision = '66ec977d8b6f'
down_revision = '3efd73867797'
branch_labels = None
depends_on = None

DEFAULT_ETCD_HOST = 'etcd'
DEFAULT_ETCD_PORT = 80
BULK_SIZE = 1000


def get_config_client():
    etcd_host = os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST)
    etcd_port = os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT)
    config_cl = ConfigClient(host=etcd_host, port=int(etcd_port))
    return config_cl


def get_mongo_collections():
    config_cl = get_config_client()
    conn_string = "mongodb://%s:%s@%s:%s" % config_cl.mongo_params()[:-1]
    mongo_cl = MongoClient(conn_string)
    return mongo_cl.restapi.resources, mongo_cl.restapi.expenses


def get_organizations(session):
    org_table = table(
        'organization',
        column('id',  String()),
        column('deleted_at', sa.Integer())
    )
    organizations = session.execute(
        select([org_table]).where(org_table.c.deleted_at == 0))
    return organizations


def get_cloud_accounts(session, organization_ids):
    ca_table = table(
        'cloudaccount',
        column('id',  String()),
        column('deleted_at', sa.Integer()),
        column('organization_id', String())
    )
    cloud_accounts = session.execute(
        select([ca_table]).where(and_(
            ca_table.c.organization_id.in_(organization_ids),
            ca_table.c.deleted_at == 0)))
    return cloud_accounts


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        org_ids = [x.id for x in get_organizations(session)]
        ca_ids = [x.id for x in get_cloud_accounts(session, org_ids)]
    finally:
        session.close()

    resources_collection, expenses_collection = get_mongo_collections()
    if org_ids:
        resources_collection.bulk_write([UpdateMany(
            filter={
                'organization_id': org_id
            },
            update={
                '$set': {'service_name': None}
            }
        ) for org_id in org_ids])

    for ca_id in ca_ids:
        pipeline = [
            {
                '$match': {
                    'cloud_account_id': ca_id
                }
            },
            {
                '$group': {
                    '_id': {
                        'resource_id': '$resource_id',
                    },
                    'service_name': {'$max': '$service_name'},
                }
            }
        ]

        updates = []
        for val in expenses_collection.aggregate(pipeline):
            updates.append(UpdateOne(
                    filter={
                        '_id': val['_id']['resource_id']
                    },
                    update={
                        '$set': {'service_name': val['service_name']}
                    }
            ))
            if len(updates) >= BULK_SIZE:
                resources_collection.bulk_write(updates)
                updates.clear()
        if updates:
            resources_collection.bulk_write(updates)


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        org_ids = [x.id for x in get_organizations(session)]
        ca_ids = [x.id for x in get_cloud_accounts(session, org_ids)]
    finally:
        session.close()

    resources_collection, expenses_collection = get_mongo_collections()
    resources_collection.bulk_write([UpdateMany(
        filter={
            'organization_id': org_id
        },
        update={
            '$unset': {'service_name': 1}
        }
    ) for org_id in org_ids])
    resources_collection.bulk_write([UpdateMany(
        filter={
            'cloud_account_id': ca_id
        },
        update={
            '$unset': {'service_name': 1}
        }
    ) for ca_id in ca_ids])
