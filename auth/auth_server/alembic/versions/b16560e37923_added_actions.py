""""added_actions"

Revision ID: b16560e37923
Revises: 3481a6b2731b
Create Date: 2017-05-23 17:15:09.118300

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

revision = 'b16560e37923'
down_revision = 'fbfbadb845f4'
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
    is_active = Column(Boolean, nullable=False, default=True)
    actions = relationship("Action", secondary="role_action", viewonly=True)
    type = relationship("Type", backref="roles", foreign_keys=[type_id])
    lvl = relationship("Type", backref="levels", foreign_keys=[lvl_id])

    def assign_action(self, action):
        self.role_action.append(RoleAction(role=self, action=action))

    def __init__(self, name=None, type=None, lvl=None, is_active=True,
                 scope_id=None, description=None):
        self.name = name
        self.type = type
        self.lvl = lvl
        self.scope_id = scope_id
        self.is_active = is_active
        self.description = description
        self.users = []

    def __repr__(self):
        return '<Role %s (type: %s) >' % (self.name, self.type.name)


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


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        partner_type = session.query(Type).filter_by(
            name='partner').one_or_none()
        customer_type = session.query(Type).filter_by(
            name='customer').one_or_none()
        group_type = session.query(Type).filter_by(name='group').one_or_none()

        action_group_customer = ActionGroup(name='customer', order=300)
        action_group_cloudsite = ActionGroup(name='cloudsite', order=400)
        action_group_protection = ActionGroup(name='protection', order=600)
        action_group_group = ActionGroup(name='group', order=700)
        action_group_user = ActionGroup(name='user', order=800)
        action_group_assignment = ActionGroup(name='assignment', order=900)
        action_group_role = ActionGroup(name='role', order=1000)

        session.add(action_group_customer)
        session.add(action_group_cloudsite)
        session.add(action_group_protection)
        session.add(action_group_group)
        session.add(action_group_user)
        session.add(action_group_assignment)
        session.add(action_group_role)

        action_list_customers = Action(name='LIST_CUSTOMERS',
                                       type=partner_type,
                                       action_group=action_group_customer)
        action_create_customer = Action(name='CREATE_CUSTOMER',
                                        type=partner_type,
                                        action_group=action_group_customer)
        action_edit_customer_info = Action(name='EDIT_CUSTOMER_INFO',
                                           type=partner_type,
                                           action_group=action_group_customer)
        action_activate_customer = Action(name='ACTIVATE_CUSTOMER',
                                          type=partner_type,
                                          action_group=action_group_customer)
        action_delete_customer = Action(name='DELETE_CUSTOMER',
                                        type=partner_type,
                                        action_group=action_group_customer)

        action_list_css = Action(name='LIST_CSS', type=customer_type,
                                 action_group=action_group_cloudsite)
        action_create_cs = Action(name='CREATE_CS', type=customer_type,
                                  action_group=action_group_cloudsite)
        action_edit_cs = Action(name='EDIT_CS', type=customer_type,
                                action_group=action_group_cloudsite)
        action_delete_cs = Action(name='DELETE_CS', type=customer_type,
                                  action_group=action_group_cloudsite)

        action_edit_retention = Action(name='EDIT_RETENTION', type=group_type,
                                       action_group=action_group_protection)
        action_edit_schedule = Action(name='EDIT_SCHEDULE', type=group_type,
                                      action_group=action_group_protection)
        action_park_unpark = Action(name='PARK_UNPARK', type=group_type,
                                    action_group=action_group_protection)

        action_edit_vsphere = Action(name='EDIT_VSPHERE', type=customer_type,
                                     action_group=action_group_protection)
        action_download_agent = Action(name='DOWNLOAD_AGENT',
                                       type=customer_type,
                                       action_group=action_group_protection)

        action_create_group = Action(name='CREATE_GROUP', type=customer_type,
                                     action_group=action_group_group)
        action_edit_group = Action(name='EDIT_GROUP', type=customer_type,
                                   action_group=action_group_group)

        action_list_users = Action(name='LIST_USERS', type=customer_type,
                                   action_group=action_group_user)
        action_create_user = Action(name='CREATE_USER', type=customer_type,
                                    action_group=action_group_user)
        action_edit_user_info = Action(name='EDIT_USER_INFO',
                                       type=customer_type,
                                       action_group=action_group_user)
        action_activate_user = Action(name='ACTIVATE_USER', type=customer_type,
                                      action_group=action_group_user)
        action_delete_user = Action(name='DELETE_USER', type=customer_type,
                                    action_group=action_group_user)
        action_reset_user_password = Action(name='RESET_USER_PASSWORD',
                                            type=customer_type,
                                            action_group=action_group_user)

        action_assign_user = Action(name='ASSIGN_USER', type=customer_type,
                                    action_group=action_group_assignment)
        action_assign_self = Action(name='ASSIGN_SELF', type=customer_type,
                                    action_group=action_group_assignment)

        action_list_roles = Action(name='LIST_ROLES', type=customer_type,
                                   action_group=action_group_role)
        action_edit_roles = Action(name='EDIT_ROLES', type=customer_type,
                                   action_group=action_group_role)
        action_edit_own_roles = Action(name='EDIT_OWN_ROLES',
                                       type=customer_type,
                                       action_group=action_group_role)
        action_delete_role = Action(name='DELETE_ROLE', type=customer_type,
                                    action_group=action_group_role)
        action_create_role = Action(name='CREATE_ROLE', type=customer_type,
                                    action_group=action_group_role)

        action_edit_sublevel_roles = Action(name='EDIT_SUBLEVEL_ROLES',
                                            type=partner_type,
                                            action_group=action_group_role)
        action_delete_sublevel_role = Action(name='DELETE_SUBLEVEL_ROLE',
                                             type=partner_type,
                                             action_group=action_group_role)

        session.add(action_list_customers)
        session.add(action_create_customer)
        session.add(action_edit_customer_info)
        session.add(action_activate_customer)
        session.add(action_delete_customer)

        session.add(action_list_css)
        session.add(action_create_cs)
        session.add(action_edit_cs)
        session.add(action_delete_cs)

        session.add(action_edit_retention)
        session.add(action_edit_schedule)
        session.add(action_park_unpark)

        session.add(action_edit_vsphere)
        session.add(action_download_agent)

        session.add(action_create_group)
        session.add(action_edit_group)

        session.add(action_list_users)
        session.add(action_create_user)
        session.add(action_edit_user_info)
        session.add(action_activate_user)
        session.add(action_delete_user)
        session.add(action_reset_user_password)

        session.add(action_assign_user)
        session.add(action_assign_self)

        session.add(action_list_roles)
        session.add(action_edit_roles)
        session.add(action_edit_own_roles)
        session.add(action_delete_role)
        session.add(action_create_role)

        session.add(action_edit_sublevel_roles)
        session.add(action_delete_sublevel_role)

        session.commit()
    finally:
        session.close()
        # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        session.query(Action).filter_by(name='LIST_CUSTOMERS').delete()
        session.query(Action).filter_by(name='CREATE_CUSTOMER').delete()
        session.query(Action).filter_by(name='EDIT_CUSTOMER_INFO').delete()
        session.query(Action).filter_by(name='ACTIVATE_CUSTOMER').delete()
        session.query(Action).filter_by(name='DELETE_CUSTOMER').delete()
        session.query(Action).filter_by(name='LIST_CSS').delete()
        session.query(Action).filter_by(name='CREATE_CS').delete()
        session.query(Action).filter_by(name='EDIT_CS').delete()
        session.query(Action).filter_by(name='DELETE_CS').delete()
        session.query(Action).filter_by(name='EDIT_RETENTION').delete()
        session.query(Action).filter_by(name='EDIT_SCHEDULE').delete()
        session.query(Action).filter_by(name='PARK_UNPARK').delete()
        session.query(Action).filter_by(name='EDIT_VSPHERE').delete()
        session.query(Action).filter_by(name='DOWNLOAD_AGENT').delete()
        session.query(Action).filter_by(name='CREATE_GROUP').delete()
        session.query(Action).filter_by(name='EDIT_GROUP').delete()
        session.query(Action).filter_by(name='LIST_USERS').delete()
        session.query(Action).filter_by(name='CREATE_USER').delete()
        session.query(Action).filter_by(name='EDIT_USER_INFO').delete()
        session.query(Action).filter_by(name='ACTIVATE_USER').delete()
        session.query(Action).filter_by(name='DELETE_USER').delete()
        session.query(Action).filter_by(name='RESET_USER_PASSWORD').delete()
        session.query(Action).filter_by(name='ASSIGN_USER').delete()
        session.query(Action).filter_by(name='ASSIGN_SELF').delete()
        session.query(Action).filter_by(name='LIST_ROLES').delete()
        session.query(Action).filter_by(name='EDIT_ROLES').delete()
        session.query(Action).filter_by(name='EDIT_OWN_ROLES').delete()
        session.query(Action).filter_by(name='DELETE_ROLE').delete()
        session.query(Action).filter_by(name='CREATE_ROLE').delete()
        session.query(Action).filter_by(name='EDIT_SUBLEVEL_ROLES').delete()
        session.query(Action).filter_by(name='DELETE_SUBLEVEL_ROLE').delete()

        session.query(ActionGroup).filter_by(name='customer').delete()
        session.query(ActionGroup).filter_by(name='cloudsite').delete()
        session.query(ActionGroup).filter_by(name='protection').delete()
        session.query(ActionGroup).filter_by(name='group').delete()
        session.query(ActionGroup).filter_by(name='user').delete()
        session.query(ActionGroup).filter_by(name='assignment').delete()
        session.query(ActionGroup).filter_by(name='role').delete()

        session.commit()
    finally:
        session.close()
        # ### end Alembic commands ###
