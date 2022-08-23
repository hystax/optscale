import enum


class ReactionTypes(enum.Enum):
    EMAIL = "EMAIL"
    SMS = "SMS"
    HTTP_CALLBACK = "HTTP_CALLBACK"
