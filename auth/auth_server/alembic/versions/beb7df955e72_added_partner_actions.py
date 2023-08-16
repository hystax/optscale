""""added_partner_actions"

Revision ID: beb7df955e72
Revises: 798a1c677131
Create Date: 2017-06-14 10:38:57.863437

"""
import json
import uuid
from datetime import datetime
from alembic import op
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import (Column, String, Integer, ForeignKey, TEXT, Boolean)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, backref

from auth.auth_server.utils import as_dict, ModelEncoder
from auth.auth_server.models.exceptions import InvalidTreeException


# revision identifiers, used by Alembic.
revision = 'beb7df955e72'
down_revision = '798a1c677131'
branch_labels = None
depends_on = None


def gen_id():
    return str(uuid.uuid4())

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
    # ### commands auto generated by Alembic - please adjust! ###
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        root_type = session.query(Type).filter_by(name='root').one_or_none()
        partner_type = session.query(Type).filter_by(
            name='partner').one_or_none()

        action_group_partners = ActionGroup(name='Manage partners', order=800)

        session.add(action_group_partners)

        action_list_partners = Action(name='LIST_PARTNERS', type=root_type,
                                      action_group=action_group_partners,
                                      order=810)
        action_create_partner = Action(name='CREATE_PARTNER', type=root_type,
                                       action_group=action_group_partners,
                                       order=820)
        action_edit_partner = Action(name='EDIT_PARTNER', type=partner_type,
                                     action_group=action_group_partners,
                                     order=830)
        action_delete_partner = Action(name='DELETE_PARTNER', type=root_type,
                                       action_group=action_group_partners,
                                       order=840)
        session.add(action_list_partners)
        session.add(action_create_partner)
        session.add(action_edit_partner)
        session.add(action_delete_partner)
        sa_role = session.query(Role).filter(
            Role.name == 'Super Admin',
            Role.deleted.is_(False)).one_or_none()
        sa_role.assign_action(action_list_partners)
        sa_role.assign_action(action_create_partner)
        sa_role.assign_action(action_edit_partner)
        sa_role.assign_action(action_delete_partner)

        session.commit()
    finally:
        session.close()
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        action_list_partners = session.query(Action).filter_by(name='LIST_PARTNERS').one_or_none()
        action_create_partner = session.query(Action).filter_by(name='CREATE_PARTNER').one_or_none()
        action_edit_partner = session.query(Action).filter_by(name='EDIT_PARTNER').one_or_none()
        action_delete_partner = session.query(Action).filter_by(name='DELETE_PARTNER').one_or_none()
        sa_role = session.query(Role).filter(
            Role.name == 'Super Admin',
            Role.deleted.is_(False)).one_or_none()
        sa_role.remove_action(action_list_partners)
        sa_role.remove_action(action_create_partner)
        sa_role.remove_action(action_edit_partner)
        sa_role.remove_action(action_delete_partner)
        session.delete(action_list_partners)
        session.delete(action_create_partner)
        session.delete(action_edit_partner)
        session.delete(action_delete_partner)

        session.query(ActionGroup).filter_by(name='Manage partners').delete()
        session.commit()
    finally:
        session.close()
    # ### end Alembic commands ###
