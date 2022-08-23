""""removed_failback_links"

Revision ID: 21c11090f310
Revises: 209d06f30664
Create Date: 2019-08-22 15:20:35.032792

"""
import datetime
from alembic import op
import sqlalchemy as sa

from sqlalchemy.sql import table, column
from sqlalchemy import Integer, String

# revision identifiers, used by Alembic.
revision = '21c11090f310'
down_revision = '209d06f30664'
branch_labels = None
depends_on = None

new_fb_states = sa.Enum('INCOMPLETE', 'IDLE', 'READY', 'RUNNING',
                        'SYNCHRONIZED', 'ERROR', 'CANCEL', 'CANCELLED',
                        'CANCELLING', 'PREPARING')
old_fb_states = sa.Enum('INCOMPLETE', 'IDLE', 'READY', 'RUNNING',
                        'SYNCHRONIZED', 'ERROR', 'CANCEL', 'CANCELLED',
                        'CANCELLING', 'PREPARING', 'DELETING')
failback_types = sa.Enum('FAILBACK', 'DOWNLOAD')


def upgrade():
    fb_table = table('failback',
                     column('failback_type', failback_types),
                     column('state', old_fb_states),
                     column('deleted_at', Integer))

    op.execute(fb_table.update().where(fb_table.c.failback_type.in_(
        ['DOWNLOAD'])).values(
        state='ERROR',
        deleted_at=int(datetime.datetime.utcnow().timestamp())))
    op.drop_column('failback', 'failback_type')
    op.alter_column('failback', 'state',
                    existing_type=new_fb_states, nullable=True)


def downgrade():
    op.add_column('failback', sa.Column('failback_type', sa.Enum(
        'FAILBACK', 'DOWNLOAD', name='failback_type'), nullable=False,
                                        server_default='FAILBACK'))
    op.alter_column('failback', 'state',
                    existing_type=old_fb_states, nullable=True)
