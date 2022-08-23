""""update_default_value_of_is_cnr_column_in_MP"

Revision ID: b532c6a989db
Revises: 9b0929b2260f
Create Date: 2018-12-19 14:00:25.538776

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import expression


# revision identifiers, used by Alembic.
revision = 'b532c6a989db'
down_revision = '9b0929b2260f'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('mountpoint', 'is_cnr', server_default=expression.true())


def downgrade():
    op.alter_column('mountpoint', 'is_cnr', server_default=None)
