"""Add alibaba cloud type to cloudsite table

Revision ID: 1ad5337f912d
Revises: e8d5e21e2f8a
Create Date: 2018-10-15 17:19:26.062572

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1ad5337f912d'
down_revision = 'e8d5e21e2f8a'
branch_labels = None
depends_on = None


fix_cloud_types = sa.Enum('OPENSTACK', 'OPENSTACK_CNR', 'FAKE', 'AWS_CNR',
                          'OPENSTACK_HUAWEI_CNR')
new_cloud_types = sa.Enum('OPENSTACK', 'OPENSTACK_CNR', 'FAKE', 'AWS_CNR',
                          'OPENSTACK_HUAWEI_CNR', 'ALIBABA_CNR')


def upgrade():
    op.alter_column('cloudsite', 'cloud_type',
                    existing_type=new_cloud_types, nullable=False)


def downgrade():
    ct = sa.sql.table('cloudsite', sa.sql.column('cloud_type', new_cloud_types))
    op.execute(ct.update().where(ct.c.cloud_type.in_(
        ['ALIBABA_CNR'])).values(cloud_type='FAKE'))
    op.alter_column('cloudsite', 'cloud_type',
                    existing_type=fix_cloud_types, nullable=False)
