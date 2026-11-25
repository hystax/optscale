"""add mfa models

Revision ID: 771437d2ff9f
Revises: 88f7bebcdcb9
Create Date: 2026-10-16 19:15:07.410336

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '771437d2ff9f'
down_revision = '88f7bebcdcb9'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'mfa_method',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('created_at', sa.Integer(), nullable=False),
        sa.Column('deleted_at', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('type', sa.Enum('totp', 'email'), nullable=False),
        sa.Column('secret', sa.String(256), nullable=True),
        sa.Column('label', sa.String(256), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=False),
        sa.Column('confirmed_at', sa.Integer(), nullable=False),
        sa.Column('last_used_step', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.UniqueConstraint('user_id', 'type', 'deleted_at',
                            name='uc_user_id_type_deleted_at')
    )

    op.create_table(
        'login_challenge',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('created_at', sa.Integer(), nullable=False),
        sa.Column('deleted_at', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('state', sa.Enum('mfa_required', 'enrollment_required'),
                  nullable=False),
        sa.Column('expires_at', sa.Integer(), nullable=False),
        sa.Column('attempts', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'])
    )
    op.create_index(op.f('ix_login_challenge_expires_at'),
                    'login_challenge', ['expires_at'], unique=False)

    op.create_table(
        'auth_policy',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('created_at', sa.Integer(), nullable=False),
        sa.Column('deleted_at', sa.Integer(), nullable=False),
        sa.Column('scope_type', sa.Enum('organization', 'domain'),
                  nullable=False),
        sa.Column('scope_id', sa.String(256), nullable=False),
        sa.Column('purpose', sa.Enum('mfa', 'sso'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('scope_type', 'scope_id', 'purpose', 'deleted_at',
                            name='uc_scope_type_scope_id_purpose_deleted_at')
    )

    # server_default fills existing rows with 'password'
    op.add_column('verification_code',
                  sa.Column('purpose', sa.Enum('password', 'mfa'),
                            nullable=False, server_default='password'))


def downgrade():
    op.drop_column('verification_code', 'purpose')
    op.drop_table('auth_policy')
    op.drop_index(op.f('ix_login_challenge_expires_at'),
                  table_name='login_challenge')
    op.drop_table('login_challenge')
    op.drop_table('mfa_method')
