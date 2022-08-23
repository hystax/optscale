""""assign_unassigned_resources"

Revision ID: e6584275de6e
Revises: 56140dd30553
Create Date: 2021-09-02 08:23:00.221917

"""
import os
import logging
from config_client.client import Client as EtcdClient
from pymongo import MongoClient, UpdateMany
from sqlalchemy import and_
import sqlalchemy as sa
from alembic import op
from sqlalchemy.orm import Session
from sqlalchemy.sql import table, column
from sqlalchemy import select, String

# revision identifiers, used by Alembic.
revision = 'e6584275de6e'
down_revision = '56140dd30553'
branch_labels = None
depends_on = None
DEFAULT_ETCD_HOST = 'etcd-client'
DEFAULT_ETCD_PORT = 2379
LOG = logging.getLogger(__name__)


def _get_etcd_config_client():
    etcd_host = os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST)
    etcd_port = os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT)
    config_cl = EtcdClient(host=etcd_host, port=int(etcd_port))
    return config_cl


def get_organizations(session):
    org_table = table('organization',
                      column('id',  String()),
                      column('deleted_at', sa.Integer()),
                      column('pool_id', String()))
    organizations = session.execute(
        select([org_table]).where(org_table.c.deleted_at == 0))
    return organizations


def get_cloud_accounts(session, organization_ids):
    ca_table = table('cloudaccount',
                     column('id',  String()),
                     column('deleted_at', sa.Integer()),
                     column('organization_id', String()))
    cloud_accounts = session.execute(
        select([ca_table]).where(and_(
            ca_table.c.organization_id.in_(organization_ids),
            ca_table.c.deleted_at == 0)))
    return cloud_accounts


def get_pools(session, pool_ids):
    pool_table = table('pool',
                       column('id',  String()),
                       column('default_owner_id', String()))
    pools = session.execute(
        select([pool_table]).where(
            pool_table.c.id.in_(pool_ids)))
    return pools


def get_pools_owners_maps(organizations, cloud_accounts, pools):
    pool_owner_map = {}
    for pool in pools:
        pool_owner_map[pool.id] = pool.default_owner_id

    org_pool_map = {}
    for org in organizations:
        org_pool_map[org.id] = (org.pool_id, pool_owner_map[org.pool_id])

    ca_pool_map = {}
    for ca in cloud_accounts:
        ca_pool_map[ca.id] = org_pool_map[ca.organization_id]
    return org_pool_map, ca_pool_map


def _mongo_collections():
    config_cl = _get_etcd_config_client()
    mongo_params = config_cl.mongo_params()
    mongo_conn_string = "mongodb://%s:%s@%s:%s" % mongo_params[:-1]
    mongo_client = MongoClient(mongo_conn_string)
    m_resources = mongo_client.restapi.resources
    m_expenses = mongo_client.restapi.expenses
    m_groupings = mongo_client.restapi.expenses_group_month_resource
    return m_resources, m_expenses, m_groupings


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    organizations = list(get_organizations(session))
    org_ids = [x.id for x in organizations]
    pool_ids = [x.pool_id for x in organizations]
    pools = get_pools(session, pool_ids)
    cloud_accounts = list(get_cloud_accounts(session, org_ids))
    session.close()
    org_pool_owner_map, ca_pool_owner_map = get_pools_owners_maps(
        organizations, cloud_accounts, pools)

    m_resources, m_expenses, m_groupings = _mongo_collections()

    for org_id in org_ids:
        ca_ids = [x.id for x in cloud_accounts if x.organization_id == org_id]
        res_pipeline = [
            {
                "$match": {
                    "$and": [
                        {
                            "$or": [
                                {
                                    "employee_id": None
                                },
                                {
                                    "pool_id": None
                                }
                            ]
                        },
                        {
                            "deleted_at": 0
                        },
                        {
                            "$or": [
                                {
                                    "cloud_account_id": {"$in": ca_ids}
                                },
                                {
                                    "organization_id": org_id
                                }
                            ]
                        }
                    ]
                }
            }
        ]
        resources = m_resources.aggregate(res_pipeline)

        resource_changes_map = {}
        resource_ids = []
        for resource in resources:
            if resource.get('organization_id'):
                pool_id = org_pool_owner_map[resource['organization_id']][0]
                employee_id = org_pool_owner_map[
                    resource['organization_id']][1]
            else:
                pool_id = ca_pool_owner_map[resource['cloud_account_id']][0]
                employee_id = ca_pool_owner_map[
                    resource['cloud_account_id']][1]
            resource_changes_map.update({
                resource['_id']: {
                    'employee_id': employee_id,
                    'pool_id': pool_id
                }
            })
            resource_ids.append(resource['_id'])

        if resource_changes_map:
            m_resources.bulk_write([
                UpdateMany(
                    filter={'_id': k},
                    update={'$set': v}
                ) for k, v in resource_changes_map.items()
            ])

        expense_changes_map = resource_changes_map.copy()
        for res_id, changes_dict in expense_changes_map.items():
            changes_dict['owner_id'] = changes_dict.pop('employee_id')

        if expense_changes_map:
            m_expenses.bulk_write([
                UpdateMany(
                    filter={'resource_id': k},
                    update={'$set': v}
                ) for k, v in expense_changes_map.items()
            ])
            m_groupings.bulk_write([
                UpdateMany(
                    filter={'resource_id': k},
                    update={'$set': v}
                ) for k, v in expense_changes_map.items()
            ])
        LOG.info('Processing finished for organization %s' % org_id)


def downgrade():
    pass
