""""added_payload"

Revision ID: 8862cb9204a8
Revises: 8f454f913981
Create Date: 2017-10-10 16:25:19.688889

"""
from alembic import op
import sqlalchemy as sa
import rest_api_server

# revision identifiers, used by Alembic.
revision = '8862cb9204a8'
down_revision = '8f454f913981'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('payload',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('drive_id', sa.String(length=36), nullable=False),
    sa.Column('snapshot_id', sa.String(length=36), nullable=True),
    sa.Column('mountpoint', sa.TEXT(), nullable=False),
    sa.ForeignKeyConstraint(['drive_id'], ['drive.id'], ),
    sa.ForeignKeyConstraint(['snapshot_id'], ['snapshot.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('payload')
