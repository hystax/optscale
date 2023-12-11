""""power_schedule"

Revision ID: 9fd932293995
Revises: 3273906c73ac
Create Date: 2023-10-11 12:22:35.328198

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '9fd932293995'
down_revision = '3273906c73ac'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'power_schedule',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('organization_id', mysql.VARCHAR(length=36), nullable=False),
        sa.Column('name', sa.String(length=36), nullable=False),
        sa.Column('power_off', sa.String(length=5), nullable=False),
        sa.Column('power_on', sa.String(length=5), nullable=False),
        sa.Column('timezone', sa.String(length=36), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False, default=True),
        sa.Column('start_date', sa.Integer(), nullable=False, default=0),
        sa.Column('end_date', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.Integer(), nullable=False),
        sa.Column('deleted_at', sa.Integer(), nullable=False),
        sa.Column('last_eval', sa.Integer(), nullable=False, default=0),
        sa.Column('last_run', sa.Integer(), nullable=False, default=0),
        sa.Column('last_run_error', sa.TEXT(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(["organization_id"], ["organization.id"], ),
        sa.UniqueConstraint(
            "organization_id",
            "name",
            "deleted_at",
            name="uc_organization_id_name_deleted_at",
        ),
    )


def downgrade():
    op.drop_table('power_schedule')
