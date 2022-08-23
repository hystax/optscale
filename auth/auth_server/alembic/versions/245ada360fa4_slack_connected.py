""""slack_connected"

Revision ID: 245ada360fa4
Revises: 96aabc8f5825
Create Date: 2021-03-10 09:58:48.119599

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from sqlalchemy import column, table
from sqlalchemy.orm import Session

revision = '245ada360fa4'
down_revision = '96aabc8f5825'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user', sa.Column('slack_connected', sa.Boolean(),
                                    nullable=False))
    bind = op.get_bind()
    session = Session(bind=bind)
    user_table = table('user', column('slack_connected', sa.Boolean()))
    try:
        session.execute(sa.update(user_table).values(slack_connected=False))
        session.commit()
    finally:
        session.close()


def downgrade():
    op.drop_column('user', 'slack_connected')
