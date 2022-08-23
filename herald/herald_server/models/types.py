from optscale_types.base_types import BaseType
from herald_server.models.enums import ReactionTypes
from sqlalchemy import Enum


class ReactionType(BaseType):
    impl = Enum(ReactionTypes)
