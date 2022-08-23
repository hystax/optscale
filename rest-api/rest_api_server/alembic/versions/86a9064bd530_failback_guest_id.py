""""failback_guest_id"

Revision ID: 86a9064bd530
Revises: 42c43eaf6cba
Create Date: 2017-10-30 09:16:33.384513

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '86a9064bd530'
down_revision = '42c43eaf6cba'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'failback_device', sa.Column('meta', sa.TEXT(), nullable=True))
    op.add_column('failback_snapshot', sa.Column('drive_size', sa.BigInteger(),
                                                 nullable=False))


def downgrade():
    op.drop_column('failback_snapshot', 'drive_size')
    op.drop_column('failback_device', 'meta')
