import logging

from optscale_exceptions.common_exc import WrongArgumentsException
from sqlalchemy.exc import IntegrityError

from slacker_server.controllers.base import (BaseHandlerController,
                                             BaseAsyncControllerWrapper)
from slacker_server.exceptions import Err
from slacker_server.message_templates.connect import get_connection_done_message
from slacker_server.models.models import User


LOG = logging.getLogger(__name__)


class ConnectController(BaseHandlerController):
    def connect(self, secret):
        user = self.session.query(User).filter(
            User.secret == secret,
            User.deleted.is_(False),
        ).one_or_none()
        if user is None:
            raise WrongArgumentsException(Err.OS0011, ['secret'])

        if user.auth_user_id is not None:
            raise WrongArgumentsException(Err.OS0013, [])

        auth_user_id = self.get_user_id()
        user.auth_user_id = auth_user_id
        self.session.add(user)
        try:
            self.session.commit()
        except IntegrityError as exc:
            LOG.exception('Unable to save user: %s', exc)
            raise WrongArgumentsException(Err.OS0009, [exc])

        auth_cl, rest_cl = self.get_user_api_clients(token=self.token)
        _, user_info = auth_cl.user_update(
            auth_user_id, **{'slack_connected': True})
        _, org_resp = rest_cl.organization_list()

        self.app.client.chat_post(
            channel_id=user.slack_channel_id,
            team_id=user.slack_team_id,
            **get_connection_done_message(
                orgs=org_resp['organizations'],
                user_email=user_info['email'],
                active_org_id=None,
            ))
        return user


class ConnectAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return ConnectController
