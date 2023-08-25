import argparse
import inspect
import logging

from datetime import datetime, timedelta

from requests import HTTPError
from retrying import Retrying
from slack_sdk.errors import SlackApiError
from sqlalchemy.exc import IntegrityError

from slacker.slacker_server.controllers.base import BaseController
from slacker.slacker_server.message_templates.alerts import (
    get_join_channel_message, get_alert_list, get_add_expense_alert_modal,
    get_add_alert_modal_empty_template, get_select_alert_type_modal,
    get_add_constraint_envs_alert_modal)
from slacker.slacker_server.message_templates.bookings import (
    get_add_bookings_form, get_booking_details_message)
from slacker.slacker_server.message_templates.connect import get_welcome_message
from slacker.slacker_server.message_templates.constraints import (
    get_update_ttl_form, get_constraint_updated)
from slacker.slacker_server.message_templates.disconnect import (
    get_disconnect_confirmation_message, get_disconnected_message)
from slacker.slacker_server.message_templates.envs import get_envs_message
from slacker.slacker_server.message_templates.org import (
    get_org_switch_message, get_org_switch_completed_message)
from slacker.slacker_server.message_templates.resources import get_resources_message
from slacker.slacker_server.message_templates.resource_details import (
    get_resource_details_message)
from slacker.slacker_server.message_templates.errors import (
    get_ca_not_connected_message, get_not_have_slack_permissions_message)
from slacker.slacker_server.models.models import User
from slacker.slacker_server.utils import gen_id

LOG = logging.getLogger(__name__)
TTL_LIMIT_TO_SHOW = 72
EXPENSE_LIMIT_TO_SHOW = 0.9
MS_IN_SEC = 1000
SEC_IN_HRS = 3600
MAX_MSG_ENVS_LENGTH = 10


def retry_too_many_requests(f, *args, **kwargs):
    try:
        return f(*args, **kwargs)
    except Exception as exc:
        if retriable_slack_api_error(exc):
            f_retry = Retrying(
                retry_on_exception=retriable_slack_api_error,
                wait_fixed=int(exc.response.headers['Retry-After']) * MS_IN_SEC,
                stop_max_attempt_number=5)
            res = f_retry.call(f, *args, **kwargs)
            return res
        else:
            raise exc


def retriable_slack_api_error(exc):
    if (isinstance(exc, SlackApiError) and
            exc.response.headers.get('Retry-After')):
        return True
    return False


class MetaSlackController:
    """
    Using it to keep common logic between handler controllers and slack event
    controllers - new controller initialized for every call
    """

    def __init__(self, engine, config_cl):
        self.engine = engine
        self.config_cl = config_cl

    def __getattr__(self, item):
        # This hack is needed due to slack bolt code which passing only
        # explicitly defined arguments into the method.
        # full list of possible args taken from slack bolt code
        def _call(logger, client, req, request, resp, response, context,
                  body, options, shortcut, action, view, command, event,
                  message, step, ack, say, respond, next):
            slack_ctrl = SlackController(self.engine, self.config_cl)
            method = getattr(slack_ctrl, item)
            method_arg_names = inspect.getfullargspec(method).args
            method_args = []
            for a in method_arg_names:
                if a in locals() and a != 'self':
                    method_args.append(locals().get(a))
            try:
                return method(*method_args)
            except SlackApiError as exc:
                LOG.error('Slack API error: %s', str(exc))
                if exc.response.get('error') == 'missing_scope':
                    say_method = locals().get('say')
                    slack_ctrl.message_slack_permissions(say_method)
                else:
                    raise exc

        return _call


