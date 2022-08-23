""""event_actions"

Revision ID: 9e311c87e269
Revises: e1032b348546
Create Date: 2017-08-28 16:25:34.255085

"""

import json
import uuid
import string
import random
from datetime import datetime
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import (Column, String, Integer, ForeignKey,
                        TEXT, Boolean, and_, Index)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, backref, Session
from alembic import op
from auth_server.utils import as_dict, ModelEncoder


# revision identifiers, used by Alembic.
revision = '9e311c87e269'
down_revision = 'e1032b348546'
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


class BaseMixin(BaseModel):
    id = Column(String(36), primary_key=True, default=gen_id)


class BaseIntKeyMixin(BaseModel):
    id = Column(Integer, primary_key=True, autoincrement=True)


class OrderMixin(object):
    order = Column(Integer, nullable=False, default=0)


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

    def append(self, node_name):
        self.children[node_name] = Type(node_name, parent=self)

    def __repr__(self):
        return "Type(name=%r, id=%r, parent_id=%r)" % (self.name, self.id,
                                                       self.parent_id)


class Role(Base, BaseIntKeyMixin):

    __tablename__ = 'role'

    name = Column(String(64), index=True, nullable=False)
    description = Column(TEXT, nullable=True)
    type_id = Column(Integer, ForeignKey('type.id'), nullable=False)
    lvl_id = Column(Integer, ForeignKey('type.id'), nullable=False)
    scope_id = Column(String(36), nullable=True)
    shared = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    actions = relationship("Action", secondary="role_action")
    type = relationship("Type", backref="roles", foreign_keys=[type_id])
    lvl = relationship("Type", backref="levels", foreign_keys=[lvl_id])
    __table_args__ = (Index('idx_role_name_scope', "name", "type_id",
                            "scope_id", "deleted_at", unique=True),)

    def assign_action(self, action):
        self.role_action.append(RoleAction(role=self, action=action))

    def remove_action(self, action):
        self.actions.remove(action)

    def __init__(self, name=None, type=None, lvl=None, shared=False,
                 is_active=True, scope_id=None, description=None, type_id=None,
                 lvl_id=None):
        if type:
            self.type = type
        if type_id is not None:
            self.type_id = type_id
        if lvl:
            self.lvl = lvl
        if lvl_id is not None:
            self.lvl_id = lvl_id
        self.name = name
        self.scope_id = scope_id
        self.shared = shared
        self.is_active = is_active
        self.description = description
        self.users = []

    def __repr__(self):
        return '<Role %s (type: %s) >' % (self.name, self.type.name)


class Action(BaseIntKeyMixin, Base, OrderMixin):

    __tablename__ = 'action'

    name = Column(String(64), index=True, nullable=False, unique=True)
    type_id = Column(Integer, ForeignKey('type.id'))
    action_group_id = Column(Integer, ForeignKey('action_group.id'),
                             nullable=False)
    action_group = relationship("ActionGroup", backref="actions")
    type = relationship("Type", backref='actions')
    roles = relationship("Role", secondary="role_action", viewonly=True)

    def __init__(self, name=None, type=None, action_group=None,
                 action_group_id=None, order=0):
        if action_group:
            self.action_group = action_group
        if action_group_id is not None:
            self.action_group_id = action_group_id
        self.name = name
        self.type = type
        self.order = order
        self.roles = []

    def __repr__(self):
        return '<Action %s>' % self.name


class ActionGroup(BaseIntKeyMixin, Base, OrderMixin):

    __tablename__ = 'action_group'

    name = Column(String(24), index=True, nullable=False, unique=True)

    def __init__(self, name=None, order=0):
        self.name = name
        self.order = order

    @property
    def actual_actions(self):
        return Session.object_session(self).query(Action).filter(
            and_(
                Action.deleted.is_(False),
                Action.action_group_id == self.id
            )
        ).all()

    def __repr__(self):
        return '<ActionGroup %s>' % self.name


class RoleAction(Base):

    __tablename__ = 'role_action'

    id = Column(String(36), default=gen_id, primary_key=True, unique=True)
    role_id = Column(Integer, ForeignKey('role.id'), primary_key=True)
    action_id = Column(Integer, ForeignKey('action.id'), primary_key=True)

    role = relationship("Role", backref=backref(
        "role_action", cascade="all, delete-orphan"))
    action = relationship("Action", backref=backref(
        "role_action", cascade="all, delete-orphan"))

    def __init__(self, role=None, action=None):
        self.id = gen_id()
        self.role = role
        self.action = action

    def __repr__(self):
        return '<RoleAction {}>'.format(self.role.name + " " +
                                        self.action.name)


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        type_customer = session.query(Type).filter(
            Type.name == 'customer'
        ).one_or_none()
        action_group_events = ActionGroup('EVENTS_NOTIFICATIONS', 900)
        action_ack_event = Action(
            'ACK_EVENT', type_customer, action_group_events, order=920)
        action_poll_event = Action(
            'POLL_EVENT', type_customer, action_group_events, order=910)
        session.add(action_ack_event)
        session.add(action_poll_event)
        session.commit()
        # try to update superadmin role
        try:
            # will not crash even superadmin role has been removed/renamed
            role_superadmin = session.query(Role).filter_by(
                name='Super Admin').one_or_none()
            role_superadmin.assign_action(action_ack_event)
            role_superadmin.assign_action(action_poll_event)
            session.add(role_superadmin)
            session.commit()
        except:
            session.rollback()
    finally:
        session.close()


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        action_ack_event = session.query(Action).filter_by(
            name='ACK_EVENT').one_or_none()
        action_poll_event = session.query(Action).filter_by(
            name='POLL_EVENT').one_or_none()
        action_group_events = session.query(ActionGroup).filter_by(
            name='EVENTS_NOTIFICATIONS').one_or_none()
        session.delete(action_ack_event)
        session.delete(action_poll_event)
        session.delete(action_group_events)
        session.commit()
    finally:
        session.close()
