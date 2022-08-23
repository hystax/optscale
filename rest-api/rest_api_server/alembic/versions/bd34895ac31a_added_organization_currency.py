"""Added organization currency

Revision ID: bd34895ac31a
Revises: e6584275de6e
Create Date: 2021-10-04 12:19:29.442551

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session


# revision identifiers, used by Alembic.
revision = 'bd34895ac31a'
down_revision = 'e6584275de6e'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('organization', sa.Column(
        'currency', sa.String(length=256), nullable=False))

    org_table = sa.table('organization',
                         sa.Column('currency', sa.String(256)),
                         sa.Column('id', sa.String(36)))
    bind = op.get_bind()
    session = Session(bind=bind)
    update_usd = sa.update(org_table).values(currency='USD')
    try:
        session.execute(update_usd)
        session.commit()
    finally:
        session.close()


def downgrade():
    op.drop_column('organization', 'currency')
