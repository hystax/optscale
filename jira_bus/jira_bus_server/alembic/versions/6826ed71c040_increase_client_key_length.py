"""increase_client_key_length

Revision ID: 6826ed71c040
Revises: 97c682297e16
Create Date: 2021-12-03 09:49:56.124204

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "6826ed71c040"
down_revision = "97c682297e16"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "app_installation",
        "client_key",
        type_=sa.String(length=128),
        existing_type=sa.String(length=36),
        existing_nullable=False,
    )


def downgrade():
    op.alter_column(
        "app_installation",
        "client_key",
        type_=sa.String(length=36),
        existing_type=sa.String(length=128),
        existing_nullable=False,
    )
