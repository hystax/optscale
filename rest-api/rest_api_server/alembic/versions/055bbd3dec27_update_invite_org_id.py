""""update_invite_org_id"

Revision ID: 055bbd3dec27
Revises: beb817a745e9
Create Date: 2021-04-01 18:18:35.993117

"""
from alembic import op
import json
import sqlalchemy as sa
from sqlalchemy import select, update, Integer
from sqlalchemy.orm import Session
from sqlalchemy.sql import table, column

# revision identifiers, used by Alembic.
revision = '055bbd3dec27'
down_revision = 'beb817a745e9'
branch_labels = None
depends_on = None
DEFAULT_ETCD_HOST = 'etcd-client'
DEFAULT_ETCD_PORT = 80


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        invite_table = table(
            'invite',
            column('id', sa.String(36)),
            column('deleted_at', Integer()),
            column('meta', sa.TEXT())
        )
        invite_stmt = select([invite_table.c.id, invite_table.c.meta]).where(invite_table.c.deleted_at == 0)
        invites = session.execute(invite_stmt)
        invite_id_meta_map = {item['id']: json.loads(item['meta']) for item in invites}

        invite_assignment_table = table(
            'invite_assignment',
            column('invite_id', sa.String(36)),
            column('scope_id', sa.String(36)),
            column('deleted_at', Integer()),
            column('scope_type', sa.Enum('ORGANIZATION', 'BUDGET'))
        )
        invite_assignment_stmt = select([
            invite_assignment_table.c.invite_id,
            invite_assignment_table.c.scope_id,
            invite_assignment_table.c.scope_type
        ]).where(
            sa.and_(
                invite_assignment_table.c.invite_id.in_(list(invite_id_meta_map.keys())),
                invite_assignment_table.c.deleted_at == 0))
        invite_assignment_invite_id_scopes_map = {}
        for invite_id, scope_id, scope_type in session.execute(invite_assignment_stmt):
            if not invite_assignment_invite_id_scopes_map.get(invite_id):
                invite_assignment_invite_id_scopes_map[invite_id] = []
            invite_assignment_invite_id_scopes_map[invite_id].append((scope_id, scope_type))

        update_invite_meta_map = {}
        budget_invites_map = {}
        # now in invite_assignments we always have ORGANIZATION scope,
        # but in staging we have invite_assignments only with BUDGET scope types, so added this handler for such cases
        for invite_id, scopes in invite_assignment_invite_id_scopes_map.items():
            invite_meta = invite_id_meta_map.get(invite_id, {})
            has_organization = False
            budget_scope_id = None
            for (scope_id, scope_type) in scopes:
                if scope_type == 'ORGANIZATION':
                    has_organization = True
                    invite_meta.update({'organization_id': scope_id})
                    update_invite_meta_map[invite_id] = invite_meta
                    break
                else:
                    budget_scope_id = scope_id
            if has_organization is False:
                if not budget_invites_map.get(budget_scope_id):
                    budget_invites_map[budget_scope_id] = []
                budget_invites_map[budget_scope_id].append(invite_id)

        budget_table = table(
            'budget',
            column('id', sa.String(36)),
            column('organization_id', sa.String(36)),
        )
        budget_stmt = select([
            budget_table.c.id,
            budget_table.c.organization_id,
        ]).where(budget_table.c.id.in_(list(budget_invites_map.keys())))
        for budget_id, budget_org_id in session.execute(budget_stmt):
            invite_ids = budget_invites_map.get(budget_id)
            for invite_id in invite_ids:
                invite_meta = invite_id_meta_map.get(invite_id, {})
                invite_meta.update({'organization_id': budget_org_id})
                update_invite_meta_map[invite_id] = invite_meta

        for invite_id, invite_meta in update_invite_meta_map.items():
            invite_meta = json.dumps(invite_meta)
            update_stmt = update(
                invite_table
            ).values(
                meta=invite_meta,
            ).where(
                invite_table.c.id == invite_id
            )
            session.execute(update_stmt)
        session.commit()
    finally:
        session.close()


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        invite_table = table(
            'invite',
            column('id', sa.String(36)),
            column('deleted_at', Integer()),
            column('meta', sa.TEXT())
        )
        invite_stmt = select([invite_table.c.id, invite_table.c.meta]).where(invite_table.c.deleted_at == 0)
        invite_id_meta_map = {item['id']: json.loads(item['meta']) for item in session.execute(invite_stmt)}
        for invite_id, invite_meta in invite_id_meta_map.items():
            invite_meta.pop('organization_id')
            invite_meta = json.dumps(invite_meta)
            update_stmt = update(
                invite_table
            ).values(
                meta=invite_meta,
            ).where(
                invite_table.c.id == invite_id
            )
            session.execute(update_stmt)
        session.commit()
    finally:
        session.close()
