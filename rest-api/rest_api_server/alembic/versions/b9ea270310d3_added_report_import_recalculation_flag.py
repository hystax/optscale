""""added_report_import_recalculation_flag"

Revision ID: b9ea270310d3
Revises: ec38c7980b10
Create Date: 2021-06-01 18:12:17.914338

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b9ea270310d3'
down_revision = 'ec38c7980b10'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('reportimport', sa.Column('is_recalculation', sa.Boolean(),
                                            nullable=False, default=False))


def downgrade():
    op.drop_column('reportimport', 'is_recalculation')
