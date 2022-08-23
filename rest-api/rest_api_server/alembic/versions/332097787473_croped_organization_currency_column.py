"""Croped organization currency column

Revision ID: 332097787473
Revises: bd34895ac31a
Create Date: 2021-10-06 14:24:53.975459

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func

revision = '332097787473'
down_revision = 'e747db0836ee'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    org_table = sa.table('organization', sa.column('currency', sa.String(255)))
    try:
        session.execute(sa.update(org_table).values(
            currency=sa.func.left(org_table.c.currency, 3)).where(
            sa.func.length(org_table.c.currency) > 3))
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
    op.alter_column('organization', 'currency',
                    existing_type=sa.String(length=255),
                    type_=sa.String(length=3),
                    existing_nullable=False)


def downgrade():
    op.alter_column('organization', 'currency',
                    existing_type=sa.String(length=3),
                    type_=sa.String(length=255),
                    existing_nullable=False)
