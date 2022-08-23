""""added_failback_cancel_states"

Revision ID: 41553a37da03
Revises: 5404227f07c3
Create Date: 2017-12-21 10:55:01.089223

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '41553a37da03'
down_revision = '5404227f07c3'
branch_labels = None
depends_on = None


old_fb_device_syncstaes = sa.Enum('IDLE', 'SYNC', 'READY', 'ERROR')
new_fbdevice_syncstates = sa.Enum('IDLE', 'SYNC', 'READY', 'ERROR', 'CANCEL')
old_fb_states = sa.Enum('INCOMPLETE', 'IDLE', 'READY', 'RUNNING',
                        'SYNCHRONIZED', 'ERROR')
new_fb_states = sa.Enum('INCOMPLETE', 'IDLE', 'READY', 'RUNNING',
                        'SYNCHRONIZED', 'ERROR', 'CANCEL', 'CANCELLED',
                        'CANCELLING')


ft = sa.sql.table('failback', sa.sql.column('state', new_fb_states))
fdt = sa.sql.table('failback_device', sa.sql.column('sync_status',
                                                    new_fbdevice_syncstates))


def upgrade():
    op.alter_column('failback_device', 'sync_status',
                    existing_type=new_fbdevice_syncstates, nullable=False)
    op.alter_column('failback', 'state',
                    existing_type=new_fb_states, nullable=False)


def downgrade():
    op.execute(fdt.update().where(fdt.c.sync_status.in_(
        ['CANCEL'])).values(sync_status='IDLE'))
    op.alter_column('failback_device', 'sync_status',
                    existing_type=old_fb_device_syncstaes, nullable=False)
    op.execute(ft.update().where(ft.c.state.in_(
        ['CANCEL', 'CANCELLED', 'CANCELLING'])).values(state='INCOMPLETE'))
    op.alter_column('failback', 'state',
                    existing_type=old_fb_states, nullable=False)
