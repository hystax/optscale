""""added_failback_snapshot_meta"

Revision ID: f65dd9250246
Revises: 41553a37da03
Create Date: 2017-12-26 17:23:38.013000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f65dd9250246'
down_revision = '41553a37da03'
branch_labels = None
depends_on = None


fdst = sa.sql.table('failback_snapshot', sa.sql.column('meta', sa.TEXT()))


def upgrade():
    op.add_column('failback_snapshot', sa.Column('meta', sa.TEXT(),
                                                 nullable=True))
    op.execute(fdst.update().values(meta='{}'))


def downgrade():
    op.drop_column('failback_snapshot', 'meta')
