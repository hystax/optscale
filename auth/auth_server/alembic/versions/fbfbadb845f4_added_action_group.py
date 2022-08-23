""""added_action_group"

Revision ID: fbfbadb845f4
Revises: 3481a6b2731b
Create Date: 2017-05-22 17:38:54.680880

"""
import json
import uuid
from datetime import datetime
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy.orm import Session
from sqlalchemy import select, update
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import (Column, String, Integer, ForeignKey, TEXT, Boolean)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, backref

from auth_server.utils import as_dict, ModelEncoder
from auth_server.models.exceptions import InvalidTreeException

# revision identifiers, used by Alembic.
revision = 'fbfbadb845f4'
down_revision = '3481a6b2731b'
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

    op.create_table('action_group',
    sa.Column('created_at', sa.Integer(), nullable=False),
    sa.Column('deleted_at', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('order', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=24), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_action_group_name'), 'action_group', ['name'],
                    unique=True)

    op.add_column('action', sa.Column('action_group_id', sa.Integer(),
                                      nullable=False))
    op.add_column('action', sa.Column('order', sa.Integer(), nullable=False))

    bind = op.get_bind()
    session = Session(bind=bind)

    action_group_admin = ActionGroup(name='admin', order=100)
    action_group_drplan = ActionGroup(name='dr_plan', order=500)
    session.add(action_group_admin)
    session.add(action_group_drplan)
    try:
        session.commit()
    except:
        session.close()
        raise
    action_group_admin_id = action_group_admin.id
    action_group_drplan_id = action_group_drplan.id

    type_table = table('type',
                       column('name', String(24)),
                       column('id', Integer))

    rt_id_stmt = select([type_table.c.id]).where(type_table.c.name == 'root')
    root_type_id = session.execute(rt_id_stmt).scalar()
    action_table = table('action',
                         column('name', String(64)),
                         column('id', Integer),
                         column('type_id', Integer),
                         column('action_group_id', Integer))

    # admin action should be root type
    update_admin_action = update(action_table).where(
        action_table.c.name == 'ADMIN').values(type_id=root_type_id)
    update_list_drplan = update(action_table).where(
        action_table.c.name == 'LIST_DRPLAN').values(name='LIST_DRPLANS')

    # update action action with drplan action groups
    update_action_type_drplan = update(action_table).values(
        action_group_id=action_group_drplan_id)

    # update admin action with admin action group
    update_action_type_admin = update(action_table).where(
        action_table.c.name == 'ADMIN').values(
        action_group_id=action_group_admin_id)
    try:
        session.execute(update_admin_action)
        session.execute(update_list_drplan)
        session.execute(update_action_type_drplan)
        session.execute(update_action_type_admin)
        session.commit()
    finally:
        session.close()

    op.create_foreign_key('action_type_ibfk_2', 'action', 'action_group',
                          ['action_group_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():

    type_table = table('type',
                       column('name', String(24)),
                       column('id', Integer))

    bind = op.get_bind()
    session = Session(bind=bind)

    gt_id_stmt = select([type_table.c.id]).where(type_table.c.name == 'group')
    group_type_id = session.execute(gt_id_stmt).scalar()
    action_table = table('action',
                         column('name', String(64)),
                         column('id', Integer),
                         column('type_id', Integer))

    # admin action should be group
    update_admin_action = update(action_table).where(
        action_table.c.name == 'ADMIN').values(type_id=group_type_id)
    update_list_drplan = update(action_table).where(
        action_table.c.name == 'LIST_DRPLANS').values(name='LIST_DRPLAN')
    try:
        session.execute(update_admin_action)
        session.execute(update_list_drplan)
        session.commit()
    finally:
        session.close()

    op.drop_constraint('action_type_ibfk_2', 'action', type_='foreignkey')
    op.drop_column('action', 'order')
    op.drop_column('action', 'action_group_id')
    op.drop_index(op.f('ix_action_group_name'), table_name='action_group')
    op.drop_table('action_group')
    ### end Alembic commands ###
