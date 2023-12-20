import json
import logging

from auth.auth_server.controllers.role import RoleAsyncController
from auth.auth_server.handlers.v1.base import (BaseAsyncAuthItemHandler,
                                               BaseAsyncAuthCollectionHandler)
from auth.auth_server.utils import ModelEncoder, as_dict

from tools.optscale_exceptions.common_exc import (
    WrongArgumentsException, NotFoundException, ConflictException,
    ForbiddenException, UnauthorizedException)
from tools.optscale_exceptions.http_exc import OptHTTPError

LOG = logging.getLogger(__name__)


class RoleAsyncItemHandler(BaseAsyncAuthItemHandler):
    def _get_controller_class(self):
        return RoleAsyncController

    async def get(self, item_id, **kwargs):
        kwargs.update(self.token)
        try:
            item = await self._get_item(item_id, **kwargs)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)
        except ConflictException as ex:
            raise OptHTTPError.from_opt_exception(409, ex)
        except ForbiddenException as ex:
            raise OptHTTPError.from_opt_exception(403, ex)
        except UnauthorizedException as ex:
            raise OptHTTPError.from_opt_exception(401, ex)
        self._validate_params(item, **kwargs)
        self.write(json.dumps(item))

    async def patch(self, item_id, **kwargs):
        data = self._request_body()
        item = await self._get_item(item_id, **kwargs)
        data.update(self.token)
        self._validate_params(item, **kwargs)
        try:
            item = await self.controller.edit(item_id, **data)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)
        except ConflictException as ex:
            raise OptHTTPError.from_opt_exception(409, ex)
        except ForbiddenException as ex:
            raise OptHTTPError.from_opt_exception(403, ex)
        except UnauthorizedException as ex:
            raise OptHTTPError.from_opt_exception(401, ex)
        self.write(json.dumps(item))

    async def delete(self, id_, **kwargs):
        await super().delete(id_, **kwargs)


class RoleAsyncCollectionHandler(BaseAsyncAuthCollectionHandler):
    def _get_controller_class(self):
        return RoleAsyncController

    async def get(self, **kwargs):
        kwargs.update(self.token)
        assignable = self.get_argument('assignable', default=None)
        try:
            roles, resources_info = await self.controller.list(
                assignable, **kwargs)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)
        except ConflictException as ex:
            raise OptHTTPError.from_opt_exception(409, ex)
        except ForbiddenException as ex:
            raise OptHTTPError.from_opt_exception(403, ex)
        except UnauthorizedException as ex:
            raise OptHTTPError.from_opt_exception(401, ex)
        role_dict = {'roles': [dict(list(as_dict(role).items()) + [
            ('scope_name', resources_info.get(role.scope_id, {}).get(
                'name'))]) for role in roles]}
        self.write(json.dumps(role_dict, cls=ModelEncoder))

    async def post(self, **url_params):
        await super().post(**url_params)
