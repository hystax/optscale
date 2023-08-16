import logging
import copy

from auth.auth_server.exceptions import Err
from auth.auth_server.models.models import Type
from auth.auth_server.auth_token.token_store import TokenStore
from auth.auth_server.controllers.base import BaseController
from auth.auth_server.controllers.base_async import BaseAsyncControllerWrapper
from tools.optscale_exceptions.common_exc import (WrongArgumentsException,
                                                  ForbiddenException)
from auth.auth_server.utils import load_payload

LOG = logging.getLogger(__name__)


class ActionResourceController(object):
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

    def _get_not_assignable_types(self):
        non_assignable_types = self.session.query(Type).filter(
            Type.assignable.is_(False)
        ).all()
        return list(map(lambda x: x.name, non_assignable_types))

    def bulk_action_resources(self, user_ids, actions, assignable_only=True):
        non_assignable = []
        if assignable_only:
            non_assignable = self._get_not_assignable_types()
        base_controller = BaseController(self.session, self._config)
        user_action_resources = base_controller.get_bulk_action_resources(
            user_ids, actions)
        for user_id, action_resources in user_action_resources.items():
            for k, v in copy.deepcopy(action_resources).items():
                action_resources[k] = list(
                    filter(lambda x: x[0] not in non_assignable, v))
        return user_action_resources

    def action_resources(self, **kwargs):
        token = kwargs.pop('token', None)
        user_id = kwargs.pop('user_id', None)
        if user_id and token:
            raise ForbiddenException(Err.OA0012, [])
        payload = kwargs.get('payload')
        payload_dict = load_payload(payload)
        actions = payload_dict.get('actions')
        if not actions or not isinstance(actions, list):
            raise WrongArgumentsException(Err.OA0014, [])
        assignable_only = payload_dict.get('assignable_only', True)
        non_assignable = []
        if assignable_only:
            non_assignable = self._get_not_assignable_types()
        base_controller = BaseController(self.session, self._config)
        action_resources = base_controller.get_action_resources(
            token, action_list=actions, user_id=user_id)
        for k, v in copy.deepcopy(action_resources).items():
            action_resources[k] = list(
                filter(lambda x: x[0] not in non_assignable, v))
        return action_resources


class ActionResourceAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return ActionResourceController
