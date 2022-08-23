""""only_full_pair_rules"

Revision ID: a9eb1e7f82d9
Revises: 30ca937baee2
Create Date: 2021-01-26 12:09:48.182764

"""
import logging

from alembic import op
import sqlalchemy as sa
from sqlalchemy import or_

# revision identifiers, used by Alembic.
from sqlalchemy.orm import Session

revision = 'a9eb1e7f82d9'
down_revision = '30ca937baee2'
branch_labels = None
depends_on = None
LOG = logging.getLogger(__name__)


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        rules_table = sa.table('rule',
                               sa.Column('id', sa.String(36)),
                               sa.Column('organization_id', sa.String(36)),
                               sa.Column('budget_id', sa.String(36)),
                               sa.Column('owner_id', sa.String(36)),
                               sa.column('priority', sa.Integer()),
                               sa.column('deleted_at', sa.Integer()))
        budget_table = sa.table('budget',
                                sa.Column('id', sa.String(36)),
                                sa.Column('default_owner_id', sa.String(36)))
        employee_table = sa.table('employee',
                                  sa.Column('id', sa.String(36)),
                                  sa.Column('default_budget_id', sa.String(36)))
        condition_table = sa.table('condition',
                                   sa.column('rule_id', sa.String(36)))

        # find half-pair rules info
        stmt = sa.select([rules_table]).where(or_(
            rules_table.c.budget_id.is_(None),
            rules_table.c.owner_id.is_(None),
        ))
        rules = []
        budget_ids = set()
        owner_ids = set()
        for rule in session.execute(stmt):
            rules.append(rule)
            budget_id = rule['budget_id']
            owner_id = rule['owner_id']
            if budget_id is not None:
                budget_ids.add(budget_id)
            if owner_id is not None:
                owner_ids.add(owner_id)

        # fill maps with defaults
        stmt = sa.select([budget_table]).where(budget_table.c.id.in_(
            list(budget_ids)))
        budget_default_owner_map = {}
        for budget in session.execute(stmt):
            budget_default_owner_map[budget['id']] = budget['default_owner_id']

        stmt = sa.select([employee_table]).where(employee_table.c.id.in_(
            list(owner_ids)))
        owner_default_budget_map = {}
        for owner in session.execute(stmt):
            owner_default_budget_map[owner['id']] = owner['default_budget_id']

        orgs_with_deleted_rules = set()

        def delete_rule(rule_id, org_id):
            session.execute(sa.delete(condition_table).where(
                condition_table.c.rule_id == rule_id))
            session.execute(sa.delete(rules_table).where(
                rules_table.c.id == rule_id))
            orgs_with_deleted_rules.add(org_id)

        # update rules to make them full-pairs
        for rule in rules:
            budget_id = rule['budget_id']
            owner_id = rule['owner_id']
            if budget_id is None and owner_id is not None:
                budget_id = owner_default_budget_map.get(owner_id)
                if budget_id is None:
                    LOG.warning('Default budget not found for employee %s, '
                                'removing rule %s', owner_id, rule['id'])
                    delete_rule(rule['id'], rule['organization_id'])
            elif owner_id is None and budget_id is not None:
                owner_id = budget_default_owner_map.get(budget_id)
                if owner_id is None:
                    LOG.warning('Default owner not found for budget %s, '
                                'removing rule %s', budget_id, rule['id'])
                    delete_rule(rule['id'], rule['organization_id'])
            elif owner_id is None and budget_id is None:
                LOG.warning('Removing invalid rule %s without target budget '
                            'and owner', rule['id'])
                delete_rule(rule['id'], rule['organization_id'])
            else:
                continue

            session.execute(sa.update(rules_table).values(
                budget_id=budget_id, owner_id=owner_id).where(
                rules_table.c.id == rule['id']))

        # updating rules priority in orgs where rules were deleted
        for org_id in orgs_with_deleted_rules:
            org_rules_stmt = sa.select([rules_table]).where(sa.and_(
                rules_table.c.organization_id == org_id,
                rules_table.c.deleted_at == 0
            )).order_by(rules_table.c.priority)
            for i, rule in enumerate(session.execute(org_rules_stmt),
                                     start=1):
                session.execute(
                    sa.update(rules_table).values(priority=i).where(
                        rules_table.c.id == rule['id']))

        session.commit()
    finally:
        session.close()

    op.alter_column('rule', 'budget_id', existing_type=sa.String(36),
                    nullable=False)
    op.alter_column('rule', 'owner_id', existing_type=sa.String(36),
                    nullable=False)


def downgrade():
    op.alter_column('rule', 'owner_id', existing_type=sa.String(36),
                    nullable=True)
    op.alter_column('rule', 'budget_id', existing_type=sa.String(36),
                    nullable=True)
