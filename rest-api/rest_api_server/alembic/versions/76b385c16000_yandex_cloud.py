"""yandex_cloud

Revision ID: 76b385c16000
Revises: 2f76766ed489
Create Date: 2019-09-10 15:27:57.609429

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '76b385c16000'
down_revision = '71ffca133505'
branch_labels = None
depends_on = None


old_cloud_types = sa.Enum('OPENSTACK', 'OPENSTACK_CNR', 'FAKE', 'AWS_CNR',
                          'OPENSTACK_HUAWEI_CNR', 'ALIBABA_CNR', 'VMWARE_CNR',
                          'AZURE_CNR')
new_cloud_types = sa.Enum('OPENSTACK', 'OPENSTACK_CNR', 'FAKE', 'AWS_CNR',
                          'OPENSTACK_HUAWEI_CNR', 'ALIBABA_CNR', 'VMWARE_CNR',
                          'AZURE_CNR', 'YANDEX_CNR')


def upgrade():
    op.alter_column('cloud', 'type', existing_type=old_cloud_types,
                    type_=new_cloud_types, nullable=False)
    op.alter_column('cloudsite', 'cloud_type', existing_type=old_cloud_types,
                    type_=new_cloud_types, nullable=False)


def downgrade():
    ct = sa.sql.table('cloud', sa.sql.column('type', new_cloud_types))
    op.execute(ct.update().where(ct.c.type.in_(
        ['YANDEX_CNR'])).values(type='FAKE'))
    op.alter_column('cloud', 'type', existing_type=new_cloud_types,
                    type_=old_cloud_types, nullable=False)

    ct = sa.sql.table('cloudsite', sa.sql.column('cloud_type', new_cloud_types))
    op.execute(ct.update().where(ct.c.cloud_type.in_(
        ['YANDEX_CNR'])).values(cloud_type='FAKE'))
    op.alter_column('cloudsite', 'cloud_type', existing_type=new_cloud_types,
                    type_=old_cloud_types, nullable=False)
