""""org_id_for_policy_constraints_and_hits"

Revision ID: 2c083c6e08ac
Revises: 728302f9e711
Create Date: 2020-12-22 16:24:54.464138

"""
import os

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session
from config_client.client import Client as EtcdClient
from pymongo import MongoClient

revision = '2c083c6e08ac'
down_revision = '728302f9e711'
branch_labels = None
depends_on = None
DEFAULT_ETCD_HOST = 'etcd-client'
DEFAULT_ETCD_PORT = 80


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
    op.add_column('budget_policy', sa.Column(
        'organization_id', sa.String(36), nullable=False))
    op.add_column('constraint_limit_hit', sa.Column(
        'organization_id', sa.String(36), nullable=False))
    op.add_column('resource_constraint', sa.Column(
        'organization_id', sa.String(36), nullable=False))

    bind = op.get_bind()
    session = Session(bind=bind)
    # budget table for budget - org map
    budget_table = sa.table(
        'budget',
        sa.column('id', sa.String(36)),
        sa.column('organization_id', sa.String(36))
    )
    # cloud account table for ca - org map
    ca_table = sa.table(
        'cloudaccount',
        sa.column('id', sa.String(36)),
        sa.column('organization_id', sa.String(36))
    )
    # constraint table for resource id and to add org id
    constraint_table = sa.table(
        'resource_constraint',
        sa.column('id', sa.String(36)),
        sa.column('resource_id', sa.String(36)),
        sa.column('organization_id', sa.String(36))
    )
    # hit table for resource ids and to add org
    hit_table = sa.table(
        'constraint_limit_hit',
        sa.column('id', sa.String(36)),
        sa.column('resource_id', sa.String(36)),
        sa.column('organization_id', sa.String(36))
    )
    # policy table for budget ids and to add org
    policy_table = sa.table(
        'budget_policy',
        sa.column('id', sa.String(36)),
        sa.column('budget_id', sa.String(36)),
        sa.column('organization_id', sa.String(36))
    )

    try:
        # get distinct resource ids in constraints
        resource_ids = set()
        for row in session.execute(sa.select(
                [sa.distinct(constraint_table.c.resource_id)])):
            resource_ids.add(row[0])

        # get distinct resource ids in hits
        for row in session.execute(sa.select(
                [sa.distinct(hit_table.c.resource_id)])):
            resource_ids.add(row[0])

        # sum all resource ids and get them from mongo
        # to create resource - ca map
        mongo_resources = _get_resources_collection()
        resource_ids = list(resource_ids)
        chunk_size = 500
        resource_ca_map = {}
        for i in range(0, len(resource_ids), chunk_size):
            ids_chunk = resource_ids[i:i + chunk_size]
            resources = mongo_resources.find({'_id': {'$in': ids_chunk}})
            for r in resources:
                resource_ca_map[r['_id']] = r['cloud_account_id']

        # get ca - org map
        ca_org_map = {}
        for row in session.execute(sa.select([ca_table])):
            ca_org_map[row['id']] = row['organization_id']

        # get all budgets and create budget - org map
        budget_org_map = {}
        for row in session.execute(sa.select([budget_table])):
            budget_org_map[row['id']] = row['organization_id']

        # fill hits table with org id
        for row in session.execute(sa.select([hit_table])):
            org_id = ca_org_map[resource_ca_map[row['resource_id']]]
            session.execute(sa.update(hit_table).values(
                organization_id=org_id).where(hit_table.c.id == row['id']))

        # fill policy table with org id
        for row in session.execute(sa.select([policy_table])):
            org_id = budget_org_map[row['budget_id']]
            session.execute(sa.update(policy_table).values(
                organization_id=org_id).where(policy_table.c.id == row['id']))

        # fill constraint table will org id
        for row in session.execute(sa.select([constraint_table])):
            org_id = ca_org_map[resource_ca_map[row['resource_id']]]
            session.execute(sa.update(constraint_table).values(
                organization_id=org_id).where(constraint_table.c.id == row['id']))

        session.commit()
    except Exception:
        session.rollback()
        drop_columns()
        raise
    finally:
        session.close()

    op.create_foreign_key('policy_org_fk', 'budget_policy', 'organization',
                          ['organization_id'], ['id'])
    op.create_foreign_key('limit_hit_org_fk', 'constraint_limit_hit',
                          'organization', ['organization_id'], ['id'])
    op.create_foreign_key('constraint_org_fk', 'resource_constraint',
                          'organization', ['organization_id'], ['id'])


def drop_columns():
    op.drop_column('resource_constraint', 'organization_id')
    op.drop_column('constraint_limit_hit', 'organization_id')
    op.drop_column('budget_policy', 'organization_id')


def downgrade():
    op.drop_constraint('constraint_org_fk', 'resource_constraint',
                       type_='foreignkey')
    op.drop_constraint('limit_hit_org_fk', 'constraint_limit_hit',
                       type_='foreignkey')
    op.drop_constraint('policy_org_fk', 'budget_policy',
                       type_='foreignkey')
    drop_columns()
