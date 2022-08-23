"""Add disabling_agent drive status

Revision ID: 772dec00afbd
Revises: 82532f479b05
Create Date: 2018-12-29 12:21:46.548119

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '772dec00afbd'
down_revision = 'ccfdd9c32f10'
branch_labels = None
depends_on = None


old_states = sa.Enum('PENDING', 'PREPARATION', 'PARTITIONING',
                     'P2V', 'READY', 'DELETING', 'ERROR')
new_states = sa.Enum('PENDING', 'PREPARATION', 'PARTITIONING',
                     'DISABLING_AGENT', 'P2V', 'READY', 'DELETING', 'ERROR')

ft = sa.sql.table('drive', sa.sql.column('state', new_states))


def upgrade():
    op.alter_column('drive', 'state',
                    existing_type=new_states, nullable=True)


def downgrade():
    op.execute(ft.update().where(ft.c.state.in_(
        ['DISABLING_AGENT'])).values(state='P2V'))
    op.alter_column('drive', 'state',
                    existing_type=old_states, nullable=True)
