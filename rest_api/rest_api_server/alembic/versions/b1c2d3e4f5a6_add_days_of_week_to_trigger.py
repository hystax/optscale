"""add days_of_week to power_schedule_trigger

Revision ID: b1c2d3e4f5a6
Revises: a7b8c9d0e1f2
Create Date: 2026-05-11
"""
import sqlalchemy as sa
from alembic import op

revision = 'b1c2d3e4f5a6'
down_revision = 'a7b8c9d0e1f2'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'power_schedule_trigger',
        sa.Column('days_of_week', sa.Text(), nullable=True)
    )


def downgrade():
    op.drop_column('power_schedule_trigger', 'days_of_week')
