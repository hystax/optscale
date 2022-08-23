"""jira_connected

Revision ID: 9f2cce682862
Revises: 69b97ccc8ec3
Create Date: 2021-10-21 13:30:14.685958

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import column, table
from sqlalchemy.orm import Session

# revision identifiers, used by Alembic.
revision = '9f2cce682862'
down_revision = '716f4735a9ea'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user', sa.Column('jira_connected', sa.Boolean(),
                                    nullable=False))
    bind = op.get_bind()
    session = Session(bind=bind)
    user_table = table('user', column('jira_connected', sa.Boolean()))
    try:
        session.execute(sa.update(user_table).values(jira_connected=False))
        session.commit()
    finally:
        session.close()


def downgrade():
    op.drop_column('user', 'jira_connected')
