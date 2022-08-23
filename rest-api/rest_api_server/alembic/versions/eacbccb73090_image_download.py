""""image_download"

Revision ID: eacbccb73090
Revises: 561160c9ae8c
Create Date: 2018-08-13 16:54:43.834311

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'eacbccb73090'
down_revision = '561160c9ae8c'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('cloudsite', sa.Column('cs_type', sa.Enum(
        'CLOUD_SITE', 'DUMMY_SITE', name='cs_type'), nullable=False,
                                         server_default='CLOUD_SITE'))
    op.add_column('cloudsite', sa.Column('ttl', sa.Integer(), nullable=False))


def downgrade():
    op.drop_column('cloudsite', 'ttl')
    op.drop_column('cloudsite', 'cs_type')
