import json

from auth.auth_server.controllers.action import ActionAsyncController
from auth.auth_server.handlers.v1.base import BaseAuthHandler
from auth.auth_server.utils import ModelEncoder
from tools.optscale_exceptions.common_exc import (
    WrongArgumentsException, NotFoundException)
from tools.optscale_exceptions.http_exc import OptHTTPError


class ActionAsyncHandler(BaseAuthHandler):
    def _get_controller_class(self):
        return ActionAsyncController

    async def get(self):
        data = self.get_request_data()
        data.update(self.token)
        try:
            res = await self.controller.allowed_actions(**data)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)
        response = {'allowed_actions': res}
        self.write(json.dumps(response, cls=ModelEncoder))

    def get_request_data(self):
        return self._request_body()
