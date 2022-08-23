""""openstack_cnr cloud type"

Revision ID: d789f6958a0e
Revises: cc36af074e8a
Create Date: 2018-05-11 12:08:37.957516

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'd789f6958a0e'
down_revision = 'cc36af074e8a'
branch_labels = None
depends_on = None


old_cloud_types = sa.Enum('OPENSTACK')
# added fake state for downgrade due to bug in migration
fix_cloud_types = sa.Enum('OPENSTACK', 'FAKE')
new_cloud_types = sa.Enum('OPENSTACK', 'OPENSTACK_CNR', 'FAKE')


def upgrade():
    op.alter_column('cloud', 'type',
                    existing_type=new_cloud_types, nullable=False)


def downgrade():
    ct = sa.sql.table('cloud', sa.sql.column('type', new_cloud_types))
    op.execute(ct.update().where(ct.c.type.in_(
        ['OPENSTACK_CNR'])).values(type='FAKE'))
    op.alter_column('cloud', 'type',
                    existing_type=fix_cloud_types, nullable=False)
