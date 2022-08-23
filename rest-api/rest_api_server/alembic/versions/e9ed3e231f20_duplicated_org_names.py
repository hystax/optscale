""""duplicated_org_names"

Revision ID: e9ed3e231f20
Revises: 01a187c9482f
Create Date: 2020-10-01 11:00:32.901290

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from sqlalchemy.orm import Session

revision = 'e9ed3e231f20'
down_revision = '145b4c9cc308'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_index('uc_name_del_at_parent_id', table_name='partner')


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)

    try:
        table_ = sa.table(
            'partner',
            sa.column('id', sa.String(36)),
            sa.column('name', sa.String(256)),
            sa.column('deleted_at', sa.Integer()),
            sa.column('parent_id', sa.String(36)),
            sa.column('created_at', sa.Integer())
        )
        inner_stmt = sa.select(
            [table_.c.name, table_.c.deleted_at, table_.c.parent_id,
             sa.func.count('*').label('cnt')]
        ).group_by(
            table_.c.name, table_.c.deleted_at, table_.c.parent_id
        ).alias('inner_stmt')
        outer_stmt = sa.select(
            [inner_stmt.c.name, inner_stmt.c.deleted_at,
             inner_stmt.c.parent_id, inner_stmt.c.cnt]
        ).select_from(inner_stmt).where(inner_stmt.c.cnt > 1)
        for duplicates in session.execute(outer_stmt):
            stmt = sa.select([table_]).where(
                sa.and_(
                    table_.c.name == duplicates['name'],
                    table_.c.deleted_at == duplicates['deleted_at'],
                    table_.c.parent_id == duplicates['parent_id'],
                )).order_by(table_.c.created_at)
            for i, duplicate in enumerate(session.execute(stmt)):
                new_name = '%s_%s' % (duplicate['name'], i)
                upd_stmt = sa.update(table_).values(
                    name=new_name
                ).where(table_.c.id == duplicate['id'])
                session.execute(upd_stmt)

        session.commit()
    finally:
        session.close()
    op.create_index('uc_name_del_at_parent_id', 'partner',
                    ['name', 'deleted_at', 'parent_id'], unique=True)
