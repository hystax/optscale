""""environment_cloud_type"

Revision ID: b8b16ddb0aab
Revises: 70dd340e1d95
Create Date: 2021-08-10 11:57:40.450327

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b8b16ddb0aab'
down_revision = '70dd340e1d95'
branch_labels = None
depends_on = None


old_cloud_types = sa.Enum('OPENSTACK', 'OPENSTACK_CNR', 'OPENSTACK_HUAWEI_CNR',
                          'AWS_CNR', 'ALIBABA_CNR', 'VMWARE_CNR', 'AZURE_CNR',
                          'FAKE', 'KUBERNETES_CNR')

new_cloud_types = sa.Enum('OPENSTACK', 'OPENSTACK_CNR', 'OPENSTACK_HUAWEI_CNR',
                          'AWS_CNR', 'ALIBABA_CNR', 'VMWARE_CNR', 'AZURE_CNR',
                          'FAKE', 'KUBERNETES_CNR', 'ENVIRONMENT')


def upgrade():
    op.alter_column('cloudaccount', 'type', existing_type=old_cloud_types,
                    type_=new_cloud_types, nullable=False)


def downgrade():
    ct = sa.sql.table('cloudaccount', sa.sql.column('type', new_cloud_types))
    op.execute(ct.update().where(ct.c.type.in_(
        ['ENVIRONMENT'])).values(type='FAKE'))
    op.alter_column('cloudaccount', 'type', existing_type=new_cloud_types,
                    type_=old_cloud_types, nullable=False)
