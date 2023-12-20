import logging

import requests

from auth.auth_server.controllers.base import BaseController
from auth.auth_server.controllers.base_async import BaseAsyncControllerWrapper
from auth.auth_server.exceptions import Err
from auth.auth_server.models.models import Assignment
from auth.auth_server.utils import check_kwargs_is_empty, pop_or_raise
from auth.auth_server.utils import get_context_values
from tools.optscale_exceptions.common_exc import (
    WrongArgumentsException, NotFoundException)

LOG = logging.getLogger(__name__)


class AuthorizationUserlistController(BaseController):
    def _get_model_type(self):
        return Assignment

    def _get_input(self, **input):
        scope_type = pop_or_raise(input, 'scope_type')
        users = pop_or_raise(input, 'users')
        actions = pop_or_raise(input, 'actions')
        for i in [(users, 'users'), (actions, 'actions')]:
            if not isinstance(i[0], list):
                raise WrongArgumentsException(Err.OA0055, [i[1]])
        scope_id = input.pop('scope_id') if 'scope_id' in input else None
        if not scope_id and scope_id is not None:
            raise WrongArgumentsException(Err.OA0054, [])
        check_kwargs_is_empty(**input)
        return users, actions, scope_type, scope_id

    def authorize_userlist(self, **kwargs):
        users, actions, scope_type, scope_id = self._get_input(**kwargs)
        try:
            context = self.get_context(scope_type, scope_id)
        except requests.exceptions.HTTPError as exc:
            if exc.response.status_code == 400:
                raise WrongArgumentsException(Err.OA0020, [scope_type])
            elif exc.response.status_code == 404:
                raise NotFoundException(Err.OA0003, [scope_type, scope_id])
            raise
        context_values = get_context_values(context)
        scope_type_name = self.context_level[len(context)]
        actual_type = self.get_type_by_name(scope_type_name)
        allowed_lvls = ([x.id for x in actual_type.parent_tree] +
                        [actual_type.id])
        auth_userlist = self.access_token_store.auth_user_list(
            users, actions, allowed_lvls, context_values)
        result = dict(map(lambda k: (k, set()), users))
        for item in auth_userlist:
            user_id, action = item
            result[user_id].add(action)
        return result


class AuthorizationUserlistAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return AuthorizationUserlistController
