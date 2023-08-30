""""removed_obect_storage_states"

Revision ID: 0f20c5e50c7e
Revises: 0ba390f82532
Create Date: 2020-08-05 11:23:38.535840

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.orm import Session
from sqlalchemy.sql import table, column
from sqlalchemy import update, String


# revision identifiers, used by Alembic.
revision = "0f20c5e50c7e"
down_revision = "0ba390f82532"
branch_labels = None
depends_on = None

old_states = sa.Enum(
    "created",
    "started",
    "getting_scopes",
    "got_scopes",
    "getting_recipients",
    "got_recipients",
    "generating_data",
    "generated_data",
    "putting_to_object_storage",
    "put_to_object_storage",
    "putting_to_herald",
    "completed",
    "error",
)
new_states = sa.Enum(
    "created",
    "started",
    "getting_scopes",
    "got_scopes",
    "getting_recipients",
    "got_recipients",
    "generating_data",
    "generated_data",
    "putting_to_herald",
    "completed",
    "error",
)
task_table = table(
    "task",
    column("state", String(128)),
)


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        update_task_stmt = (
            update(task_table)
            .values(state="generating_data")
            .where(
                task_table.c.state.in_(["generated_data", "putting_to_object_storage"])
            )
        )
        update_task_stmt2 = (
            update(task_table)
            .values(state="generated_data")
            .where(task_table.c.state == "put_to_object_storage")
        )
        session.execute(update_task_stmt)
        session.execute(update_task_stmt2)
        session.commit()
    finally:
        session.close()

    op.alter_column("task", "state", existing_type=new_states, nullable=False)


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        update_task_stmt = (
            update(task_table)
            .values(state="put_to_object_storage")
            .where(task_table.c.state == "generated_data")
        )
        session.execute(update_task_stmt)
        session.commit()
    finally:
        session.close()

    op.alter_column("task", "state", existing_type=old_states, nullable=False)
