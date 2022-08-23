""""resource_budget_assign_history"

Revision ID: 45ab0909f70b
Revises: d4e6b2040357
Create Date: 2020-04-06 15:34:21.503485

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '45ab0909f70b'
down_revision = 'd4e6b2040357'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'resourcebudgetassignmenthistory',
        sa.Column('deleted_at', sa.Integer(), nullable=False),
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('resource_id', sa.String(36), nullable=False),
        sa.Column('budget_id', sa.String(36), nullable=False),
        sa.Column('created_at', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['budget_id'], ['budget.id'], ),
        sa.ForeignKeyConstraint(['resource_id'], ['resource.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade():
    op.drop_table('resourcebudgetassignmenthistory')
