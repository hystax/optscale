""""update budget parent id for created cloud accounts"

Revision ID: 0c99b4c498d5
Revises: 747407eaa2db
Create Date: 2021-02-20 09:34:50.182764

"""
from alembic import op
import logging
import re
import sqlalchemy as sa
from sqlalchemy import select, and_, join
from sqlalchemy.exc import IntegrityError

# revision identifiers, used by Alembic.
from sqlalchemy.orm import Session

revision = '0c99b4c498d5'
down_revision = '747407eaa2db'
branch_labels = None
depends_on = None

LOG = logging.getLogger(__name__)

purposes = sa.Enum('BUDGET', 'BUSINESS_UNIT', 'TEAM', 'PROJECT', 'CICD', 'MLAI', 'ASSET_POOL')


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        budget_table = sa.table('budget',
                                sa.Column('id', sa.String(36)),
                                sa.Column('parent_id', sa.String(36)),
                                sa.Column('organization_id', sa.String(36)),
                                sa.Column('purpose', purposes),
                                sa.Column('name', sa.String(256)))
        organization_table = sa.table('organization',
                                      sa.Column('id', sa.String(36)),
                                      sa.Column('name', sa.String(256)),
                                      sa.Column('budget_id', sa.String(36)))

        budget_org_join_stmt = join(budget_table, organization_table,
                                    and_(budget_table.c.organization_id == organization_table.c.id,
                                         budget_table.c.parent_id.is_(None),
                                         budget_table.c.id != organization_table.c.budget_id))

        budget_org_stmt = select(
            [budget_table.c.id, budget_table.c.name, organization_table.c.budget_id]
        ).select_from(budget_org_join_stmt)
        budget_org_map = {entry['id']: (entry['name'], entry['budget_id'])
                          for entry in session.execute(budget_org_stmt)}
        for budget_id, budget_value in budget_org_map.items():
            budget_name, org_budget_id = budget_value
            update_budget(budget_id, budget_table, budget_name, org_budget_id, session)
    finally:
        session.close()


def update_budget(budget_id, budget_table, budget_name, org_budget_id, session):
    try:
        session.execute(sa.update(budget_table).values(
            parent_id=org_budget_id, name=budget_name, purpose='BUDGET').where(
            budget_table.c.id == budget_id))
        session.commit()
    except IntegrityError:
        new_budget_name = generate_budget_name(budget_name)
        LOG.warning('Budget with name %s already exists, will replace budget name on %s', budget_name, new_budget_name)
        update_budget(budget_id, budget_table, new_budget_name, org_budget_id, session)


def generate_budget_name(budget_name):
    budget_for_cloud_name_groups = re.findall(r'[a-zA-Z0-9]+', budget_name)
    if budget_for_cloud_name_groups[-1].isdigit():
        number = int(budget_for_cloud_name_groups[-1]) + 1
        budget_name_result = budget_name[0:len(budget_name) - len(budget_for_cloud_name_groups[-1])]
        return '%s%s' % (budget_name_result, number)
    else:
        return '%s %s' % (budget_name, '1')


def downgrade():
    pass
