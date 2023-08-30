""""cleaned_at_for_cloudaccount"

Revision ID: 18ff48efa898
Revises: 9cba239b08c7
Create Date: 2022-12-08 11:05:44.325516

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '18ff48efa898'
down_revision = '9cba239b08c7'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('cloudaccount',
                  sa.Column('cleaned_at', sa.Integer(), nullable=False,
                            default=0))


def downgrade():
    op.drop_column('cloudaccount', 'cleaned_at')
