""""added_meta_discover_cache_request"

Revision ID: 339120401327
Revises: 350e9a4a2489
Create Date: 2020-05-27 00:23:11.348683

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '339120401327'
down_revision = '350e9a4a2489'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('resource_cache_request', sa.Column(
        'meta', sa.TEXT(), nullable=False))

    ct = sa.sql.table('resource_cache_request', sa.sql.column(
        'meta', sa.TEXT()))
    op.execute(ct.update().values(meta='{}'))


def downgrade():
    op.drop_column('resource_cache_request', 'meta')
