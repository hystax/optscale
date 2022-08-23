"""last_import_attempt_for_cloud_acc

Revision ID: 2d3df696c196
Revises: 0706e4e548d7
Create Date: 2021-05-06 17:59:06.793313

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2d3df696c196'
down_revision = '0706e4e548d7'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('cloudaccount',
                  sa.Column('last_import_attempt_at', sa.Integer(),
                            nullable=False, default=0))
    op.add_column('cloudaccount',
                  sa.Column('last_import_attempt_error', sa.TEXT(),
                            nullable=True))


def downgrade():
    op.drop_column('cloudaccount', 'last_import_attempt_at')
    op.drop_column('cloudaccount', 'last_import_attempt_error')
