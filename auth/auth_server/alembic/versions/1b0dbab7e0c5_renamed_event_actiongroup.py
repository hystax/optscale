""""renamed_event_actiongroup"

Revision ID: 1b0dbab7e0c5
Revises: 9e311c87e269
Create Date: 2017-08-30 14:03:29.444139

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
revision = '1b0dbab7e0c5'
down_revision = '9e311c87e269'
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


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        action_group_events = session.query(ActionGroup).filter_by(
            name='EVENTS_NOTIFICATIONS').one_or_none()
        action_group_events.name = 'MANAGE_NOTIFICATIONS'
        session.add(action_group_events)
        session.commit()
    finally:
        session.close()


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        action_group_events = session.query(ActionGroup).filter_by(
            name='MANAGE_NOTIFICATIONS').one_or_none()
        action_group_events.name = 'EVENTS_NOTIFICATIONS'
        session.add(action_group_events)
        session.commit()
    finally:
        session.close()
