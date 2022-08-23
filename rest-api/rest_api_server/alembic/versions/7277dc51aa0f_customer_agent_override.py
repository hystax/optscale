"""customer_agent_override

Revision ID: 7277dc51aa0f
Revises: c1095c9b7b6a
Create Date: 2019-11-06 09:43:30.207447

"""
from alembic import op
import sqlalchemy as sa
from rest_api_server.alembic.utils import utils


# revision identifiers, used by Alembic.
revision = '7277dc51aa0f'
down_revision = '8c5a8f3bf3d4'
branch_labels = None
depends_on = None


def upgrade():
    if not utils.table_has_column('customer', 'agent_override'):
        op.add_column('customer', sa.Column(
            'agent_override', sa.TEXT(), nullable=False))
        dt = sa.sql.table('customer', sa.sql.column(
            'agent_override', sa.TEXT()))
        op.execute(dt.update().values(agent_override='{}'))


def downgrade():
    if utils.table_has_column('customer', 'agent_override'):
        op.drop_column('customer', 'agent_override')
