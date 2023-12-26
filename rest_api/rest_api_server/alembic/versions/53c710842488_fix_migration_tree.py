""""fix_migration_tree"

Revision ID: 53c710842488
Revises: a9ee3d861023, 1418b07142ce
Create Date: 2023-08-02 07:22:46.900343

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '53c710842488'
down_revision = ('a9ee3d861023', '1418b07142ce')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
