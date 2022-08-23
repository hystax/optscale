""""employee_bu_relations"

Revision ID: 91cc0a587255
Revises: db8d5f85eff1
Create Date: 2020-04-13 11:15:52.113170

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from sqlalchemy.orm import Session

revision = '91cc0a587255'
down_revision = '45d37c59f778'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('employee', sa.Column('business_unit_id', sa.String(36),
                                        nullable=False))
    bind = op.get_bind()
    session = Session(bind=bind)
    employee_table = sa.table('employee', sa.Column('id', sa.String(36)))
    project_employee_table = sa.table('projectemployee',
                                      sa.Column('employee_id', sa.String(36)))
    budget_table = sa.table('budget', sa.Column('employee_id', sa.String(36)))
    try:
        session.execute(project_employee_table.delete())
        session.execute(budget_table.delete().where(
            budget_table.c.employee_id.isnot(None)))
        session.execute(employee_table.delete())
        session.commit()
    finally:
        session.close()

    op.create_unique_constraint(
        'uc_employee_bu_auth_user', 'employee',
        ['business_unit_id', 'auth_user_id', 'deleted_at'])
    op.create_foreign_key('employee_ibfk_partner', 'employee', 'partner',
                          ['business_unit_id'], ['id'])


def downgrade():
    op.drop_constraint('employee_ibfk_partner', 'employee', type_='foreignkey')
    op.drop_constraint('uc_employee_bu_auth_user', 'employee', type_='unique')
    op.drop_column('employee', 'business_unit_id')
