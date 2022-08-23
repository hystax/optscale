""""deleting_process"

Revision ID: 34ea1c1bfe4c
Revises: 16fbe453abeb
Create Date: 2019-04-08 10:24:27.576177

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '34ea1c1bfe4c'
down_revision = '16fbe453abeb'
branch_labels = None
depends_on = None


current_types = sa.Enum('replicating', 'canceling', 'idle')
new_types = sa.Enum('replicating', 'canceling', 'idle', 'deleting')


def upgrade():
    op.alter_column('device_state', 'process', existing_type=current_types,
                    type_=new_types, existing_nullable=True)


def downgrade():
    ct = sa.sql.table('device_state', sa.sql.column('process', new_types))
    op.execute(ct.update().where(ct.c.process == 'deleting').values(
        process='idle'))

    op.alter_column('device_state', 'state', existing_type=new_types,
                    type_=current_types, existing_nullable=True)
