import logging

from requests.exceptions import RequestException, HTTPError

LOG = logging.getLogger(__name__)


def _wrap_request_errors(http_exception_class):
    def decorator(func):
        def func_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except HTTPError as exc:
                LOG.error(
                    "HTTP error from Atlassian: %s, response: %s",
                    str(exc),
                    exc.response.text,
                )
                try:
                    json_response = exc.response.json()
                    reason = ", ".join(json_response["errorMessages"])
                except ValueError:
                    reason = exc.response.text
                raise http_exception_class(reason)
            except RequestException as exc:
                LOG.error("Error contacting Atlassian: %s", str(exc))
                reason = str(exc)
                raise http_exception_class(reason)

        return func_wrapper

    return decorator
