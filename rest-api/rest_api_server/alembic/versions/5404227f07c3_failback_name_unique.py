""""failback_name_unique"

Revision ID: 5404227f07c3
Revises: 7f37849091e8
Create Date: 2017-12-18 12:05:27.995893

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '5404227f07c3'
down_revision = '7f37849091e8'
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint('uc_failback_name_customer_id', 'failback',
                                ['customer_id', 'name', 'deleted_at'])


def downgrade():
    op.drop_constraint('uc_failback_name_customer_id', 'failback',
                       type_='unique')
