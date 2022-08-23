"""empty message

Revision ID: cf9a93d988c3
Revises: 42160b466586
Create Date: 2021-04-28 12:15:47.340018

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cf9a93d988c3'
down_revision = '42160b466586'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'organization_option',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('created_at', sa.Integer(), nullable=False),
        sa.Column('deleted_at', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(256), nullable=False),
        sa.Column('value', sa.TEXT(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id']),
        sa.PrimaryKeyConstraint('organization_id', 'name', 'deleted_at')
    )


def downgrade():
    op.drop_table('organization_option')
