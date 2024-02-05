# pylint: disable=C0103
""""remove_legacy_users"

Revision ID: 0321f4e3fe3f
Revises: cd08c646c952
Create Date: 2024-01-28 04:57:36.488047

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.orm import Session
from auth.auth_server.models.models import Action, Type, Role, RoleAction


# revision identifiers, used by Alembic.
revision = '0321f4e3fe3f'
down_revision = 'cd08c646c952'
branch_labels = None
depends_on = None

DRPLAN_OPERATOR = 'Drplan Operator'
ADMIN = 'Super Admin'


def upgrade():
    assignment_t = sa.table('assignment',
                            sa.column('role_id', sa.String()))
    role_t = sa.table('role',
                      sa.column('id', sa.String()),
                      sa.column('name', sa.String()))
    role_action_t = sa.table('role_action',
                             sa.column('role_id', sa.String()))
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        roles_q = sa.select([role_t.c.id]).where(
            role_t.c.name.in_([DRPLAN_OPERATOR, ADMIN]))
        roles_ids = [x[0] for x in session.execute(roles_q)]
        session.execute(assignment_t.delete().where(
            assignment_t.c.role_id.in_(roles_ids)))
        session.execute(role_action_t.delete().where(
            role_action_t.c.role_id.in_(roles_ids)))
        session.execute(role_t.delete().where(
            role_t.c.id.in_(roles_ids)))
        session.commit()
    finally:
        session.close()


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    actions = session.query(Action).all()
    type_root = session.query(Type).filter_by(name='root').one_or_none()
    type_organization = session.query(Type).filter_by(
        name='organization').one_or_none()
    type_pool = session.query(Type).filter_by(name='pool').one_or_none()
    role_drplan_operator = Role(name=DRPLAN_OPERATOR, type_=type_pool,
                                description='DR plan operator',
                                lvl_id=type_pool.id, is_active=True)
    role_admin = Role(name=ADMIN, type_=type_root,
                      description='Hystax Admin', lvl_id=type_root.id,
                      is_active=True)
    actions = session.query(Action).all()
    for action in actions:
        role_admin.assign_action(action)
    session.add(role_drplan_operator)
    session.add(role_admin)
    try:
        session.commit()
    finally:
        session.close()
