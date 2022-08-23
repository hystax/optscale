""""removed_token_value_from_table"

Revision ID: 5771980b501b
Revises: 716f4735a9ea
Create Date: 2021-10-20 14:42:28.607083

"""
from datetime import datetime

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session
from sqlalchemy import String, Integer, table, column

# revision identifiers, used by Alembic.
revision = '5771980b501b'
down_revision = '716f4735a9ea'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    now = datetime.utcnow()
    try:
        token_table = table(
            'token',
            sa.Column('valid_until', sa.TIMESTAMP()),
        )
        op.execute(token_table.update().where(
            token_table.c.valid_until > now
        ).values(
            valid_until=now
        ))
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

    op.drop_column('token', 'token')
    op.drop_index('ix_token_digest', table_name='token')
    op.create_primary_key('pk_token', 'token', ['digest'])


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        token_table = table('token')
        op.execute(token_table.delete())
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

    op.add_column('token', sa.Column('token', sa.String(length=350), nullable=False))
    op.drop_constraint('pk_token', 'token', type_='primary')
    op.create_index('ix_token_digest', 'token', ['digest'], unique=True)
    op.create_primary_key('pk_token', 'token', ['token'])
