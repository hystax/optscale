""""deleted_rightsizing_rds_options"

Revision ID: 20c5be16bc87
Revises: 36440f4efae7
Create Date: 2021-07-15 16:28:06.474100

"""
import json
import sqlalchemy as sa

from alembic import op
from datetime import datetime
from operator import and_

# revision identifiers, used by Alembic.
revision = '20c5be16bc87'
down_revision = '36440f4efae7'
branch_labels = None
depends_on = None

option_table = sa.table('organization_option',
                        sa.Column('name', sa.String(256)),
                        sa.Column('deleted_at', sa.Integer()),
                        sa.Column('value', sa.Text()))
default_value = {
    "days_threshold": 3,
    "cpu_threshold_map": [
        [16, [[5, 8], [10, 4], [30, 2]]],
        [8, [[10, 4], [30, 2]]],
        [4, [[30, 2]]]
    ]
}


def upgrade():
    op.execute(option_table.update().where(and_(
        option_table.c.name == 'recommendation_rightsizing_rds',
        option_table.c.deleted_at == 0
    )).values(
        deleted_at=int(datetime.utcnow().timestamp())))


def downgrade():
    dumped_value = json.dumps(default_value)
    op.execute(option_table.update().where(and_(
        option_table.c.name == 'recommendation_rightsizing_rds',
        option_table.c.deleted_at == 0
    )).values(value=dumped_value))
