""""extended_tag_condition_types"

Revision ID: e114908c1ac1
Revises: d05097bd5cd2
Create Date: 2020-12-04 14:52:36.014326

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session


# revision identifiers, used by Alembic.
revision = 'e114908c1ac1'
down_revision = '0ba63efb08e1'
branch_labels = None
depends_on = None

old_condition_types = sa.Enum(
    'NAME_IS', 'NAME_STARTS_WITH', 'NAME_ENDS_WITH', 'NAME_CONTAINS',
    'RESOURCE_TYPE_IS', 'CLOUD_IS', 'TAG_IS', 'REGION_IS')
new_condition_types = sa.Enum(
    'NAME_IS', 'NAME_STARTS_WITH', 'NAME_ENDS_WITH', 'NAME_CONTAINS',
    'RESOURCE_TYPE_IS', 'CLOUD_IS', 'TAG_IS', 'REGION_IS', 'TAG_EXISTS',
    'TAG_VALUE_STARTS_WITH')


def upgrade():
    op.alter_column('condition', 'type', existing_type=new_condition_types,
                    nullable=False)


def downgrade():
    condition_table = sa.table(
        'condition',
        sa.column('rule_id', sa.String(36)),
        sa.column('type', new_condition_types),
    )
    rule_table = sa.table(
        'rule',
        sa.column('id', sa.String(36)),
    )
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        stmt = sa.select([condition_table]).where(condition_table.c.type.in_(
            ['TAG_EXISTS', 'TAG_VALUE_STARTS_WITH']))
        rule_ids = set()
        for cond in session.execute(stmt):
            rule_ids.add(cond['rule_id'])
        del_cond_stmt = sa.delete(condition_table).where(
            condition_table.c.rule_id.in_(rule_ids))
        del_rule_stmt = sa.delete(rule_table).where(
            rule_table.c.id.in_(rule_ids))
        session.execute(del_cond_stmt)
        session.execute(del_rule_stmt)
        session.commit()
    finally:
        session.close()

    op.alter_column('condition', 'type', existing_type=old_condition_types,
                    nullable=False)
