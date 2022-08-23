"""increase_client_key_length

Revision ID: 02a9af761e4e
Revises: d3f57dc2c021
Create Date: 2021-12-03 09:42:07.278150

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '02a9af761e4e'
down_revision = '74a1d07a30e5'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('jira_issue_attachment', 'client_key',
                    type_=sa.String(length=128),
                    existing_type=sa.String(length=36),
                    existing_nullable=False)


def downgrade():
    op.alter_column('jira_issue_attachment', 'client_key',
                    type_=sa.String(length=36),
                    existing_type=sa.String(length=128),
                    existing_nullable=False)
