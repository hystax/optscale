""""gcp_cloud_type"

Revision ID: 32b34ca9b0d9
Revises: 9c892a70c395
Create Date: 2022-04-26 09:33:57.882212

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '32b34ca9b0d9'
down_revision = '9c892a70c395'
branch_labels = None
depends_on = None


old_cloud_types = sa.Enum('AWS_CNR', 'ALIBABA_CNR', 'AZURE_CNR', 'KUBERNETES_CNR', 'ENVIRONMENT')

new_cloud_types = sa.Enum('AWS_CNR', 'ALIBABA_CNR', 'AZURE_CNR', 'KUBERNETES_CNR', 'ENVIRONMENT', 'GCP_CNR')


def upgrade():
    op.alter_column('cloudaccount', 'type', existing_type=old_cloud_types,
                    type_=new_cloud_types, nullable=False)


def downgrade():
    ct = sa.sql.table('cloudaccount', sa.sql.column('type', new_cloud_types))
    op.execute(ct.update().where(ct.c.type.in_(
        ['GCP_CNR'])).values(type='FAKE'))
    op.alter_column('cloudaccount', 'type', existing_type=new_cloud_types,
                    type_=old_cloud_types, nullable=False)
