"""Add Chiron to agent types

Revision ID: 6eeb9a2f5207
Revises: ea57c92cb215
Create Date: 2019-07-29 12:12:31.077657

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6eeb9a2f5207'
down_revision = 'ea57c92cb215'
branch_labels = None
depends_on = None


fix_agent_types = sa.Enum('BAGET', 'CABRIO', 'ELM', 'OSA', 'UNKNOWN')
new_agent_types = sa.Enum('BAGET', 'CABRIO', 'ELM', 'OSA', 'CHIRON', 'UNKNOWN')


def upgrade():
    op.alter_column('agent', 'type',
                    existing_type=new_agent_types, nullable=False)


def downgrade():
    ct = sa.sql.table('agent', sa.sql.column('type', new_agent_types))
    op.execute(ct.update().where(ct.c.type.in_(
        ['CHIRON'])).values(type='UNKNOWN'))
    op.alter_column('agent', 'type',
                    existing_type=fix_agent_types, nullable=False)