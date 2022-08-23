"""Add assignment resource table

Revision ID: 700b47bd8891
Revises: db8d5f85eff1
Create Date: 2020-04-14 09:20:21.110825

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '700b47bd8891'
down_revision = 'afba5e482333'
branch_labels = None
depends_on = None



def upgrade():
    op.create_table(
        'assignment_request',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('resource_id', sa.String(36), nullable=False),
        sa.Column('source_budget_id', sa.String(36), nullable=True),
        sa.Column('message', sa.String(255), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
        sa.Column('deleted_at', sa.Integer(), nullable=False),
        sa.Column('approver_id', sa.String(36), nullable=False),
        sa.Column('requester_id', sa.String(36), nullable=False),
        sa.Column('status', sa.Enum(
            'PENDING', 'APPROVED', 'DECLINED', 'CANCELED'),
                  nullable=False, server_default='PENDING'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['resource_id'], ['resource.id'], ),
        sa.ForeignKeyConstraint(['source_budget_id'], ['budget.id'], ),
        sa.ForeignKeyConstraint(['approver_id'], ['employee.id'], ),
        sa.ForeignKeyConstraint(['requester_id'], ['employee.id'], ),
    )


def downgrade():
    op.drop_table('assignment_request')
