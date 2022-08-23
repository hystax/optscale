""""bucket_type_resource_cache"

Revision ID: e0cde169e379
Revises: de2e74456ef3
Create Date: 2020-08-20 11:57:47.582017

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from sqlalchemy.orm import Session

revision = 'e0cde169e379'
down_revision = '5c83c578b7f9'
branch_labels = None
depends_on = None


OLD_TYPES = sa.Enum('instance', 'volume', 'snapshot')
NEW_TYPES = sa.Enum('instance', 'volume', 'snapshot', 'bucket')


def upgrade():
    op.alter_column('resource_cache_request', 'resource_type',
                    type_=NEW_TYPES, existing_type=OLD_TYPES, nullable=False)


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    request_table = sa.table('resource_cache_request',
                             sa.Column('resource_type', NEW_TYPES),
                             sa.Column('id', sa.String(36)))
    cache_table = sa.table('resource_cache', sa.Column('cache_id'))
    try:
        session.execute(cache_table.delete().where(cache_table.c.cache_id.in_(
            session.query(request_table.c.id).filter(
                request_table.c.resource_type == 'bucket')
        )))
        session.execute(request_table.delete().where(
            request_table.c.resource_type == 'bucket'))
        session.commit()
    finally:
        session.close()

    op.alter_column('resource_cache_request', 'resource_type',
                    type_=OLD_TYPES, existing_type=NEW_TYPES, nullable=False)
