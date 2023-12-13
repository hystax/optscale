# pylint: disable=C0103
""""budget_exceed_for_managers_only"

Revision ID: 6556e12c599c
Revises: caecb94fc78a
Create Date: 2020-07-06 05:17:55.067820

"""
import uuid
from datetime import datetime

from alembic import op
from sqlalchemy.orm import Session
from sqlalchemy.sql import table, column
from sqlalchemy import Integer, delete, String, select, and_, update


# revision identifiers, used by Alembic.
revision = "6556e12c599c"
down_revision = "caecb94fc78a"
branch_labels = None
depends_on = None

OLD_CRONTAB = "0 */3 * * *"
NEW_CRONTAB = "0 0 * * *"
MODULE_NAME = "budget_exceed"

report_table = table(
    "report",
    column("id", String(length=36)),
    column("module_name", String(128)),
)

schedule_table = table(
    "schedule",
    column("id", String(length=36)),
    column("report_id", String(length=36)),
    column("recipient_id", String(length=36)),
    column("crontab", String(length=128)),
    column("last_run", Integer),
    column("next_run", Integer),
    column("created_at", Integer),
)

recipient_table = table(
    "recipient",
    column("id", String(length=36)),
    column("role_purpose", String(128)),
)


def get_current_timestamp():
    return int(datetime.utcnow().timestamp())


def gen_id():
    return str(uuid.uuid4())


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)

    try:
        recipients_stmt = select([recipient_table]).where(
            recipient_table.c.role_purpose == "optscale_engineer"
        )
        engineers = session.execute(recipients_stmt)
        engineers_ids = list(map(lambda x: x["id"], engineers))
        budget_exceed_stmt = select([report_table]).where(
            report_table.c.module_name == MODULE_NAME
        )
        for budget_exceed_report in session.execute(budget_exceed_stmt):
            update_schedule_stmt = (
                update(schedule_table)
                .values(crontab=NEW_CRONTAB)
                .where(schedule_table.c.report_id == budget_exceed_report[
                    "id"])
            )
            delete_schedule_stmt = delete(schedule_table).where(
                and_(
                    schedule_table.c.report_id == budget_exceed_report["id"],
                    schedule_table.c.recipient_id.in_(engineers_ids),
                )
            )
            session.execute(delete_schedule_stmt)
            session.execute(update_schedule_stmt)
            session.commit()
    finally:
        session.close()


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)

    try:
        recipients_stmt = select([recipient_table]).where(
            recipient_table.c.role_purpose == "optscale_engineer"
        )
        budget_exceed_stmt = select([report_table]).where(
            report_table.c.module_name == MODULE_NAME
        )

        schedules = []
        now = get_current_timestamp()
        for budget_exceed_report in session.execute(budget_exceed_stmt):
            for engineer in session.execute(recipients_stmt):
                schedules.append(
                    {
                        "id": gen_id(),
                        "report_id": budget_exceed_report["id"],
                        "recipient_id": engineer["id"],
                        "crontab": OLD_CRONTAB,
                        "last_run": 0,
                        "next_run": now,
                        "created_at": now,
                    }
                )
            update_schedule_stmt = (
                update(schedule_table)
                .values(crontab=OLD_CRONTAB)
                .where(schedule_table.c.report_id == budget_exceed_report[
                    "id"])
            )
            session.execute(update_schedule_stmt)
            op.bulk_insert(schedule_table, schedules)
        session.commit()
    finally:
        session.close()
