""""rule_unique_priority"

Revision ID: 593c49b7b72f
Revises: e114908c1ac1
Create Date: 2020-12-15 17:41:15.261476

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from sqlalchemy.orm import Session

revision = '593c49b7b72f'
down_revision = '2c083c6e08ac'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    org_table = sa.table('organization', sa.column('id', sa.String(36)))

    rule_table = sa.table(
        'rule',
        sa.column('organization_id', sa.String(36)),
        sa.column('id', sa.String(36)),
        sa.column('priority', sa.Integer()),
        sa.column('deleted_at', sa.Integer()),
    )

    try:
        for org in session.execute(sa.select([org_table])):
            org_id = org['id']
            org_rules_stmt = sa.select([rule_table]).where(sa.and_(
                rule_table.c.organization_id == org_id,
                rule_table.c.deleted_at == 0
            )).order_by(rule_table.c.priority)
            for i, rule in enumerate(session.execute(org_rules_stmt), start=1):
                session.execute(sa.update(rule_table).values(priority=i).where(
                    rule_table.c.id == rule['id']))
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

    op.create_unique_constraint('uc_priority_del_at_org_id', 'rule',
                                ['priority', 'deleted_at', 'organization_id'])


def downgrade():
    op.drop_constraint('uc_priority_del_at_org_id', 'rule', type_='unique')
