""""image_type_for_discovery_info"

Revision ID: 08e49b457ebb
Revises: 2e70ebe0bc86
Create Date: 2023-01-13 10:18:12.926016

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '08e49b457ebb'
down_revision = '2e70ebe0bc86'
branch_labels = None
depends_on = None


old_res_types = sa.Enum('instance', 'volume', 'snapshot', 'bucket', 'k8s_pod',
                        'snapshot_chain', 'rds_instance', 'ip_address')

new_res_types = sa.Enum('instance', 'volume', 'snapshot', 'bucket', 'k8s_pod',
                        'snapshot_chain', 'rds_instance', 'ip_address', 'image')


def upgrade():
    op.alter_column('discovery_info', 'resource_type',
                    existing_type=old_res_types,
                    type_=new_res_types, nullable=False)


def downgrade():
    di_t = sa.sql.table('discovery_info', sa.sql.column(
        'resource_type', new_res_types))
    op.execute(di_t.delete().where(di_t.c.resource_type == 'image'))
    op.alter_column('discovery_info', 'resource_type',
                    existing_type=new_res_types,
                    type_=old_res_types, nullable=False)
