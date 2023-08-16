""""changes_auth_actions"

Revision ID: b547c54448d2
Revises: 481dbdfd5d18
Create Date: 2017-06-22 14:00:25.804001

"""
import json
import uuid
import string
import random
from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import (Column, String, Integer, ForeignKey, TIMESTAMP,
                        TEXT, Boolean, and_)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, backref, Session
from alembic import op
import sqlalchemy as sa

from auth.auth_server.utils import as_dict, ModelEncoder
from auth.auth_server.models.exceptions import InvalidTreeException


# revision identifiers, used by Alembic.
revision = 'b547c54448d2'
down_revision = '481dbdfd5d18'
branch_labels = None
depends_on = None


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


class Action(BaseIntKeyMixin, Base, OrderMixin):

    __tablename__ = 'action'

    name = Column(String(64), index=True, nullable=False, unique=True)
    type_id = Column(Integer, ForeignKey('type.id'))
    action_group_id = Column(Integer, ForeignKey('action_group.id'),
                             nullable=False)
    action_group = relationship("ActionGroup", backref="actions")
    type = relationship("Type", backref='actions')

    def __init__(self, name=None, type=None, action_group=None,
                 action_group_id=None, order=0):
        if action_group:
            self.action_group = action_group
        if action_group_id is not None:
            self.action_group_id = action_group_id
        self.name = name
        self.type = type
        self.order = order

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


action_map = (
    # (old-name, new-name, old-type, new-type)
    ('LIST_PARTNERS', 'INFO_PARTNER', 'root', 'partner'),
    ('LIST_CUSTOMERS', 'INFO_CUSTOMER', 'partner', 'customer'),
    ('LIST_DRPLANS', 'INFO_DRPLAN', None, None),
    ('LIST_CSS', 'INFO_CS', None, None),
    ('EDIT_VSPHERE', 'MANAGE_VSPHERE_CREDENTIALS', None, None),
    ('PARK_UNPARK', 'EDIT_REPLICATION_STATE', None, None)
)


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        type_group = session.query(Type).filter_by(name='group').one_or_none()
        mg_replication_grp = session.query(ActionGroup).filter_by(
            name='MANAGE_REPLICATION').one_or_none()
        action_manage_device = Action(name='MANAGE_DEVICE', type=type_group,
                                      action_group=mg_replication_grp,
                                      order=705)
        action_generate_drplan = session.query(Action).filter_by(
            name='GENERATE_DRPLAN').one_or_none()
        action_generate_drplan.deleted_at = int(datetime.utcnow().timestamp())
        session.add(action_manage_device)
        session.add(action_generate_drplan)

        for act in action_map:
            old_name, new_name, old_type, new_type = act
            action = session.query(Action).filter_by(
                name=old_name).one_or_none()
            action.name = new_name
            if new_type:
                type_ = session.query(Type).filter_by(
                    name=new_type).one_or_none()
                action.type = type_
            session.add(action)
        session.commit()
    finally:
        session.close()


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        action_manage_device = session.query(Action).filter_by(
            name='MANAGE_DEVICE').one_or_none()

        action_generate_drplan = session.query(Action).filter_by(
            name='GENERATE_DRPLAN').one_or_none()
        action_generate_drplan.deleted_at = 0
        session.delete(action_manage_device)
        session.add(action_generate_drplan)

        for act in action_map:
            old_name, new_name, old_type, new_type = act
            action = session.query(Action).filter_by(
                name=new_name).one_or_none()
            action.name = old_name
            if old_type:
                type_ = session.query(Type).filter_by(
                    name=old_type).one_or_none()
                action.type = type_
            session.add(action)
        session.commit()

    finally:
        session.close()
