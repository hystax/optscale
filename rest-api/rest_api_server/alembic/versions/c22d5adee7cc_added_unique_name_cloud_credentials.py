""""added_unique_name_cloud_credentials"

Revision ID: c22d5adee7cc
Revises: c8f2cab6e4d0
Create Date: 2020-05-07 19:03:29.380311

"""
from alembic import op
import uuid
import sqlalchemy as sa
from sqlalchemy.orm import Session
from sqlalchemy.sql import table, column
from sqlalchemy import select, String, update, Text, func, Integer, and_


# revision identifiers, used by Alembic.
revision = 'c22d5adee7cc'
down_revision = 'c8f2cab6e4d0'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)

    try:
        table_ = table('cloudcredentials',
                       column('id', String(36)),
                       column('business_unit_id', String(36)),
                       column('name', Text),
                       column('deleted_at', Integer))
        inner_stmt = select(
            [table_.c.name, table_.c.deleted_at, table_.c.business_unit_id,
             func.count('*').label('cnt')]
        ).group_by(table_.c.name, table_.c.deleted_at,
                   table_.c.business_unit_id).alias('inner_stmt')
        outer_stmt = select(
            [inner_stmt.c.name, inner_stmt.c.deleted_at,
             inner_stmt.c.business_unit_id, inner_stmt.c.cnt]
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
    op.create_unique_constraint('uc_bu_name_del_at', 'cloudcredentials',
                                ['business_unit_id', 'name', 'deleted_at'])


def downgrade():
    op.drop_constraint('cloudcredentials_ibfk_1', 'cloudcredentials', type_='foreignkey')
    op.drop_constraint('uc_bu_name_del_at', 'cloudcredentials', type_='unique')
    op.create_foreign_key('cloudcredentials_ibfk_1', 'cloudcredentials', 'partner',
                          ['business_unit_id'], ['id'])

