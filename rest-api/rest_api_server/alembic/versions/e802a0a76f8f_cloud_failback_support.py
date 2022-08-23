""""cloud_failback_support"

Revision ID: e802a0a76f8f
Revises: 1252a2eca545
Create Date: 2019-07-24 13:56:06.414778

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e802a0a76f8f'
down_revision = '1252a2eca545'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('failback_device', sa.Column(
        'cloud_server_id', sa.String(length=36), nullable=True))
    op.add_column('failback_snapshot', sa.Column(
        'cloud_snapshot_id', sa.String(length=36), nullable=True))
    op.add_column('failback_snapshot', sa.Column(
        'cloud_volume_id', sa.String(length=36), nullable=True))


def downgrade():
    op.drop_column('failback_snapshot', 'cloud_volume_id')
    op.drop_column('failback_snapshot', 'cloud_snapshot_id')
    op.drop_column('failback_device', 'cloud_server_id')

