import json

from auth.auth_server.controllers.token import TokenAsyncController
from auth.auth_server.handlers.v1.base import BaseAsyncCollectionHandler
from auth.auth_server.utils import run_task, ModelEncoder

from tools.optscale_exceptions.common_exc import WrongArgumentsException
from tools.optscale_exceptions.http_exc import OptHTTPError


class TokenAsyncCollectionHandler(BaseAsyncCollectionHandler):
    def _get_controller_class(self):
        return TokenAsyncController

    async def _validate_params(self, **kwargs):
        await self.controller.check_create_restrictions(**kwargs)

    async def post(self, **url_params):
        data = self._request_body()
        try:
            await self._validate_params(**data)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        data.update(url_params)
        data.update({'ip': self.get_ip_addr()})
        res = await run_task(self.controller.create, **data)
        self.set_status(201)
        self.write(json.dumps(res, cls=ModelEncoder))