class SlackController(BaseController):
    def get_user(self, slack_user_id):
        return self.session.query(User).filter(
            User.slack_user_id == slack_user_id,
            User.deleted.is_(False),
        ).one_or_none()

    def is_user_connected(self, user, check_org=False):
        if user is None or user.auth_user_id is None:
            return False
        if check_org and user.organization_id is None:
            return False
        return True

    def app_home_opened(self, ack, body, say, logger):
        user_id = body['event']['user']
        team_id = body['team_id']
        channel_id = body['event']['channel']
        # message from this event only sent once,
        # so looking even for deleted user
        users = self.session.query(User).filter(
            User.slack_user_id == user_id,
        ).all()
        if not users:
            self._init_new_user(user_id, team_id, channel_id, logger, say)

    def _init_new_user(self, user_id, team_id, channel_id, logger, say):
        secret = gen_id()
        user = User(slack_user_id=user_id,
                    slack_team_id=team_id,
                    secret=secret,
                    slack_channel_id=channel_id)
        self.session.add(user)
        try:
            self.session.commit()
        except IntegrityError as exc:
            logger.exception('Unable to save user: %s', exc)
            raise
        message_blocks = get_welcome_message(
            public_ip=self.config_cl.public_ip(), secret=secret)
        say(message_blocks)

    def message(self, ack, body, say, logger):
        user_id = body['event']['user']
        team_id = body['team_id']
        channel_id = body['event']['channel']
        user = self.get_user(user_id)
        if user is None:
            self._init_new_user(user_id, team_id, channel_id, logger, say)
        ack()

    def log_request(self, logger, body, next):
        logger.debug(body)
        return next()

    def message_logout(self, ack, body, say, logger):
        slack_user_id = body['event']['user']
        user = self.get_user(slack_user_id)
        if not self.is_user_connected(user):
            self.message(ack, body, say, logger)
            ack()
            return

        auth_cl, _ = self.get_user_api_clients(user.auth_user_id)
        _, user_info = auth_cl.user_get(user.auth_user_id)
        say(get_disconnect_confirmation_message(
            user_email=user_info['email'],
            public_ip=self.config_cl.public_ip()))
        ack()

    def disconnect(self, ack, say, body, logger):
        slack_user_id = body['user']['id']
        user = self.get_user(slack_user_id)
        if not self.is_user_connected(user):
            ack()
            return

        auth_cl, _ = self.get_user_api_clients(user.auth_user_id)
        _, user_info = auth_cl.user_get(user.auth_user_id)

        now_ts = int(datetime.utcnow().timestamp())
        user.deleted_at = now_ts
        self.session.add(user)
        try:
            self.session.commit()
        except IntegrityError as exc:
            logger.exception('Unable to save user: %s', exc)
            raise

        _, user_info = auth_cl.user_update(
            user.auth_user_id, **{'slack_connected': False})

        say(get_disconnected_message(
            user_email=user_info['email'],
            public_ip=self.config_cl.public_ip()))
        ack()

    def message_org(self, ack, body, say, logger):
        slack_user_id = body['event']['user']
        user = self.get_user(slack_user_id)
        if not self.is_user_connected(user):
            ack()
            self.message(ack, body, say, logger)
            return

        _, rest_cl = self.get_user_api_clients(user.auth_user_id)
        _, org_resp = rest_cl.organization_list()
        say(get_org_switch_message(
            org_resp['organizations'], active_org_id=user.organization_id
        ))
        ack()

    def switch_org(self, ack, say, action, body, logger):
        slack_user_id = body['user']['id']
        user = self.get_user(slack_user_id)
        if not self.is_user_connected(user):
            ack()
            return

        target_org_id = action['value']

        _, rest_cl = self.get_user_api_clients(user.auth_user_id)
        _, employee_list = rest_cl.employee_list(
            target_org_id, current_only=True)
        employee = employee_list['employees'][0]

        user.organization_id = target_org_id
        user.employee_id = employee['id']
        self.session.add(user)
        try:
            self.session.commit()
        except IntegrityError as exc:
            logger.exception('Unable to save user: %s', exc)
            raise

        _, org = rest_cl.organization_get(target_org_id)
        say(get_org_switch_completed_message(org['name']))
        ack()

    def message_resources(self, ack, body, say, logger):
        slack_user_id = body['event']['user']
        user = self.get_user(slack_user_id)
        # slack raises timeout if we process request more than 3s
        # so we ack before api call
        ack()
        if not self.is_user_connected(user, check_org=True):
            self.message(ack, body, say, logger)
            return

        _, rest_cl = self.get_user_api_clients(user.auth_user_id)
        _, org = rest_cl.organization_get(user.organization_id)
        _, cloud_accounts = rest_cl.cloud_account_list(user.organization_id)
        tel_enabled = self.total_expense_limit_enabled(user.organization_id)
        if not cloud_accounts.get('cloud_accounts', []):
            say(get_ca_not_connected_message(
                org_name=org['name'],
                public_ip=self.config_cl.public_ip()),
                unfurl_links=False, unfurl_media=False)
            return

        _, expenses_resp = rest_cl.clean_expenses_get(
            organization_id=user.organization_id,
            start_date=0,
            end_date=int(datetime.utcnow().timestamp()),
            params={'owner_id': [user.employee_id], 'active': True}
        )

        shown_data = sorted(expenses_resp['clean_expenses'],
                            key=lambda x: x['cost'], reverse=True)[:7]
        total_count = len(expenses_resp['clean_expenses'])
        total_sum = round(sum([e['cost'] for e in expenses_resp[
            'clean_expenses']]), 2)

        resource_ids = [expense['resource_id'] for expense in shown_data]
        for i, resource in enumerate(resource_ids):
            _, resource_details = rest_cl.cloud_resource_get(
                resource, details=True)
            constraints = resource_details['details']['constraints']
            policies = resource_details['details']['policies']

            ttl_constr = None
            if constraints.get('ttl'):
                ttl_constr = constraints['ttl']
            elif policies.get('ttl', {}).get('active'):
                ttl_constr = policies['ttl']

            daily_expense_constr = None
            if constraints.get('daily_expense_limit'):
                daily_expense_constr = constraints['daily_expense_limit']
            elif policies.get('daily_expense_limit', {}).get('active'):
                daily_expense_constr = policies['daily_expense_limit']

            total_expense_constr = None
            if tel_enabled:
                if constraints.get('total_expense_limit'):
                    total_expense_constr = constraints['total_expense_limit']
                elif policies.get('total_expense_limit', {}).get('active'):
                    total_expense_constr = policies['total_expense_limit']

            def _check_expense_limit(expense_constr):
                return (expense_constr['limit'] != 0 and
                        shown_data[i]['cost'] / expense_constr['limit'] >=
                        EXPENSE_LIMIT_TO_SHOW)

            if ttl_constr:
                hrs = (ttl_constr['limit'] - datetime.utcnow().timestamp()) / SEC_IN_HRS
                if int(hrs) <= TTL_LIMIT_TO_SHOW:
                    shown_data[i]['ttl'] = hrs
            if (total_expense_constr and
                    _check_expense_limit(total_expense_constr)):
                shown_data[i]['total_expense_limit'] = total_expense_constr[
                    'limit']
            if (daily_expense_constr and
                    _check_expense_limit(daily_expense_constr)):
                shown_data[i]['daily_expense_limit'] = daily_expense_constr[
                    'limit']

        say(get_resources_message(
            org_id=user.organization_id, org_name=org['name'],
            shown_data=shown_data, public_ip=self.config_cl.public_ip(),
            total_count=total_count, total_sum=total_sum,
            currency=org['currency']))

    def resource_details(self, ack, say, action, body, logger):
        slack_user_id = body['user']['id']
        user = self.get_user(slack_user_id)
        if user is None or user.auth_user_id is None or user.organization_id is None:
            ack()
            return
        target_resource_id = action['value']

        _, rest_cl = self.get_user_api_clients(user.auth_user_id)
        ack()
        _, resource = rest_cl.cloud_resource_get(
            target_resource_id, details=True)
        _, org = rest_cl.organization_get(user.organization_id)
        tel_enabled = self.total_expense_limit_enabled(user.organization_id)
        constraint_types = ['ttl', 'daily_expense_limit']
        if tel_enabled:
            constraint_types.append('total_expense_limit')
        constraints = {}
        for constraint in constraint_types:
            if resource['details']['constraints'].get(constraint):
                constraints[constraint] = resource['details']['constraints'][
                    constraint]
                constraints[constraint]['constraint_type'] = 'resource specific'
            elif resource['details']['policies'].get(constraint, {}).get('active'):
                constraints[constraint] = resource['details']['policies'][
                    constraint]
                constraints[constraint]['constraint_type'] = 'pool policy'

        current_booking = None
        if resource['details'].get('shareable_bookings'):
            current_booking = self.get_current_booking(
                resource['details']['shareable_bookings'])
            if current_booking:
                current_booking['acquired_since'] = self._ts_to_string(
                    current_booking['acquired_since'])
                if current_booking['released_at']:
                    current_booking['released_at'] = self._ts_to_string(
                        current_booking['released_at'])
                else:
                    current_booking['released_at'] = 'Not set'

        say(get_resource_details_message(
            resource=resource, org_id=user.organization_id,
            public_ip=self.config_cl.public_ip(), booking=current_booking,
            currency=org['currency'], total_expense_limit_enabled=tel_enabled))

    def create_update_ttl_view(self, ack, action, client, body, say, logger):
        slack_user_id = body['user']['id']
        user = self.get_user(slack_user_id)
        resource_id = action['value']
        logger.info("Opened 'Update TTL' view for resource {}".format(
            resource_id))
        ack()
        if not self.is_user_connected(user, check_org=True):
            return

        _, rest_cl = self.get_user_api_clients(user.auth_user_id)
        _, resource = rest_cl.cloud_resource_get(
            resource_id, details=True)
        client.views_open(
            trigger_id=body["trigger_id"],
            view=get_update_ttl_form(resource, user.organization_id,
                                     self.config_cl.public_ip()))

    def update_ttl_submit(self, ack, body, client, view, say, logger):
        view_value = int(view["state"]["values"]["ttl_actions"]["based"][
            "selected_option"]["value"])
        resource_id = view["private_metadata"]
        user_id = body["user"]["id"]
        logger.info('Update TTL form input data: %s', view_value)
        ack()

        user = self.get_user(user_id)
        say.channel = user.slack_channel_id
        _, rest_cl = self.get_user_api_clients(user.auth_user_id)
        _, resource = rest_cl.cloud_resource_get(
            resource_id, details=True)
        try:
            if view_value != -1:
                limit = int(datetime.utcnow().timestamp()) + view_value * SEC_IN_HRS
                if resource["details"]["constraints"].get("ttl"):
                    rest_cl.resource_constraint_update(
                        resource["details"]["constraints"]["ttl"]["id"],
                        {"limit": limit})
                else:
                    rest_cl.resource_constraint_create(
                        resource_id, {"limit": limit, "type": "ttl"})
            else:
                rest_cl.resource_constraint_delete(
                    resource["details"]["constraints"]["ttl"]["id"])
            _, resource = rest_cl.cloud_resource_get(resource_id, details=True)
            self.constraint_updated(resource, say, body, logger)
        except HTTPError as exc:
            logger.exception(str(exc))
            client.chat_postMessage(
                channel=user.slack_channel_id,
                text=f"Resource constraint updating error: "
                     f"{exc.response.reason}")

    def constraint_updated(self, resource, say, body, logger):
        slack_user_id = body['user']['id']
        user = self.get_user(slack_user_id)
        say(get_constraint_updated(
            resource,
            org_id=user.organization_id,
            public_ip=self.config_cl.public_ip()))

    def ack_event(self, ack):
        ack()

    def member_joined_channel(self, client, ack, event, say):
        user_id = event['user']
        auth_info = client.auth_test()
        bot_user_id = auth_info['user_id']
        if user_id == bot_user_id:
            say(get_join_channel_message())
        ack()

    @staticmethod
    def _get_user_conversations(client, user, cursor='',
                                types='public_channel, private_channel',
                                exclude_archived=True):
        conversation_list = []
        while True:
            resp = retry_too_many_requests(
                client.users_conversations, user=user, cursor=cursor,
                types=types, limit=1000, exclude_archived=exclude_archived)
            cursor = resp['response_metadata']['next_cursor']
            conversation_list.extend(resp['channels'])
            if not cursor:
                break
        return conversation_list

    def _channels_map(self, client, user, exclude_archived=True):
        channels = self._get_user_conversations(
            client, user, exclude_archived=exclude_archived)
        return {ch['id']: ch['name'] for ch in channels}

    def message_alerts(self, client, ack, body, say, logger):
        slack_user_id = body['event']['user']
        bot_user = body['authorizations'][0]['user_id']
        user = self.get_user(slack_user_id)
        ack()

        if not self.is_user_connected(user, check_org=True):
            self.message(ack, body, say, logger)
            return

        _, rest_cl = self.get_user_api_clients(user.auth_user_id)
        _, org = rest_cl.organization_get(user.organization_id)

        _, pools = rest_cl.pools_get(user.organization_id,
                                     permission=['INFO_ORGANIZATION'])
        _, alerts = rest_cl.alert_list(org['id'])

        channel_map = self._channels_map(client, bot_user,
                                         exclude_archived=False)

        alert_list = []
        for alert in alerts['alerts']:
            if any(filter(lambda x: channel_map.get(x['slack_channel_id']),
                          alert['contacts'])):
                alert_list.append(alert)

        pool_map = {b['id']: b for b in pools['pools']}

        say(get_alert_list(
                alerts=alert_list, pool_map=pool_map,
                public_ip=self.config_cl.public_ip(),
                organization_id=org['id'], organization_name=org['name'],
                channel_map=channel_map, currency=org['currency']))

    def create_alert_view(self, ack, client, body, say, logger):
        slack_user_id = body['user']['id']
        bot_user = body['message']['user']
        user = self.get_user(slack_user_id)
        ack()

        if not self.is_user_connected(user, check_org=True):
            return

        view = client.views_open(
            trigger_id=body["trigger_id"],
            view=get_add_alert_modal_empty_template("Loading..."))
        view_id = view['view']['id']

        _, rest_cl = self.get_user_api_clients(user.auth_user_id)
        _, org = rest_cl.organization_get(user.organization_id)

        if self._channels_map(client, bot_user):
            client.views_update(
                view=get_select_alert_type_modal(org['name'],
                                                 private_metadata=bot_user),
                view_id=view_id)
        else:
            error_text = 'Error: Bot was not invited into any channel'
            client.views_update(
                view=get_add_alert_modal_empty_template(error_text),
                view_id=view_id)
            say(error_text)

    def update_alert_view(self,  ack, body, client, logger):
        view = body['view']
        view_id = view['id']
        view_values = view['state']['values']
        alert_type = view_values['alert_types']['alert_view_next'][
            'selected_option']['value']
        slack_user_id = body['user']['id']
        bot_user = view['private_metadata']
        ack()
        user = self.get_user(slack_user_id)

        if not self.is_user_connected(user, check_org=True):
            return

        _, rest_cl = self.get_user_api_clients(user.auth_user_id)
        _, org = rest_cl.organization_get(user.organization_id)
        _, pools = rest_cl.pools_get(user.organization_id,
                                     permission=['INFO_ORGANIZATION'])
        pool_map = {b['id']: b for b in pools['pools']}

        channel_map = self._channels_map(client, bot_user)

        alert_types = {
            'expense': get_add_expense_alert_modal,
            'constraint': get_add_constraint_envs_alert_modal,
            'env_change': get_add_constraint_envs_alert_modal
        }

        client.views_update(
            view=alert_types[alert_type](pool_map, channel_map, org['name'],
                                         currency=org['currency'],
                                         alert_type=alert_type),
            view_id=view_id)

    def create_alert_submit(self, ack, body, client, view, logger):
        view_values = view["state"]["values"]
        slack_user = body["user"]
        fields = [
            ('pool_id', str),
            ('include_children', bool),
            ('threshold', int),
            ('based', str),
            ('channel_id', str),
        ]
        input_data = {
            'threshold_type': 'percentage',
            'threshold': 0
        }
        for field, type_ in fields:
            view_value = view_values.get(field, {}).get(field)
            if view_value is not None:
                if 'selected_option' in view_value:
                    value = view_value['selected_option']
                else:
                    value = view_value['selected_options']
            else:
                continue
            if type_ == bool:
                input_data[field] = len(value) > 0
            else:
                input_data[field] = type_(value['value'])
        if not input_data.get('based'):
            input_data['based'] = view["private_metadata"]

        user_id = slack_user["id"]
        logger.info('input data: %s', input_data)
        ack()

        channel_id = input_data.pop('channel_id')
        input_data['contacts'] = [{
            'slack_channel_id': channel_id,
            'slack_team_id': slack_user['team_id']
        }]

        user = self.get_user(user_id)
        _, rest_cl = self.get_user_api_clients(user.auth_user_id)
        try:
            rest_cl.alert_create(user.organization_id, input_data)
        except HTTPError as exc:
            logger.exception(str(exc))
            client.chat_postMessage(
                channel=user.slack_channel_id,
                text=f"Failed to create alert: {exc.response.reason}")

    def delete_alert(self, ack, action, body, say, logger):
        slack_user_id = body['user']['id']
        user = self.get_user(slack_user_id)
        ack()

        if not self.is_user_connected(user, check_org=True):
            return

        _, rest_cl = self.get_user_api_clients(user.auth_user_id)

        alert_id = action['value']
        try:
            rest_cl.alert_delete(alert_id)
        except HTTPError as exc:
            logger.exception(str(exc))
            say(f"Failed to delete alert: {exc.response.reason}")

    def message_slack_permissions(self, say):
        say(get_not_have_slack_permissions_message())

    def get_current_booking(self, booking_list):
        now_ts = int(datetime.utcnow().timestamp())
        for booking in booking_list:
            if (booking['acquired_since'] <= now_ts < booking['released_at'] or
                    (booking['acquired_since'] <= now_ts and
                     booking['released_at'] == 0)):
                return booking

    def _ts_to_string(self, date_ts):
        date = datetime.utcfromtimestamp(date_ts)
        return datetime.strftime(date, "%m/%d/%Y %H:%M UTC")

    def get_booking_parameters(self, booking):
        if booking:
            since = self._ts_to_string(booking['acquired_since'])
            if booking['released_at']:
                until = self._ts_to_string(booking['released_at'])
            else:
                until = None
            return booking['acquired_by']['name'], since, until

    def message_envs(self, ack, body, say, logger):
        slack_user_id = body['event']['user']
        msg_text = body['event']['text']
        user = self.get_user(slack_user_id)
        ack()
        if not self.is_user_connected(user, check_org=True):
            self.message(ack, body, say, logger)
            return

        _, rest_cl = self.get_user_api_clients(user.auth_user_id)
        _, org = rest_cl.organization_get(user.organization_id)
        _, shareable_res = rest_cl.shareable_resources_list(
            user.organization_id)

        resource_status_map = {}
        if shareable_res.get('data'):
            shown_resources = sorted(shareable_res['data'],
                                     key=lambda x: x.get('name') or '')

            parser = argparse.ArgumentParser()
            parser.add_argument('envs', nargs="*", type=str)
            args = parser.parse_args(msg_text.split())
            if len(args.envs) > 1:
                envs_index = [i for i, v in enumerate(args.envs) if 'envs' in v]
                res_filter = ''.join(args.envs[envs_index[0] + 1:])
                if res_filter.startswith('"') and res_filter.endswith('"'):
                    res_filter = res_filter.strip('\"')
                    shown_resources = list(
                        filter(lambda x:
                               res_filter in x.get('resource_type') or
                               res_filter in x.get('name'), shown_resources))
                else:
                    res_filter = res_filter.lower()
                    shown_resources = list(
                        filter(
                            lambda x:
                            res_filter in (x.get('name') or '').lower() or
                            res_filter in (x.get('resource_type') or '').lower(),
                            shown_resources))

            shown_resources = shown_resources[:MAX_MSG_ENVS_LENGTH]
            for resource in shown_resources:
                if not resource.get('name'):
                    resource['name'] = resource['cloud_resource_id']
            for resource in shown_resources:
                bookings = resource.get('shareable_bookings')
                current_booking = self.get_current_booking(bookings)
                if current_booking:
                    book_params = self.get_booking_parameters(current_booking)
                    until = book_params[2]
                    if until:
                        booking_status = 'occupied until {0} by {1}'.format(
                            book_params[2], book_params[0])
                    else:
                        booking_status = 'occupied by {0}'.format(
                            book_params[0])
                else:
                    booking_status = 'available'
                resource_status_map[resource['id']] = booking_status
        else:
            shown_resources = []

        say(get_envs_message(
            user.organization_id, org['name'], shown_resources,
            resource_status_map, self.config_cl.public_ip()))

    def create_booking_view(self, ack, client, body, action):
        slack_user_id = body['user']['id']
        user = self.get_user(slack_user_id)
        ack()
        if not self.is_user_connected(user, check_org=True):
            return

        resource_id = action['value']
        _, rest_cl = self.get_user_api_clients(user.auth_user_id)
        _, resource = rest_cl.cloud_resource_get(resource_id)

        client.views_open(
            trigger_id=body["trigger_id"],
            view=get_add_bookings_form(resource, self.config_cl.public_ip()))

    def create_booking_submit(self, ack, body, client, view, logger):
        view_values = view['state']['values']
        user_id = body['user']['id']
        start_date_str = view_values['datepicker']['datepicker'][
            'selected_date']
        start_time_in_min = int(view_values['time_selector']['time_selector'][
                                    'selected_option']['value'])
        book_period_in_hrs = int(view_values['book_period']['book_period'][
                                    'selected_option']['value'])
        resource = view['private_metadata']
        user = self.get_user(user_id)
        ack()

        date = datetime.strptime(start_date_str, "%Y-%m-%d")
        acquired_since = date + timedelta(minutes=start_time_in_min)
        if book_period_in_hrs:
            released_at = acquired_since + timedelta(hours=book_period_in_hrs)
        else:
            released_at = 0

        _, rest_cl = self.get_user_api_clients(user.auth_user_id)
        resource_id = resource.split('/')[0]
        resource_name = resource.split('/')[1]
        book = {
            "acquired_since": int(acquired_since.timestamp()),
            "released_at": int(released_at.timestamp()) if released_at else 0,
            "resource_id": resource_id,
            "acquired_by_id": user.employee_id
        }
        try:
            rest_cl.shareable_book_create(user.organization_id, book)
            since = self._ts_to_string(int(acquired_since.timestamp()))
            text = 'Resource {0} is booked since {1}'.format(
                resource_name, since)
            if released_at:
                text = text + ' until {0}'.format(self._ts_to_string(
                    int(released_at.timestamp())))
            client.chat_postMessage(
                channel=user.slack_channel_id, text=text)
        except HTTPError as exc:
            logger.exception(str(exc))
            client.chat_postMessage(
                channel=user.slack_channel_id,
                text=f"Failed to create booking: {exc.response.reason}")

    def booking_details(self, ack, say, action, body, logger):
        slack_user_id = body['user']['id']
        user = self.get_user(slack_user_id)
        resource_id = action['value']
        ack()
        if not self.is_user_connected(user, check_org=True):
            self.message(ack, body, say, logger)
            return

        auth_user_id = user.auth_user_id
        auth_cl, rest_cl = self.get_user_api_clients(auth_user_id)
        _, org = rest_cl.organization_get(user.organization_id)
        _, resource = rest_cl.cloud_resource_get(resource_id, details=True)
        bookings = resource['details'].get('shareable_bookings')
        booking_data = []
        if bookings:
            is_admin = False
            bookings.sort(key=lambda x: x['acquired_since'])
            if len(bookings) > 10:
                bookings = bookings[:10]
            try:
                auth_cl.authorize(
                    'MANAGE_RESOURCES', 'cloud_resource', resource_id)
                is_admin = True
            except HTTPError:
                pass
            current_booking = self.get_current_booking(bookings)
            now_ts = int(datetime.utcnow().timestamp())
            _, employee_list = rest_cl.employee_list(org['id'])
            employee_id_map = {x['id']: x for x in employee_list['employees']}
            for booking in bookings:
                acquired_by_id = booking['acquired_by']['id']
                is_future = now_ts < booking['acquired_since']
                is_acquired_by = False
                if is_admin is False:
                    employee = employee_id_map.get(acquired_by_id, {})
                    if auth_user_id == employee.get('auth_user_id'):
                        is_acquired_by = True
                employee_name, since, until = self.get_booking_parameters(
                    booking)
                booking['acquired_since'] = since
                if not until:
                    booking['released_at'] = 'Not set'
                else:
                    booking['released_at'] = until
                if booking == current_booking:
                    if is_admin:
                        booking['allow_release'] = True
                        booking['allow_delete'] = True
                    if is_acquired_by:
                        booking['allow_release'] = True
                elif is_admin or (is_acquired_by and is_future):
                    booking['allow_delete'] = True
                booking_data.append(booking)

        say(get_booking_details_message(
            self.config_cl.public_ip(), resource_id, resource.get('name'),
            org['id'], org['name'], booking_data))

    def delete_booking(self, ack, action, body, say, logger):
        slack_user_id = body['user']['id']
        user = self.get_user(slack_user_id)
        booking_id = action['value']
        ack()

        if not self.is_user_connected(user, check_org=True):
            return

        _, rest_cl = self.get_user_api_clients(user.auth_user_id)

        try:
            _, book = rest_cl.shareable_book_get(booking_id)
            _, resource = rest_cl.cloud_resource_get(book['resource_id'])
            rest_cl.shareable_book_delete(booking_id)
            say("Booking for Resource %s has been deleted" % resource.get(
                'name'))
        except HTTPError as exc:
            logger.exception(str(exc))
            say(f"Failed to delete booking: {exc.response.reason}")

    def release_booking(self, ack, action, body, say, logger):
        slack_user_id = body['user']['id']
        user = self.get_user(slack_user_id)
        booking_id = action['value']
        ack()

        if not self.is_user_connected(user, check_org=True):
            return

        _, rest_cl = self.get_user_api_clients(user.auth_user_id)

        now_ts = int(datetime.utcnow().timestamp())
        try:
            _, book = rest_cl.shareable_book_get(booking_id)
            _, resource = rest_cl.cloud_resource_get(book['resource_id'])
            params = {'released_at': now_ts}
            rest_cl.shareable_book_release(booking_id, params)
            say("Booking for Resource %s has been released" % resource.get(
                'name'))
        except HTTPError as exc:
            logger.exception(str(exc))
            say(f"Failed to release booking: {exc.response.reason}")
