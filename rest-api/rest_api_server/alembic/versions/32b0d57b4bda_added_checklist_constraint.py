""""added_checklist_constraint"

Revision ID: 32b0d57b4bda
Revises: 33b0cba5925a
Create Date: 2022-02-25 16:42:07.754751

"""
from collections import defaultdict
from datetime import datetime

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session


# revision identifiers, used by Alembic.
revision = '32b0d57b4bda'
down_revision = '33b0cba5925a'
branch_labels = None
depends_on = None


def upgrade():
    checklist_table = sa.table(
        'checklist',
        sa.Column('id', sa.String()),
        sa.Column('organization_id', sa.String()),
        sa.Column('deleted_at', sa.Integer()))

    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        inner_stmt = sa.select(
            [checklist_table.c.organization_id]
        ).where(
            checklist_table.c.deleted_at == 0
        ).group_by(
            checklist_table.c.organization_id
        ).having(
            sa.func.count(checklist_table.c.organization_id) > 1
        ).alias('inner')
        outer_stmt = sa.select(
            [checklist_table.c.id, checklist_table.c.organization_id]
        ).where(
            sa.and_(
                checklist_table.c.organization_id.in_(inner_stmt),
                checklist_table.c.deleted_at == 0
            )
        )

        delete_candidates_map = defaultdict(list)
        organization_checklist_map = {}
        for checklist in session.execute(outer_stmt):
            if not organization_checklist_map.get(checklist['organization_id']):
                organization_checklist_map[checklist['organization_id']] = checklist['id']
            else:
                delete_candidates_map[checklist['organization_id']].append(checklist['id'])

        now = int(datetime.utcnow().timestamp())
        # one by one to get rid of > 2 records per organization
        for checklist_ids in delete_candidates_map.values():
            for i, id_ in enumerate(checklist_ids):
                upd_stmt = sa.update(checklist_table).values(
                    deleted_at=now - i
                ).where(
                    checklist_table.c.id == id_
                )
                session.execute(upd_stmt)
        session.commit()
    finally:
        session.close()
    op.create_unique_constraint('uc_del_at_org_id', 'checklist', ['deleted_at', 'organization_id'])


def downgrade():
    op.drop_constraint('uc_del_at_org_id', 'checklist', type_='unique')
