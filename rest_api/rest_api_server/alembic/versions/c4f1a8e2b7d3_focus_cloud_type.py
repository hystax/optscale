""""focus_cloud_type"

Revision ID: c4f1a8e2b7d3
Revises: 7b3e5d1f9a24
Create Date: 2026-10-07 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime, timezone

# revision identifiers, used by Alembic.
revision = 'c4f1a8e2b7d3'
down_revision = '7b3e5d1f9a24'
branch_labels = None
depends_on = None


old_cloud_types = sa.Enum('AWS_CNR', 'ALIBABA_CNR', 'AZURE_CNR', 'AZURE_TENANT',
                          'KUBERNETES_CNR', 'ENVIRONMENT', 'GCP_CNR',
                          'GCP_TENANT', 'NEBIUS', 'DATABRICKS')
new_cloud_types = sa.Enum('AWS_CNR', 'ALIBABA_CNR', 'AZURE_CNR', 'AZURE_TENANT',
                          'KUBERNETES_CNR', 'ENVIRONMENT', 'GCP_CNR',
                          'GCP_TENANT', 'NEBIUS', 'DATABRICKS', 'FOCUS')


def upgrade():
    op.alter_column('cloudaccount', 'type', existing_type=old_cloud_types,
                    type_=new_cloud_types, nullable=False)


def downgrade():
    ct = sa.sql.table('cloudaccount', sa.sql.column('type', new_cloud_types),
                      sa.sql.column('deleted_at', sa.Integer()))
    op.execute(
        ct.update().where(ct.c.type.in_(['FOCUS'])).values(
            type='ENVIRONMENT', deleted_at=int(datetime.now(
                tz=timezone.utc).timestamp())
        )
    )
    op.alter_column('cloudaccount', 'type', existing_type=new_cloud_types,
                    type_=old_cloud_types, nullable=False)
