from datetime import datetime
import json

from sqlalchemy import Column, Integer, String, UniqueConstraint
from sqlalchemy import inspect
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.ext.hybrid import hybrid_property

from slacker.slacker_server.utils import ModelEncoder, gen_id


def get_current_timestamp():
    return int(datetime.utcnow().timestamp())


class Base(object):
    @declared_attr
    # pylint: disable=E0213
    def __tablename__(cls):
        return cls.__name__.lower()

    def to_dict(self):
        return {c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs}

    def to_json(self):
        return json.dumps(self.to_dict(), cls=ModelEncoder)


Base = declarative_base(cls=Base)


class BaseModel:
    id = Column(String(36), primary_key=True, default=gen_id)
    created_at = Column(Integer, default=get_current_timestamp, nullable=False)
    deleted_at = Column(Integer, default=0, nullable=False)

    @hybrid_property
    def deleted(self):
        return self.deleted_at != 0


class User(Base, BaseModel):
    slack_user_id = Column(String(160), index=True, nullable=False)
    auth_user_id = Column(String(36), nullable=True, index=True)
    secret = Column(String(36), nullable=False, index=True)
    slack_channel_id = Column(String(160), nullable=False)
    organization_id = Column(String(36), nullable=True)
    employee_id = Column(String(36), nullable=True)
    slack_team_id = Column(String(160), nullable=False)

    __table_args__ = (UniqueConstraint(
        'slack_user_id', 'deleted_at',
        name='uc_slack_user_id_deleted_at'),)
