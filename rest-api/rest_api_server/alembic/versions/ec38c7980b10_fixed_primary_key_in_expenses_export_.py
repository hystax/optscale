"""Fixed primary key in expenses_export table

Revision ID: ec38c7980b10
Revises: cf999915ed15
Create Date: 2021-06-07 11:01:36.246652

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ec38c7980b10'
down_revision = 'cf999915ed15'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('expenses_export_ibfk_1', 'expenses_export', type_='foreignkey')
    op.drop_constraint('PRIMARY', 'expenses_export', type_='primary')
    op.create_primary_key('pk_expenses_export', 'expenses_export', ['id'])
    op.create_foreign_key('fk_pool_expenses_export', 'expenses_export',
                          'budget', ['pool_id'], ['id'])
    op.create_unique_constraint('uc_pool_id_deleted_at', 'expenses_export', ['pool_id', 'deleted_at'])


def downgrade():
    op.drop_constraint('uc_pool_id_deleted_at', 'expenses_export', type_='unique')
    op.drop_constraint('fk_pool_expenses_export', 'expenses_export', type_='foreignkey')
    op.drop_constraint('PRIMARY', 'expenses_export', type_='primary')
    op.create_primary_key('PRIMARY', 'expenses_export', ['pool_id'])
    op.create_foreign_key('expenses_export_ibfk_1', 'expenses_export', 'budget', ['pool_id'], ['id'])
