from herald.herald_server.processors.base import BaseProcessor

from tools.optscale_exceptions.common_exc import WrongArgumentsException


class SmsProcessor(BaseProcessor):

    @staticmethod
    def validate_payload(payload):
        if 'phone' not in payload:
            raise WrongArgumentsException(
                'G0022',
                'must provide phone number in payload for reaction "sms"', [])
