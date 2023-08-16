import json
import logging

from tools.optscale_exceptions.common_exc import (NotFoundException,
                                                  UnauthorizedException)
from tools.optscale_exceptions.http_exc import OptHTTPError
from auth.auth_server.controllers.type import TypeAsyncController
from auth.auth_server.handlers.v1.base import (BaseAsyncAuthCollectionHandler,
                                               BaseAsyncAuthItemHandler)
from auth.auth_server.utils import as_dict, ModelEncoder

LOG = logging.getLogger(__name__)


class TypeAsyncItemHandler(BaseAsyncAuthItemHandler):
    def _get_controller_class(self):
        return TypeAsyncController

    async def _get_item(self, item_id, **kwargs):
        try:
            item = await self.controller.get(item_id, **kwargs)
            return item
        except UnauthorizedException as ex:
            raise OptHTTPError.from_opt_exception(401, ex)
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)

    async def get(self, id, **kwargs):
        kwargs.update(self.token)
        res = await self._get_item(id, **kwargs)
        self.write(json.dumps(dict(list(res.to_dict().items())),
                              cls=ModelEncoder))


class TypeAsyncCollectionHandler(BaseAsyncAuthCollectionHandler):
    def _get_controller_class(self):
        return TypeAsyncController

    async def get(self, **kwargs):
        kwargs.update(self.token)
        types = await self.controller.list(**kwargs)
        types_dict = {'types': [
            as_dict(type_) for type_ in types]}
        self.write(json.dumps(types_dict, cls=ModelEncoder))
