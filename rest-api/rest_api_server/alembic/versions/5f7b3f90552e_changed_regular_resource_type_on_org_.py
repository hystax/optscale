""""changed_regular_resource_type_on_org_constraints"

Revision ID: 5f7b3f90552e
Revises: 23f9b12582bd
Create Date: 2022-04-05 18:01:06.376665

"""
import json
import os

import sqlalchemy as sa

from alembic import op
from sqlalchemy.orm import Session

from config_client.client import Client as EtcdClient


# revision identifiers, used by Alembic.
revision = '5f7b3f90552e'
down_revision = '23f9b12582bd'
branch_labels = None
depends_on = None


ORGANIZATION_TABLE = sa.table(
    'organization',
    sa.Column('id', sa.String()),
    sa.Column('deleted_at', sa.Integer()),
)

ORGANIZATION_CONSTRAINT_TABLE = sa.table(
    'organization_constraint',
    sa.Column('id', sa.String()),
    sa.Column('organization_id', sa.String()),
    sa.Column('created_at', sa.Integer()),
    sa.Column('deleted_at', sa.Integer()),
    sa.Column('filters', sa.String()),
)

REGULAR_IDENTITY = 'regular'

DEFAULT_ETCD_HOST = 'etcd'
DEFAULT_ETCD_PORT = 80


def get_organization_ids(session):
    orgs_q = sa.select([
        ORGANIZATION_TABLE.c.id
    ]).where(ORGANIZATION_TABLE.c.deleted_at == 0)
    return [x[0] for x in session.execute(orgs_q)]


def get_constraints(session, organization_ids):
    filtered_constraints_q = sa.select([
        ORGANIZATION_CONSTRAINT_TABLE.c.id,
        ORGANIZATION_CONSTRAINT_TABLE.c.organization_id,
        ORGANIZATION_CONSTRAINT_TABLE.c.created_at,
        ORGANIZATION_CONSTRAINT_TABLE.c.filters
    ]).where(sa.and_(
        ORGANIZATION_CONSTRAINT_TABLE.c.organization_id.in_(organization_ids),
        ORGANIZATION_CONSTRAINT_TABLE.c.deleted_at == 0,
        ORGANIZATION_CONSTRAINT_TABLE.c.filters != '{}'
    ))
    return session.execute(filtered_constraints_q)


def get_etcd_config_client():
    etcd_host = os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST)
    etcd_port = os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT)
    config_cl = EtcdClient(host=etcd_host, port=int(etcd_port))
    return config_cl


def switch_filters_type(source_type, destination_type):
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        orgs = get_organization_ids(session)
        constraint_filters_map = {}
        for constraint in get_constraints(session, orgs):
            loaded_filters = json.loads(constraint['filters'])
            if not loaded_filters.get('resource_type'):
                continue

            type_changed = False
            for resource_type in loaded_filters['resource_type']:
                if resource_type and resource_type['type'] == source_type:
                    resource_type['type'] = destination_type
                    type_changed = True
            if type_changed:
                constraint_filters_map[constraint['id']] = json.dumps(
                    loaded_filters)

        for constraint_id, filters in constraint_filters_map.items():
            session.execute(sa.update(ORGANIZATION_CONSTRAINT_TABLE).values(
                {'filters': filters}).where(
                ORGANIZATION_CONSTRAINT_TABLE.c.id == constraint_id))
        session.commit()
    finally:
        session.close()


def upgrade():
    switch_filters_type(None, REGULAR_IDENTITY)


def downgrade():
    switch_filters_type(REGULAR_IDENTITY, None)
