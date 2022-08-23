""""fix_role_name_unique"

Revision ID: dcdab2085d32
Revises: 2b5e2351dc6a
Create Date: 2017-07-18 16:16:02.692154

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dcdab2085d32'
down_revision = 'b743d2ee7700'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_index('idx_role_name_scope', table_name='role')
    op.create_index('idx_role_name_scope', 'role', [
        'name', 'type_id', 'scope_id', 'deleted_at'], unique=True)


def downgrade():
    op.drop_index('idx_role_name_scope', table_name='role')
    op.create_index('idx_role_name_scope', 'role', [
        'name', 'type_id', 'scope_id'], unique=True)
