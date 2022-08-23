""""extend_organization_constraint_types"

Revision ID: 33b9ef190421
Revises: 5f7b3f90552e
Create Date: 2022-03-15 13:29:46.057780

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '33b9ef190421'
down_revision = '5f7b3f90552e'
branch_labels = None
depends_on = None

old_constr_types = sa.Enum('EXPENSE_ANOMALY', 'RESOURCE_COUNT_ANOMALY')
new_constr_types = sa.Enum('EXPENSE_ANOMALY', 'RESOURCE_COUNT_ANOMALY',
                           'RESOURCE_QUOTA', 'RECURRING_BUDGET',
                           'EXPIRING_BUDGET')


def upgrade():
    op.alter_column('organization_constraint', 'type',
                    existing_type=new_constr_types, nullable=False)


def downgrade():
    oct = sa.sql.table('organization_constraint',
                       sa.sql.column('type', new_constr_types))
    op.execute(oct.delete().where(oct.c.type.in_(
        ['RESOURCE_QUOTA', 'RECURRING_BUDGET', 'EXPIRING_BUDGET'])))
    op.alter_column('organization_constraint', 'type',
                    existing_type=old_constr_types, nullable=False)
