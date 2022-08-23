""""user"

Revision ID: 6edf443cadf7
Revises: 50fde88f196b
Create Date: 2021-03-15 10:22:45.760891

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6edf443cadf7'
down_revision = '50fde88f196b'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'user',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.Integer(), nullable=False),
        sa.Column('deleted_at', sa.Integer(), nullable=False),
        sa.Column('slack_user_id', sa.String(length=160), nullable=False),
        sa.Column('auth_user_id', sa.String(length=36), nullable=True),
        sa.Column('secret', sa.String(length=36), nullable=False),
        sa.Column('slack_channel_id', sa.String(length=160), nullable=False),
        sa.Column('organization_id', sa.String(length=36), nullable=True),
        sa.Column('employee_id', sa.String(length=36), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slack_user_id', 'deleted_at',
                            name='uc_slack_user_id_deleted_at')
    )
    op.create_index(op.f('ix_user_auth_user_id'), 'user', ['auth_user_id'],
                    unique=False)
    op.create_index(op.f('ix_user_secret'), 'user', ['secret'], unique=False)
    op.create_index(op.f('ix_user_slack_user_id'), 'user', ['slack_user_id'],
                    unique=False)


def downgrade():
    op.drop_index(op.f('ix_user_slack_user_id'), table_name='user')
    op.drop_index(op.f('ix_user_secret'), table_name='user')
    op.drop_index(op.f('ix_user_auth_user_id'), table_name='user')
    op.drop_table('user')
