import logging

from rest_api_server.exceptions import Err
from rest_api_server.handlers.v1.base import BaseHandler
from optscale_exceptions.http_exc import OptHTTPError
from optscale_exceptions.common_exc import NotFoundException
from rest_api_server.utils import run_task

LOG = logging.getLogger(__name__)


class BaseAsyncCollectionHandler(BaseHandler):

    def _validate_params(self, **kwargs):
        pass

    async def post(self, **url_params):
        data = self._request_body()
        data.update(url_params)
        self._validate_params(**data)
        res = await run_task(self.controller.create, **data)
        self.set_status(201)
        self.write(res.to_json())


class BaseAsyncItemHandler(BaseHandler):

    def _validate_params(self, item, **kwargs):
        pass

    async def _get_item(self, item_id, **kwargs):
        res = await run_task(self.controller.get, item_id, **kwargs)
        type_name = self.controller.model_type.__name__
        if res is None:
            raise OptHTTPError(404, Err.OE0002, [type_name, item_id])
        return res

    async def get(self, id, **kwargs):
        try:
            item = await self._get_item(id, **kwargs)
            self._validate_params(item, **kwargs)
            self.write(item.to_json())
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)

    async def patch(self, id, **kwargs):
        data = self._request_body()
        item = await self._get_item(id)
        self._validate_params(item, **kwargs)
        res = await run_task(self.controller.edit, id, **data)
        self.write(res.to_json())

    async def delete(self, id, **kwargs):
        item = await self._get_item(id)
        self._validate_params(item, **kwargs)
        await run_task(self.controller.delete, id, **kwargs)
        self.set_status(204)
