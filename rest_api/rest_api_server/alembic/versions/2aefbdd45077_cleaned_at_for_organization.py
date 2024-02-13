""""cleaned_at_for_organization"

Revision ID: 2aefbdd45077
Revises: a84e2b6e2053
Create Date: 2024-01-30 12:11:43.232671

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2aefbdd45077'
down_revision = 'a84e2b6e2053'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('organization',
                  sa.Column('cleaned_at', sa.Integer(), nullable=False,
                            default=0))


def downgrade():
    op.drop_column('organization', 'cleaned_at')
