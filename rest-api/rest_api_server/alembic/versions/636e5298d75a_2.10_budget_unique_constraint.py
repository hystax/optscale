""""budget_unique_constraint"

Revision ID: 636e5298d75a
Revises: 498e3685ed8f
Create Date: 2020-10-09 11:19:19.721063

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from sqlalchemy.orm import Session

revision = '636e5298d75a'
down_revision = '498e3685ed8f'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)

    try:
        table_ = sa.table(
            'budget',
            sa.column('id', sa.String(36)),
            sa.column('name', sa.String(256)),
            sa.column('deleted_at', sa.Integer()),
            sa.column('parent_id', sa.String(36)),
            sa.column('created_at', sa.Integer()),
            sa.column('organization_id', sa.String(36)),
        )
        inner_stmt = sa.select(
            [table_.c.name, table_.c.deleted_at, table_.c.parent_id,
             table_.c.organization_id, sa.func.count('*').label('cnt')]
        ).group_by(
            table_.c.name, table_.c.deleted_at, table_.c.parent_id,
            table_.c.organization_id
        ).alias('inner_stmt')
        outer_stmt = sa.select(
            [inner_stmt.c.name, inner_stmt.c.deleted_at, inner_stmt.c.parent_id,
             inner_stmt.c.organization_id, inner_stmt.c.cnt]
        ).select_from(inner_stmt).where(inner_stmt.c.cnt > 1)
        for duplicates in session.execute(outer_stmt):
            stmt = sa.select([table_]).where(
                sa.and_(
                    table_.c.name == duplicates['name'],
                    table_.c.deleted_at == duplicates['deleted_at'],
                    table_.c.parent_id == duplicates['parent_id'],
                    table_.c.parent_id == duplicates['organization_id'],
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
    op.create_unique_constraint(
        'uc_name_del_at_parent_id_organization_id',
        'budget', ['name', 'deleted_at', 'parent_id', 'organization_id'])


def downgrade():
    op.drop_constraint('uc_name_del_at_parent_id_organization_id', 'budget',
                       type_='unique')
