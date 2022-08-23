""""tagging_policy_organization_constraint"

Revision ID: bd1ca74c5343
Revises: 33b9ef190421
Create Date: 2022-03-24 15:04:50.998164

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bd1ca74c5343'
down_revision = '33b9ef190421'
branch_labels = None
depends_on = None

old_constr_types = sa.Enum('EXPENSE_ANOMALY', 'RESOURCE_COUNT_ANOMALY',
                           'RESOURCE_QUOTA', 'RECURRING_BUDGET',
                           'EXPIRING_BUDGET')
new_constr_types = sa.Enum('EXPENSE_ANOMALY', 'RESOURCE_COUNT_ANOMALY',
                           'RESOURCE_QUOTA', 'RECURRING_BUDGET',
                           'EXPIRING_BUDGET', 'TAGGING_POLICY')


def upgrade():
    op.alter_column('organization_constraint', 'type',
                    existing_type=new_constr_types, nullable=False)


def downgrade():
    oct = sa.sql.table('organization_constraint',
                       sa.sql.column('type', new_constr_types))
    op.execute(oct.delete().where(oct.c.type == 'TAGGING_POLICY'))
    op.alter_column('organization_constraint', 'type',
                    existing_type=old_constr_types, nullable=False)
