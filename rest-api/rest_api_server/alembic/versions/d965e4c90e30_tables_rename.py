""""tables_rename"

Revision ID: d965e4c90e30
Revises: 86ba08cbef8d
Create Date: 2017-05-24 03:30:43.237144

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'd965e4c90e30'
down_revision = '86ba08cbef8d'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "ALTER TABLE devicestate RENAME device_state;")
    op.execute(
        "ALTER TABLE vspherecredential RENAME vsphere_credential;")


def downgrade():
    op.execute(
        "ALTER TABLE device_state RENAME devicestate;")
    op.execute(
        "ALTER TABLE vsphere_credential RENAME vspherecredential;")
