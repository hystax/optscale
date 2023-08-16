import requests
import tornado.web


from tools.optscale_exceptions.common_exc import OptException


class OptHTTPError(tornado.web.HTTPError):
    def __init__(self, status_code, error_code, params):
        """
        Creates a new OptScale HTTP error

        :type status_code: int
        :type error_code: Enum
        :type params: list
        """
        reason = error_code.value[0]
        reason = reason % tuple(params)
        base_params = [status_code, None, *params]
        super().__init__(*base_params, reason=reason)
        self.error_code = error_code.name
        self.reason = reason
        self.params = params

    @classmethod
    def from_opt_exception(cls, status_code, opt_exception):
        """
        Creates a new OptScale HTTP error from provided OptScale exception

        :type status_code: int
        :type opt_exception: OptException
        :rtype: OptHTTPError
        """
        return cls(status_code, opt_exception.err_code,
                   opt_exception.params)


def handle503(f):
    def wrapped(*args, **kwargs):
        try:
            result = f(*args, **kwargs)
        except requests.exceptions.HTTPError as exc:
            if exc.response.status_code == 503:
                raise tornado.web.HTTPError(503, reason='Service Unavailable')
            raise
        return result

    return wrapped
