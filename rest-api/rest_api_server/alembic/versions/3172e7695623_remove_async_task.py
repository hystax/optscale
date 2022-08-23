"""remove_async_task

Revision ID: 3172e7695623
Revises: 325c35031a08
Create Date: 2020-07-17 15:03:25.269963

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session

# revision identifiers, used by Alembic.

revision = '3172e7695623'
down_revision = 'dbc597a97c60'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('async_task')


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        op.create_table('async_task',
            sa.Column('deleted_at', sa.Integer(), nullable=False),
            sa.Column('id', sa.String(36), nullable=False),
            sa.Column('user_id', sa.String(36), nullable=True),
            sa.Column('state', sa.Enum('NEW', 'PROCESSING', 'DONE', 'ERROR'), nullable=False),
            sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
            sa.Column('updated_at', sa.TIMESTAMP(), nullable=False),
            sa.Column('request_url', sa.String(length=256), nullable=False),
            sa.Column('request_method', sa.String(length=256), nullable=False),
            sa.Column('request_headers', sa.TEXT(), nullable=False),
            sa.Column('request_body', sa.TEXT(), nullable=True),
            sa.Column('response_code', sa.Integer(), nullable=True),
            sa.Column('response_headers', sa.TEXT(), nullable=True),
            sa.Column('response_body', sa.TEXT(), nullable=True),
            sa.Column('response_message', sa.TEXT(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        session.execute(
            'ALTER TABLE async_task CHANGE `created_at` `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP')
        session.execute(
            'ALTER TABLE async_task CHANGE `updated_at` `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP')
    finally:
        session.close()
