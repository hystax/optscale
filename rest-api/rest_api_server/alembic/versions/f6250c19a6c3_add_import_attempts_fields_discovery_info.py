"""last_attempt_for_discovery_info

Revision ID: f6250c19a6c3
Revises: 9fe68f16a0b3
Create Date: 2021-09-14 17:00:06.793313

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f6250c19a6c3'
down_revision = '9fe68f16a0b3'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('discovery_info',
                  sa.Column('last_attempt_at', sa.Integer(),
                            nullable=False, default=0))
    op.add_column('discovery_info',
                  sa.Column('last_attempt_error', sa.TEXT(),
                            nullable=True))


def downgrade():
    op.drop_column('discovery_info', 'last_attempt_at')
    op.drop_column('discovery_info', 'last_attempt_error')
