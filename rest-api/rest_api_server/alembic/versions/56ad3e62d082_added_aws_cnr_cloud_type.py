""""added_aws_cnr_cloud_type"

Revision ID: 56ad3e62d082
Revises: ee8874cb72d8
Create Date: 2018-06-18 17:29:59.172314

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '56ad3e62d082'
down_revision = 'ee8874cb72d8'
branch_labels = None
depends_on = None


fix_cloud_types = sa.Enum('OPENSTACK', 'OPENSTACK_CNR', 'FAKE')
new_cloud_types = sa.Enum('OPENSTACK', 'OPENSTACK_CNR', 'FAKE', 'AWS_CNR')


def upgrade():
    op.alter_column('cloud', 'type',
                    existing_type=new_cloud_types, nullable=False)


def downgrade():
    ct = sa.sql.table('cloud', sa.sql.column('type', new_cloud_types))
    op.execute(ct.update().where(ct.c.type.in_(
        ['AWS_CNR'])).values(type='FAKE'))
    op.alter_column('cloud', 'type',
                    existing_type=fix_cloud_types, nullable=False)
