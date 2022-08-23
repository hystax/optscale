""""failback_hb"

Revision ID: 42c43eaf6cba
Revises: 875c236094ba
Create Date: 2017-10-24 15:53:57.916522

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '42c43eaf6cba'
down_revision = '4451a81a7415'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'failback_snapshot', sa.Column('failback_device_id',
                                       sa.String(length=36), nullable=False))
    op.create_foreign_key('fk_fb_device_id', 'failback_snapshot',
                          'failback_device', ['failback_device_id'], ['id'])


def downgrade():
    op.drop_constraint('fk_fb_device_id', 'failback_snapshot',
                       type_='foreignkey')
    op.drop_column('failback_snapshot', 'failback_device_id')
