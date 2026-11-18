import datetime
import hashlib
import logging

from sqlalchemy.exc import IntegrityError

from auth.auth_server.auth_token.macaroon import MacaroonToken, MFA_NONE
from auth.auth_server.controllers.base import BaseController
from auth.auth_server.exceptions import Err
from auth.auth_server.models.models import Token
from tools.optscale_exceptions.common_exc import WrongArgumentsException
from tools.optscale_time import utcnow
from optscale_client.config_client.client import etcd

LOG = logging.getLogger(__name__)
DEFAULT_TOKEN_EXPIRATION = 168


def xstr(s):
    if s is None:
        return ''
    return str(s)


class TokenIssuer(BaseController):
    """
    Mints tokens for an already authenticated user. Kept apart from the
    login logic (TokenController) so the MFA controllers can issue a token
    without depending on the login flow that depends on them.
    """

    def _get_model_type(self):
        return Token

    @property
    def expiration(self):
        try:
            return int(self._config.read('/token_expiration').value)
        except (etcd.EtcdKeyNotFound, ValueError):
            return DEFAULT_TOKEN_EXPIRATION

    def create_user_token(self, user, mfa=MFA_NONE, **kwargs):
        model_type = self._get_model_type()
        LOG.info("Creating %s with parameters %s", model_type.__name__, kwargs)
        now = utcnow()
        macaroon_token = MacaroonToken(user.salt, user.id).create(
            xstr(kwargs.get('register', False)),
            xstr(kwargs.get('provider', 'optscale')),
            mfa,
        )
        params = {
            'user_id': user.id,
            'created_at': now,
            'valid_until': now + datetime.timedelta(hours=self.expiration),
            'ip': kwargs.get('ip'),
            'digest': hashlib.md5(macaroon_token.encode('utf-8')).hexdigest()
        }
        token = model_type(**params)
        self.session.add(token)
        try:
            self.session.commit()
        except IntegrityError as ex:
            raise WrongArgumentsException(Err.OA0061, [str(ex)])
        return {'token': macaroon_token, **token.to_dict()}
