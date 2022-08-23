""""removed_failback_progress"

Revision ID: 8beda2f3740a
Revises: ee0476ed5da2
Create Date: 2017-11-07 15:06:50.132221

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '8beda2f3740a'
down_revision = 'ee0476ed5da2'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('failback', 'progress')


def downgrade():
    op.add_column('failback', sa.Column('progress', sa.Integer,
                                        autoincrement=False, nullable=False))
