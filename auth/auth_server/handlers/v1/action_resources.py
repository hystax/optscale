import json
from auth.auth_server.controllers.action_resource import (
    ActionResourceAsyncController)
from auth.auth_server.handlers.v1.base import BaseAuthHandler
from auth.auth_server.utils import ModelEncoder
from tools.optscale_exceptions.common_exc import WrongArgumentsException
from tools.optscale_exceptions.http_exc import OptHTTPError


class ActionResourcesAsyncHandler(BaseAuthHandler):
    def _get_controller_class(self):
        return ActionResourceAsyncController

    async def get(self):
        data = self.get_request_data()
        data.update(self.token)
        try:
            res = await self.controller.action_resources(**data)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        response = {'action_resources': res}
        self.write(json.dumps(response, cls=ModelEncoder))

    def get_request_data(self):
        return self._request_body()
