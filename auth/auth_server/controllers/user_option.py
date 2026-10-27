import logging

from auth.auth_server.controllers.base import BaseController
from auth.auth_server.controllers.base_async import BaseAsyncControllerWrapper
from auth.auth_server.exceptions import Err
from auth.auth_server.models.models import UserOption, User
from auth.auth_server.utils import (strtobool, check_string_attribute,
                                    check_valid_json)
from tools.optscale_exceptions.common_exc import (
    WrongArgumentsException, ForbiddenException, NotFoundException)

LOG = logging.getLogger(__name__)


class UserOptionsController(BaseController):
    def _get_model_type(self):
        return UserOption

    def check_user_access(self, user_id, token):
        req_user = self.get_user_by_id(user_id)
        if not req_user:
            raise NotFoundException(Err.OA0003, [User.__name__, user_id])
        if token:
            token_user = self.get_user(token)
            if token_user.id != user_id:
                raise ForbiddenException(Err.OA0012, [])
        return req_user

    def get_by_name(self, user_id, option_name, **kwargs):
        token = kwargs.get('token', None)
        self.check_user_access(user_id, token)
        user_options = super().list(user_id=user_id, name=option_name)
        if len(user_options) > 1:
            raise WrongArgumentsException(Err.OA0029, [])
        elif len(user_options) == 0:
            return '{}'
        else:
            return user_options[0].value

    def list(self, user_id, **kwargs):
        token = kwargs.get('token', None)
        self.check_user_access(user_id, token)
        with_values = kwargs.get('with_values', False)
        try:
            if not isinstance(with_values, bool):
                with_values = strtobool(with_values)
        except ValueError:
            raise WrongArgumentsException(Err.OA0063, ['with_values'])
        base_list = super().list(user_id=user_id)
        result = [
            {
                'name': obj.name, 'value': obj.value
            } if with_values else obj.name for obj in base_list
        ]
        return result

    def patch(self, user_id, option_name, value_data, **kwargs):
        token = kwargs.get('token', None)
        self.check_user_access(user_id, token)

        options = super().list(user_id=user_id, name=option_name)
        check_valid_json(value_data, 'value')
        if len(options) > 1:
            raise WrongArgumentsException(Err.OA0029, [])
        elif len(options) == 0:
            check_string_attribute('option_name', option_name,
                                   max_length=256)
            res = super().create(user_id=user_id, name=option_name,
                                 deleted_at=0, value=value_data)
            return res.value
        else:
            option = options[0]
            res = super().edit(option.id, value=value_data)
            return res.value

    def delete(self, user_id, option_name, **kwargs):
        token = kwargs.get('token', None)
        self.check_user_access(user_id, token)

        options = super().list(user_id=user_id, name=option_name)
        if len(options) > 1:
            raise WrongArgumentsException(Err.OA0029, [])
        elif len(options) == 0:
            raise NotFoundException(
                Err.OA0003, [UserOption.__name__, option_name])
        else:
            option = options[0]
            super().delete(option.id)


class UserOptionsAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return UserOptionsController
