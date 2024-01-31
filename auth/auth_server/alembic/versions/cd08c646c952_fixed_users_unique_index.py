""""fixed_users_unique_index"

Revision ID: cd08c646c952
Revises: 86bb9ebc3c20
Create Date: 2024-01-28 05:01:58.248505

"""
from alembic import op
from sqlalchemy.exc import ProgrammingError


# revision identifiers, used by Alembic.
revision = 'cd08c646c952'
down_revision = '86bb9ebc3c20'
branch_labels = None
depends_on = None


def upgrade():
    try:
        op.create_index('idx_user_email_unique', 'user',
                        ['email', 'deleted_at'],
                        unique=True)
    except ProgrammingError as exc:
        if "Duplicate key name" in str(exc):
            pass
        else:
            raise exc


def downgrade():
    pass
