from sqlalchemy import (Integer, String, TypeDecorator, TEXT, Boolean,
                        BigInteger)

from optscale_types.utils import (raise_not_provided_exception, is_email_format,
                                  raise_invalid_argument_exception, is_uuid,
                                  MAX_32_INT, MAX_64_INT, is_valid_hostname,
                                  check_ipv4_addr, is_valid_meta, gen_id)
from optscale_types.errors import Err

from optscale_exceptions.common_exc import WrongArgumentsException


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
    def __init__(self, key='name',  **kwargs):
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
            raise WrongArgumentsException(Err.OE0219,  [self.key])
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


class BaseEnum(TypeDecorator):
    def __init__(self, key='', **kwargs):
        self.key = key
        super().__init__(**kwargs)

    def validator(self, value):
        res = None
        if value is not None:
            try:
                res = self.impl.enum_class(value)
            except ValueError as exc:
                raise WrongArgumentsException(Err.OE0004, [str(exc)])
        return res


class BaseState(BaseEnum):
    def __init__(self, key='state', **kwargs):
        super().__init__(key, **kwargs)


class BaseType(BaseEnum):
    def __init__(self, key='type', **kwargs):
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
