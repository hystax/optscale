"""removed cloud_account last_import_modified_at

Revision ID: ae1027a6acf
Revises: c1d4f7a92b08
Create Date: 2026-09-04

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ae1027a6acf'
down_revision = 'c1d4f7a92b08'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('cloudaccount', 'last_import_modified_at')


def downgrade():
    op.add_column('cloudaccount',
                  sa.Column('last_import_modified_at', sa.Integer(),
                            nullable=False, default=0))
