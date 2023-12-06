import json
import datetime
import pytz
from cryptography.fernet import Fernet
from sqlalchemy import (Integer, String, TypeDecorator, TEXT, LargeBinary,
                        Boolean, Enum, BigInteger, Float as FloatAlchemy)

from tools.cloud_adapter.model import ResourceTypes
from tools.optscale_exceptions.common_exc import WrongArgumentsException
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.models.enums import (
    CloudTypes, AssignmentRequestStatuses,
    ImportStates, RolePurposes, ThresholdTypes, ConditionTypes,
    ThresholdBasedTypes, ConstraintTypes, PoolPurposes,
    InviteAssignmentScopeTypes, CostModelTypes, WebhookObjectTypes,
    WebhookActionTypes, ConstraintLimitStates, OrganizationConstraintTypes,
    BIOrganizationStatuses, BITypes, GeminiStatuses)
from rest_api.rest_api_server.utils import (
    is_email_format, is_uuid, is_valid_meta, MAX_32_INT,
    get_encryption_key, gen_id, MAX_64_INT,
    raise_invalid_argument_exception, raise_not_provided_exception)


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
                if min_length == 0:
                    count = 'max %s' % max_length
                elif max_length == min_length:
                    count = max_length
                else:
                    count = '%s-%s' % (min_length, max_length)
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


class CloudResourceId(BaseString):
    impl = String(512)

    def validator(self, value, max_length=512, min_length=1):
        super().validator(value, max_length=max_length, min_length=min_length)
        return value


class NotWhiteSpaceString(BaseString):

    def validator(self, value, max_length=255, min_length=1):
        """Provides a validator/converter for @validates usage."""
        super().validator(value, max_length=max_length, min_length=min_length)
        if value.isspace():
            raise WrongArgumentsException(Err.OE0416, [self.key])
        return value


class HMTimeString(BaseString):
    """Class for saving time as string in format 'HH:MM'"""
    impl = String(5)

    def validator(self, value, max_length=5, min_length=5):
        if value is None:
            raise_not_provided_exception(self.key)
        try:
            datetime.datetime.strptime(value, "%H:%M").time()
        except (TypeError, ValueError):
            raise WrongArgumentsException(Err.OE0550, [self.key])
        return value


class TimezoneString(BaseString):
    """Class for saving timezone names"""
    impl = String(32)

    def validator(self, value, max_length=32, min_length=1):
        super().validator(value, max_length=max_length, min_length=min_length)
        if value not in pytz.all_timezones:
            raise WrongArgumentsException(Err.OE0553, [self.key])
        return value


class SmallNullableString(NullableString):
    impl = String(36)

    def validator(self, value, max_length=36, min_length=1):
        """Provides a validator/converter for @validates usage."""
        if value is not None:
            super().validator(value, max_length=max_length, min_length=min_length)
        return value


class MediumNullableString(NullableString):
    impl = String(60)

    def validator(self, value, max_length=60, min_length=1):
        """Provides a validator/converter for @validates usage."""
        if value is not None:
            super().validator(value, max_length=60, min_length=1)
        return value


class MediumString(MediumNullableString):
    def validator(self, value, max_length=60, min_length=1):
        if value is None:
            raise_not_provided_exception(self.key)
        return super().validator(value, max_length, min_length)


class MediumLargeNullableString(NullableString):
    impl = String(128)

    def validator(self, value, max_length=128, min_length=1):
        """Provides a validator/converter for @validates usage."""
        if value is not None:
            super().validator(value, max_length=128, min_length=1)
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


class NullableEmail(NullableString):
    def __init__(self, key='email', **kwargs):
        super().__init__(key, **kwargs)

    def validator(self, value):
        super().validator(value)
        if value is not None and not is_email_format(value):
            raise WrongArgumentsException(Err.OE0218, [self.key, value])
        return value


class Email(NullableEmail):
    def __init__(self, key='email', **kwargs):
        super().__init__(key, **kwargs)

    def validator(self, value):
        if value is None:
            raise_not_provided_exception(self.key)
        super().validator(value)
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


class NullableJSON(JSON):
    def __init__(self, key='json', **kwargs):
        super().__init__(key, **kwargs)

    def validator(self, value):
        if value is not None:
            super().validator(value)
        return value


class NullableMetadata(NullableJSON):
    def __init__(self, key='meta', **kwargs):
        super().__init__(key, **kwargs)


class SerializableNullableJSON(JSON):
    def __init__(self, key='json', **kwargs):
        super().__init__(key, **kwargs)

    def validator(self, value):
        if value is not None:
            if isinstance(value, dict):
                value = json.dumps(value)
            super().validator(value)
        else:
            value = '{}'
        return value


