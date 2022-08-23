import json

from auth_server.controllers.scope import ScopeAsyncController
from auth_server.exceptions import Err
from auth_server.handlers.v1.base import BaseAuthHandler
from auth_server.utils import ModelEncoder
from optscale_exceptions.common_exc import NotFoundException
from optscale_exceptions.http_exc import OptHTTPError


class ScopeAsyncHandler(BaseAuthHandler):
    def _get_controller_class(self):
        return ScopeAsyncController

    async def get_create_user_scope(self, **kwargs):
        res = await self.controller.scope_create_user(**kwargs)
        return res

    async def get_create_role_scope(self, **kwargs):
        res = await self.controller.scope_create_role(**kwargs)
        return res

    async def get_assign_user_scope(self, user_id, role_id, **kwargs):
        res = await self.controller.scope_assign_user(user_id, role_id, **kwargs)
        return res

    def _get_assing_user_arguments(self):
        user_id = self.get_argument('user_id', None)
        role_id = self.get_argument('role_id', None)
        if user_id is None or role_id is None:
            raise OptHTTPError(400, Err.OA0008, [])
        return user_id, role_id

    async def get(self, **kwargs):
        action = self.get_argument('action', default=None)
        kwargs.update(self.token)
        try:
            if action == 'create_user':
                result = await self.get_create_user_scope(**kwargs)
            elif action == 'create_role':
                result = await self.get_create_role_scope(**kwargs)
            elif action == 'assign_user':
                user_id, role_id = self._get_assing_user_arguments()
                result = await self.get_assign_user_scope(
                    user_id, role_id, **kwargs)
            else:
                raise OptHTTPError(400, Err.OA0009, [])
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)
        response = {'scopes': result}
        self.write(json.dumps(response, cls=ModelEncoder))
