""""limit_hit_budget_id_nullable"

Revision ID: 47e873452902
Revises: fb929606710b
Create Date: 2020-08-20 10:45:42.233069

"""
import sqlalchemy as sa

from alembic import op
from sqlalchemy.orm import Session


# revision identifiers, used by Alembic.
revision = '47e873452902'
down_revision = 'fb929606710b'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('constraint_limit_hit', 'budget_id',
                    existing_type=sa.String(length=36),
                    nullable=True)


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    constraint_limit_hit_table = sa.table(
        'constraint_limit_hit',
        sa.Column('budget_id', sa.String(36)))
    try:
        session.execute(constraint_limit_hit_table.delete().where(
            constraint_limit_hit_table.c.budget_id.is_(None)))
        session.commit()
    finally:
        session.close()
    op.alter_column('constraint_limit_hit', 'budget_id',
                    existing_type=sa.String(length=36),
                    nullable=False)
