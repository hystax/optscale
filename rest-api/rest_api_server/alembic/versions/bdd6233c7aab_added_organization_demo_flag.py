""""added_organization_demo_flag"

Revision ID: bdd6233c7aab
Revises: 577e258bd4fb
Create Date: 2020-10-30 03:34:24.869031

"""
from datetime import datetime

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session
from sqlalchemy.sql import table, column
from sqlalchemy import update, Boolean, Integer


# revision identifiers, used by Alembic.
revision = 'bdd6233c7aab'
down_revision = '153ba1bf5091'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('organization', sa.Column('is_demo', sa.Boolean(), nullable=False, default=False))


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        org_table = table(
            'organization',
            column('deleted_at', Integer()),
            column('is_demo', Boolean())
        )
        upd_customer_id = update(org_table).values(
            deleted_at=int(datetime.utcnow().timestamp())).where(
            org_table.c.is_demo.is_(True))
        session.execute(upd_customer_id)
        session.commit()
    finally:
        session.close()
    op.drop_column('organization', 'is_demo')
