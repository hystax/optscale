from sqlalchemy import Enum, TypeDecorator

from herald. herald_server.models.enums import ReactionTypes
from tools.optscale_exceptions.common_exc import WrongArgumentsException
from herald.herald_server.exceptions import Err


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


class BaseType(BaseEnum):
    def __init__(self, key='type', **kwargs):
        super().__init__(key, **kwargs)


class ReactionType(BaseType):
    impl = Enum(ReactionTypes)
