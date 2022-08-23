import json
from auth_server.handlers.v1.base import BaseSecretHandler
from auth_server.controllers.digest import DigestAsyncController
from optscale_exceptions.common_exc import (WrongArgumentsException,
                                            NotFoundException)
from optscale_exceptions.http_exc import OptHTTPError
from auth_server.utils import ModelEncoder


class DigestAsyncHandler(BaseSecretHandler):
    def _get_controller_class(self):
        return DigestAsyncController

    async def get(self):
        self.check_cluster_secret()
        data = self.get_request_data()
        try:
            res = await self.controller.digest(**data)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)
        self.write(json.dumps(res, cls=ModelEncoder))

    def get_request_data(self):
        return self._request_body()
