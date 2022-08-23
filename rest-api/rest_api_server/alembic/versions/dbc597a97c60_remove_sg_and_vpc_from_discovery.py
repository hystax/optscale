"""Remove sg and vpc from discovery

Revision ID: dbc597a97c60
Revises: 325c35031a08
Create Date: 2020-07-20 12:22:41.977186

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import or_
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'dbc597a97c60'
down_revision = '325c35031a08'
branch_labels = None
depends_on = None

old_types = sa.Enum('instance', 'volume', 'vpc', 'sg', 'snapshot')
new_types = sa.Enum('instance', 'volume', 'snapshot')


def upgrade():
    raht = sa.sql.table(
        'resource_assignment_history', sa.sql.column('resource_id'))
    rt = sa.sql.table(
        'resource', sa.sql.column('id'), sa.sql.column('resource_type'))
    assign_request = sa.sql.table(
        'assignment_request', sa.sql.column('resource_id'))
    op.execute(raht.delete().where(raht.c.resource_id == rt.c.id).where(
        rt.c.resource_type.in_(['Vpc', 'SecurityGroup'])))
    op.execute(assign_request.delete().where(
        assign_request.c.resource_id == rt.c.id).where(
        rt.c.resource_type.in_(['Vpc', 'SecurityGroup'])))
    op.execute(rt.delete().where(
        rt.c.resource_type.in_(['Vpc', 'SecurityGroup'])))

    rct = sa.sql.table(
        'resource_cache', sa.sql.column('cidr'), sa.sql.column('vpc_id'),
        sa.sql.column('is_default'))
    op.execute(rct.delete().where(
        or_(rct.c.cidr.isnot(None), rct.c.vpc_id.isnot(None),
            rct.c.is_default.isnot(None))))

    rcrt = sa.sql.table(
        'resource_cache_request', sa.sql.column('resource_type', new_types))
    op.execute(
        rcrt.delete().where(rcrt.c.resource_type.in_(['vpc', 'sg'])))
    op.alter_column(
        'resource_cache_request', 'resource_type', existing_type=old_types,
        type_=new_types, existing_nullable=False)

    op.drop_column('resource_cache', 'cidr')
    op.drop_column('resource_cache', 'vpc_id')
    op.drop_column('resource_cache', 'is_default')


def downgrade():
    op.alter_column(
        'resource_cache_request', 'resource_type', existing_type=new_types,
        type_=old_types, existing_nullable=False)

    op.add_column(
        'resource_cache', sa.Column('cidr', mysql.VARCHAR(
            collation='utf8mb4_unicode_ci', length=18), nullable=True))
    op.add_column(
        'resource_cache', sa.Column('is_default', mysql.TINYINT(
            display_width=1), autoincrement=False, nullable=True))
    op.add_column(
        'resource_cache', sa.Column('vpc_id', mysql.VARCHAR(
            collation='utf8mb4_unicode_ci', length=64), nullable=True))
