"""Fixed_migration_tree

Revision ID: edad38e1dd89
Revises: 4115e967f2f7
Create Date: 2018-11-09 16:22:06.644570

"""
from alembic import op
from sqlalchemy.orm import Session

# revision identifiers, used by Alembic.
revision = 'edad38e1dd89'
down_revision = ('edad38e1dd88', '5d3fea32d151')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
