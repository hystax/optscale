"""add openstack_huawei_cnr cloud type

Revision ID: edad38e1dd88
Revises: 4115e967f2f7
Create Date: 2018-11-09 16:22:06.644570

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'edad38e1dd88'
down_revision = '4115e967f2f7'
branch_labels = None
depends_on = None


fix_cloud_types = sa.Enum('OPENSTACK', 'OPENSTACK_CNR', 'FAKE', 'AWS_CNR')
new_cloud_types = sa.Enum('OPENSTACK', 'OPENSTACK_CNR', 'FAKE', 'AWS_CNR',
                          'OPENSTACK_HUAWEI_CNR')


def upgrade():
    op.alter_column('cloud', 'type',
                    existing_type=new_cloud_types, nullable=False)
    op.alter_column('cloudsite', 'cloud_type',
                    existing_type=new_cloud_types, nullable=False)


def downgrade():
    ct = sa.sql.table('cloud', sa.sql.column('type', new_cloud_types))
    op.execute(ct.update().where(ct.c.type.in_(
        ['OPENSTACK_HUAWEI_CNR'])).values(type='FAKE'))
    op.alter_column('cloud', 'type',
                    existing_type=fix_cloud_types, nullable=False)

    ct = sa.sql.table('cloudsite', sa.sql.column('cloud_type', new_cloud_types))
    op.execute(ct.update().where(ct.c.cloud_type.in_(
        ['OPENSTACK_HUAWEI_CNR'])).values(cloud_type='FAKE'))
    op.alter_column('cloudsite', 'cloud_type',
                    existing_type=fix_cloud_types, nullable=False)
