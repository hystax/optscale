""""Add ownership to assignments history"

Revision ID: afba5e482333
Revises: 45d37c59f778
Create Date: 2020-04-15 15:27:13.052535

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'afba5e482333'
down_revision = '91cc0a587255'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "ALTER TABLE resourcebudgetassignmenthistory "
        "RENAME resource_assignment_history;")
    op.add_column('resource_assignment_history',
                  sa.Column('owner_id', sa.String(length=36), nullable=True))
    op.create_foreign_key('resource_assignment_history_ibfk_employee',
                          'resource_assignment_history', 'employee',
                          ['owner_id'], ['id'])


def downgrade():
    op.drop_constraint('resource_assignment_history_ibfk_employee',
                       'resource_assignment_history', type_='foreignkey')
    op.drop_column('resource_assignment_history', 'owner_id')
    op.execute(
        "ALTER TABLE resource_assignment_history "
        "RENAME resourcebudgetassignmenthistory;")

