""""action_group_literal"

Revision ID: 481dbdfd5d18
Revises: 3a5a296318db
Create Date: 2017-06-21 17:39:29.043752

"""
import json
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import Session
from sqlalchemy.ext.hybrid import hybrid_property
from alembic import op
import sqlalchemy as sa

from auth.auth_server.utils import as_dict, ModelEncoder

# revision identifiers, used by Alembic.
revision = '481dbdfd5d18'
down_revision = '3a5a296318db'
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


class ActionGroup(BaseIntKeyMixin, Base, OrderMixin):

    __tablename__ = 'action_group'

    name = Column(String(24), index=True, nullable=False, unique=True)

    def __init__(self, name=None, order=0):
        self.name = name
        self.order = order

    def __repr__(self):
        return '<ActionGroup %s>' % self.name

action_group_map = (
    ('Manage users and assignments', 'MANAGE_ASSIGNMENTS'),
    ('Manage user roles', 'MANAGE_ROLES'),
    ('Manage customers', 'MANAGE_CUSTOMERS'),
    ('Manage Disaster Recovery plans', 'MANAGE_DRPLANS'),
    ('Manage Cloud Sites', 'MANAGE_CLOUDSITES'),
    ('Manage device groups and replication settings', 'MANAGE_REPLICATION'),
    ('Manage partners', 'MANAGE_PARTNERS')
)


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        for ag in action_group_map:
            key, new_key = ag
            action_group = session.query(ActionGroup).filter_by(
                name=key).one_or_none()
            action_group.name = new_key
            session.add(action_group)
        session.commit()
    finally:
        session.close()


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        for ag in action_group_map:
            key, new_key = ag
            action_group = session.query(ActionGroup).filter_by(
                name=new_key).one_or_none()
            action_group.name = key
            session.add(action_group)
        session.commit()
    finally:
        session.close()
