""""set_is_cnr_true_for_cnr_mountpoint"

Revision ID: 82532f479b05
Revises: 6e9445ee5340
Create Date: 2018-12-26 10:04:54.286975

"""
import json
from alembic import op
import sqlalchemy as sa
from sqlalchemy import and_
from sqlalchemy.orm import Session


# revision identifiers, used by Alembic.
revision = '82532f479b05'
down_revision = '6e9445ee5340'
branch_labels = None
depends_on = None

CNR_MOUNTPOINT = {"type": "cloud_agent",
                  "url": "%URL%",
                  "offset": "%OFFSET%",
                  "device": "%DEVICE%"}


def upgrade():
    update_mountpoint(True)


def downgrade():
    update_mountpoint(False)


def update_mountpoint(is_cnr):
    bind = op.get_bind()
    session = Session(bind=bind)
    mountpoint_table = sa.table('mountpoint',
                                sa.Column('id', sa.String(length=36)),
                                sa.Column('is_cnr', sa.Boolean()),
                                sa.Column('deleted_at', sa.Integer()),
                                sa.Column('mountpoint', sa.TEXT()))
    try:
        select_cmd = sa.select([mountpoint_table.c.mountpoint,
                                mountpoint_table.c.id]).where(
            and_(mountpoint_table.c.deleted_at == 0,
                 mountpoint_table.c.is_cnr.is_(not is_cnr)))

        for mountpoint_row in session.execute(select_cmd):
            try:
                mountpoint = json.loads(mountpoint_row['mountpoint'])
            except (ValueError, TypeError, json.decoder.JSONDecodeError):
                continue

            if mountpoint == CNR_MOUNTPOINT:
                upd_stmt = sa.update(mountpoint_table).values(
                    is_cnr=is_cnr).where(
                    mountpoint_table.c.id == mountpoint_row['id'])
                session.execute(upd_stmt)
                session.commit()
    finally:
        session.close()
