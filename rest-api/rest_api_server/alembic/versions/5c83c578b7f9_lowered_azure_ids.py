""""lowered_azure_ids"

Revision ID: 5c83c578b7f9
Revises: 45a63e2baa4a
Create Date: 2020-08-27 10:48:02.709441

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from sqlalchemy.orm import Session

revision = '5c83c578b7f9'
down_revision = '45a63e2baa4a'
branch_labels = None
depends_on = None


def upgrade():
    resource_table = sa.table(
        'resource', sa.Column('cloud_resource_id', sa.String(512)))
    resource_cache_table = sa.table(
        'resource_cache', sa.Column('cloud_resource_id', sa.String(512)))
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        session.execute(sa.update(resource_table).values(
            cloud_resource_id=sa.func.lower(
                resource_table.c.cloud_resource_id)).where(
                resource_table.c.cloud_resource_id.ilike('%microsoft%')))
        session.execute(sa.update(resource_cache_table).values(
            cloud_resource_id=sa.func.lower(
                resource_cache_table.c.cloud_resource_id)).where(
            resource_cache_table.c.cloud_resource_id.ilike('%microsoft%')))
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def downgrade():
    pass
