import json

from tools.optscale_exceptions.common_exc import WrongArgumentsException

from auth.auth_server.exceptions import Err
from auth.auth_server.handlers.v1.base import BaseHandler as BaseHandler_v1


class BaseHandler(BaseHandler_v1):
    def get_arg(self, name, type_, default=None, repeated=False):
        try:
            if repeated:
                return [type_(a) for a in self.get_arguments(name)]
            else:
                arg = self.get_argument(name, default=default)
                if arg:
                    if type_ == bool and isinstance(arg, str):
                        lowered = arg.lower()
                        if lowered not in ['true', 'false']:
                            raise WrongArgumentsException(Err.OA0063, [name])
                        return lowered == 'true'
                    return type_(arg)
                else:
                    return arg
        except ValueError:
            raise WrongArgumentsException(Err.OA0060, [name])

    def parse_url_params_into_payload(self, payload_map_params):
        data = {}
        payload = {}
        for k in self.request.arguments.keys():
            extract_target = data
            repeated = False
            param = k
            param_type = str
            if k in payload_map_params.keys():
                param, param_type, repeated = payload_map_params.get(k)
                extract_target = payload
            extract_target[param] = self.get_arg(
                k, param_type, repeated=repeated)
        data['payload'] = json.dumps(payload)
        return data
