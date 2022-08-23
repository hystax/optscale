class AzurePartnerException(Exception):
    pass


class AzurePartnerConnectionException(AzurePartnerException):
    pass


class AzurePartnerHttpException(AzurePartnerException):
    def __init__(self, error_message, error_codes, status_code):
        super().__init__(error_message)
        self._error_codes = error_codes
        self._status_code = status_code

    @property
    def error_codes(self):
        return self._error_codes

    @property
    def status_code(self):
        return self._status_code


class AzurePartnerAuthException(AzurePartnerHttpException):
    pass


class AzurePartnerApiException(AzurePartnerHttpException):
    pass
