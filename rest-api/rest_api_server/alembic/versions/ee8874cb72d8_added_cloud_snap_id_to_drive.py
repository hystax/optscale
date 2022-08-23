""""added_cloud_snap_id_to_drive"

Revision ID: ee8874cb72d8
Revises: 71e871c7d1f3
Create Date: 2018-05-24 16:10:14.404693

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'ee8874cb72d8'
down_revision = '71e871c7d1f3'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('drive', sa.Column('cloud_snapshot_id',
                                     sa.String(length=36), nullable=True))


def downgrade():
    op.drop_column('drive', 'cloud_snapshot_id')
