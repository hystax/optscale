""""added_token_digest"

Revision ID: e1032b348546
Revises: 22e57b7a4186
Create Date: 2017-08-18 16:22:41.427825

"""
from alembic import op
import sqlalchemy as sa


import json
import hashlib
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import Session
from sqlalchemy import (Column, String, TIMESTAMP)
from auth.auth_server.utils import as_dict, ModelEncoder


# revision identifiers, used by Alembic.
revision = 'e1032b348546'
down_revision = '22e57b7a4186'
branch_labels = None
depends_on = None



class Base(object):
    @declared_attr
    # pylint: disable=E0213
    def __tablename__(cls):
        # pylint: disable=E1101
        return cls.__name__.lower()

    def to_dict(self):
        return as_dict(self)

    def to_json(self):
        return json.dumps(self.to_dict(), cls=ModelEncoder)


Base = declarative_base(cls=Base)


class Token(Base):

    __tablename__ = 'token'

    token = Column(String(350), primary_key=True, nullable=False)
    digest = Column(String(32), index=True, unique=True, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    valid_until = Column(TIMESTAMP, nullable=False, index=True)
    ip = Column(String(39), nullable=False)


def upgrade():
    op.add_column('token', sa.Column('digest', sa.String(length=32),
                                     nullable=False))
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        tokens = session.query(Token).all()
        for token in tokens:
            digest = hashlib.md5(token.token.encode('utf-8')).hexdigest()
            token.digest = digest
            session.add(token)
        session.commit()
    finally:
        session.close()
    op.create_index(op.f('ix_token_digest'), 'token', ['digest'], unique=True)


def downgrade():
    op.drop_index(op.f('ix_token_digest'), table_name='token')
    op.drop_column('token', 'digest')
