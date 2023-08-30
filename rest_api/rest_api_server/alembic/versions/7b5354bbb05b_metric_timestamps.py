""""metric_timestamps"

Revision ID: 7b5354bbb05b
Revises: b4f668663526
Create Date: 2022-10-04 21:13:03.424140

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7b5354bbb05b'
down_revision = 'b4f668663526'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('cloudaccount', sa.Column('last_getting_metrics_at', sa.Integer(),
                                            nullable=False, default=0))
    op.add_column('cloudaccount', sa.Column('last_getting_metric_attempt_at', sa.Integer(),
                                            nullable=False, default=0))
    op.add_column('cloudaccount', sa.Column('last_getting_metric_attempt_error', sa.TEXT(),
                                            nullable=True))


def downgrade():
    op.drop_column('cloudaccount', 'last_getting_metrics_at')
    op.drop_column('cloudaccount', 'last_getting_metric_attempt_at')
    op.drop_column('cloudaccount', 'last_getting_metric_attempt_error')
