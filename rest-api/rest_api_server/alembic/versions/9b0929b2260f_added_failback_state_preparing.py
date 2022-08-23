""""added_failback_state_preparing"

Revision ID: 9b0929b2260f
Revises: ee333643755f
Create Date: 2018-12-24 12:43:27.382170

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9b0929b2260f'
down_revision = 'ee333643755f'
branch_labels = None
depends_on = None


old_fb_states = sa.Enum('INCOMPLETE', 'IDLE', 'READY', 'RUNNING',
                        'SYNCHRONIZED', 'ERROR', 'CANCEL', 'CANCELLED',
                        'CANCELLING')
new_fb_states = sa.Enum('INCOMPLETE', 'IDLE', 'READY', 'RUNNING',
                        'SYNCHRONIZED', 'ERROR', 'CANCEL', 'CANCELLED',
                        'CANCELLING', 'PREPARING')

ft = sa.sql.table('failback', sa.sql.column('state', new_fb_states))


def upgrade():
    op.alter_column('failback', 'state',
                    existing_type=new_fb_states, nullable=False)


def downgrade():
    op.execute(ft.update().where(ft.c.state.in_(
        ['PREPARING'])).values(state='IDLE'))
    op.alter_column('failback', 'state',
                    existing_type=old_fb_states, nullable=False)
