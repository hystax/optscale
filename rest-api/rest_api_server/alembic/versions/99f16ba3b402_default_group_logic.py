""""default_group_logic"

Revision ID: 99f16ba3b402
Revises: 6b5edd98bcef
Create Date: 2017-04-12 16:03:50.614008

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session
from sqlalchemy.dialects import mysql
from sqlalchemy.sql import table, column
from sqlalchemy import select, String, update, Boolean

# revision identifiers, used by Alembic.
revision = '99f16ba3b402'
down_revision = '6b5edd98bcef'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)

    op.add_column('customer', sa.Column('default_group_id',
                                        sa.String(length=36), nullable=True))

    try:
        customer_table = table('customer',
                               column('default_group_id', String(36)),
                               column('id', String(36)))
        group_table = table('group',
                            column('customer_id', String(36)),
                            column('id', String(36)),
                            column('default', Boolean))
        stmt = select([group_table]).where(group_table.c.default == True)
        groups = session.execute(stmt)
        for group in groups:
            upd_stmt = update(customer_table).values(
                default_group_id=group['id']).where(
                customer_table.c.id == group['customer_id'])
            session.execute(upd_stmt)
        session.commit()
    finally:
        session.close()

    op.drop_column('group', 'default')


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)

    op.add_column(
        'group', sa.Column('default', mysql.TINYINT(display_width=1),
                           autoincrement=False, nullable=True))

    try:
        customer_table = table('customer',
                               column('default_group_id', String(36)),
                               column('id', String(36)))
        group_table = table('group',
                            column('customer_id', String(36)),
                            column('id', String(36)),
                            column('default', Boolean))
        stmt = select([customer_table]).where(
            customer_table.c.default_group_id != None)
        customers = session.execute(stmt)
        for customer in customers:
            upd_stmt = update(group_table).values(default=True).where(
                group_table.c.id == customer['default_group_id'])
            session.execute(upd_stmt)
        session.commit()
    finally:
        session.close()

    op.drop_column('customer', 'default_group_id')
