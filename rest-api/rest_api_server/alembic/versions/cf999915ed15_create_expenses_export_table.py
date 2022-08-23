"""create_expenses_export_table

Revision ID: cf999915ed15
Revises: 
Create Date: 2021-05-28 09:55:25.344073

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cf999915ed15'
down_revision = '2d3df696c196'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'expenses_export',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('created_at', sa.Integer(), nullable=False),
        sa.Column('deleted_at', sa.Integer(), nullable=False),
        sa.Column('pool_id', sa.String(36), nullable=False),
        sa.ForeignKeyConstraint(['pool_id'], ['budget.id']),
        sa.PrimaryKeyConstraint('pool_id')
    )


def downgrade():
    op.drop_table('expenses_export')
