import json

from auth.auth_server.controllers.user import UserAsyncController
from auth.auth_server.controllers.assignment import AssignmentAsyncController
from auth.auth_server.exceptions import Err
from auth.auth_server.handlers.v1.base import (BaseAsyncAuthItemHandler,
                                               BaseAsyncAuthCollectionHandler,
                                               WrongArgumentsException)
from tools.optscale_exceptions.http_exc import OptHTTPError
from tools.optscale_exceptions.common_exc import NotFoundException, ForbiddenException
from auth.auth_server.utils import as_dict, ModelEncoder


class AssignmentAsyncItemHandler(BaseAsyncAuthItemHandler):
    def _get_controller_class(self):
        return AssignmentAsyncController

    def _validate_params(self, item, **kwargs):
        user_id = kwargs.get('user_id')
        if user_id:
            if item.user_id != user_id:
                raise OptHTTPError(404, Err.OA0004, [user_id, item.id])

    async def _get_item(self, item_id, **kwargs):
        try:
            item, resource_info = await self.controller.get(item_id, **kwargs)
            type_name = self.controller.model_type.__name__
            if item is None:
                raise OptHTTPError(404, Err.OA0003, [type_name, item_id])
            return item, resource_info
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)
        except ForbiddenException as ex:
            raise OptHTTPError.from_opt_exception(403, ex)
        except NotImplementedError:
            raise OptHTTPError(405, Err.OA0002, [])

    async def get(self, id, **kwargs):
        kwargs.update(self.token)
        item, resource_info = await self._get_item(id, **kwargs)
        self._validate_params(item, **kwargs)
        response = self.merge_resource_info(item, resource_info)
        self.write(json.dumps(response, cls=ModelEncoder))


class AssignmentAsyncCollectionHandler(BaseAsyncAuthCollectionHandler):
    def _get_controller_class(self):
        return AssignmentAsyncController

    async def _check_user(self, user_id):
        controller = UserAsyncController(self.session(), self._config)
        try:
            res = await controller.get(user_id)
            if res is None:
                raise OptHTTPError(404, Err.OA0005, [user_id])
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)

    async def get(self, user_id, **kwargs):
        params = {'user_id': user_id}
        if not kwargs.get('ignore_permissions', False):
            params.update(self.token)
        await self._check_user(user_id)
        try:
            assignments = await self.controller.list(**params)
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)
        assignments_dict = {'assignments': assignments}
        self.write(json.dumps(assignments_dict, cls=ModelEncoder))

    async def post(self, user_id, **url_params):
        await super().post(user_id=user_id, **url_params)
