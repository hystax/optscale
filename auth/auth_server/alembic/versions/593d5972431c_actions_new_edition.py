""""actions_new_edition"

Revision ID: 593d5972431c
Revises: b16560e37923
Create Date: 2017-05-30 11:56:18.035219

"""
import json
import uuid
import time
from datetime import datetime
from alembic import op
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import (Column, String, Integer, ForeignKey, TEXT, Boolean, Table, VARCHAR)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, backref

from auth_server.utils import as_dict, ModelEncoder
from auth_server.models.exceptions import InvalidTreeException

# revision identifiers, used by Alembic.
revision = '593d5972431c'
down_revision = 'b16560e37923'
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
    actions = relationship("Action", secondary="role_action")
    type = relationship("Type", backref="roles", foreign_keys=[type_id])
    lvl = relationship("Type", backref="levels", foreign_keys=[lvl_id])

    def assign_action(self, action):
        self.role_action.append(RoleAction(role=self, action=action))

    def remove_action(self, action):
        self.actions.remove(action)

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
        op.alter_column(
            table_name='action_group',
            column_name='name',
            nullable=False,
            type_=VARCHAR(length=50)
        )

        root_type = session.query(Type).filter_by(name='root').one_or_none()
        partner_type = session.query(Type).filter_by(name='partner').one_or_none()
        customer_type = session.query(Type).filter_by(name='customer').one_or_none()
        group_type = session.query(Type).filter_by(name='group').one_or_none()

        session.query(ActionGroup).filter_by(name='admin').update({"name": "Super Admin", "order": 100})
        session.query(ActionGroup).filter_by(name='dr_plan').update({"name": "Manage users and assignments", "order": 200})
        session.query(ActionGroup).filter_by(name='customer').update({"name": "Manage user roles", "order": 300})
        session.query(ActionGroup).filter_by(name='cloudsite').update({"name": "Manage customers", "order": 400})
        session.query(ActionGroup).filter_by(name='protection').update({"name": "Manage Disaster Recovery plans", "order": 500})
        session.query(ActionGroup).filter_by(name='group').update({"name": "Manage Cloud Sites", "order": 600})
        session.query(ActionGroup).filter_by(name='user').update({"name": "Manage device groups and replication settings", "order": 700})
        session.query(ActionGroup).filter_by(name='assignment').update({"deleted_at": int(time.time())})
        session.query(ActionGroup).filter_by(name='role').update({"deleted_at": int(time.time())})

        action_group_admin = session.query(ActionGroup).filter_by(name='Super Admin').one_or_none()
        action_group_customer = session.query(ActionGroup).filter_by(name='Manage customers').one_or_none()
        action_group_cloudsite = session.query(ActionGroup).filter_by(name='Manage Cloud Sites').one_or_none()
        action_group_dr_plans = session.query(ActionGroup).filter_by(name='Manage Disaster Recovery plans').one_or_none()
        action_group_group = session.query(ActionGroup).filter_by(name='Manage device groups and replication settings').one_or_none()
        action_group_user = session.query(ActionGroup).filter_by(name='Manage users and assignments').one_or_none()
        action_group_role = session.query(ActionGroup).filter_by(name='Manage user roles').one_or_none()

        # Super Admin
        session.query(Action).filter_by(name='ADMIN').update({"type_id": root_type.id, "action_group_id": action_group_admin.id, "order": 110})

        # Manage users and assignments
        session.query(Action).filter_by(name='LIST_USERS').update({"type_id": customer_type.id, "action_group_id": action_group_user.id, "order": 210})
        session.query(Action).filter_by(name='CREATE_USER').update({"type_id": customer_type.id, "action_group_id": action_group_user.id, "order": 220})
        session.query(Action).filter_by(name='EDIT_USER_INFO').update({"type_id": customer_type.id, "action_group_id": action_group_user.id, "order": 230})
        session.query(Action).filter_by(name='ACTIVATE_USER').update({"type_id": customer_type.id, "action_group_id": action_group_user.id, "order": 240})
        session.query(Action).filter_by(name='DELETE_USER').update({"type_id": customer_type.id, "action_group_id": action_group_user.id, "order": 250})
        session.query(Action).filter_by(name='RESET_USER_PASSWORD').update({"type_id": customer_type.id, "action_group_id": action_group_user.id, "order": 260})
        session.query(Action).filter_by(name='ASSIGN_USER').update({"type_id": customer_type.id, "action_group_id": action_group_user.id, "order": 270})
        session.query(Action).filter_by(name='ASSIGN_SELF').update({"type_id": customer_type.id, "action_group_id": action_group_user.id, "order": 280})

        # Manage user roles
        session.query(Action).filter_by(name='LIST_ROLES').update({"type_id": customer_type.id, "action_group_id": action_group_role.id, "order": 310})
        session.query(Action).filter_by(name='CREATE_ROLE').update({"type_id": customer_type.id, "action_group_id": action_group_role.id, "order": 320})
        session.query(Action).filter_by(name='EDIT_ROLES').update({"type_id": customer_type.id, "action_group_id": action_group_role.id, "order": 330})
        session.query(Action).filter_by(name='EDIT_OWN_ROLES').update({"type_id": customer_type.id, "action_group_id": action_group_role.id, "order": 340})
        session.query(Action).filter_by(name='EDIT_SUBLEVEL_ROLES').update({"type_id": partner_type.id, "action_group_id": action_group_role.id, "order": 350})
        session.query(Action).filter_by(name='DELETE_ROLE').update({"type_id": customer_type.id, "action_group_id": action_group_role.id, "order": 360})
        session.query(Action).filter_by(name='DELETE_SUBLEVEL_ROLE').update({"type_id": partner_type.id, "action_group_id": action_group_role.id, "order": 370})

        # Manage customers
        session.query(Action).filter_by(name='LIST_CUSTOMERS').update({"type_id": partner_type.id, "action_group_id": action_group_customer.id, "order": 410})
        session.query(Action).filter_by(name='CREATE_CUSTOMER').update({"type_id": partner_type.id, "action_group_id": action_group_customer.id, "order": 420})
        session.query(Action).filter_by(name='EDIT_CUSTOMER_INFO').update({"type_id": customer_type.id, "action_group_id": action_group_customer.id, "order": 430})
        session.query(Action).filter_by(name='ACTIVATE_CUSTOMER').update({"type_id": partner_type.id, "action_group_id": action_group_customer.id, "order": 440})
        session.query(Action).filter_by(name='DELETE_CUSTOMER').update({"type_id": partner_type.id, "action_group_id": action_group_customer.id, "order": 450})

        # Manage Disaster Recovery plans
        session.query(Action).filter_by(name='LIST_DRPLANS').update({"type_id": customer_type.id, "action_group_id": action_group_dr_plans.id, "order": 510})
        session.query(Action).filter_by(name='CREATE_DRPLAN').update({"type_id": customer_type.id, "action_group_id": action_group_dr_plans.id, "order": 520})
        session.query(Action).filter_by(name='GENERATE_DRPLAN').update({"type_id": customer_type.id, "action_group_id": action_group_dr_plans.id, "order": 530})
        session.query(Action).filter_by(name='EDIT_DRPLAN').update({"type_id": customer_type.id, "action_group_id": action_group_dr_plans.id, "order": 540})
        session.query(Action).filter_by(name='DELETE_DRPLAN').update({"type_id": customer_type.id, "action_group_id": action_group_dr_plans.id, "order": 550})

        # Manage Cloud Sites
        session.query(Action).filter_by(name='LIST_CSS').update({"type_id": customer_type.id, "action_group_id": action_group_cloudsite.id, "order": 610})
        session.query(Action).filter_by(name='CREATE_CS').update({"type_id": customer_type.id, "action_group_id": action_group_cloudsite.id, "order": 620})
        session.query(Action).filter_by(name='EDIT_CS').update({"type_id": customer_type.id, "action_group_id": action_group_cloudsite.id, "order": 630})
        session.query(Action).filter_by(name='DELETE_CS').update({"type_id": customer_type.id, "action_group_id": action_group_cloudsite.id, "order": 640})

        # Manage device groups and replication settings
        session.query(Action).filter_by(name='CREATE_GROUP').update({"type_id": customer_type.id, "action_group_id": action_group_group.id, "order": 710})
        session.query(Action).filter_by(name='EDIT_GROUP').update({"type_id": customer_type.id, "action_group_id": action_group_group.id, "order": 720})
        session.query(Action).filter_by(name='PARK_UNPARK').update({"type_id": group_type.id, "action_group_id": action_group_group.id, "order": 730})
        session.query(Action).filter_by(name='EDIT_RETENTION').update({"type_id": group_type.id, "action_group_id": action_group_group.id, "order": 740})
        session.query(Action).filter_by(name='EDIT_SCHEDULE').update({"type_id": group_type.id, "action_group_id": action_group_group.id, "order": 750})
        session.query(Action).filter_by(name='EDIT_VSPHERE').update({"type_id": customer_type.id, "action_group_id": action_group_group.id, "order": 760})
        session.query(Action).filter_by(name='DOWNLOAD_AGENT').update({"type_id": customer_type.id, "action_group_id": action_group_group.id, "order": 770})

        session.commit()
    finally:
        session.close()
        # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    bind = op.get_bind()
    session = Session(bind=bind)
    try:

        root_type = session.query(Type).filter_by(name='root').one_or_none()
        partner_type = session.query(Type).filter_by(
            name='partner').one_or_none()
        customer_type = session.query(Type).filter_by(
            name='customer').one_or_none()
        group_type = session.query(Type).filter_by(name='group').one_or_none()

        session.query(ActionGroup).filter_by(name="Super Admin").update({"name": 'admin', "order": 100})
        session.query(ActionGroup).filter_by(name="Manage users and assignments").update({"name": 'dr_plan', "order": 500})
        session.query(ActionGroup).filter_by(name="Manage user roles").update({"name": 'customer', "order": 300})
        session.query(ActionGroup).filter_by(name="Manage customers").update({"name": 'cloudsite', "order": 400})
        session.query(ActionGroup).filter_by(name="Manage Disaster Recovery plans").update({"name": 'protection', "order": 600})
        session.query(ActionGroup).filter_by(name="Manage Cloud Sites").update({"name": 'group', "order": 700})
        session.query(ActionGroup).filter_by(name="Manage device groups and replication settings").update({"name": 'user', "order": 800})
        session.query(ActionGroup).filter_by(name='assignment').update({"deleted_at": 0})
        session.query(ActionGroup).filter_by(name='role').update({"deleted_at": 0})

        action_group_admin = session.query(ActionGroup).filter_by(name='admin').one_or_none()
        action_group_drplan = session.query(ActionGroup).filter_by(name='dr_plan').one_or_none()
        action_group_customer = session.query(ActionGroup).filter_by(name='customer').one_or_none()
        action_group_cloudsite = session.query(ActionGroup).filter_by(name='cloudsite').one_or_none()
        action_group_protection = session.query(ActionGroup).filter_by(name='protection').one_or_none()
        action_group_group = session.query(ActionGroup).filter_by(name='group').one_or_none()
        action_group_user = session.query(ActionGroup).filter_by(name='user').one_or_none()
        action_group_assignment = session.query(ActionGroup).filter_by(name='assignment').one_or_none()
        action_group_role = session.query(ActionGroup).filter_by(name='role').one_or_none()

        session.query(Action).filter_by(name='LIST_CUSTOMERS').update({"type_id": partner_type.id, "action_group_id": action_group_customer.id})
        session.query(Action).filter_by(name='CREATE_CUSTOMER').update({"type_id": partner_type.id,
                                                                        "action_group_id": action_group_customer.id})
        session.query(Action).filter_by(name='EDIT_CUSTOMER_INFO').update({"type_id": partner_type.id,
                                                                           "action_group_id": action_group_customer.id})
        session.query(Action).filter_by(name='ACTIVATE_CUSTOMER').update({"type_id": partner_type.id,
                                                                          "action_group_id": action_group_customer.id})
        session.query(Action).filter_by(name='DELETE_CUSTOMER').update({"type_id": partner_type.id,
                                                                        "action_group_id": action_group_customer.id})

        session.query(Action).filter_by(name='LIST_CSS').update({"type_id": customer_type.id,
                                                                 "action_group_id": action_group_cloudsite.id})
        session.query(Action).filter_by(name='CREATE_CS').update({"type_id": customer_type.id,
                                                                  "action_group_id": action_group_cloudsite.id})
        session.query(Action).filter_by(name='EDIT_CS').update({"type_id": customer_type.id,
                                                                "action_group_id": action_group_cloudsite.id})
        session.query(Action).filter_by(name='DELETE_CS').update({"type_id": customer_type.id,
                                                                  "action_group_id": action_group_cloudsite.id})

        session.query(Action).filter_by(name='EDIT_RETENTION').update({"type_id": group_type.id,
                                                                       "action_group_id": action_group_protection.id})
        session.query(Action).filter_by(name='EDIT_SCHEDULE').update({"type_id": group_type.id,
                                                                      "action_group_id": action_group_protection.id})
        session.query(Action).filter_by(name='PARK_UNPARK').update({"type_id": group_type.id,
                                                                    "action_group_id": action_group_protection.id})

        session.query(Action).filter_by(name='EDIT_VSPHERE').update({"type_id": customer_type.id,
                                                                     "action_group_id": action_group_protection.id})
        session.query(Action).filter_by(name='DOWNLOAD_AGENT').update({"type_id": customer_type.id,
                                                                       "action_group_id": action_group_protection.id})

        session.query(Action).filter_by(name='CREATE_GROUP').update({"type_id": customer_type.id,
                                                                     "action_group_id": action_group_group.id})
        session.query(Action).filter_by(name='EDIT_GROUP').update({"type_id": customer_type.id,
                                                                   "action_group_id": action_group_group.id})

        session.query(Action).filter_by(name='LIST_USERS').update({"type_id": customer_type.id,
                                                                   "action_group_id": action_group_user.id})
        session.query(Action).filter_by(name='CREATE_USER').update({"type_id": customer_type.id,
                                                                    "action_group_id": action_group_user.id})
        session.query(Action).filter_by(name='EDIT_USER_INFO').update({"type_id": customer_type.id,
                                                                       "action_group_id": action_group_user.id})
        session.query(Action).filter_by(name='ACTIVATE_USER').update({"type_id": customer_type.id,
                                                                      "action_group_id": action_group_user.id})
        session.query(Action).filter_by(name='DELETE_USER').update({"type_id": customer_type.id,
                                                                    "action_group_id": action_group_user.id})
        session.query(Action).filter_by(name='RESET_USER_PASSWORD').update({"type_id": customer_type.id,
                                                                            "action_group_id": action_group_user.id})

        session.query(Action).filter_by(name='ASSIGN_USER').update({"type_id": customer_type.id,
                                                                    "action_group_id": action_group_assignment.id})
        session.query(Action).filter_by(name='ASSIGN_SELF').update({"type_id": customer_type.id,
                                                                    "action_group_id": action_group_assignment.id})

        session.query(Action).filter_by(name='LIST_ROLES').update({"type_id": customer_type.id,
                                                                   "action_group_id": action_group_role.id})
        session.query(Action).filter_by(name='EDIT_ROLES').update({"type_id": customer_type.id,
                                                                   "action_group_id": action_group_role.id})
        session.query(Action).filter_by(name='EDIT_OWN_ROLES').update({"type_id": customer_type.id,
                                                                       "action_group_id": action_group_role.id})
        session.query(Action).filter_by(name='DELETE_ROLE').update({"type_id": customer_type.id,
                                                                    "action_group_id": action_group_role.id})
        session.query(Action).filter_by(name='CREATE_ROLE').update({"type_id": customer_type.id,
                                                                    "action_group_id": action_group_role.id})

        session.query(Action).filter_by(name='EDIT_SUBLEVEL_ROLES').update({"type_id": partner_type.id,
                                                                            "action_group_id": action_group_role.id})
        session.query(Action).filter_by(name='DELETE_SUBLEVEL_ROLE').update({"type_id": partner_type.id,
                                                                             "action_group_id": action_group_role.id})

        session.query(Action).filter_by(name='ADMIN').update({"type_id": root_type.id,
                                                              "action_group_id": action_group_admin.id})
        session.query(Action).filter_by(name='CREATE_DRPLAN').update({"type_id": customer_type.id,
                                                                      "action_group_id": action_group_drplan.id})
        session.query(Action).filter_by(name='UPDATE_DRPLAN').update({"type_id": customer_type.id,
                                                                      "action_group_id": action_group_drplan.id})
        session.query(Action).filter_by(name='DELETE_DRPLAN').update({"type_id": customer_type.id,
                                                                      "action_group_id": action_group_drplan.id})
        session.query(Action).filter_by(name='LIST_DRPLANS').update({"type_id": customer_type.id,
                                                                     "action_group_id": action_group_drplan.id})
        session.query(Action).filter_by(name='GENERATE_DRPLAN').update({"type_id": customer_type.id,
                                                                        "action_group_id": action_group_drplan.id})

        op.alter_column(
            table_name='action_group',
            column_name='name',
            nullable=False,
            type_=VARCHAR(length=24)
        )

        session.commit()
    finally:
        session.close()
        # ### end Alembic commands ###
