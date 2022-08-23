""""add_new_daily_contraint"

Revision ID: c1a37bc921c9
Revises: d198c302b116
Create Date: 2021-11-16 17:09:27.382170

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session


# revision identifiers, used by Alembic.
revision = 'c1a37bc921c9'
down_revision = 'd198c302b116'
branch_labels = None
depends_on = None


old_limit_hits = sa.Enum('TTL', 'EXPENSE_LIMIT')
temp_limit_hits = sa.Enum('TTL', 'EXPENSE_LIMIT', 'TOTAL_EXPENSE_LIMIT',
                          'DAILY_EXPENSE_LIMIT')
new_limit_hits = sa.Enum('TTL', 'TOTAL_EXPENSE_LIMIT',
                         'DAILY_EXPENSE_LIMIT')
updated_table_names = ['resource_constraint', 'pool_policy',
                       'constraint_limit_hit']


def _updated_constraint_types(session, table_name, source_type, target_type,
                              delete_type=None):
    table = sa.table(table_name, sa.Column('id', sa.String(36)),
                     sa.Column('type', temp_limit_hits))
    session.execute(sa.update(table).values(type=target_type).where(
        table.c.type == source_type))
    if delete_type:
        session.execute(sa.delete(table).where(table.c.type == delete_type))


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        for table_name in updated_table_names:
            op.alter_column(table_name, 'type', existing_type=old_limit_hits,
                            type_=temp_limit_hits, existing_nullable=False)
            _updated_constraint_types(session, table_name, 'EXPENSE_LIMIT',
                                      'TOTAL_EXPENSE_LIMIT')
            op.alter_column(table_name, 'type', existing_type=temp_limit_hits,
                            type_=new_limit_hits, existing_nullable=False)
        session.commit()
    finally:
        session.close()


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        for table_name in updated_table_names:
            op.alter_column(table_name, 'type', existing_type=new_limit_hits,
                            type_=temp_limit_hits, existing_nullable=False)
            _updated_constraint_types(session, table_name,
                                      'TOTAL_EXPENSE_LIMIT',
                                      'EXPENSE_LIMIT', 'DAILY_EXPENSE_LIMIT')
            op.alter_column(table_name, 'type', existing_type=temp_limit_hits,
                            type_=old_limit_hits, existing_nullable=False)
        session.commit()
    finally:
        session.close()
