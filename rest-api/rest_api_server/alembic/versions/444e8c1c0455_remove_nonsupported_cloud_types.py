""""remove_nonsupported_cloud_types"

Revision ID: 444e8c1c0455
Revises: 8b09bc063963
Create Date: 2022-07-04 13:20:14.716975

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '444e8c1c0455'
down_revision = '8b09bc063963'
branch_labels = None
depends_on = None

old_cloud_types = sa.Enum('OPENSTACK', 'OPENSTACK_CNR', 'OPENSTACK_HUAWEI_CNR',
                          'AWS_CNR', 'ALIBABA_CNR', 'VMWARE_CNR', 'AZURE_CNR',
                          'FAKE', 'KUBERNETES_CNR', 'ENVIRONMENT')

new_cloud_types = sa.Enum('AWS_CNR', 'ALIBABA_CNR', 'AZURE_CNR', 'KUBERNETES_CNR', 'ENVIRONMENT')


def upgrade():
    op.alter_column('cloudaccount', 'type', existing_type=old_cloud_types,
                    type_=new_cloud_types, nullable=False)


def downgrade():
    op.alter_column('cloudaccount', 'type', existing_type=new_cloud_types,
                    type_=old_cloud_types, nullable=False)
