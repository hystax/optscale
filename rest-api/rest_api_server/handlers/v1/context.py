import json

from rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api_server.controllers.context import ContextAsyncController
from rest_api_server.utils import ModelEncoder, run_task


class ContextAsyncHandler(BaseAuthHandler):
    def _get_controller_class(self):
        return ContextAsyncController

    async def get(self):
        self.check_cluster_secret()
        data = self.get_request_data()
        res = await run_task(self.controller.context, **data)
        self.write(json.dumps(res, cls=ModelEncoder))

    def get_request_data(self):
        return self._request_body()
