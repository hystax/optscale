""""added_organization_expenses_module"

Revision ID: caecb94fc78a
Revises: 0f2b068b24b3
Create Date: 2020-07-03 02:26:41.169615

"""
import datetime
import uuid

from alembic import op
from sqlalchemy.orm import Session
from sqlalchemy.sql import table, column
from sqlalchemy import Integer, insert, String, TEXT, Enum


# revision identifiers, used by Alembic.
revision = "caecb94fc78a"
down_revision = "0f2b068b24b3"
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
report_module = "organization_expenses"


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)

    try:
        ins_stmt = insert(report_table).values(
            id=str(uuid.uuid4()),
            created_at=int(datetime.datetime.utcnow().timestamp()),
            name=report_module,
            module_name=report_module,
            report_format="html",
            template=report_module,
            description="Organization expenses report",
        )
        session.execute(ins_stmt)
        session.commit()
    finally:
        session.close()


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)

    try:
        session.execute(
            report_table.delete().where(report_table.c.module_name == report_module)
        )
        session.commit()
    finally:
        session.close()
