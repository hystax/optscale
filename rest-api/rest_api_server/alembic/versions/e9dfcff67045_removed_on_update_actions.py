""""removed_on_update_actions"

Revision ID: e9dfcff67045
Revises: c0e63dc9adce
Create Date: 2019-02-11 09:09:09.680821

"""
from alembic import op
from sqlalchemy.orm import Session

# revision identifiers, used by Alembic.
revision = 'e9dfcff67045'
down_revision = 'c0e63dc9adce'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        session.execute(
            'ALTER TABLE async_task CHANGE `created_at` `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP')
        session.execute(
            'ALTER TABLE async_task CHANGE `updated_at` `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP')
        session.execute(
            'ALTER TABLE script CHANGE `created_at` `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP')
    finally:
        session.close()


def downgrade():
    pass
