""""snapshot offset"

Revision ID: 71e871c7d1f3
Revises: f3e204bc77e7
Create Date: 2018-05-17 15:34:52.814785

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '71e871c7d1f3'
down_revision = 'f3e204bc77e7'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('snapshot', sa.Column('offset', sa.BIGINT(), nullable=True))


def downgrade():
    op.drop_column('snapshot', 'offset')

