import json

from rest_api.rest_api_server.handlers.v1.base import BaseAuthHandler
from rest_api.rest_api_server.controllers.auth_hierarchy import (
    AuthHierarchyAsyncController)
from rest_api.rest_api_server.utils import ModelEncoder, run_task


class AuthHierarchyAsyncHandler(BaseAuthHandler):
    def _get_controller_class(self):
        return AuthHierarchyAsyncController

    async def get(self):
        self.check_cluster_secret()
        type = self.get_argument('type', default=None)
        scope_id = self.get_argument('scope_id', default=None)
        res = await run_task(self.controller.auth_hierarchy, type, scope_id)
        self.write(json.dumps(res, cls=ModelEncoder))
