"""create cloud_volume_size field in drive table

Revision ID: 4115e967f2f7
Revises: 116f5bf4c7dc
Create Date: 2018-11-09 10:03:04.499806

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4115e967f2f7'
down_revision = '116f5bf4c7dc'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('drive', sa.Column('cloud_volume_size', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('drive', 'cloud_volume_size')
