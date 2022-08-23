import logging

from auth_server.controllers.base import BaseController
from auth_server.controllers.base_async import BaseAsyncControllerWrapper
from auth_server.exceptions import Err
from auth_server.models.models import Assignment
from optscale_exceptions.common_exc import WrongArgumentsException
from auth_server.utils import check_kwargs_is_empty, pop_or_raise

LOG = logging.getLogger(__name__)


class AuthorizationController(BaseController):
    def _get_model_type(self):
        return Assignment

    def _get_input(self, **input):
        token = input.pop('token')
        action = pop_or_raise(input, 'action')
        res_type = pop_or_raise(input, 'resource_type')
        uuid = input.pop('uuid') if 'uuid' in input else None
        if not uuid and uuid is not None:
            raise WrongArgumentsException(Err.OA0054, [])
        check_kwargs_is_empty(**input)
        return token, action, res_type, uuid

    def authorize(self, **kwargs):
        token, action, res_type, uuid = self._get_input(**kwargs)
        assignments = self.check_permissions(token, res_type, uuid, action)
        return {
            'status': 'ok',
            'assignments': list(map(lambda x: {
                'id': x.id,
                'user': x.user.email,
                'type': x.type.name,
                'role': x.role.name,
                'resource': x.resource_id
            }, assignments))
        }


class AuthorizationAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return AuthorizationController
