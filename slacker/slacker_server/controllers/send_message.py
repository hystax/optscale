import logging
from slack_sdk.errors import SlackApiError
from optscale_exceptions.common_exc import (WrongArgumentsException,
                                            NotFoundException)
from slacker_server.models.models import User
from slacker_server.controllers.base import (BaseHandlerController,
                                             BaseAsyncControllerWrapper)
from slacker_server.exceptions import Err
from slacker_server.message_templates.constraint_violations import (
    get_constraint_violation_alert)
from slacker_server.message_templates.alerts import (
    get_alert_message, get_alert_added_message, get_alert_removed_message)
from slacker_server.message_templates.env_alerts import (
    get_property_updated_message, get_message_changed_active_state,
    get_message_acquired, get_message_released)
from slacker_server.message_templates.warnings import get_archived_message_block


LOG = logging.getLogger(__name__)


class SendMessageController(BaseHandlerController):
    MESSAGE_TEMPLATES = {
        'alert': get_alert_message,
        'alert_added': get_alert_added_message,
        'alert_removed': get_alert_removed_message,
        'constraint_violated_alert': get_constraint_violation_alert,
        'env_acquired': get_message_acquired,
        'env_released': get_message_released,
        'env_property_updated': get_property_updated_message,
        'env_active_state_changed': get_message_changed_active_state
    }

    def send_message(self, **kwargs):
        type_ = kwargs['type']
        channel_id = kwargs.get('channel_id')
        team_id = kwargs.get('team_id')
        auth_user_id = kwargs.get('auth_user_id')
        parameters = kwargs.get('parameters', {})
        warning = parameters.pop('warning', None)
        warning_params = parameters.pop('warning_params', None)
        if auth_user_id:
            user = self.session.query(User).filter(
                User.auth_user_id == auth_user_id,
                User.deleted.is_(False),
            ).one_or_none()
            if not user:
                raise NotFoundException(Err.OS0016, ['auth_user_id',
                                                     auth_user_id])
            team_id = user.slack_team_id
            channel_id = user.slack_channel_id

        template_func = self.MESSAGE_TEMPLATES.get(type_)
        if template_func is None:
            raise WrongArgumentsException(Err.OS0011, ['type'])

        message = template_func(**parameters)
        if warning:
            warnings_map = {
                'is_archived': get_archived_message_block
            }
            if warnings_map.get(warning):
                message['blocks'] = warnings_map[warning](
                    **warning_params) + message['blocks']

        try:
            self.app.client.chat_post(
                channel_id=channel_id, team_id=team_id,
                **message)
        except TypeError as exc:
            LOG.error('Failed to send message: %s', exc)
            raise WrongArgumentsException(Err.OS0011, ['parameters'])
        except SlackApiError as exc:
            LOG.error('Failed to send message: %s', exc)
            if exc.response['error'] == 'is_archived':
                raise WrongArgumentsException(Err.OS0019, [channel_id])
            raise


class SendMessageAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return SendMessageController
