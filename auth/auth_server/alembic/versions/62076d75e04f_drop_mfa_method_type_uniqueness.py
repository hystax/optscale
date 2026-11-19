# pylint: disable=C0103
"""Drop mfa_method type uniqueness

Revision ID: 62076d75e04f
Revises: 771437d2ff9f
Create Date: 2026-11-19 18:14:40.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '62076d75e04f'
down_revision = '771437d2ff9f'
branch_labels = None
depends_on = None


def upgrade():
    # a user can enroll several authenticator apps; the single e-mail
    # method is enforced by the auth controller under the user lock (MySQL
    # has no partial unique index). The foreign key on user_id relied on the
    # unique index, so a plain index is created before the constraint goes
    op.create_index(op.f('ix_mfa_method_user_id'), 'mfa_method',
                    ['user_id'], unique=False)
    op.drop_constraint('uc_user_id_type_deleted_at', 'mfa_method',
                       type_='unique')


def downgrade():
    # fails if a user has several active methods of the same type
    op.create_unique_constraint('uc_user_id_type_deleted_at', 'mfa_method',
                                ['user_id', 'type', 'deleted_at'])
    op.drop_index(op.f('ix_mfa_method_user_id'), table_name='mfa_method')
