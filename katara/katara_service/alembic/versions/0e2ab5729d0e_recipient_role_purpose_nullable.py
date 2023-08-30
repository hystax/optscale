""""recipient_role_purpose_nullable"

Revision ID: 0e2ab5729d0e
Revises: b4443e4dd1ed
Create Date: 2020-07-07 07:40:10.208914

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0e2ab5729d0e"
down_revision = "b4443e4dd1ed"
branch_labels = None
depends_on = None

role_purposes = sa.Enum("optscale_member", "optscale_engineer", "optscale_manager")


def upgrade():
    op.alter_column(
        "recipient", "role_purpose", existing_type=role_purposes, nullable=True
    )


def downgrade():
    op.alter_column(
        "recipient", "role_purpose", existing_type=role_purposes, nullable=False
    )
