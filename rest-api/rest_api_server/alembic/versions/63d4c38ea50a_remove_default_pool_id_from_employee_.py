"""Remove default_pool_id from employee table

Revision ID: 63d4c38ea50a
Revises: 36e46b1db43d
Create Date: 2021-11-17 17:14:43.165436

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '63d4c38ea50a'
down_revision = '36e46b1db43d'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('def_pool_employee_fk', 'employee', type_='foreignkey')
    op.drop_column('employee', 'default_pool_id')


def downgrade():
    op.add_column('employee', sa.Column(
        'default_pool_id', sa.String(length=36), nullable=True))
    op.create_foreign_key(
        'def_pool_employee_fk', 'employee', 'pool', ['default_pool_id'], ['id'])
