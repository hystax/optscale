import enum
import json
import uuid
from sqlalchemy.ext.declarative.base import _declarative_constructor
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import (Column, String, Integer, Enum, ForeignKey)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from herald_server.utils import as_dict, ModelEncoder
from sqlalchemy.orm import validates
from optscale_types.models import ValidatorMixin
from optscale_types.base_types import (Name, Uuid, JSON, NullableString,
                                       AutogenUuid, NullableUuid)
from herald_server.models.types import ReactionType
from herald_server.models.enums import ReactionTypes
from optscale_types.utils import gen_id


def get_current_timestamp():
    return int(datetime.utcnow().timestamp())


class PermissionKeys(Enum):
    is_creatable = 'is_creatable'
    is_updatable = 'is_updatable'


class ColumnPermissions(Enum):
    full = {PermissionKeys.is_creatable: True,
            PermissionKeys.is_updatable: True}
    create_only = {PermissionKeys.is_creatable: True,
                   PermissionKeys.is_updatable: False}
    update_only = {PermissionKeys.is_creatable: False,
                   PermissionKeys.is_updatable: True}


class Base(object):
    def __init__(self, **kwargs):
        init_columns = list(filter(lambda x: x.info.get(
            PermissionKeys.is_creatable) is True, self.__table__.c))
        for col in init_columns:
            setattr(self, col.name, kwargs.get(col.name))
            kwargs.pop(col.name, None)
        _declarative_constructor(self, **kwargs)

    @declared_attr
    # pylint: disable=E0213
    def __tablename__(cls):
        # pylint: disable=E1101
        return cls.__name__.lower()

    def to_dict(self):
        return as_dict(self)

    def to_json(self):
        return json.dumps(self, cls=ModelEncoder)


Base = declarative_base(cls=Base, constructor=None)


class BaseModel(object):
    created_at = Column(Integer, default=get_current_timestamp,
                        nullable=False)
    deleted_at = Column(Integer, default=0, nullable=False)

    @hybrid_property
    def deleted(self):
        return self.deleted_at != 0


class BaseMixin(BaseModel):
    id = Column(AutogenUuid('id'), primary_key=True, default=gen_id)


class BaseIntKeyMixin(BaseModel):
    id = Column(Integer, primary_key=True, autoincrement=True)


class Notification(Base, BaseMixin, ValidatorMixin):
    name = Column(Name, nullable=False, info=ColumnPermissions.full)
    user_id = Column(Uuid('user_id'), nullable=False,
                     info=ColumnPermissions.create_only)

    reactions = relationship("Reaction", backref="notification",
                             cascade="all, delete-orphan",
                             passive_deletes=True)

    criterias = relationship("FilterCriteria", backref="notification",
                             cascade="all, delete-orphan",
                             passive_deletes=True)

    def to_dict(self):
        result = super().to_dict()
        result['reactions'] = self.reactions
        result['filter'] = ' '.join(
            ':'.join((criteria.field.name, criteria.value))
            for criteria in self.criterias)
        return result

    @validates('id')
    def _validate_id(self, key, id):
        return self.get_validator(key, id)

    @validates('name')
    def _validate_name(self, key, name):
        return self.get_validator(key, name)

    @validates('user_id')
    def _validate_user_id(self, key, user_id):
        return self.get_validator(key, user_id)


class Reaction(Base, BaseMixin, ValidatorMixin):

    notification_id = Column(NullableUuid('notification_id'),
                             ForeignKey('notification.id'),
                             info=ColumnPermissions.create_only)
    name = Column(NullableString('name'), info=ColumnPermissions.create_only)
    type = Column(ReactionType, nullable=False,
                  default=ReactionTypes.EMAIL.value,
                  info=ColumnPermissions.create_only)
    payload = Column(JSON('payload'), info=ColumnPermissions.create_only)

    @validates('id')
    def _validate_id(self, key, id):
        return self.get_validator(key, id)

    @validates('notification_id')
    def _validate_notification_id(self, key, notification_id):
        return self.get_validator(key, notification_id)

    @validates('name')
    def _validate_name(self, key, name):
        return self.get_validator(key, name)

    @validates('payload')
    def _validate_payload(self, key, payload):
        return self.get_validator(key, payload)

    @validates('type')
    def _validate_type(self, key, type):
        return self.get_validator(key, type)


class Field(Base, BaseIntKeyMixin):

    name = Column(String(256))


class FilterCriteria(Base, BaseMixin, ValidatorMixin):

    __tablename__ = 'filter_criteria'

    notification_id = Column(String(36), ForeignKey('notification.id'))
    field_id = Column(Integer, ForeignKey('field.id'))
    value = Column(String(64))

    field = relationship("Field")
