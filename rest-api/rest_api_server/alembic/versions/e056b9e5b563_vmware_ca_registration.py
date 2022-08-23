""""vmware_ca_registration"

Revision ID: e056b9e5b563
Revises: cc783549e477
Create Date: 2019-01-24 18:07:19.768278

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'e056b9e5b563'
down_revision = 'cc783549e477'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('cloud_agent', sa.Column('last_reported',
                                           sa.Integer(), nullable=False))
    op.add_column('cloud_agent', sa.Column('version', sa.String(length=32),
                                           nullable=True))
    op.add_column('cloud_agent', sa.Column(
        'vmware_host', sa.String(length=256), nullable=True))
    op.add_column('cloud_agent', sa.Column(
        'vsphere_credential_id', sa.String(length=36), nullable=True))
    op.create_foreign_key('cloud_agent_ibfk_vsphere_credential', 'cloud_agent',
                          'vsphere_credential',
                          ['vsphere_credential_id'], ['id'])


def downgrade():
    op.drop_constraint('cloud_agent_ibfk_vsphere_credential', 'cloud_agent',
                       type_='foreignkey')
    op.drop_column('cloud_agent', 'vsphere_credential_id')
    op.drop_column('cloud_agent', 'vmware_host')
    op.drop_column('cloud_agent', 'version')
    op.drop_column('cloud_agent', 'last_reported')
