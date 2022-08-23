""""snapshot-cache-fields"

Revision ID: 5d5b4d5d032b
Revises: c8ec43fa40ac
Create Date: 2020-06-03 16:23:21.825662

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from sqlalchemy.orm import Session

revision = '5d5b4d5d032b'
down_revision = 'c8ec43fa40ac'
branch_labels = None
depends_on = None


OLD_TYPES = sa.Enum('instance', 'volume', 'vpc', 'sg')
NEW_TYPES = sa.Enum('instance', 'volume', 'vpc', 'sg', 'snapshot')


def upgrade():
    op.add_column('resource_cache',
                  sa.Column('description', sa.TEXT(), nullable=True))
    op.add_column('resource_cache',
                  sa.Column('state', sa.String(length=64), nullable=True))
    op.alter_column('resource_cache_request', 'resource_type',
                    type_=NEW_TYPES, existing_type=OLD_TYPES, nullable=False)


def downgrade():
    op.drop_column('resource_cache', 'state')
    op.drop_column('resource_cache', 'description')

    bind = op.get_bind()
    session = Session(bind=bind)
    request_table = sa.table('resource_cache_request',
                             sa.Column('resource_type', NEW_TYPES),
                             sa.Column('id', sa.String(36)))
    cache_table = sa.table('resource_cache', sa.Column('cache_id'))
    try:
        session.execute(cache_table.delete().where(cache_table.c.cache_id.in_(
            session.query(request_table.c.id).filter(
                request_table.c.resource_type == 'snapshot')
        )))
        session.execute(request_table.delete().where(
            request_table.c.resource_type == 'snapshot'))
        session.commit()
    finally:
        session.close()

    op.alter_column('resource_cache_request', 'resource_type',
                    type_=OLD_TYPES, existing_type=NEW_TYPES, nullable=False)
