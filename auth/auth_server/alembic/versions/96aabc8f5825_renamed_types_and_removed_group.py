""""renamed_types_and_removed_group"

Revision ID: 96aabc8f5825
Revises: 8efd63cec7a4
Create Date: 2020-10-13 13:35:04.580849

"""
import time

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from sqlalchemy.orm import Session

revision = '96aabc8f5825'
down_revision = '8efd63cec7a4'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)

    try:
        type_table = sa.table(
            'type',
            sa.column('id', sa.Integer()),
            sa.column('name', sa.String(24)),
        )
        res = list(session.execute(sa.select([type_table.c.id]).where(
            type_table.c.name == 'group')))
        group_type_id = res[0]['id']

        # we don't have any group-related objects on most optscale clusters.
        # this is just in case someone created them manually
        user_table = sa.table('user', sa.column('type_id', sa.Integer()))
        assignment_table = sa.table('assignment',
                                    sa.column('type_id', sa.Integer()),
                                    sa.column('role_id', sa.Integer()))
        action_table = sa.table('action', sa.column('type_id', sa.Integer()),
                                sa.column('id', sa.Integer()))
        role_table = sa.table('role', sa.column('type_id', sa.Integer()),
                              sa.column('lvl_id', sa.Integer()),
                              sa.column('id', sa.Integer()))
        role_action_table = sa.table('role_action',
                                     sa.column('role_id', sa.Integer()),
                                     sa.column('action_id', sa.Integer()))

        session.execute(sa.delete(assignment_table).where(
            sa.or_(
                assignment_table.c.type_id == group_type_id,
                assignment_table.c.role_id.in_(
                    sa.select([role_table.c.id]).where(
                        sa.or_(role_table.c.type_id == group_type_id,
                               role_table.c.lvl_id == group_type_id)
                    )
                )
            )
        ))
        session.execute(sa.delete(user_table).where(
            user_table.c.type_id == group_type_id))
        session.execute(sa.delete(role_action_table).where(
            sa.or_(
                role_action_table.c.role_id.in_(
                    sa.select([role_table.c.id]).where(
                        sa.or_(role_table.c.type_id == group_type_id,
                               role_table.c.lvl_id == group_type_id))),
                role_action_table.c.action_id.in_(
                    sa.select([action_table.c.id]).where(
                        action_table.c.type_id == group_type_id))
            )
        ))
        session.execute(sa.delete(role_table).where(
            sa.or_(role_table.c.type_id == group_type_id,
                   role_table.c.lvl_id == group_type_id)))
        session.execute(sa.delete(action_table).where(
            action_table.c.type_id == group_type_id))

        session.execute(sa.delete(type_table).where(
            type_table.c.name == 'group'))

        session.execute(sa.update(type_table).values(name='organization').where(
            type_table.c.name == 'partner'))
        session.execute(sa.update(type_table).values(name='budget').where(
            type_table.c.name == 'customer'))
        session.commit()
    finally:
        session.close()


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)

    try:
        type_table = sa.table(
            'type',
            sa.column('id', sa.Integer()),
            sa.column('name', sa.String(24)),
            sa.column('parent_id', sa.Integer()),
            sa.column('assignable', sa.Boolean()),
            sa.column('created_at', sa.Integer()),
            sa.column('deleted_at', sa.Integer()),
        )
        session.execute(sa.update(type_table).values(name='partner').where(
            type_table.c.name == 'organization'))
        session.execute(sa.update(type_table).values(name='customer').where(
            type_table.c.name == 'budget'))

        res = list(session.execute(sa.select([type_table.c.id]).where(
            type_table.c.name == 'customer')))
        customer_type_id = res[0]['id']

        session.execute(sa.insert(type_table).values(
            name='group', parent_id=customer_type_id, assignable=False,
            created_at=int(time.time()), deleted_at=0))

        session.commit()
    finally:
        session.close()
