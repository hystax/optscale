""""organization_limit_hit"

Revision ID: 33b0cba5925a
Revises: 99e80e2aea51
Create Date: 2022-02-14 16:43:22.600975

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '33b0cba5925a'
down_revision = '99e80e2aea51'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('organization_limit_hit',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('created_at', sa.Integer(), nullable=False),
        sa.Column('deleted_at', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.String(36), nullable=False),
        sa.Column('constraint_id', sa.String(36), nullable=False),
        sa.Column('constraint_limit', sa.Float(), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id']),
        sa.ForeignKeyConstraint(['constraint_id'],
                                ['organization_constraint.id']),
        sa.UniqueConstraint('constraint_id', 'created_at',
                            name='uc_constraint_id_created_at')
    )


def downgrade():
    op.drop_table('organization_limit_hit')
