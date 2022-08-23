"""change import period

Revision ID: 432ba5426923
Revises: d41c82067a5b
Create Date: 2020-06-25 11:11:04.099779

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '432ba5426923'
down_revision = 'd41c82067a5b'
branch_labels = None
depends_on = None

creds_table = sa.table('cloudcredentials', sa.Column(
    'import_period', sa.Integer()))


def upgrade():
    op.execute(creds_table.update().where(
        creds_table.c.import_period == 24).values(import_period=1))


def downgrade():
    op.execute(creds_table.update().where(
        creds_table.c.import_period == 1).values(import_period=24))
