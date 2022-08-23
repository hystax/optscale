""""aws_recovery"

Revision ID: 74822032eb8f
Revises: 9c83d5c18b66
Create Date: 2018-08-09 11:09:18.915337

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '74822032eb8f'
down_revision = '9c83d5c18b66'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('drive', sa.Column('temp_snapshot_id', sa.String(length=36),
                                     nullable=True))
    op.add_column('failover', sa.Column('image_id', sa.String(length=36),
                                        nullable=True))


def downgrade():
    op.drop_column('failover', 'image_id')
    op.drop_column('drive', 'temp_snapshot_id')
