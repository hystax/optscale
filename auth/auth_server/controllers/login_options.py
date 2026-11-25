import logging

from auth.auth_server.controllers.base import BaseController
from auth.auth_server.controllers.base_async import BaseAsyncControllerWrapper
from auth.auth_server.exceptions import Err
from tools.optscale_exceptions.common_exc import WrongArgumentsException

LOG = logging.getLogger(__name__)

PASSWORD_METHOD = 'password'
SSO_NOT_CONFIGURED = 'not_configured'


class LoginOptionsController(BaseController):

    def _check_input(self, **input_):
        email = input_.get('email')
        if not email:
            raise WrongArgumentsException(Err.OA0032, ['email'])
        if not isinstance(email, str):
            raise WrongArgumentsException(Err.OA0033, ['email'])

        unexpected = [k for k in input_ if k != 'email']
        if unexpected:
            raise WrongArgumentsException(
                Err.OA0022, [', '.join(unexpected)])

    def resolve(self, **kwargs):
        self._check_input(**kwargs)
        return self.resolve_login_options()

    def resolve_login_options(self):
        # constant until SSO: must be identical for known and unknown
        return {
            'methods': [PASSWORD_METHOD],
            'sso': {'state': SSO_NOT_CONFIGURED}
        }


class LoginOptionsAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return LoginOptionsController
