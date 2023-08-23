import json
import logging
import requests

from keeper.report_server.exceptions import Err
from keeper.report_server.utils import Config
from keeper.report_server.handlers.v1.base import BaseAuthHandler as BaseAuthHandlerV1
from keeper.report_server.handlers.v1.base import BaseReportHandler as BaseReportHandlerV1
from keeper.report_server.handlers.v1.base import BaseReceiveHandler as BaseReceiveHandlerV1

from tools.optscale_exceptions.http_exc import OptHTTPError
from tools.optscale_exceptions.common_exc import WrongArgumentsException
from optscale_client.auth_client.client_v2 import Client as AuthClient

LOG = logging.getLogger(__name__)


class BaseAuthHandler(BaseAuthHandlerV1):
    def get_arg(self, name, type, default=None, repeated=False):
        try:
            if repeated:
                return [type(a) for a in self.get_arguments(name)]
            else:
                arg = self.get_argument(name, default=default)
                if arg:
                    if type == bool:
                        lowered = arg.lower()
                        if lowered not in ['true', 'false']:
                            raise WrongArgumentsException(
                                Err.OK0046, [name])
                        return lowered == 'true'
                    return type(arg)
                else:
                    return arg
        except ValueError:
            raise WrongArgumentsException(Err.OK0045, [name])

    def get_params(self):
        return {}

    def get_request_data(self):
        payload = {k: v for k, v in self.get_params().items() if v is not None}
        return {
            'payload': json.dumps(payload)
        }

    async def check_token(self):
        await self.get_awaitable(self._check_token)

    def _check_token(self):
        client = AuthClient(url=Config().auth_url)
        client.token = self.token
        try:
            client.type_list()
        except requests.exceptions.HTTPError as exc:
            if exc.response.status_code == 401:
                raise OptHTTPError(401, Err.OK0003, [])
            raise


class BaseReportHandler(BaseAuthHandler, BaseReportHandlerV1):
    def get_params(self):
        return {
            'time_start': self.get_arg('time_start', int),
            'time_end': self.get_arg('time_end', int),
        }


class BaseReceiveHandler(BaseAuthHandler, BaseReceiveHandlerV1):
    pass
