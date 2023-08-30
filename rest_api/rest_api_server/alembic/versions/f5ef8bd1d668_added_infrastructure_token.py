""""added_infrastructure_token"

Revision ID: f5ef8bd1d668
Revises: acef45928ac5
Create Date: 2023-04-11 12:43:43.225691

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f5ef8bd1d668'
down_revision = 'acef45928ac5'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'profiling_token',
        sa.Column('infrastructure_token', sa.String(36), nullable=False)
    )


def downgrade():
    op.drop_column('profiling_token', 'infrastructure_token')
