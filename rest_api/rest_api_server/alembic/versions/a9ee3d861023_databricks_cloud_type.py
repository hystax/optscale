""""databricks_cloud_type"

Revision ID: a9ee3d861023
Revises: 3273906c73ac
Create Date: 2022-11-23 15:28:17.062870

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = 'a9ee3d861023'
down_revision = '3273906c73ac'
branch_labels = None
depends_on = None


old_cloud_types = sa.Enum('AWS_CNR', 'ALIBABA_CNR', 'AZURE_CNR', 'AZURE_TENANT',
                          'KUBERNETES_CNR', 'ENVIRONMENT', 'GCP_CNR', 'NEBIUS')
new_cloud_types = sa.Enum('AWS_CNR', 'ALIBABA_CNR', 'AZURE_CNR', 'AZURE_TENANT',
                          'KUBERNETES_CNR', 'ENVIRONMENT', 'GCP_CNR', 'NEBIUS',
                          'DATABRICKS')

old_cost_models_types = sa.Enum('CLOUD_ACCOUNT', 'RESOURCE')
new_cost_models_types = sa.Enum('CLOUD_ACCOUNT', 'RESOURCE', 'SKU')


def upgrade():
    op.alter_column('cloudaccount', 'type', existing_type=old_cloud_types,
                    type_=new_cloud_types, nullable=False)
    op.alter_column('cost_model', 'type', existing_type=old_cost_models_types,
                    type_=new_cost_models_types, nullable=False)


def downgrade():
    ct = sa.sql.table('cloudaccount', sa.sql.column('type', new_cloud_types),
                      sa.sql.column('deleted_at', sa.Integer()))
    op.execute(
        ct.update().where(ct.c.type.in_(['DATABRICKS'])).values(
            type='ENVIRONMENT', deleted_at=int(datetime.utcnow().timestamp())
        )
    )
    op.alter_column('cloudaccount', 'type', existing_type=new_cloud_types,
                    type_=old_cloud_types, nullable=False)

    ct = sa.sql.table('cost_model', sa.sql.column('type', new_cost_models_types),
                      sa.sql.column('deleted_at', sa.Integer()))
    op.execute(
        ct.update().where(ct.c.type.in_(['SKU'])).values(
            type='CLOUD_ACCOUNT', deleted_at=int(datetime.utcnow().timestamp())
        )
    )
    op.alter_column('cost_model', 'type', existing_type=new_cost_models_types,
                    type_=old_cost_models_types, nullable=False)
