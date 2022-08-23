import json
import logging

from auth_server.controllers.role import RoleAsyncController
from optscale_exceptions.common_exc import (
    WrongArgumentsException, NotFoundException, ConflictException,
    ForbiddenException, UnauthorizedException)
from auth_server.handlers.v1.base import (BaseAsyncAuthItemHandler,
                                          BaseAsyncAuthCollectionHandler)
from optscale_exceptions.http_exc import OptHTTPError
from auth_server.utils import ModelEncoder, as_dict

LOG = logging.getLogger(__name__)


class RoleAsyncItemHandler(BaseAsyncAuthItemHandler):
    def _get_controller_class(self):
        return RoleAsyncController

    async def get(self, id, **kwargs):
        kwargs.update(self.token)
        try:
            item = await self._get_item(id, **kwargs)
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

    async def patch(self, id, **kwargs):
        data = self._request_body()
        item = await self._get_item(id, **kwargs)
        data.update(self.token)
        self._validate_params(item, **kwargs)
        try:
            item = await self.controller.edit(id, **data)
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

    async def delete(self, id, **kwargs):
        await super().delete(id, **kwargs)


class RoleAsyncCollectionHandler(BaseAsyncAuthCollectionHandler):
    def _get_controller_class(self):
        return RoleAsyncController

    async def get(self, **kwargs):
        kwargs.update(self.token)
        assignable = self.get_argument('assignable', default=None)
        try:
            roles, resources_info = await self.controller.list(assignable, **kwargs)
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
