""""set_root_assignable"

Revision ID: 2b5e2351dc6a
Revises: 965d03612833
Create Date: 2017-07-13 10:21:07.052461

"""
import json
from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, backref, Session
from alembic import op

from auth_server.utils import as_dict, ModelEncoder

# revision identifiers, used by Alembic.
revision = '2b5e2351dc6a'
down_revision = '965d03612833'
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


class BaseModel(object):
    created_at = Column(Integer, default=datetime.utcnow().timestamp,
                        nullable=False)
    deleted_at = Column(Integer, default=0, nullable=False)

    @hybrid_property
    def deleted(self):
        return self.deleted_at != 0


class BaseIntKeyMixin(BaseModel):
    id = Column(Integer, primary_key=True, autoincrement=True)


class Type(Base, BaseIntKeyMixin):

    __tablename__ = 'type'

    parent_id = Column(Integer, ForeignKey('type.id'))
    name = Column(String(24), nullable=False, index=True, unique=True)
    assignable = Column(Boolean, nullable=False, default=True)
    children = relationship(
        'Type',
        # cascade deletions
        cascade="all",
        # many to one + adjacency list - remote_side
        # is required to reference the 'remote'
        # column in the join condition.
        backref=backref("parent", remote_side='Type.id'),
        # children will be represented as a dictionary
        # on the "name" attribute.
        collection_class=list)

    def __init__(self, id=None, name=None, parent=None, assignable=True):
        self.id = id
        self.name = name
        self.parent = parent
        self.assignable = assignable


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        type_root = session.query(Type).filter_by(
                name='root').one_or_none()
        type_root.assignable = True
        session.add(type_root)
        session.commit()
    finally:
        session.close()


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        type_root = session.query(Type).filter_by(
                name='root').one_or_none()
        type_root.assignable = False
        session.add(type_root)
        session.commit()
    finally:
        session.close()
