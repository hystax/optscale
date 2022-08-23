""""add unique constraint for res_id assignment request table"

Revision ID: d41c82067a5b
Revises: 339120401327
Create Date: 2020-05-29 17:05:19.123150

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session


# revision identifiers, used by Alembic.
revision = 'd41c82067a5b'
down_revision = '1c36f18f71c7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    bind = op.get_bind()
    session = Session(bind=bind)
    table_ = sa.table('assignment_request',
                      sa.column('id', sa.String(36)),
                      sa.column('resource_id', sa.String(36)),
                      sa.column('created_at', sa.Integer),
                      sa.column('deleted_at', sa.Integer))
    inner_stmt = sa.select(
        [table_.c.resource_id, table_.c.created_at, table_.c.deleted_at,
         sa.func.count('*').label('cnt')]
    ).group_by(
        table_.c.resource_id, table_.c.deleted_at
    ).alias('inner_stmt')
    outer_stmt = sa.select(
        [inner_stmt.c.resource_id, inner_stmt.c.created_at,
         inner_stmt.c.deleted_at, inner_stmt.c.cnt]
    ).select_from(
        inner_stmt
    ).where(inner_stmt.c.cnt > 1)
    duplicate_ids = []
    for duplicates in session.execute(outer_stmt):
        stmt = sa.select(
            [table_.c.id, table_.c.created_at]
        ).where(
            sa.and_(
                table_.c.resource_id == duplicates['resource_id'],
                table_.c.deleted_at == duplicates['deleted_at'])
        ).order_by(table_.c.created_at)
        # all duplicates will be deleted except the lat one (created_at field)
        ids = [item['id'] for item in session.execute(stmt)][:-1]
        duplicate_ids.extend(ids)
    delete_stmt = sa.delete(table_).where(table_.c.id.in_(duplicate_ids))
    try:
        session.execute(delete_stmt)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
    op.create_unique_constraint(
        'uc_resource_id_deleted_at', 'assignment_request',
        ['resource_id', 'deleted_at'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('assignment_request_ibfk_1', 'assignment_request',
                       type_='foreignkey')
    op.drop_constraint('uc_resource_id_deleted_at', 'assignment_request',
                       type_='unique')
    op.create_foreign_key('assignment_request_ibfk_1', 'assignment_request',
                          'resource', ['resource_id'], ['id'])
    # ### end Alembic commands ###
