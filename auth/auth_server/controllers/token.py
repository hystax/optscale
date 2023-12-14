import logging
import datetime
import hashlib
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError

from auth.auth_server.controllers.base import BaseController
from auth.auth_server.controllers.base_async import BaseAsyncControllerWrapper
from auth.auth_server.exceptions import Err
from auth.auth_server.models.models import Token, User
from auth.auth_server.auth_token.macaroon import MacaroonToken
from auth.auth_server.utils import (hash_password, popkey,
                                    raise_not_provided_error)

from tools.optscale_exceptions.common_exc import (WrongArgumentsException,
                                                  ForbiddenException,
                                                  NotFoundException)
from optscale_client.config_client.client import etcd

LOG = logging.getLogger(__name__)
DEFAULT_TOKEN_EXPIRATION = 168


def xstr(s):
    if s is None:
        return ''
    return str(s)


class TokenController(BaseController):
    def _get_model_type(self):
        return Token

    @property
    def create_restrictions(self):
        return super().create_restrictions + ['email', 'password']

    @property
    def expiration(self):
        try:
            return int(self._config.read('/token_expiration').value)
        except (etcd.EtcdKeyNotFound, ValueError):
            return DEFAULT_TOKEN_EXPIRATION

    def _check_user(self, email, password):
        user = self.session.query(User).filter(
            and_(
                User.email == email,
                User.deleted.is_(False)
            )
        ).one_or_none()
        if not user or user.password != hash_password(password, user.salt):
            raise ForbiddenException(Err.OA0037, [])
        if not user.is_active:
            raise ForbiddenException(Err.OA0038, [])
        return user

    def _check_input(self, **input_):
        email = input_.get('email')
        password = input_.get('password')
        if not email or not password:
            raise WrongArgumentsException(Err.OA0039, [])
        user = self._check_user(email, password)
        return user

    def create(self, **kwargs):
        user = self._check_input(**kwargs)
        popkey(kwargs, 'password')
        return self.create_user_token(user, **kwargs)

    def create_token_by_user_id(self, **kwargs):
        user_id = kwargs.get('user_id')
        if user_id is None:
            raise_not_provided_error('user_id')
        user = self.session.query(User).filter(
            and_(
                User.id == user_id,
                User.deleted.is_(False)
            )
        ).one_or_none()
        if not user:
            raise NotFoundException(Err.OA0043, [user_id])
        if not user.is_active:
            raise ForbiddenException(Err.OA0038, [])
        return self.create_user_token(user, **kwargs)

    def create_user_token(self, user, **kwargs):
        model_type = self._get_model_type()
        LOG.info("Creating %s with parameters %s", model_type.__name__, kwargs)
        now = datetime.datetime.utcnow()
        macaroon_token = MacaroonToken(user.salt, user.id).create(
            xstr(kwargs.get('register', False)),
            xstr(kwargs.get('provider', 'optscale'))
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


class TokenAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return TokenController
