""""extended_k8s_node_with_cpu_and_memory"

Revision ID: 36440f4efae7
Revises: 44c50323f3bb
Create Date: 2021-07-09 15:46:51.965894

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '36440f4efae7'
down_revision = '44c50323f3bb'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('k8s_node')
    op.create_table(
        'k8s_node',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('cloud_account_id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.Integer(), nullable=False),
        sa.Column('deleted_at', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=256), nullable=False),
        sa.Column('flavor', sa.String(length=256), nullable=True),
        sa.Column('provider_id', sa.String(length=256), nullable=True),
        sa.Column('hourly_price', sa.Float(), nullable=True),
        sa.Column('last_seen', sa.Integer(), nullable=False),
        sa.Column('cpu', sa.Integer(), nullable=False),
        sa.Column('memory', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['cloud_account_id'], ['cloudaccount.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('cloud_account_id', 'name', 'provider_id', 'deleted_at',
                            name='uc_cloud_acc_id_name_provider_id_deleted_at')
    )


def downgrade():
    op.drop_column('k8s_node', 'memory')
    op.drop_column('k8s_node', 'cpu')
