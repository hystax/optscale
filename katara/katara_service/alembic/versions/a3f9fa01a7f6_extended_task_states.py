""""extended_task_states"

Revision ID: a3f9fa01a7f6
Revises: 003afab1a585
Create Date: 2020-06-21 14:48:44.180604

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a3f9fa01a7f6"
down_revision = "003afab1a585"
branch_labels = None
depends_on = None


new_states = sa.Enum(
    "created",
    "started",
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


def upgrade():
    op.alter_column("task", "state", existing_type=new_states, nullable=False)


def downgrade():
    pass