class ConstraintDefinition(JSON):
    def __init__(self, key='definition', **kwargs):
        super().__init__(key, **kwargs)

    def validator(self, value):
        if value is not None:
            if isinstance(value, dict):
                value = json.dumps(value)
            super().validator(value)
        else:
            raise WrongArgumentsException(Err.OE0216, [self.key])
        return value


class RunResult(SerializableNullableJSON):
    def __init__(self, key='run_result', **kwargs):
        super().__init__(key, **kwargs)

    def validator(self, value):
        if value is not None:
            if not isinstance(value, dict):
                raise WrongArgumentsException(Err.OE0344, [self.key])
        else:
            value = {}
        return super().validator(value)


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
                raise WrongArgumentsException(Err.OE0287, [str(exc)])
        return res


class BaseState(BaseEnum):
    def __init__(self, key='state', **kwargs):
        super().__init__(key, **kwargs)


class CachedResourceType(BaseEnum):
    impl = Enum(ResourceTypes)

    def __init__(self, key='resource_type', **kwargs):
        self.key = key
        super().__init__(key, **kwargs)

    def validator(self, value):
        if not value:
            raise WrongArgumentsException(Err.OE0216, [self.key])
        try:
            res_type = value
            if isinstance(value, str):
                res_type = ResourceTypes[value]
            res = self.impl.enum_class(res_type)
        except (ValueError, KeyError):
            raise WrongArgumentsException(Err.OE0384, [value])
        return res


class BaseType(BaseEnum):
    def __init__(self, key='type', **kwargs):
        super().__init__(key, **kwargs)


class CloudType(BaseType):
    impl = Enum(CloudTypes)


class ImportState(BaseType):
    impl = Enum(ImportStates)


class RolePurpose(BaseType):
    impl = Enum(RolePurposes)


class AssignmentRequestStatus(BaseType):
    impl = Enum(AssignmentRequestStatuses)


class ConditionType(BaseType):
    impl = Enum(ConditionTypes)


class CostModelType(BaseType):
    impl = Enum(CostModelTypes)


class InviteAssignmentScopeType(BaseType):
    impl = Enum(InviteAssignmentScopeTypes)


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


class NullableFloat(TypeDecorator):
    impl = FloatAlchemy

    def __init__(self, key='', **kwargs):
        self.key = key
        super().__init__(**kwargs)

    def validator(self, value, max_int_value=MAX_32_INT):
        if value is not None:
            if not isinstance(value, float) and not isinstance(value, int):
                raise WrongArgumentsException(Err.OE0466, [self.key])
            if not max_int_value >= value >= 0:
                raise WrongArgumentsException(
                    Err.OE0224, [self.key, 0, max_int_value])
        return value


class Float(NullableFloat):
    def validator(self, value, max_int_value=MAX_32_INT):
        if value is None:
            raise_not_provided_exception(self.key)
        super().validator(value, max_int_value)
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


class Password(BaseString):
    impl = LargeBinary

    def __init__(self, key='password', **kwargs):
        super().__init__(key, **kwargs)

    @staticmethod
    def _encrypt_password(password, salt):
        fernet = Fernet(get_encryption_key())
        return fernet.encrypt((password + salt).encode())

    def validator(self, salt, value):
        super().validator(value)
        value = self._encrypt_password(value, salt)
        return value


class NullablePassword(Password):
    def validator(self, salt, value):
        if value is not None:
            value = super().validator(salt, value)
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


class ThresholdType(BaseType):
    impl = Enum(ThresholdTypes)


class ThresholdBasedType(BaseType):
    impl = Enum(ThresholdBasedTypes)


class ConstraintType(BaseType):
    impl = Enum(ConstraintTypes)


class ConstraintLimitState(BaseType):
    impl = Enum(ConstraintLimitStates)


class OrganizationConstraintType(BaseType):
    impl = Enum(OrganizationConstraintTypes)


class PoolPurpose(BaseType):
    impl = Enum(PoolPurposes)


class WebhookObjectType(BaseEnum):
    impl = Enum(WebhookObjectTypes)


class WebhookActionType(BaseEnum):
    impl = Enum(WebhookActionTypes)


class BIType(BaseType):
    impl = Enum(BITypes)


class BIOrganizationStatus(BaseType):
    impl = Enum(BIOrganizationStatuses)


class GeminiStatus(BaseType):
    impl = Enum(GeminiStatuses)
