""""created_model"

Revision ID: 8fda986dfc7d
Revises: e6c4471a6224
Create Date: 2017-04-18 15:13:36.362731

"""

import json
import uuid
import string
import random
from datetime import datetime

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import (Column, String, Integer, ForeignKey, TEXT)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Session

from auth.auth_server.models.exceptions import InvalidTreeException
from auth.auth_server.utils import as_dict, ModelEncoder

# revision identifiers, used by Alembic.
revision = '8fda986dfc7d'
down_revision = 'e6c4471a6224'
branch_labels = None
depends_on = None


def gen_id():
    return str(uuid.uuid4())


def gen_salt():
    return ''.join(random.choice(string.ascii_lowercase + string.digits)
                   for _ in range(20))


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

    def __init__(self, id=None, name=None, parent=None):
        self.id = id
        self.name = name
        self.parent = parent

    def append(self, node_name):
        self.children[node_name] = Type(node_name, parent=self)

    def __repr__(self):
        return "Type(name=%r, id=%r, parent_id=%r)" % (self.name, self.id,
                                                       self.parent_id)


class User(Base, BaseMixin):

    __tablename__ = 'user'

    name = Column(String(256), nullable=False, index=True, unique=True)
    type_id = Column(Integer, ForeignKey('type.id'), nullable=False)
    email = Column(String(256), nullable=False, unique=True, index=True)
    password = Column(String(20), nullable=False)
    salt = Column(String(20), nullable=False)
    scope_id = Column(String(36), index=True, nullable=True)
    type = relationship("Type", backref="users")

    def __init__(self, name=None, type=None, email=None, password=None,
                 salt=None, scope_id=None, type_id=None):
        self.name = name
        if type:
            self.type = type
        if type_id is not None:
            self.type_id = type_id
        self.email = email
        self.password = password
        self.salt = salt if salt else gen_salt()
        self.scope_id = scope_id
        self.roles = []

    def __repr__(self):
        return '<User %s>' % self.name


class Role(Base, BaseIntKeyMixin):

    __tablename__ = 'role'

    name = Column(String(64), index=True, nullable=False, unique=True)
    description = Column(TEXT, nullable=True)
    type_id = Column(Integer, ForeignKey('type.id'), nullable=False)
    actions = relationship("Action", secondary="role_action",
                           viewonly=True)
    type = relationship("Type", backref="roles")

    def assign_action(self, action):
        self.role_action.append(RoleAction(role=self, action=action))

    def __init__(self, name=None, type=None, description=None):
        self.name = name
        self.type = type
        self.description = description
        self.users = []

    def __repr__(self):
        return '<Role %s (type: %s) >' % (self.name, self.type.name)


class Action(BaseIntKeyMixin, Base):
    __tablename__ = 'action'

    name = Column(String(64), index=True, nullable=False, unique=True)
    type_id = Column(Integer, ForeignKey('type.id'))
    type = relationship("Type", backref='actions')
    roles = relationship("Role", secondary="role_action",
                         viewonly=True)

    def __init__(self, name=None, type=None):
        self.name = name
        self.type = type
        self.roles = []

    def __repr__(self):
        return '<Action %s>' % self.name


class RoleAction(Base):
    __tablename__ = 'role_action'

    id = Column(String(36), default=gen_id, primary_key=True,
                unique=True)
    role_id = Column(Integer, ForeignKey('role.id'), primary_key=True)
    action_id = Column(Integer, ForeignKey('action.id'),
                       primary_key=True)

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


