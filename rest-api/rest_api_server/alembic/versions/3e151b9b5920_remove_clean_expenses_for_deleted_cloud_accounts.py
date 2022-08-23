""""remove_clean_expenses_for_deleted_cloud_accounts_and_for_not_existing_resources, insert_for_actual_resources"

Revision ID: 3e151b9b5920
Revises: e114908c1ac1
Create Date: 2020-12-31 09:20:00.261476

"""
import os

from alembic import op
from config_client.client import Client as EtcdClient
from datetime import datetime
from pymongo import MongoClient, UpdateOne
import sqlalchemy as sa
from sqlalchemy import select, Integer
from sqlalchemy.orm import Session
from sqlalchemy.sql import table, column

revision = '3e151b9b5920'
down_revision = '593c49b7b72f'
branch_labels = None
depends_on = None
DEFAULT_ETCD_HOST = 'etcd-client'
DEFAULT_ETCD_PORT = 80

CHUNK_CLOUD_ACCOUNT_DELETE_SIZE = 5
CHUNK_DELETE_SIZE = 1000
CHUNK_INSERT_SIZE = 200


def _get_etcd_config_client():
    etcd_host = os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST)
    etcd_port = os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT)
    config_cl = EtcdClient(host=etcd_host, port=int(etcd_port))
    return config_cl


def _get_mongo_client():
    config_cl = _get_etcd_config_client()
    mongo_params = config_cl.mongo_params()
    mongo_conn_string = "mongodb://%s:%s@%s:%s" % mongo_params[:-1]
    return MongoClient(mongo_conn_string)


def _get_expenses_collection(mongo_client):
    return mongo_client.restapi.expenses


def _get_resources_collection(mongo_client):
    return mongo_client.restapi.resources


def remove_clean_expenses_for_deleted_cloud_accounts(deleted_cloud_account_ids, mongo_expenses):
    for i in range(0, len(deleted_cloud_account_ids), CHUNK_CLOUD_ACCOUNT_DELETE_SIZE):
        cloud_account_ids_chunk = deleted_cloud_account_ids[i:i + CHUNK_CLOUD_ACCOUNT_DELETE_SIZE]
        mongo_expenses.delete_many({'cloud_account_id': {'$in': cloud_account_ids_chunk}})


def remove_expenses_with_not_existing_resources(all_existing_resource_ids, mongo_expenses):
    filters = {
        '_initial': True,
        'cost': 0,
        'raw_data_links': [],
    }
    expense_resource_ids = {x['resource_id'] for x in
                            mongo_expenses.find(filters, ['resource_id'])}
    invalid_resource_ids = list(expense_resource_ids - all_existing_resource_ids)
    for i in range(0, len(invalid_resource_ids), CHUNK_DELETE_SIZE):
        ids_chunk = invalid_resource_ids[i:i + CHUNK_DELETE_SIZE]
        mongo_expenses.delete_many({'resource_id': {'$in': ids_chunk}})


def insert_clean_expenses_for_actual_resources(all_actual_resource_ids, mongo_resource, mongo_expenses):
    expense_resource_ids = {x['resource_id'] for x in
                            mongo_expenses.find({}, ['resource_id'])}
    resources_without_expenses = list(all_actual_resource_ids - expense_resource_ids)
    for i in range(0, len(resources_without_expenses), CHUNK_INSERT_SIZE):
        ids_chunk = resources_without_expenses[i:i + CHUNK_INSERT_SIZE]
        create_initial_expenses(ids_chunk, mongo_resource, mongo_expenses)


def create_initial_expenses(resource_ids_chunk, mongo_resource, mongo_expenses):
    resources = mongo_resource.aggregate([
        {
            '$match': {
                '_id': {'$in': resource_ids_chunk}
            }
        }
    ])
    clean_expenses = []
    for resource in resources:
        clean_expense = {
            'budget_id': resource.get('budget_id'),
            'cloud_account_id': resource['cloud_account_id'],
            'region': resource.get('region'),
            'resource_id': resource['_id'],
            'cost': 0,
            'resource_type': resource['resource_type'],
            'cloud_resource_id': resource['cloud_resource_id'],
            'service_name': None,
            'date': datetime.utcnow().replace(
                hour=0, minute=0, second=0, microsecond=0),
            'raw_data_links': [],
            'owner_id': resource.get('employee_id'),
            '_initial': True
        }
        clean_expenses.append(clean_expense)
    if clean_expenses:
        mongo_expenses.bulk_write([
            UpdateOne(
                filter={
                    k: e[k] for k in ['cloud_resource_id', 'cloud_account_id']
                },
                update={
                    '$setOnInsert': {k: v for k, v in e.items()},
                },
                upsert=True,
            ) for e in clean_expenses
        ])


def get_all_resources_ids(mongo_resource):
    return {x['_id'] for x in mongo_resource.find({}, ['_id'])}


def get_actual_resources_ids(actual_cloud_account_ids, mongo_resources):
    actual_cloud_account_resource_filters = {'cloud_account_id': {'$in': actual_cloud_account_ids}}
    return {x['_id'] for x in mongo_resources.find(actual_cloud_account_resource_filters, ['_id'])}


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        cloud_acc_table = table('cloudaccount',
                                column('id', sa.String(36)),
                                column('deleted_at', Integer()))
        all_cloud_accounts_stmt = select(
            [cloud_acc_table.c.id, cloud_acc_table.c.deleted_at]
        )
        all_cloud_accounts = session.execute(all_cloud_accounts_stmt)
        deleted_cloud_account_ids = []
        actual_cloud_account_ids = []
        for id_, deleted_at_ in all_cloud_accounts:
            if deleted_at_ != 0:
                deleted_cloud_account_ids.append(id_)
            else:
                actual_cloud_account_ids.append(id_)

        mongo_client = _get_mongo_client()
        mongo_expenses = _get_expenses_collection(mongo_client)
        mongo_resources = _get_resources_collection(mongo_client)

        remove_clean_expenses_for_deleted_cloud_accounts(deleted_cloud_account_ids, mongo_expenses)

        all_existing_resource_ids = get_all_resources_ids(mongo_resources)
        remove_expenses_with_not_existing_resources(all_existing_resource_ids, mongo_expenses)

        all_actual_resource_ids = get_actual_resources_ids(actual_cloud_account_ids, mongo_resources)

        insert_clean_expenses_for_actual_resources(all_actual_resource_ids, mongo_resources, mongo_expenses)
    finally:
        session.close()


def downgrade():
    pass
