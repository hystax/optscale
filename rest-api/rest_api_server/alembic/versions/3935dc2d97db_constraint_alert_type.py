""""constraint_alert_type"

Revision ID: 3935dc2d97db
Revises: 9341c038cc7c
Create Date: 2021-08-03 13:56:47.649658

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '3935dc2d97db'
down_revision = '9341c038cc7c'
branch_labels = None
depends_on = None

old_types = sa.Enum('COST', 'FORECAST')
new_types = sa.Enum('COST', 'FORECAST', 'CONSTRAINT')


def upgrade():
    op.alter_column('pool_alert', 'based', existing_type=old_types,
                    type_=new_types, nullable=False)


def downgrade():
    pool_alert_t = sa.sql.table('pool_alert', sa.sql.column('id'),
                                sa.sql.column('based'))
    alert_contact_t = sa.sql.table('alert_contact',
                                   sa.sql.column('pool_alert_id'))
    op.execute(alert_contact_t.delete().where(
        alert_contact_t.c.pool_alert_id == pool_alert_t.c.id).where(
        pool_alert_t.c.based == 'CONSTRAINT'))
    op.execute(
        pool_alert_t.delete().where(pool_alert_t.c.based == 'CONSTRAINT'))
    op.alter_column('pool_alert', 'based', existing_type=new_types,
                    type_=old_types, nullable=False)
