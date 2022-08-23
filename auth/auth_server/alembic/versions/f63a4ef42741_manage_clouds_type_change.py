"""manage_clouds_type_change

Revision ID: f63a4ef42741
Revises: a130f8e76eb9
Create Date: 2019-10-08 17:48:05.927962

"""
import uuid

import sqlalchemy as sa
from alembic import op
from datetime import datetime
from sqlalchemy import and_
from sqlalchemy.orm import Session

# revision identifiers, used by Alembic.

revision = 'f63a4ef42741'
down_revision = 'a130f8e76eb9'
branch_labels = None
depends_on = None


OLD_TYPE = 1
NEW_TYPE = 3
MANAGE_CREDS = 'MANAGE_VSPHERE_CREDENTIALS'
MANAGE_CLOUDS = 'MANAGE_CLOUDS'


role_table = sa.table('role',
                      sa.column('id', sa.Integer),
                      sa.column('name', sa.String(64)),
                      sa.column('lvl_id', sa.Integer))

action_table = sa.table('action', sa.column('id', sa.Integer),
                        sa.column('name', sa.String(64)),
                        sa.column('deleted_at', sa.Integer))

role_action_table = sa.table('role_action',
                             sa.column('id', sa.String(36)),
                             sa.column('role_id', sa.Integer),
                             sa.column('action_id', sa.Integer))


def update_type(type_):
    bind = op.get_bind()
    session = Session(bind=bind)
    action_table = sa.table("action", sa.column('name', sa.String(64)),
                            sa.column('type_id', sa.Integer))

    try:
        update_cmd = sa.update(action_table).values(type_id=type_).where(
            action_table.c.name == MANAGE_CLOUDS)
        session.execute(update_cmd)
        session.commit()
    finally:
        session.close()


def get_action_id_by_name(session, action_table, name):
    for row in session.execute(sa.select([action_table.c.id]).where(
            action_table.c.name == name)):
        return row['id']


def upgrade():
    # - update type for MANAGE_CLOUDS to 3(customer-level)
    # - make sure that every role with MANAGE_VSPHERE_CREDENTIALS gets MANAGE_CLOUDS action
    # - mark MANAGE_VSPHERE_CREDENTIALS action as deleted
    update_type(NEW_TYPE)

    bind = op.get_bind()
    session = Session(bind=bind)

    try:
        creds_action_id = get_action_id_by_name(session, action_table, MANAGE_CREDS)
        clouds_action_id = get_action_id_by_name(session, action_table, MANAGE_CLOUDS)

        roles_with_manage_clouds = sa.select([role_action_table.c.role_id]).where(
            role_action_table.c.action_id == clouds_action_id)
        roles_with_manage_creds = sa.select([role_action_table.c.role_id]).where(
            role_action_table.c.action_id == creds_action_id)

        roles_with_creds_and_without_clouds = sa.select([role_table.c.id]).where(
            and_(
                role_table.c.id.notin_(roles_with_manage_clouds),
                role_table.c.id.in_(roles_with_manage_creds)
            )
        )

        new_role_actions = []
        for row in session.execute(roles_with_creds_and_without_clouds):
            _id = str(uuid.uuid4())
            new_role_actions.append({
                'id': _id,
                'role_id': row['id'],
                'action_id': clouds_action_id,
            })

        op.bulk_insert(role_action_table, new_role_actions)

        session.execute(
            sa.update(action_table).values(deleted_at=int(datetime.utcnow().timestamp())).where(
                action_table.c.name == MANAGE_CREDS))
        session.commit()
    finally:
        session.close()


def downgrade():
    # - update type for MANAGE_CLOUDS to 1(rool-level)
    # - remove MANAGE_CLOUDS action for every non-root role
    # - undelete MANAGE_VSPHERE_CREDENTIALS
    update_type(OLD_TYPE)

    bind = op.get_bind()
    session = Session(bind=bind)

    try:
        clouds_action_id = get_action_id_by_name(session, action_table, MANAGE_CLOUDS)

        non_root_roles = sa.select([role_table.c.id]).where(role_table.c.lvl_id > 1)
        session.execute(
            sa.delete(role_action_table).where(
                and_(
                    role_action_table.c.role_id.in_(non_root_roles),
                    role_action_table.c.action_id == clouds_action_id
                )
            )
        )

        session.execute(sa.update(action_table).values(
            deleted_at=0).where(action_table.c.name == MANAGE_CREDS))
        session.commit()
    finally:
        session.close()
