""""blocked_state"

Revision ID: 16fbe453abeb
Revises: bcd2ac6d3474
Create Date: 2019-03-28 17:59:04.689790

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '16fbe453abeb'
down_revision = 'bcd2ac6d3474'
branch_labels = None
depends_on = None


current_types = sa.Enum('unprotected', 'scheduled', 'running', 'idle', 'cancel',
                        'error')
new_types = sa.Enum('unprotected', 'scheduled', 'running', 'idle', 'cancel',
                    'error', 'blocked')


def upgrade():
    op.alter_column('device_state', 'state', existing_type=current_types,
                    type_=new_types, existing_nullable=False)


def downgrade():
    ct = sa.sql.table('device_state', sa.sql.column('state', new_types))
    op.execute(ct.update().where(ct.c.state == 'blocked').values(state='idle'))

    op.alter_column('device_state', 'state', existing_type=new_types,
                    type_=current_types, existing_nullable=False)
