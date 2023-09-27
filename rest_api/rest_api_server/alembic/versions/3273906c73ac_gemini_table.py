"""gemini_table

Revision ID: 3273906c73ac
Revises: 457e1b52d5a0
Create Date: 2023-08-17 14:35:56.405439

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import MEDIUMTEXT

# revision identifiers, used by Alembic.
revision = "3273906c73ac"
down_revision = "457e1b52d5a0"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "organization_gemini",
        sa.Column("deleted_at", sa.Integer(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column("last_run", sa.Integer(), nullable=False),
        sa.Column("last_completed", sa.Integer(), nullable=False),
        sa.Column("last_error", sa.TEXT(), nullable=True),
        sa.Column("status", sa.Enum("CREATED", "QUEUED", "RUNNING", "FAILED", "SUCCESS"), nullable=False),
        sa.Column("filters", sa.TEXT(), nullable=True),
        sa.Column("stats", MEDIUMTEXT(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["organization_id"], ["organization.id"], )
    )


def downgrade():
    op.drop_table("organization_gemini")
