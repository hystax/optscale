import json

from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.controllers.resource import ResourceAsyncController
from rest_api.rest_api_server.utils import ModelEncoder, run_task


class ResourcesAsyncHandler(BaseAuthHandler):
    def _get_controller_class(self):
        return ResourceAsyncController

    async def get(self):
        self.check_cluster_secret()
        data = self.get_request_data()
        res = await run_task(self.controller.resources_get, **data)
        self.write(json.dumps(res, cls=ModelEncoder))

    def get_request_data(self):
        return self._request_body()
