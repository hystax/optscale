"""Update indexes from budget to pool

Revision ID: 93c81a1434d7
Revises: a46a37cfef14
Create Date: 2021-05-19 09:53:30.489104

"""
from alembic import op
import os
from pymongo import MongoClient
from config_client.client import Client as EtcdClient

# revision identifiers, used by Alembic.
revision = '93c81a1434d7'
down_revision = 'a46a37cfef14'
branch_labels = None
depends_on = None

FOREIGN_KEYS = [
    {
        'old_name': 'alert_contact_ibfk_1',
        'new_name': 'alert_contact_pool_alert_fk',
        'table': 'alert_contact',
        'ref_table': 'pool_alert',
        'local_cols': ['pool_alert_id'],
        'remote_cols': ['id']
    },
    {
        'old_name': 'assignment_request_ibfk_2',
        'new_name': 'assignment_request_source_pool_fk',
        'table': 'assignment_request',
        'ref_table': 'pool',
        'local_cols': ['source_pool_id'],
        'remote_cols': ['id']
    },
    {
        'old_name': 'def_owner_budget_fk',
        'new_name': 'def_owner_pool_fk',
        'table': 'pool',
        'ref_table': 'employee',
        'local_cols': ['default_owner_id'],
        'remote_cols': ['id']
    },
    {
        'old_name': 'budget_organization_fk',
        'new_name': 'pool_organization_fk',
        'table': 'pool',
        'ref_table': 'organization',
        'local_cols': ['organization_id'],
        'remote_cols': ['id']
    },
    {
        'old_name': 'pool_alert_ibfk_1',
        'new_name': 'pool_alert_pool_fk',
        'table': 'pool_alert',
        'ref_table': 'pool',
        'local_cols': ['pool_id'],
        'remote_cols': ['id']
    },
    {
        'old_name': 'policy_budget_fk',
        'new_name': 'pool_policy_pool_fk',
        'table': 'pool_policy',
        'ref_table': 'pool',
        'local_cols': ['pool_id'],
        'remote_cols': ['id']
    },
    {
        'old_name': 'limit_hit_budget_fk',
        'new_name': 'limit_hit_pool_fk',
        'table': 'constraint_limit_hit',
        'ref_table': 'pool',
        'local_cols': ['pool_id'],
        'remote_cols': ['id']
    },
    {
        'old_name': 'def_budget_employee_fk',
        'new_name': 'def_pool_employee_fk',
        'table': 'employee',
        'ref_table': 'pool',
        'local_cols': ['default_pool_id'],
        'remote_cols': ['id']
    },
    {
        'old_name': 'organization_budget_fk',
        'new_name': 'organization_pool_fk',
        'table': 'organization',
        'ref_table': 'pool',
        'local_cols': ['pool_id'],
        'remote_cols': ['id']
    },
    {
        'old_name': 'rule_ibfk_1',
        'new_name': 'rule_pool_fk',
        'table': 'rule',
        'ref_table': 'pool',
        'local_cols': ['pool_id'],
        'remote_cols': ['id']
    }
]
MONGO_INDEXES = {
    'expenses': [
        {
            'old_name': 'BudgetId',
            'new_name': 'PoolId',
            'old_cols': [('budget_id', 1)],
            'new_cols': [('pool_id', 1)]
        }
    ],
    'expenses_group_month_resource': [
        {
            'old_name': 'BudgetDate',
            'new_name': 'PoolDate',
            'old_cols': [('budget_id', 1), ('date', 1)],
            'new_cols': [('pool_id', 1), ('date', 1)]
        },
        {
            'old_name': 'CloudAccountBudget',
            'new_name': 'CloudAccountPool',
            'old_cols': [('budget_id', 1), ('cloud_account_id', 1)],
            'new_cols': [('pool_id', 1), ('cloud_account_id', 1)]
        }
    ],
    'resources': [
        {
            'old_name': 'BudgetID',
            'new_name': 'PoolID',
            'old_cols': [('budget_id', 1)],
            'new_cols': [('pool_id', 1)]
        }
    ]
}
DEFAULT_ETCD_HOST = 'etcd-client'
DEFAULT_ETCD_PORT = 80


def _get_etcd_config_client():
    etcd_host = os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST)
    etcd_port = os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT)
    config_cl = EtcdClient(host=etcd_host, port=int(etcd_port))
    return config_cl


def _get_restapi_mongo():
    config_cl = _get_etcd_config_client()
    mongo_params = config_cl.mongo_params()
    mongo_conn_string = "mongodb://%s:%s@%s:%s" % mongo_params[:-1]
    mongo_client = MongoClient(mongo_conn_string)
    return mongo_client.restapi


def _drop_indexes(collection, indexes):
    list_indexes = [x['name'] for x in collection.list_indexes()]
    for index in indexes:
        if index in list_indexes:
            collection.drop_index(index)


def _create_indexes(collection, indexes, downgrade=False):
    for index in indexes:
        if downgrade:
            collection.create_index(index['old_cols'], name=index['old_name'])
        else:
            collection.create_index(index['new_cols'], name=index['new_name'])


def upgrade():
    for fk in FOREIGN_KEYS:
        op.drop_constraint(constraint_name=fk['old_name'],
                           table_name=fk['table'], type_='foreignkey')
        op.create_foreign_key(
            name=fk['new_name'], source_table=fk['table'],
            referent_table=fk['ref_table'], local_cols=fk['local_cols'],
            remote_cols=fk['remote_cols'])

    mongo_restapi = _get_restapi_mongo()
    for collection_name, indexes in MONGO_INDEXES.items():
        collection = getattr(mongo_restapi, collection_name)
        indexes_names = [x['old_name'] for x in indexes]
        _drop_indexes(collection, indexes_names)
        _create_indexes(collection, indexes)


def downgrade():
    for fk in FOREIGN_KEYS:
        op.drop_constraint(constraint_name=fk['new_name'],
                           table_name=fk['table'], type_='foreignkey')
        op.create_foreign_key(
            name=fk['old_name'], source_table=fk['table'],
            referent_table=fk['ref_table'], local_cols=fk['local_cols'],
            remote_cols=fk['remote_cols'])

    mongo_restapi = _get_restapi_mongo()
    for collection_name, indexes in MONGO_INDEXES.items():
        collection = getattr(mongo_restapi, collection_name)
        indexes_names = [x['new_name'] for x in indexes]
        _drop_indexes(collection, indexes_names)
        _create_indexes(collection, indexes, True)
