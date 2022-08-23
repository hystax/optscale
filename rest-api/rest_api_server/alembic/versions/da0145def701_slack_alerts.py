""""slack_alerts"

Revision ID: da0145def701
Revises: 055bbd3dec27
Create Date: 2021-03-22 10:43:22.969698

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
from sqlalchemy.orm import Session

revision = 'da0145def701'
down_revision = '055bbd3dec27'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('alert_contact',
                  sa.Column('slack_channel_id', sa.String(36), nullable=True))
    op.drop_constraint('PRIMARY', 'alert_contact', type_='primary')
    op.create_primary_key('alert_contact_pk', 'alert_contact', ['id'])
    op.alter_column('alert_contact', 'employee_id', existing_type=sa.String(36),
                    existing_nullable=False, nullable=True)
    op.add_column('budget_alert',
                  sa.Column('include_children', sa.Boolean(), nullable=False))

    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        contact_table = sa.table(
            'budget_alert', sa.column('include_children', sa.Boolean()))
        session.execute(sa.update(contact_table).values(include_children=False))
        session.commit()
    finally:
        session.close()


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        contact_table = sa.table(
            'alert_contact', sa.column('employee_id', sa.String(36)))
        session.execute(sa.delete(contact_table).where(
            contact_table.c.employee_id.is_(None)))
        session.commit()
    finally:
        session.close()

    op.drop_column('budget_alert', 'include_children')
    op.alter_column('alert_contact', 'employee_id', existing_type=sa.String(36),
                    existing_nullable=True, nullable=False)
    op.drop_constraint('alert_contact_pk', 'alert_contact', type_='primary')
    op.create_primary_key('alert_contact_pk', 'alert_contact',
                          ['id', 'budget_alert_id', 'employee_id'])
    op.drop_column('alert_contact', 'slack_channel_id')
