from herald.herald_server.processors.base import BaseProcessor
from herald.herald_server.exceptions import Err
from tools.optscale_exceptions.common_exc import WrongArgumentsException


class SmsProcessor(BaseProcessor):

    @staticmethod
    def validate_payload(payload):
        if 'phone' not in payload:
            raise WrongArgumentsException(Err.G0022, [])
