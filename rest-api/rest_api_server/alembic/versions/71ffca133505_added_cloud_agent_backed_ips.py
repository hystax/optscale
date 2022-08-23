""""added_cloud_agent_api_urls"

Revision ID: 71ffca133505
Revises: 0e9e37eef8d6
Create Date: 2019-11-28 10:46:46.419306

"""
from alembic import op
import sqlalchemy as sa
from rest_api_server.alembic.utils import utils


# revision identifiers, used by Alembic.
revision = '71ffca133505'
down_revision = '0e9e37eef8d6'
branch_labels = None
depends_on = None


def upgrade():
    if not utils.table_has_column('cloud_agent', 'backed_ips'):
        op.add_column('cloud_agent', sa.Column('backed_ips', sa.TEXT(), nullable=True))


def downgrade():
    if utils.table_has_column('cloud_agent', 'backed_ips'):
        op.drop_column('cloud_agent', 'backed_ips')
