import json
from auth.auth_server.controllers.authorization import (
    AuthorizationAsyncController)
from auth.auth_server.handlers.v1.base import BaseAsyncAuthCollectionHandler
from auth.auth_server.utils import ModelEncoder
from tools.optscale_exceptions.common_exc import (ForbiddenException,
                                                  WrongArgumentsException,
                                                  NotFoundException)
from tools.optscale_exceptions.http_exc import OptHTTPError


class AuthorizationAsyncHandler(BaseAsyncAuthCollectionHandler):
    def _get_controller_class(self):
        return AuthorizationAsyncController

    async def post(self, **url_params):
        data = self._request_body()
        data.update(url_params)
        data.update(self.token)
        self._validate_params(**data)
        try:
            res = await self.controller.authorize(**data)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        except ForbiddenException as ex:
            raise OptHTTPError.from_opt_exception(403, ex)
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)
        self.set_status(200)
        self.write(json.dumps(res, cls=ModelEncoder))
