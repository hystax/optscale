""""added_calendar_synchronization_table"

Revision ID: 56140dd30553
Revises: 393bd13a6820
Create Date: 2021-08-26 11:01:51.906900

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '56140dd30553'
down_revision = '393bd13a6820'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'calendar_synchronization',
        sa.Column('deleted_at', sa.Integer(), nullable=False),
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('created_at', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.String(36), nullable=False),
        sa.Column('calendar_id', sa.String(256), nullable=False),
        sa.Column('last_completed', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('deleted_at', 'organization_id', name='uc_org_id_deleted_at')
    )


def downgrade():
    op.drop_table('calendar_synchronization')
