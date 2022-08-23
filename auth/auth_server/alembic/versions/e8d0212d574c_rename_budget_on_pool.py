""""rename_budget_on_pool"

Revision ID: e8d0212d574c
Revises: 245ada360fa4
Create Date: 2021-05-04 18:15:48.119599

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from sqlalchemy import column, table
from sqlalchemy.orm import Session

revision = 'e8d0212d574c'
down_revision = '245ada360fa4'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        type_table = sa.table('type', sa.Column('name', sa.String(24)))
        session.execute(sa.update(type_table).values(name='pool').where(type_table.c.name == 'budget'))
        action_table = sa.table('action', sa.Column('name', sa.String(64)))
        session.execute(sa.update(action_table).values(name='MANAGE_POOLS').where(
            action_table.c.name == 'MANAGE_BUDGETS'))
        session.commit()
    finally:
        session.close()


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        type_table = sa.table('type', sa.Column('name', sa.String(24)))
        session.execute(sa.update(type_table).values(name='budget').where(type_table.c.name == 'pool'))
        action_table = sa.table('action', sa.Column('name', sa.String(64)))
        session.execute(sa.update(action_table).values(name='MANAGE_BUDGETS').where(
            action_table.c.name == 'MANAGE_POOLS'))
        session.commit()
    finally:
        session.close()
