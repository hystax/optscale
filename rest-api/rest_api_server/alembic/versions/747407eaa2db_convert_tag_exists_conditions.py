""""convert_tag_exists_conditions"

Revision ID: 747407eaa2db
Revises: a9eb1e7f82d9
Create Date: 2021-02-19 15:33:35.980226

"""
import json

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from sqlalchemy.orm import Session

revision = '747407eaa2db'
down_revision = 'a9eb1e7f82d9'
branch_labels = None
depends_on = None

condition_table = sa.table(
        'condition',
        sa.column('id', sa.String(36)),
        sa.Column('type',
                  sa.Enum('NAME_IS', 'NAME_STARTS_WITH', 'NAME_ENDS_WITH',
                          'NAME_CONTAINS', 'RESOURCE_TYPE_IS', 'CLOUD_IS',
                          'TAG_IS', 'REGION_IS', 'TAG_EXISTS',
                          'TAG_VALUE_STARTS_WITH')),
        sa.column('meta_info', sa.String(256)))


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        stmt = sa.select([condition_table]).where(
            condition_table.c.type == 'TAG_EXISTS')
        for condition in session.execute(stmt):
            try:
                loaded = json.loads(condition['meta_info'])
            except Exception:
                continue
            if not isinstance(loaded, dict):
                continue
            key = loaded.get('key')
            if key is None:
                continue
            session.execute(
                sa.update(condition_table).values(meta_info=key).where(
                    condition_table.c.id == condition['id']))
        session.commit()
    finally:
        session.close()


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        stmt = sa.select([condition_table]).where(
            condition_table.c.type == 'TAG_EXISTS')
        for condition in session.execute(stmt):
            new_meta = json.dumps({'key': condition['meta_info']})
            session.execute(
                sa.update(condition_table).values(meta_info=new_meta).where(
                    condition_table.c.id == condition['id']))
        session.commit()
    finally:
        session.close()
