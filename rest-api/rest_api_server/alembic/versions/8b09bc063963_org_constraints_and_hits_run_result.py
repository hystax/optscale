""""org_constraints_and_hits_run_result"

Revision ID: 8b09bc063963
Revises: eceabb30d586
Create Date: 2022-05-25 10:00:04.152416

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8b09bc063963'
down_revision = 'eceabb30d586'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('organization_constraint', sa.Column(
        'last_run_result', sa.TEXT(), nullable=False, server_default='{}'))
    op.add_column('organization_limit_hit', sa.Column(
        'run_result', sa.TEXT(), nullable=False, server_default='{}'))


def downgrade():
    op.drop_column('organization_limit_hit', 'run_result')
    op.drop_column('organization_constraint', 'last_run_result')
