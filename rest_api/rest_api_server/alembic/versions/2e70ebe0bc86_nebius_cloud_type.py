""""nebius_cloud_type"

Revision ID: 2e70ebe0bc86
Revises: f5ef8bd1d668
Create Date: 2022-11-23 15:28:17.062870

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2e70ebe0bc86'
down_revision = 'f5ef8bd1d668'
branch_labels = None
depends_on = None


old_cloud_types = sa.Enum('AWS_CNR', 'ALIBABA_CNR', 'AZURE_CNR', 'AZURE_TENANT',
                          'KUBERNETES_CNR', 'ENVIRONMENT', 'GCP_CNR')

new_cloud_types = sa.Enum('AWS_CNR', 'ALIBABA_CNR', 'AZURE_CNR', 'AZURE_TENANT',
                          'KUBERNETES_CNR', 'ENVIRONMENT', 'GCP_CNR', 'NEBIUS')


def upgrade():
    op.alter_column('cloudaccount', 'type', existing_type=old_cloud_types,
                    type_=new_cloud_types, nullable=False)


def downgrade():
    ct = sa.sql.table('cloudaccount', sa.sql.column('type', new_cloud_types))
    op.execute(ct.delete().where(ct.c.type == 'NEBIUS'))
    op.alter_column('cloudaccount', 'type', existing_type=new_cloud_types,
                    type_=old_cloud_types, nullable=False)
