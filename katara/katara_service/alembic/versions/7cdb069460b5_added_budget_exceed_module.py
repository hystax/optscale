""""added_budget_exceed_module"

Revision ID: 7cdb069460b5
Revises: d777a3b2707c
Create Date: 2020-06-29 03:02:39.378545

"""
import datetime
import uuid

from alembic import op
from sqlalchemy.orm import Session
from sqlalchemy.sql import table, column
from sqlalchemy import Integer, insert, delete, String, TEXT, Enum


# revision identifiers, used by Alembic.
revision = "7cdb069460b5"
down_revision = "d777a3b2707c"
branch_labels = None
depends_on = None

report_table = table(
    "report",
    column("id", String(length=36)),
    column("created_at", Integer()),
    column("name", String(50)),
    column("module_name", String(128)),
    column("report_format", Enum("html")),
    column("template", String(128)),
    column("description", TEXT()),
)


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)

    try:
        ins_stmt = insert(report_table).values(
            id=str(uuid.uuid4()),
            created_at=int(datetime.datetime.utcnow().timestamp()),
            name="budget_exceed",
            module_name="budget_exceed",
            report_format="html",
            template="budget_exceed",
            description="Budget exceed report",
        )
        session.execute(ins_stmt)
        session.commit()
    finally:
        session.close()


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)

    try:
        ins_stmt = delete(report_table)
        session.execute(ins_stmt)
        session.commit()
    finally:
        session.close()
