""""process_recommendations_ca_field"

Revision ID: a816cc32e6e3
Revises: bdd6233c7aab
Create Date: 2020-11-25 12:15:35.753333

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from sqlalchemy.orm import Session

revision = 'a816cc32e6e3'
down_revision = 'bdd6233c7aab'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('cloudaccount', sa.Column(
        'process_recommendations', sa.Boolean(), nullable=False, default=True))

    ca_table = sa.table('cloudaccount', sa.Column(
        'process_recommendations', sa.Boolean(), nullable=False))
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        session.execute(sa.update(ca_table).values(process_recommendations=True))
        session.commit()
    finally:
        session.close()


def downgrade():
    op.drop_column('cloudaccount', 'process_recommendations')
