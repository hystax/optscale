from herald_server.models.enums import ReactionTypes
from herald_server.processors.email import EmailProcessor
from herald_server.processors.sms import SmsProcessor


class ProcessorFactory:
    processors = {
        ReactionTypes.EMAIL: EmailProcessor,
        ReactionTypes.SMS: SmsProcessor
    }

    @classmethod
    def get(cls, reaction_type):
        return cls.processors.get(reaction_type)
