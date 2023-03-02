import json
import logging
from ohsu.controllers.link import SHSLinkAsyncController
from ohsu.handlers.v2.base import BaseHandler
from optscale_exceptions.common_exc import (
    NotFoundException, WrongArgumentsException)
from optscale_exceptions.http_exc import OptHTTPError


LOG = logging.getLogger(__name__)


class SHSLinkAsyncHandler(BaseHandler):

    def _get_controller_class(self):
        return SHSLinkAsyncController

    async def get(self, organization_id):
        """
        body:
        {
            "app_id": "123"
        }
        """
        body = self._request_body()
        try:
            res = await self.controller.get(organization_id, **body)
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        self.set_status(200)
        self.write(json.dumps(res))

    async def delete(self, organization_id):
        try:
            await self.controller.delete(organization_id)
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)
        self.set_status(204)
