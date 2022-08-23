""""increased_user_displayname"

Revision ID: 8efd63cec7a4
Revises: ff740b5b3df3
Create Date: 2020-10-02 07:24:27.241301

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func
from sqlalchemy.orm import Session
from sqlalchemy.sql import table, column
from sqlalchemy import update, String


# revision identifiers, used by Alembic.
revision = '8efd63cec7a4'
down_revision = 'ff740b5b3df3'
branch_labels = None
depends_on = None

OLD_TYPE = sa.String(length=64)
NEW_TYPE = sa.String(length=256)


def upgrade():
    op.alter_column('user', 'display_name',
                    existing_type=OLD_TYPE, type_=NEW_TYPE, nullable=False)


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)

    user_table = table('user',
                       column('display_name', String(256)))
    update_stmt = update(user_table).values(
        display_name=func.substr(user_table.c.display_name, 1, 64)).where(
        func.length(user_table.c.display_name) > 64)
    try:
        session.execute(update_stmt)
        session.commit()
    finally:
        session.close()

    op.alter_column('user', 'display_name',
                    existing_type=NEW_TYPE, type_=OLD_TYPE, nullable=False)
