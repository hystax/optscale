""""deprecated_ca"

Revision ID: b2b5f61c00be
Revises: baa9439f17b2
Create Date: 2019-12-02 14:36:52.892389

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
from sqlalchemy.orm import Session

revision = 'b2b5f61c00be'
down_revision = 'baa9439f17b2'
branch_labels = None
depends_on = None


ca_table = sa.table("cloud_agent", sa.Column('version', sa.String(32)))


def upgrade():
    op.add_column('cloud_agent', sa.Column('deprecated', sa.Boolean(),
                                           nullable=False, default=False))

    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        session.execute(sa.update(ca_table).values(version='3.2'))
        session.commit()
    finally:
        session.close()


def downgrade():
    op.drop_column('cloud_agent', 'deprecated')

    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        session.execute(sa.update(ca_table).values(version=None))
        session.commit()
    finally:
        session.close()
