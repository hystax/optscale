import json
from auth_server.handlers.v1.base import BaseSecretHandler
from auth_server.controllers.authorization_userlist import (
    AuthorizationUserlistAsyncController)
from optscale_exceptions.common_exc import (
    WrongArgumentsException, NotFoundException)
from optscale_exceptions.http_exc import OptHTTPError
from auth_server.utils import ModelEncoder


class AuthorizationUserlistAsyncHandler(BaseSecretHandler):
    def _get_controller_class(self):
        return AuthorizationUserlistAsyncController

    async def post(self):
        self.check_cluster_secret()
        data = self._request_body()
        try:
            res = await self.controller.authorize_userlist(**data)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)
        self.write(json.dumps(res, cls=ModelEncoder))
