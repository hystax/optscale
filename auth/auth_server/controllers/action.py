import json
import logging
from auth.auth_server.auth_token.token_store import TokenStore
from auth.auth_server.controllers.base import BaseController
from auth.auth_server.controllers.base_async import BaseAsyncControllerWrapper
from tools.optscale_exceptions.common_exc import (
    WrongArgumentsException, NotFoundException)
from requests import HTTPError
from auth.auth_server.exceptions import Err
from auth.auth_server.utils import check_kwargs_is_empty, get_context_values

LOG = logging.getLogger(__name__)


class ActionController(object):
    def __init__(self, db_session, config=None):
        self._session = db_session
        self._config = config
        self._db = None
        self.access_token_store = TokenStore(db_session)

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, val):
        self._session = val

    def allowed_actions(self, **kwargs):
        token = kwargs.pop('token')
        payload = kwargs.pop('payload')
        check_kwargs_is_empty(**kwargs)
        try:
            li = json.loads(payload)
            if not isinstance(li, list):
                raise ValueError
        except (ValueError, json.decoder.JSONDecodeError) as ex:
            LOG.error("Failed to get payload %s token %s because of %s",
                      payload, token, str(ex))
            raise WrongArgumentsException(Err.OA0013, [])
        base_controller = BaseController(self.session, self._config)
        user = base_controller.get_user(token)
        action_resources = self.access_token_store.action_resources(user)
        if not action_resources:
            return dict(map(lambda k: (k[1], set()), li))
        result = {}
        for type_, scope_id in li:
            try:
                context = base_controller.get_context(type_, scope_id)
            except HTTPError as exc:
                if exc.response.status_code == 404:
                    raise NotFoundException(Err.OA0028, [type_, scope_id])
                if exc.response.status_code == 400:
                    exc_info = exc.response.json()['error']
                    if exc_info['error_code'] == 'OE0472':
                        deleted_type = exc_info['params'][2]
                        deleted_id = exc_info['params'][3]
                        raise WrongArgumentsException(Err.OA0066, [
                            type_, scope_id, deleted_type, deleted_id])
                    raise WrongArgumentsException(Err.OA0020, [type_])
                raise exc
            context_values = get_context_values(context)
            result[scope_id] = set(
                map(
                    lambda x: x[2],
                    filter(lambda x: x[0] in context_values, action_resources)
                )
            )
        return result


class ActionAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return ActionController
