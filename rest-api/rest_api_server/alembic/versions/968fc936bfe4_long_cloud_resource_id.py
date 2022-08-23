""""long_cloud_resource_id"

Revision ID: 968fc936bfe4
Revises: 325c35031a08
Create Date: 2020-07-22 12:26:19.845453

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from sqlalchemy import func

revision = '968fc936bfe4'
down_revision = '3172e7695623'
branch_labels = None
depends_on = None


OLD_TYPE = sa.String(length=256)
NEW_TYPE = sa.String(length=512)


def upgrade():
    op.alter_column('resource', 'cloud_resource_id',
                    existing_type=OLD_TYPE, type_=NEW_TYPE, nullable=False)
    op.alter_column('resource_cache', 'cloud_resource_id',
                    existing_type=OLD_TYPE, type_=NEW_TYPE, nullable=True)


def downgrade():
    r_a_h = sa.sql.table(
        'resource_assignment_history', sa.sql.column('resource_id'))
    resource = sa.sql.table(
        'resource', sa.sql.column('id'), sa.sql.column('cloud_resource_id'))
    resource_cache = sa.sql.table(
        'resource_cache', sa.sql.column('cloud_resource_id'))
    assign_request = sa.sql.table(
        'assignment_request', sa.sql.column('resource_id'))
    # clean history
    op.execute(r_a_h.delete().where(r_a_h.c.resource_id == resource.c.id).where(
        func.length(resource.c.cloud_resource_id) > 256))
    # clean assignment requests
    op.execute(assign_request.delete().where(
        assign_request.c.resource_id == resource.c.id).where(
        func.length(resource.c.cloud_resource_id) > 256))
    # clean resources
    op.execute(resource.delete().where(
        func.length(resource.c.cloud_resource_id) > 256))
    # clean resource cache
    op.execute(resource_cache.delete().where(
        func.length(resource_cache.c.cloud_resource_id) > 256))

    op.alter_column('resource', 'cloud_resource_id',
                    existing_type=NEW_TYPE, type_=OLD_TYPE, nullable=False)
    op.alter_column('resource_cache', 'cloud_resource_id',
                    existing_type=NEW_TYPE, type_=OLD_TYPE, nullable=True)
