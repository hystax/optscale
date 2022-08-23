""""added_import_image_id_failover"

Revision ID: 8c81d4727bdb
Revises: 3de565d98c77
Create Date: 2018-08-29 22:55:45.364808

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '8c81d4727bdb'
down_revision = '3de565d98c77'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('failover', sa.Column('import_task_id',
                                        sa.String(length=36), nullable=True))


def downgrade():
    op.drop_column('failover', 'import_task_id')


