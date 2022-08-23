"""kubernetes_cloud_type

Revision ID: ce384e9c23cc
Revises: cf9a93d988c3
Create Date: 2021-05-11 18:29:50.552663

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'ce384e9c23cc'
down_revision = 'cf9a93d988c3'
branch_labels = None
depends_on = None

old_cloud_types = sa.Enum('OPENSTACK', 'OPENSTACK_CNR', 'OPENSTACK_HUAWEI_CNR',
                          'AWS_CNR', 'ALIBABA_CNR', 'VMWARE_CNR', 'AZURE_CNR',
                          'FAKE')

new_cloud_types = sa.Enum('OPENSTACK', 'OPENSTACK_CNR', 'OPENSTACK_HUAWEI_CNR',
                          'AWS_CNR', 'ALIBABA_CNR', 'VMWARE_CNR', 'AZURE_CNR',
                          'FAKE', 'KUBERNETES_CNR')


def upgrade():
    op.alter_column('cloudaccount', 'type', existing_type=old_cloud_types,
                    type_=new_cloud_types, nullable=False)


def downgrade():
    ct = sa.sql.table('cloudaccount', sa.sql.column('type', new_cloud_types))
    op.execute(ct.update().where(ct.c.type.in_(
        ['KUBERNETES_CNR'])).values(type='FAKE'))
    op.alter_column('cloudaccount', 'type', existing_type=new_cloud_types,
                    type_=old_cloud_types, nullable=False)
