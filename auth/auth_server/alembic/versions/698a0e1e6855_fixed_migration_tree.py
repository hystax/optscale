"""Fixed_migration_tree

Revision ID: 698a0e1e6855
Revises: 5771980b501b, 9f2cce682862
Create Date: 2022-07-07 15:38:20.323980

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '698a0e1e6855'
down_revision = ('5771980b501b', '9f2cce682862')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
