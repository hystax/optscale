"""add last_run_details to power_schedule

Revision ID: e2f3a4b5c6d7
Revises: c3d4e5f6a7b8
Create Date: 2026-05-15
"""
import sqlalchemy as sa
from alembic import op

revision = 'e2f3a4b5c6d7'
down_revision = 'c3d4e5f6a7b8'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'power_schedule',
        sa.Column('last_run_details', sa.Text(), nullable=True)
    )


def downgrade():
    op.drop_column('power_schedule', 'last_run_details')
