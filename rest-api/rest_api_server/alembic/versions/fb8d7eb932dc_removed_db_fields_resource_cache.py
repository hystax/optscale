""""removed_db_fields_resource_cache"

Revision ID: fb8d7eb932dc
Revises: a73a5a839f5a
Create Date: 2020-05-20 13:26:54.202514

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'fb8d7eb932dc'
down_revision = 'a73a5a839f5a'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('resource_cache', 'owner_id')
    op.drop_column('resource_cache', 'budget_type')
    op.drop_column('resource_cache', 'budget_name')
    op.drop_column('resource_cache', 'budget_id')
    op.drop_column('resource_cache', 'owner_name')


def downgrade():
    op.add_column('resource_cache', sa.Column('owner_name', sa.String(
        length=256), nullable=True))
    op.add_column('resource_cache', sa.Column(
        'budget_id', sa.String(length=36), nullable=True))
    op.add_column('resource_cache', sa.Column(
        'budget_name', sa.String(length=256), nullable=True))
    op.add_column('resource_cache', sa.Column(
        'budget_type', sa.String(length=255), nullable=True))
    op.add_column('resource_cache', sa.Column('owner_id', sa.String(length=36),
                                              nullable=True))
