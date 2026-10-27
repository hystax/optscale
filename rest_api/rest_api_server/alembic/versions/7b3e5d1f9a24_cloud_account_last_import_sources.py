"""added last_import_source_id and last_import_source_account_id fields

Revision ID: 7b3e5d1f9a24
Revises: ae1027a6acf
Create Date: 2026-09-29

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7b3e5d1f9a24'
down_revision = 'ae1027a6acf'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('cloudaccount', sa.Column(
        'last_import_source_id', sa.String(36), nullable=True))
    op.add_column('cloudaccount', sa.Column(
        'last_import_source_account_id', sa.String(256), nullable=True))


def downgrade():
    op.drop_column('cloudaccount', 'last_import_source_account_id')
    op.drop_column('cloudaccount', 'last_import_source_id')
