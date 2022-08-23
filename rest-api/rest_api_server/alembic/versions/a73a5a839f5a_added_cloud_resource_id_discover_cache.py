""""added_cloud_resource_id_discover_cache"

Revision ID: a73a5a839f5a
Revises: b6a5c7a77110
Create Date: 2020-05-12 17:21:21.011119

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a73a5a839f5a'
down_revision = 'b6a5c7a77110'
branch_labels = None
depends_on = None

old_name = 'resource_id'
new_name = 'cloud_resource_id'


def upgrade():
    op.alter_column('resource_cache', old_name, existing_type=sa.String(256),
                    nullable=True, new_column_name=new_name)
    op.add_column('resource_cache', sa.Column(
        'resource_id', sa.String(length=36), nullable=True))
    op.create_unique_constraint('uc_res_cred_del_at', 'resource',
                                ['cloud_resource_id', 'cloud_credentials_id',
                                 'deleted_at'])


def downgrade():
    op.drop_column('resource_cache', 'resource_id')
    op.alter_column('resource_cache', new_name, existing_type=sa.String(256),
                    nullable=True, new_column_name=old_name)
    op.drop_constraint('uc_res_cred_del_at', 'resource', type_='unique')
