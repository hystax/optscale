"""Add alibaba cloud type

Revision ID: cc783549e477
Revises: 1ad5337f912d
Create Date: 2018-10-09 12:14:24.014117

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cc783549e477'
down_revision = '1ad5337f912d'
branch_labels = None
depends_on = None


fix_cloud_types = sa.Enum('OPENSTACK', 'OPENSTACK_CNR', 'FAKE', 'AWS_CNR',
                          'OPENSTACK_HUAWEI_CNR')
new_cloud_types = sa.Enum('OPENSTACK', 'OPENSTACK_CNR', 'FAKE', 'AWS_CNR',
                          'OPENSTACK_HUAWEI_CNR', 'ALIBABA_CNR')


def upgrade():
    op.alter_column('cloud', 'type',
                    existing_type=new_cloud_types, nullable=False)


def downgrade():
    ct = sa.sql.table('cloud', sa.sql.column('type', new_cloud_types))
    op.execute(ct.update().where(ct.c.type.in_(
        ['ALIBABA_CNR'])).values(type='FAKE'))
    op.alter_column('cloud', 'type',
                    existing_type=fix_cloud_types, nullable=False)
