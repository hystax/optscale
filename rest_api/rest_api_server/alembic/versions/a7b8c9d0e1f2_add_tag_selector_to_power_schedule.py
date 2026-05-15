"""add tag_selector to power_schedule

Revision ID: a7b8c9d0e1f2
Revises: c1d4f7a92b08
Create Date: 2026-05-08
"""
import sqlalchemy as sa
from alembic import op

revision = 'a7b8c9d0e1f2'
down_revision = 'c1d4f7a92b08'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'power_schedule',
        sa.Column('tag_selector', sa.Text(), nullable=True)
    )


def downgrade():
    op.drop_column('power_schedule', 'tag_selector')
