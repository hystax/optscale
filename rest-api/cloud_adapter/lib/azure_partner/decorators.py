import requests


def _wrap_http_errors(http_exception_class):
    def decorator(func):
        def func_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except requests.HTTPError as exc:
                error_info = {}
                try:
                    error_info = exc.response.json()
                except ValueError:
                    pass

                error_message = error_info.get('description')
                if not error_message:
                    error_message = error_info.get('error_description')
                if not error_message:
                    error_message = exc.response.reason

                # Our RestAPI back-end currently doesn't handle multi-line
                # error messages well. Also, secondary lines don't seem to
                # contain meaningful information here. So let's take only the
                # first line.
                error_message = error_message.splitlines()[0]

                error_codes = error_info.get('error_codes', [])
                if not error_codes and 'code' in error_info:
                    error_codes = [error_info['code']]

                status_code = exc.response.status_code

                raise http_exception_class(
                    error_message, error_codes, status_code)

        return func_wrapper

    return decorator


def _wrap_connection_errors(connection_exception_class):
    def decorator(func):
        def func_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except requests.ConnectionError as exc:
                error_name = exc.__class__.__name__
                error_message = f'Could not connect to Azure: {error_name}'
                raise connection_exception_class(error_message)

        return func_wrapper

    return decorator
