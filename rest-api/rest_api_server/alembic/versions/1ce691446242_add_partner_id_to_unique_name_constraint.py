"""Add partner_id to unique name constraint

Revision ID: 1ce691446242
Revises: 436019c61530
Create Date: 2020-03-23 17:01:52.363706

"""
import uuid

from alembic import op
from sqlalchemy.orm import Session
from sqlalchemy.sql import table, column
from sqlalchemy import select, String, update, Text, func, Integer, and_


# revision identifiers, used by Alembic.
revision = '1ce691446242'
down_revision = '436019c61530'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('uc_name_del_at', 'partner', type_='unique')
    op.create_unique_constraint('uc_name_del_at_parent_id', 'partner',
                                ['name', 'deleted_at', 'parent_id'])


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)

    try:
        for table_name in ['partner']:
            table_ = table(table_name,
                           column('id', String(36)),
                           column('name', Text),
                           column('deleted_at', Integer))
            inner_stmt = select(
                [table_.c.name, table_.c.deleted_at,
                 func.count('*').label('cnt')]
            ).group_by(table_.c.name, table_.c.deleted_at).alias('inner_stmt')
            outer_stmt = select(
                [inner_stmt.c.name, inner_stmt.c.deleted_at, inner_stmt.c.cnt]
            ).select_from(inner_stmt).where(inner_stmt.c.cnt > 1)
            for duplicates in session.execute(outer_stmt):
                stmt = select([table_]).where(
                    and_(table_.c.name == duplicates['name'],
                         table_.c.deleted_at == duplicates['deleted_at']))
                for duplicate in session.execute(stmt):
                    new_name = '%s_%s' % (
                        duplicate['name'],
                        str(uuid.uuid4())[:5])
                    upd_stmt = update(table_).values(
                        name=new_name
                    ).where(table_.c.id == duplicate['id'])
                    session.execute(upd_stmt)

        session.commit()
    finally:
        session.close()

    op.drop_constraint('uc_name_del_at_parent_id', 'partner', type_='unique')
    op.create_unique_constraint('uc_name_del_at', 'partner',
                                ['name', 'deleted_at'])