class Assignment(Base, BaseMixin):

    __tablename__ = 'assignment'

    id = Column(String(36), default=gen_id, primary_key=True, unique=True)
    type_id = Column(Integer, ForeignKey('type.id'), nullable=False)
    role_id = Column(Integer, ForeignKey('role.id'), nullable=False)
    user_id = Column(String(36), ForeignKey('user.id'), nullable=False)
    resource_id = Column(String(36), index=True, nullable=True)
    user = relationship("User", backref='assignments')
    role = relationship("Role", backref='assignments')
    type = relationship("Type", backref='assignments')

    def __init__(self, user=None, role=None, type=None, resource_id=None):
        self.user = user
        self.role = role
        self.type = type
        self.resource_id = resource_id

    def __repr__(self):
        return '<Assignment type: %s user: %s role: %s resource: %s>' % (
            self.type.name, self.user.name, self.role.name, self.resource_id)


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.Integer(), nullable=False),
    sa.Column('deleted_at', sa.Integer(), nullable=False),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=24), nullable=False),
    sa.ForeignKeyConstraint(['parent_id'], ['type.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_type_name'), 'type', ['name'], unique=True)
    op.create_table('action',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.Integer(), nullable=False),
    sa.Column('deleted_at', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('type_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['type_id'], ['type.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_action_name'), 'action', ['name'], unique=True)
    op.create_table('role',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.Integer(), nullable=False),
    sa.Column('deleted_at', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('description', sa.TEXT(), nullable=True),
    sa.Column('type_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['type_id'], ['type.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_role_name'), 'role', ['name'], unique=True)
    op.create_table('user',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('created_at', sa.Integer(), nullable=False),
    sa.Column('deleted_at', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=False),
    sa.Column('type_id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=256), nullable=False),
    sa.Column('password', sa.String(length=20), nullable=False),
    sa.Column('salt', sa.String(length=20), nullable=False),
    sa.Column('scope_id', sa.String(length=36), nullable=True),
    sa.ForeignKeyConstraint(['type_id'], ['type.id'], ),
    sa.PrimaryKeyConstraint('id'), mysql_row_format='DYNAMIC')
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_name'), 'user', ['name'], unique=True)
    op.create_index(op.f('ix_user_scope_id'), 'user', ['scope_id'],
                    unique=False)
    op.create_table('assignment',
    sa.Column('created_at', sa.Integer(), nullable=False),
    sa.Column('deleted_at', sa.Integer(), nullable=False),
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('type_id', sa.Integer(), nullable=False),
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('resource_id', sa.String(length=36), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['role.id'], ),
    sa.ForeignKeyConstraint(['type_id'], ['type.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_index(op.f('ix_assignment_resource_id'), 'assignment',
                    ['resource_id'], unique=False)
    op.create_table('role_action',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.Column('action_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['action_id'], ['action.id'], ),
    sa.ForeignKeyConstraint(['role_id'], ['role.id'], ),
    sa.PrimaryKeyConstraint('id', 'role_id', 'action_id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('token',
    sa.Column('token', sa.String(length=150), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
    sa.Column('valid_until', sa.TIMESTAMP(), nullable=False),
    sa.Column('ip', sa.String(length=39), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('token')
    )
    op.create_index(op.f('ix_token_valid_until'), 'token', ['valid_until'],
                    unique=False)
    # ### end Alembic commands ###

    # Data migration
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        type_root = Type(name='root')
        type_partner = Type(name='partner', parent=type_root)
        type_customer = Type(name='customer', parent=type_partner)
        type_group = Type(name='group', parent=type_customer)
        action_admin = Action(name='ADMIN', type=type_group)
        action_create_drplan = Action(name='CREATE_DRPLAN', type=type_customer)
        action_update_drplan = Action(name='UPDATE_DRPLAN', type=type_customer)
        action_delete_drplan = Action(name='DELETE_DRPLAN', type=type_customer)
        action_list_drplan = Action(name='LIST_DRPLAN', type=type_customer)
        action_generate_drplan = Action(name='GENERATE_DRPLAN',
                                        type=type_customer)
        role_admin = Role(name='Super Admin', type=type_root,
                          description='Hystax Admin')
        role_drplan_operator = Role(name='Drplan Operator', type=type_customer,
                                    description='DR plan operator')
        # TODO: change password to salted (outside of the POC scope)
        user_root = User('root', type_root, 'root@hystax.com', 'p@ssw0rd',
                         scope_id=None)
        assignment_root = Assignment(user_root, role_admin, type_root, None)
        session.add(type_root)
        session.add(type_partner)
        session.add(type_group)
        session.add(action_admin)
        session.add(action_create_drplan)
        session.add(action_update_drplan)
        session.add(action_delete_drplan)
        session.add(action_list_drplan)
        session.add(action_generate_drplan)
        session.add(role_admin)
        session.add(role_drplan_operator)
        role_admin.assign_action(action_admin)
        role_drplan_operator.assign_action(action_create_drplan)
        role_drplan_operator.assign_action(action_update_drplan)
        role_drplan_operator.assign_action(action_delete_drplan)
        role_drplan_operator.assign_action(action_list_drplan)
        role_drplan_operator.assign_action(action_generate_drplan)
        session.add(user_root)
        session.add(assignment_root)
        session.commit()
    finally:
        session.close()


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_token_valid_until'), table_name='token')
    op.drop_table('token')
    op.drop_table('role_action')
    op.drop_index(op.f('ix_assignment_resource_id'), table_name='assignment')
    op.drop_table('assignment')
    op.drop_index(op.f('ix_user_scope_id'), table_name='user')
    op.drop_index(op.f('ix_user_name'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_index(op.f('ix_role_name'), table_name='role')
    op.drop_table('role')
    op.drop_index(op.f('ix_action_name'), table_name='action')
    op.drop_table('action')
    op.drop_index(op.f('ix_type_name'), table_name='type')
    op.drop_table('type')
    # ### end Alembic commands ###
