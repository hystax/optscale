""""env_change_alert_type"

Revision ID: 9c2012e13f95
Revises: 6684759fb02e
Create Date: 2021-10-04 16:39:37.338702

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '9c2012e13f95'
down_revision = '6684759fb02e'
branch_labels = None
depends_on = None


old_types = sa.Enum('COST', 'FORECAST', 'CONSTRAINT')
new_types = sa.Enum('COST', 'FORECAST', 'CONSTRAINT', 'ENV_CHANGE')


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
        pool_alert_t.c.based == 'ENV_CHANGE'))
    op.execute(
        pool_alert_t.delete().where(pool_alert_t.c.based == 'ENV_CHANGE'))
    op.alter_column('pool_alert', 'based', existing_type=new_types,
                    type_=old_types, nullable=False)
