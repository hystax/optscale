""""reschedule_organization_expenses"

Revision ID: fb5d8764b7aa
Revises: 0f20c5e50c7e
Create Date: 2020-08-12 02:22:13.539933

"""
from alembic import op
from sqlalchemy.orm import Session
from sqlalchemy.sql import table, column
from sqlalchemy import update, String


# revision identifiers, used by Alembic.
revision = 'fb5d8764b7aa'
down_revision = '0f20c5e50c7e'
branch_labels = None
depends_on = None

SCHEDULE_TABLE = table(
    'schedule',
    column('crontab', String(length=128))
)
OLD_CRONTAB = '0 0 * * MON'
NEW_CRONTAB = '0 13 * * FRI'


def update_crontab(curr_crontab, new_crontab):
    bind = op.get_bind()
    session = Session(bind=bind)

    try:
        update_schedule_stmt = update(SCHEDULE_TABLE).values(
            crontab=new_crontab
        ).where(
            SCHEDULE_TABLE.c.crontab == curr_crontab)
        session.execute(update_schedule_stmt)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def upgrade():
    update_crontab(OLD_CRONTAB, NEW_CRONTAB)


def downgrade():
    update_crontab(NEW_CRONTAB, OLD_CRONTAB)
