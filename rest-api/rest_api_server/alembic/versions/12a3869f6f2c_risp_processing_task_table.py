""""risp_processing_task_table"

Revision ID: 12a3869f6f2c
Revises: 002792d433a3
Create Date: 2023-03-31 12:15:17.965952

"""
import sqlalchemy as sa
from alembic import op
from rest_api_server.models import types

# revision identifiers, used by Alembic.
revision = '12a3869f6f2c'
down_revision = '002792d433a3'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'risp_processing_task',
        sa.Column('deleted_at', sa.Integer(), nullable=False),
        sa.Column('id', types.NullableUuid(length=36),
                  nullable=False),
        sa.Column('created_at', sa.Integer(), nullable=False),
        sa.Column('cloud_account_id', types.Uuid(length=36), nullable=False),
        sa.Column('start_date', types.Int(), nullable=False),
        sa.Column('end_date', types.Int(), nullable=False),
        sa.ForeignKeyConstraint(['cloud_account_id'],
                                ['cloudaccount.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('cloud_account_id', 'start_date',
                            'end_date', 'deleted_at',
                            name='uc_acc_id_start_end_deleted_at')
        )


def downgrade():
    op.drop_table('risp_processing_task')
