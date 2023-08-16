""""removed_acura_actions"

Revision ID: d0609ecf1e68
Revises: b21c7712ec21
Create Date: 2020-09-04 03:12:04.028982

"""
import json
import uuid
from datetime import datetime
from alembic import op
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import (
    Column, String, Integer, ForeignKey, TEXT, Boolean, VARCHAR, and_)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, backref

from auth.auth_server.utils import as_dict, ModelEncoder
from auth.auth_server.models.exceptions import InvalidTreeException


# revision identifiers, used by Alembic.
revision = 'd0609ecf1e68'
down_revision = 'b21c7712ec21'
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
                 action_group_id=None, order=0, deleted=False):
        if action_group:
            self.action_group = action_group
        if action_group_id is not None:
            self.action_group_id = action_group_id
        self.name = name
        self.type = type
        self.order = order
        self.roles = []
        if deleted:
            self.deleted_at = int(datetime.utcnow().timestamp())

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


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        action_group_names = [
            'MANAGE_FAILBACKS', 'MANAGE_REPLICATION',
            'MANAGE_CLOUDSITES', 'MANAGE_DRPLANS',
            'MANAGE_CUSTOMERS']
        action_groups = session.query(ActionGroup).filter(
            and_(
                ActionGroup.name.in_(action_group_names)
            )
        ).all()
        action_group_ids = list(map(lambda x: x.id, action_groups))

        actions = session.query(Action).filter(
            Action.action_group_id.in_(action_group_ids)
        ).all()
        action_ids = list(map(lambda x: x.id, actions))

        session.query(RoleAction).filter(
            RoleAction.action_id.in_(action_ids)
        ).delete(synchronize_session=False)
        session.query(Action).filter(
            Action.id.in_(action_ids)
        ).delete(synchronize_session=False)
        session.query(ActionGroup).filter(
            ActionGroup.id.in_(action_group_ids)
        ).delete(synchronize_session=False)
        session.commit()
    finally:
        session.close()


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        action_groups = [
            ActionGroup(name='MANAGE_CUSTOMERS', order=400),
            ActionGroup(name='MANAGE_DRPLANS', order=500),
            ActionGroup(name='MANAGE_CLOUDSITES', order=600),
            ActionGroup(name='MANAGE_REPLICATION', order=700),
            ActionGroup(name='MANAGE_FAILBACKS', order=1100)
        ]
        action_groups = {ag.name: ag for ag in action_groups}

        types = session.query(Type).filter(
            Type.deleted.is_(False)
        ).all()
        types = {t.name: t for t in types}

        actions = {
            'MANAGE_CUSTOMERS': [
                Action(name='INFO_CUSTOMER', type=types.get('customer'), order=410,
                       action_group=action_groups.get('MANAGE_CUSTOMERS')),
                Action(name='CREATE_CUSTOMER', type=types.get('partner'), order=420,
                       action_group=action_groups.get('MANAGE_CUSTOMERS')),
                Action(name='EDIT_CUSTOMER_INFO', type=types.get('customer'), order=430,
                       action_group=action_groups.get('MANAGE_CUSTOMERS')),
                Action(name='ACTIVATE_CUSTOMER', type=types.get('partner'), order=440,
                       action_group=action_groups.get('MANAGE_CUSTOMERS')),
                Action(name='DELETE_CUSTOMER', type=types.get('partner'), order=450,
                       action_group=action_groups.get('MANAGE_CUSTOMERS')),
            ],
            'MANAGE_DRPLANS': [
                Action(name='CREATE_DRPLAN', type=types.get('customer'), order=520,
                       action_group=action_groups.get('MANAGE_DRPLANS')),
                Action(name='GENERATE_DRPLAN', type=types.get('customer'), order=530,
                       action_group=action_groups.get('MANAGE_DRPLANS'), deleted=True),
                Action(name='INFO_DRPLAN', type=types.get('customer'), order=510,
                       action_group=action_groups.get('MANAGE_DRPLANS')),
                Action(name='DELETE_DRPLAN', type=types.get('customer'), order=550,
                       action_group=action_groups.get('MANAGE_DRPLANS')),
                Action(name='EDIT_DRPLAN', type=types.get('customer'), order=540,
                       action_group=action_groups.get('MANAGE_DRPLANS')),
                Action(name='MANAGE_SCRIPTS', type=types.get('customer'), order=560,
                       action_group=action_groups.get('MANAGE_DRPLANS')),
            ],
            'MANAGE_CLOUDSITES': [
                Action(name='EDIT_CS', type=types.get('customer'), order=630,
                       action_group=action_groups.get('MANAGE_CLOUDSITES')),
                Action(name='DELETE_CS', type=types.get('partner'), order=640,
                       action_group=action_groups.get('MANAGE_CLOUDSITES')),
                Action(name='INFO_CS', type=types.get('customer'), order=610,
                       action_group=action_groups.get('MANAGE_CLOUDSITES')),
                Action(name='CREATE_CS', type=types.get('partner'), order=620,
                       action_group=action_groups.get('MANAGE_CLOUDSITES')),
            ],
            'MANAGE_REPLICATION': [
                Action(name='EDIT_REPLICATION_STATE', type=types.get('group'), order=730,
                       action_group=action_groups.get('MANAGE_REPLICATION')),
                Action(name='MANAGE_DEVICE', type=types.get('group'), order=705,
                       action_group=action_groups.get('MANAGE_REPLICATION')),
                Action(name='EDIT_GROUP', type=types.get('customer'), order=720,
                       action_group=action_groups.get('MANAGE_REPLICATION')),
                Action(name='EDIT_RETENTION', type=types.get('group'), order=740,
                       action_group=action_groups.get('MANAGE_REPLICATION')),
                Action(name='DOWNLOAD_AGENT', type=types.get('customer'), order=770,
                       action_group=action_groups.get('MANAGE_REPLICATION')),
                Action(name='MANAGE_VSPHERE_CREDENTIALS', type=types.get('customer'), order=760,
                       action_group=action_groups.get('MANAGE_REPLICATION'), deleted=True),
                Action(name='CREATE_GROUP', type=types.get('customer'), order=710,
                       action_group=action_groups.get('MANAGE_REPLICATION')),
                Action(name='EDIT_SCHEDULE', type=types.get('group'), order=750,
                       action_group=action_groups.get('MANAGE_REPLICATION')),
            ],
            'MANAGE_FAILBACKS': [
                Action(name='MANAGE_FAILBACK', type=types.get('customer'), order=1110,
                       action_group=action_groups.get('MANAGE_FAILBACKS')),
            ]
        }
        action_roles = {
            'INFO_CUSTOMER': ['Super Admin', 'Manager', 'Engineer', 'Member'],
            'CREATE_CUSTOMER': ['Super Admin', 'Manager'],
            'EDIT_CUSTOMER_INFO': ['Super Admin', 'Manager'],
            'ACTIVATE_CUSTOMER': ['Super Admin', 'Manager'],
            'DELETE_CUSTOMER': ['Super Admin', 'Manager'],
            'CREATE_DRPLAN': ['Super Admin', 'Manager', 'Engineer'],
            'GENERATE_DRPLAN': ['Super Admin', 'Drplan Operator'],
            'INFO_DRPLAN': ['Super Admin', 'Manager', 'Engineer', 'Member'],
            'DELETE_DRPLAN': ['Manager', 'Super Admin', 'Engineer'],
            'EDIT_DRPLAN': ['Manager', 'Super Admin', 'Engineer', 'Drplan Operator'],
            'MANAGE_SCRIPTS': ['Manager', 'Engineer', 'Super Admin'],
            'EDIT_CS': ['Super Admin', 'Manager', 'Engineer'],
            'DELETE_CS': ['Super Admin', 'Manager', 'Engineer'],
            'INFO_CS': ['Super Admin', 'Manager', 'Engineer', 'Member'],
            'CREATE_CS': ['Manager', 'Engineer', 'Super Admin'],
            'EDIT_REPLICATION_STATE': ['Manager', 'Engineer', 'Super Admin'],
            'MANAGE_DEVICE': ['Manager', 'Engineer', 'Super Admin'],
            'EDIT_GROUP': ['Super Admin', 'Manager'],
            'EDIT_RETENTION': ['Manager', 'Engineer', 'Super Admin'],
            'DOWNLOAD_AGENT': ['Super Admin', 'Manager', 'Engineer'],
            'MANAGE_VSPHERE_CREDENTIALS': ['Super Admin'],
            'CREATE_GROUP': ['Super Admin', 'Manager'],
            'EDIT_SCHEDULE': ['Manager', 'Engineer', 'Super Admin'],
            'MANAGE_FAILBACK': ['Manager', 'Engineer', 'Super Admin']
        }
        roles = session.query(Role).all()
        roles = {r.name: r for r in roles}

        for ag_name, ag in action_groups.items():
            session.add(ag)
            for action in actions.get(ag_name, []):
                session.add(action)
                for role_name in action_roles.get(action.name, []):
                    role = roles.get(role_name)
                    if role:
                        role.assign_action(action)
        session.commit()
    finally:
        session.close()
