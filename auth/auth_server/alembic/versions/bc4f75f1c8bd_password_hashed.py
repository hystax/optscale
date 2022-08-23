""""password_hashed"

Revision ID: bc4f75f1c8bd
Revises: bfca79015852
Create Date: 2017-06-07 11:29:59.690148

"""
import json
import uuid
import string
import random
from datetime import datetime

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session
from sqlalchemy import (Column, String, Integer, ForeignKey, Boolean)
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, backref

from auth_server.utils import as_dict, hash_password, ModelEncoder
from auth_server.models.exceptions import InvalidTreeException


# revision identifiers, used by Alembic.
revision = 'bc4f75f1c8bd'
down_revision = 'bfca79015852'
branch_labels = None
depends_on = None


def gen_id():
    return str(uuid.uuid4())


def gen_salt():
    return ''.join(random.choice(string.ascii_lowercase + string.digits)
                   for _ in range(8))


class Base(object):
    @declared_attr
    # pylint: disable=E0213
    def __tablename__(cls):
        # pylint: disable=E1101
        return cls.__name__.lower()

    def to_json(self):
        return json.dumps(as_dict(self), cls=ModelEncoder)


Base = declarative_base(cls=Base)


class BaseModel(object):
    created_at = Column(Integer, default=datetime.utcnow().timestamp,
                        nullable=False)
    deleted_at = Column(Integer, default=0, nullable=False)

    @hybrid_property
    def deleted(self):
        return self.deleted_at != 0


class BaseMixin(BaseModel):
    id = Column(String(36), primary_key=True, default=gen_id)


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

    @hybrid_property
    def child_tree(self):
        all_ = []

        def get_childs(node, li):
            if node:
                list_element = node.children
                if len(list_element) == 1:
                    li.append(list_element[0])
                    get_childs(list_element[0], li)
                elif len(list_element) > 1:
                    raise InvalidTreeException("Invalid tree format")
            else:
                return

        get_childs(self, all_)
        return sorted(all_, key=lambda x: x.id)

    @hybrid_property
    def parent_tree(self):
        all_ = []

        def get_parents(node, li):
            if node:
                element = node.parent
                if element:
                    li.append(element)
                    get_parents(element, li)
            else:
                return

        get_parents(self, all_)
        return sorted(all_, key=lambda x: x.id, reverse=True)

    def __init__(self, id=None, name=None, parent=None, assignable=True):
        self.id = id
        self.name = name
        self.parent = parent
        self.assignable = assignable

    def append(self, node_name):
        self.children[node_name] = Type(node_name, parent=self)

    def __repr__(self):
        return "Type(name=%r, id=%r, parent_id=%r)" % (self.name, self.id,
                                                       self.parent_id)


class User(Base, BaseMixin):

    __tablename__ = 'user'

    display_name = Column(String(64), nullable=False, index=False)
    is_active = Column(Boolean, nullable=False, default=True)
    type_id = Column(Integer, ForeignKey('type.id'), nullable=False)
    email = Column(String(256), nullable=False, unique=True, index=True)
    password = Column(String(64), nullable=False)
    salt = Column(String(20), nullable=False)
    scope_id = Column(String(36), index=True, nullable=True)
    type = relationship("Type", backref="users")

    def __init__(self, email=None, type=None, password=None,
                 salt=None, scope_id=None, type_id=None, display_name=None,
                 is_active=True):
        if type:
            self.type = type
        if type_id is not None:
            self.type_id = type_id
        self.email = email
        self.password = password
        self.salt = salt if salt else gen_salt()
        self.scope_id = scope_id
        self.is_active = is_active
        self.display_name = display_name
        self.roles = []

    def __repr__(self):
        return '<User %s>' % self.email


def upgrade():
    op.alter_column('user', 'password', existing_type=sa.String(64),
                    nullable=False)

    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        users = session.query(User).all()
        for user in users:
            user_salt = gen_salt()
            user.salt = user_salt
            user.password = hash_password(user.password, user_salt)
            session.add(user)
        session.commit()
    finally:
        session.close()


def downgrade():
    # ### since hashing is irreversible, there is no downgrade ###
    pass
