"""expand discovery_info resource_type enum with redshift_serverless, emr_application, etc.

Revision ID: c3d4e5f6a7b8
Revises: b1c2d3e4f5a6
Create Date: 2026-05-14
"""
from alembic import op

revision = 'c3d4e5f6a7b8'
down_revision = 'b1c2d3e4f5a6'
branch_labels = None
depends_on = None

_NEW_ENUM = (
    "'instance','volume','snapshot','bucket','k8s_pod','snapshot_chain',"
    "'rds_instance','redshift_cluster','redshift_serverless','emr_application',"
    "'savings_plan','reserved_instances','ip_address','image','load_balancer'"
)
_OLD_ENUM = (
    "'instance','volume','snapshot','bucket','k8s_pod','snapshot_chain',"
    "'rds_instance','ip_address','image','load_balancer'"
)


def upgrade():
    op.execute(
        f"ALTER TABLE discovery_info MODIFY COLUMN resource_type "
        f"ENUM({_NEW_ENUM}) NOT NULL"
    )


def downgrade():
    op.execute(
        f"ALTER TABLE discovery_info MODIFY COLUMN resource_type "
        f"ENUM({_OLD_ENUM}) NOT NULL"
    )
