""""added_resources_discovery_cache"

Revision ID: 311bd7d6b356
Revises: c22d5adee7cc
Create Date: 2020-05-05 22:13:54.090978

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '311bd7d6b356'
down_revision = 'c22d5adee7cc'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('resource_cache_request',
    sa.Column('id', sa.String(length=36),
              nullable=False),
    sa.Column('valid_until', sa.Integer(), nullable=False),
    sa.Column('resource_type', sa.Enum(
        'instance', 'volume', 'vpc', 'sg'), nullable=False),
    sa.Column('business_unit_id',sa.String(length=36), nullable=False),
    sa.PrimaryKeyConstraint('id'))

    op.create_table('resource_cache',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('cache_id', sa.String(length=36), nullable=False),
    sa.Column('resource_id', sa.String(length=256), nullable=True),
    sa.Column('region', sa.String(length=255), nullable=True),
    sa.Column('budget_type', sa.String(length=255), nullable=True),
    sa.Column('budget_name', sa.String(length=256), nullable=True),
    sa.Column('budget_id', sa.String(length=36), nullable=True),
    sa.Column('owner_id', sa.String(length=36), nullable=True),
    sa.Column('owner_name', sa.String(length=256), nullable=True),
    sa.Column('cloud_credential_id', sa.String(length=36), nullable=True),
    sa.Column('cloud_credential_name', sa.String(length=256), nullable=True),
    sa.Column('size', sa.Integer(), nullable=True),
    sa.Column('volume_type', sa.String(length=32), nullable=True),
    sa.Column('name', sa.String(length=256), nullable=True),
    sa.Column('flavor', sa.String(length=64), nullable=True),
    sa.Column('business_unit_id', sa.String(length=36), nullable=False),
    sa.Column('is_default', sa.Boolean(), nullable=True),
    sa.Column('cidr', sa.String(length=18), nullable=True),
    sa.Column('vpc_id', sa.String(length=64), nullable=True),
    sa.ForeignKeyConstraint(['cache_id'], ['resource_cache_request.id'], ),
    sa.PrimaryKeyConstraint('id'))


def downgrade():
    op.drop_table('resource_cache')
    op.drop_table('resource_cache_request')
