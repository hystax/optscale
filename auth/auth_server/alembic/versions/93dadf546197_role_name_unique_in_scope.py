""""role_name_unique_in_scope"

Revision ID: 93dadf546197
Revises: cd45fc1e24e1
Create Date: 2017-07-05 11:05:01.418558

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '93dadf546197'
down_revision = 'cd45fc1e24e1'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index('idx_role_name_scope', 'role',
                    ['name', 'type_id', 'scope_id'], unique=True)


def downgrade():
    op.drop_index('idx_role_name_scope', table_name='role')
