""""unique_role_purpose"

Revision ID: 2a75057a4cb3
Revises: 48dd5187b11e
Create Date: 2020-03-30 08:49:01.112399

"""

import datetime
from alembic import op
from sqlalchemy.orm import Session
from sqlalchemy.sql import table, column
from sqlalchemy import select, String, update, Text, func, Integer, and_


# revision identifiers, used by Alembic.
revision = '2a75057a4cb3'
down_revision = '48dd5187b11e'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)

    try:
        role_table = table('role',
                           column('id', String(36)),
                           column('purpose', String(36)),
                           column('deleted_at', Integer))
        inner_stmt = select(
            [role_table.c.purpose, role_table.c.deleted_at,
             func.count('*').label('cnt')]
        ).group_by(
            role_table.c.purpose, role_table.c.deleted_at).alias('inner_stmt')
        outer_stmt = select(
            [inner_stmt.c.purpose, inner_stmt.c.deleted_at, inner_stmt.c.cnt]
        ).select_from(inner_stmt).where(inner_stmt.c.cnt > 1)
        for duplicates in session.execute(outer_stmt):
            stmt = select([role_table]).where(
                and_(role_table.c.purpose == duplicates['purpose'],
                     role_table.c.deleted_at == duplicates['deleted_at']))
            now = datetime.datetime.utcnow().timestamp()
            for i, duplicate in enumerate(session.execute(stmt)):
                if i == 0:
                    continue
                upd_stmt = update(role_table).values(
                    deleted_at=now + i
                ).where(role_table.c.id == duplicate['id'])
                session.execute(upd_stmt)
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
    op.create_unique_constraint('uc_purpose_deleted_at', 'role',
                                ['purpose', 'deleted_at'])


def downgrade():
    op.drop_constraint('uc_purpose_deleted_at', 'role', type_='unique')
