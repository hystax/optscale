import json

from optscale_exceptions.common_exc import WrongArgumentsException

from herald_server.processors.base import BaseProcessor


class SmsProcessor(BaseProcessor):

    @staticmethod
    def validate_payload(payload):
        if 'phone' not in payload:
            raise WrongArgumentsException(
                'G0022',
                'must provide phone number in payload for reaction "sms"', [])
