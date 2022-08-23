""""added_failback_type"

Revision ID: f2f07bc2fd82
Revises: 2f76766ed489
Create Date: 2019-09-04 17:08:21.980917

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f2f07bc2fd82'
down_revision = '2f76766ed489'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('failback', sa.Column('project_id', sa.String(length=36),
                                        nullable=True))
    op.add_column('failback', sa.Column('type', sa.Enum(
        'OPENSTACK', 'HUAWEI', 'VMWARE', name='type'), nullable=False,
                                        server_default='VMWARE'))


def downgrade():
    op.drop_column('failback', 'type')
    op.drop_column('failback', 'project_id')
