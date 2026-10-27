# pylint: disable=C0103
"""Add user option table

Revision ID: 88f7bebcdcb9
Revises: 998f27cb8c46
Create Date: 2026-03-10 16:27:40.340018

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '88f7bebcdcb9'
down_revision = '998f27cb8c46'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'user_option',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('created_at', sa.Integer(), nullable=False),
        sa.Column('deleted_at', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(256), nullable=False),
        sa.Column('value', sa.TEXT(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.UniqueConstraint('user_id', 'name', 'deleted_at',
                            name='uc_user_id_name_deleted_at')
    )
    op.create_index(op.f('ix_user_option_user_name'),
                    'user_option', ['user_id', 'name'],
                    unique=False)


def downgrade():
    op.drop_table('user_option')
