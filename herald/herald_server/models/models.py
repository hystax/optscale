import json
from datetime import datetime

from sqlalchemy.ext.declarative.base import _declarative_constructor
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import (
    Column,
    String,
    Integer,
    Enum,
    ForeignKey,
    TypeDecorator,
    TEXT,
    Boolean,
    BigInteger
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.orm import validates

from herald.herald_server.utils import as_dict, ModelEncoder
from herald.herald_server.models.types import ReactionType, BaseEnum
from herald.herald_server.models.enums import ReactionTypes
from herald.herald_server.exceptions import Err
from herald.herald_server.utils import (
    raise_not_provided_exception,
    is_email_format,
    raise_invalid_argument_exception,
    is_uuid,
    MAX_32_INT,
    MAX_64_INT,
    is_valid_hostname,
    check_ipv4_addr,
    is_valid_meta,
    gen_id,
)


from tools.optscale_exceptions.common_exc import WrongArgumentsException


class ValidatorMixin(object):
    def get_validator(self, key, *args, **kwargs):
        return getattr(type(self), key).type.validator(*args, **kwargs)


class NullableString(TypeDecorator):
    impl = String(256)

    def __init__(self, key='', **kwargs):
        self.key = key
        super().__init__(**kwargs)

    def validator(self, value, max_length=255, min_length=1):
        """Provides a validator/converter for @validates usage."""
        if value is not None:
            if not isinstance(value, str):
                raise WrongArgumentsException(Err.OE0214, [self.key])
            if not min_length <= len(value) <= max_length:
                count = ('max %s' % max_length if min_length == 0
                         else '%s-%s' % (min_length, max_length))
                raise WrongArgumentsException(Err.OE0215, [self.key, count])
        return value


class BaseString(NullableString):
    impl = String(256)

    def validator(self, value, max_length=255, min_length=1):
        """Provides a validator/converter for @validates usage."""
        if value is None:
            raise_not_provided_exception(self.key)
        super().validator(value, max_length=max_length, min_length=min_length)
        return value


class IpAddressString(BaseString):
    impl = String(39)


class NullableUuid(TypeDecorator):
    impl = String(36)

    def __init__(self, key='', **kwargs):
        self.key = key
        super().__init__(**kwargs)

    def validator(self, value):
        if value is not None:
            if not isinstance(value, str):
                raise WrongArgumentsException(Err.OE0214, [self.key])
            if not is_uuid(value):
                raise_invalid_argument_exception(self.key)
        return value


class Email(BaseString):
    def __init__(self, key='email', **kwargs):
        super().__init__(key, **kwargs)

    def validator(self, value):
        super().validator(value)
        if not is_email_format(value):
            raise WrongArgumentsException(Err.OE0218, [self.key, value])
        return value


class Name(BaseString):
    def __init__(self, key='name', **kwargs):
        super().__init__(key, **kwargs)


class Uuid(NullableUuid):
    def __init__(self, key='', **kwargs):
        super().__init__(key, **kwargs)

    def validator(self, value):
        if value is None:
            raise_not_provided_exception(self.key)
        super().validator(value)
        return value


class JSON(TypeDecorator):
    impl = TEXT

    def __init__(self, key='json', **kwargs):
        self.key = key
        super().__init__(**kwargs)

    def validator(self, value):
        if not is_valid_meta(value):
            raise WrongArgumentsException(Err.OE0219, [self.key])
        return value


class NullableMetadata(JSON):
    def __init__(self, key='meta', **kwargs):
        super().__init__(key, **kwargs)

    def validator(self, value):
        if value is not None:
            super().validator(value)
        return value


class NullableText(TypeDecorator):
    impl = TEXT

    def __init__(self, key='', **kwargs):
        self.key = key
        super().__init__(**kwargs)

    def validator(self, value):
        if value is not None:
            if not isinstance(value, str):
                raise WrongArgumentsException(Err.OE0214, [self.key])
        return value


class BaseText(NullableText):
    def validator(self, value):
        if value is None:
            raise_not_provided_exception(self.key)
        super().validator(value)
        return value


class BaseState(BaseEnum):
    def __init__(self, key='state', **kwargs):
        super().__init__(key, **kwargs)


class NullableInt(TypeDecorator):
    impl = Integer

    def __init__(self, key='', **kwargs):
        self.key = key
        super().__init__(**kwargs)

    def validator(self, value, max_int_value=MAX_32_INT):
        if value is not None:
            if not isinstance(value, int):
                raise WrongArgumentsException(Err.OE0223, [self.key])
            if not max_int_value >= value >= 0:
                raise WrongArgumentsException(
                    Err.OE0224, [self.key, 0, max_int_value])
        return value


class Int(NullableInt):
    def validator(self, value):
        if value is None:
            raise_not_provided_exception(self.key)
        super().validator(value)
        return value


class BigInt(NullableInt):
    impl = BigInteger

    def validator(self, value):
        super().validator(value, max_int_value=MAX_64_INT)
        return value


class Endpoint(BaseString):
    def __init__(self, key='endpoint', **kwargs):
        super().__init__(key, **kwargs)

    def validator(self, value):
        if value is None:
            raise WrongArgumentsException(Err.OE0216, [self.key])
        if not isinstance(value, str):
            raise WrongArgumentsException(Err.OE0214, [self.key])
        try:
            check_ipv4_addr(value)
        except ValueError:
            if not is_valid_hostname(value):
                raise WrongArgumentsException(Err.OE0225, [self.key])
        return value


class AutogenUuid(NullableUuid):
    def __init__(self, key='', **kwargs):
        super().__init__(key, **kwargs)

    def validator(self, value):
        if value is None:
            value = gen_id()
        super().validator(value)
        return value


class NullableBool(TypeDecorator):
    impl = Boolean

    def __init__(self, key='', **kwargs):
        self.key = key
        super().__init__(**kwargs)

    def validator(self, value):
        if value is not None:
            if not isinstance(value, bool):
                raise WrongArgumentsException(Err.OE0226, [self.key])
        return value


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
