from tools.optscale_exceptions.http_exc import OptHTTPError
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.handlers.v1.base import BaseHandler as BaseHandler_v1


class BaseHandler(BaseHandler_v1):
    def get_arg(self, name, type, default=None, repeated=False):
        try:
            if repeated:
                result = [type(a) for a in self.get_arguments(name)]
                if not result and default:
                    result = default
                return result
            else:
                arg = self.get_argument(name, default=default)
                if arg:
                    if type == bool and isinstance(arg, str):
                        lowered = arg.lower()
                        if lowered not in ['true', 'false']:
                            raise ValueError('%s should be true or false' % arg)
                        return lowered == 'true'
                    return type(arg)
                else:
                    return arg
        except (ValueError, TypeError):
            raise OptHTTPError(400, Err.OE0217, [name])

    def parse_url_params_into_payload(self, payload_map_params):
        data = {}
        payload = {}
        for k in self.request.arguments.keys():
            repeated = False
            param = k
            param_type = str
            if k in payload_map_params.keys():
                param, param_type, repeated = payload_map_params.get(k)
            payload[param] = self.get_arg(
                k, param_type, repeated=repeated)
        data['payload'] = payload
        return data
