""""remove_customer_email_unique"

Revision ID: b6f7ce253259
Revises: 53877d99024e
Create Date: 2017-05-05 11:29:10.387283

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'b6f7ce253259'
down_revision = '53877d99024e'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_index(op.f('ix_customer_email'), table_name='customer')


def downgrade():
    op.create_index(op.f('ix_customer_email'), 'customer', ['email'],
                    unique=True)
