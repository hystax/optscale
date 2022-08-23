"""add_edit_customer_to_seed

Revision ID: 59d180a33635
Revises: f63a4ef42741
Create Date: 2019-11-27 18:00:56.917877

"""
import uuid

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from sqlalchemy import and_
from sqlalchemy.orm import Session

revision = '59d180a33635'
down_revision = 'f63a4ef42741'
branch_labels = None
depends_on = None


user_table = sa.table('user',
                      sa.column('id', sa.String(36)),
                      sa.column('type_id', sa.Integer),
                      sa.column('display_name', sa.String(64)))
assignment_table = sa.table('assignment',
                            sa.column('role_id', sa.String(36)),
                            sa.column('user_id', sa.Integer))
action_table = sa.table('action',
                        sa.column('id', sa.Integer),
                        sa.column('name', sa.String(64)))
role_action_table = sa.table('role_action',
                             sa.column('id', sa.String(36)),
                             sa.column('role_id', sa.Integer),
                             sa.column('action_id', sa.Integer))
EDIT_CUSTOMER_INFO = 'EDIT_CUSTOMER_INFO'
role_q = sa.select([assignment_table.c.role_id]).where(
    assignment_table.c.user_id.in_(
        sa.select([user_table.c.id]).where(
            and_(
                user_table.c.type_id == 1,
                user_table.c.display_name == 'SEED',
            )
        ))
)
action_q = sa.select([action_table.c.id]).where(
    action_table.c.name == EDIT_CUSTOMER_INFO)


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)

    try:
        role = session.execute(role_q).fetchone()
        if role is None:
            # there is not seed user in this
            return
        role_id = role['role_id']
        action_id = session.execute(action_q).fetchone()['id']

        session.execute(role_action_table.insert().values(
            id=str(uuid.uuid4()), role_id=role_id, action_id=action_id))
        session.commit()
    finally:
        session.close()


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)

    try:
        session.execute(
            sa.delete(role_action_table).where(
                and_(
                    role_action_table.c.role_id.in_(role_q),
                    role_action_table.c.action_id.in_(action_q),
                )
            )
        )
        session.commit()
    finally:
        session.close()
