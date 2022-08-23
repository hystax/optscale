"""Azure support

Revision ID: e156d7295f1a
Revises: 34ea1c1bfe4c
Create Date: 2019-04-29 16:36:31.511993

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e156d7295f1a'
down_revision = 'ff5f881f5088'
branch_labels = None
depends_on = None


old_cloud_types = sa.Enum('OPENSTACK', 'OPENSTACK_CNR', 'FAKE', 'AWS_CNR',
                          'OPENSTACK_HUAWEI_CNR', 'ALIBABA_CNR', 'VMWARE_CNR')
new_cloud_types = sa.Enum('OPENSTACK', 'OPENSTACK_CNR', 'FAKE', 'AWS_CNR',
                          'OPENSTACK_HUAWEI_CNR', 'ALIBABA_CNR', 'VMWARE_CNR',
                          'AZURE_CNR')


def upgrade():
    op.alter_column('cloud', 'type',
                    existing_type=new_cloud_types, nullable=False)
    op.alter_column('cloudsite', 'cloud_type',
                    existing_type=new_cloud_types, nullable=False)


def downgrade():
    ct = sa.sql.table('cloud', sa.sql.column('type', new_cloud_types))
    op.execute(ct.update().where(ct.c.type.in_(
        ['AZURE_CNR'])).values(type='FAKE'))
    op.alter_column('cloud', 'type',
                    existing_type=old_cloud_types, nullable=False)

    ct = sa.sql.table('cloudsite', sa.sql.column('cloud_type', new_cloud_types))
    op.execute(ct.update().where(ct.c.cloud_type.in_(
        ['AZURE_CNR'])).values(cloud_type='FAKE'))
    op.alter_column('cloudsite', 'cloud_type',
                    existing_type=old_cloud_types, nullable=False)