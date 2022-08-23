""""added_failbacksnap_origin_drive_id"

Revision ID: ee333643755f
Revises: 62b9a635c7ab
Create Date: 2018-12-20 14:13:09.692589

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session
from sqlalchemy.sql import table, column
from sqlalchemy import select, String, update, Boolean

# revision identifiers, used by Alembic.
revision = 'ee333643755f'
down_revision = '62b9a635c7ab'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    op.add_column(
        'failback_snapshot', sa.Column('origin_drive_id',
                                       sa.String(length=36), nullable=False))

    try:
        failback_snapshot_table = table('failback_snapshot',
                                        column('drive_id', String(36)),
                                        column('id', String(36)),
                                        column('origin_drive_id', String(36)))

        upd_stmt = update(failback_snapshot_table).values(
            origin_drive_id=failback_snapshot_table.c.drive_id)
        session.execute(upd_stmt)

        op.create_foreign_key('fb_snapshot_ibfk1', 'failback_snapshot',
                              'drive',
                              ['origin_drive_id'], ['id'])
    finally:
        session.close()


def downgrade():
    op.drop_constraint('fb_snapshot_ibfk1', 'failback_snapshot',
                       type_='foreignkey')
    op.drop_column('failback_snapshot', 'origin_drive_id')
