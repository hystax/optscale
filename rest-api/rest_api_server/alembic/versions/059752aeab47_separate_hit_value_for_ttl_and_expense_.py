"""Separate hit_value for ttl and expense constraint limits

Revision ID: 059752aeab47
Revises: 0791536a84a8
Create Date: 2021-12-29 10:22:37.234632

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session


# revision identifiers, used by Alembic.
revision = '059752aeab47'
down_revision = '0791536a84a8'
branch_labels = None
depends_on = None
limit_hits_type = sa.Enum('TTL', 'TOTAL_EXPENSE_LIMIT', 'DAILY_EXPENSE_LIMIT')

def upgrade():
    op.add_column('constraint_limit_hit', sa.Column(
        'expense_value', sa.Float(), nullable=True))
    op.alter_column(
        'constraint_limit_hit', 'hit_value', existing_type=sa.Integer(),
        nullable=True, new_column_name='ttl_value')
    bind = op.get_bind()
    session = Session(bind=bind)
    clh_table = sa.table(
        'constraint_limit_hit',
        sa.Column('ttl_value', sa.Integer()),
        sa.Column('expense_value', sa.Float()),
        sa.Column('deleted_at', sa.Integer()),
        sa.Column('type', limit_hits_type))
    try:
        session.execute(sa.update(clh_table).where(
            sa.and_(clh_table.c.type != 'TTL', clh_table.c.deleted_at == 0)
        ).values(expense_value=clh_table.c.ttl_value))
        session.execute(sa.update(clh_table).where(
            sa.and_(clh_table.c.type != 'TTL', clh_table.c.deleted_at == 0)
        ).values(ttl_value=None))
        session.commit()
        op.create_check_constraint(
            'hit_value_xor',
            table_name='constraint_limit_hit',
            condition='(ttl_value IS NULL) <> (expense_value IS NULL)'
        )
    finally:
        session.close()


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    # requires updating the alembic presumably to 0.9.8
    # op.drop_constraint('hit_value_xor', 'constraint_limit_hit', type_='check')
    clh_table = sa.table(
        'constraint_limit_hit',
        sa.Column('ttl_value', sa.Integer()),
        sa.Column('deleted_at', sa.Integer()),
        sa.Column('expense_value', sa.Float()))
    try:
        session.execute(
            'ALTER TABLE constraint_limit_hit DROP CONSTRAINT hit_value_xor')
        session.execute(sa.update(clh_table).where(
            sa.and_(clh_table.c.ttl_value.is_(None), clh_table.c.deleted_at == 0)
        ).values(ttl_value=sa.cast(clh_table.c.expense_value, sa.Integer)))
        session.commit()
    finally:
        session.close()
    op.drop_column('constraint_limit_hit', 'expense_value')
    op.alter_column(
        'constraint_limit_hit', 'ttl_value', existing_type=sa.Integer(),
        nullable=False, new_column_name='hit_value')
