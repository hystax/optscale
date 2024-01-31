#!/usr/bin/env python
import os
import time
from datetime import datetime
from threading import Thread
from kombu.mixins import ConsumerMixin
from kombu.log import get_logger
from kombu import Connection
from kombu.utils.debug import setup_logging
from kombu import Exchange, Queue, binding
from requests import HTTPError
import urllib3

from optscale_client.auth_client.client_v2 import Client as AuthClient
from optscale_client.config_client.client import Client as ConfigClient
from optscale_client.rest_api_client.client_v2 import Client as RestClient
from optscale_client.slacker_client.client import Client as SlackerClient

LOG = get_logger(__name__)
QUEUE_NAME = 'slacker-task'
TASK_EXCHANGE = Exchange('activities-tasks', type='topic')
TASK_QUEUE = Queue(QUEUE_NAME, TASK_EXCHANGE, bindings=[
    binding(TASK_EXCHANGE, routing_key='booking.action.#'),
    binding(TASK_EXCHANGE, routing_key='alert.#')])
ACTION_MSG_MAP = {
    'booking_acquire': 'env_acquired',
    'booking_release': 'env_released',
    'constraint_violated': 'constraint_violated_alert',
    'expenses_alert': 'alert',
    'alert_added': 'alert_added',
    'alert_removed': 'alert_removed',
    'env_active_state_changed': 'env_active_state_changed',
    'env_property_updated': 'env_property_updated'
}


class InvalidExecutorTask(Exception):
    pass


class SlackerExecutorWorker(ConsumerMixin):
    def __init__(self, connection, config_cl):
        self.connection = connection
        self.config_cl = config_cl
        self._auth_cl = None
        self._rest_cl = None
        self._slacker_cl = None
        self.running = True
        self.thread = Thread(target=self.heartbeat)
        self.thread.start()

    @property
    def auth_cl(self):
        if self._auth_cl is None:
            self._auth_cl = AuthClient(
                url=self.config_cl.auth_url(),
                secret=self.config_cl.cluster_secret(),
                verify=False)
        return self._auth_cl

    @property
    def rest_cl(self):
        if self._rest_cl is None:
            self._rest_cl = RestClient(
                url=self.config_cl.restapi_url(),
                secret=self.config_cl.cluster_secret(),
                verify=False)
        return self._rest_cl

    @property
    def slacker_cl(self):
        if not self._slacker_cl:
            self._slacker_cl = SlackerClient(
                url=self.config_cl.slacker_url(),
                secret=self.config_cl.cluster_secret())
        return self._slacker_cl

    def send(self, type_, params, channel_id=None, team_id=None,
             auth_user_id=None, archived_channel_handle=False,
             organization_id=None, pool_id=None, warning_params=None):
        try:
            _, resp = self.slacker_cl.send_message(
                type_=type_, channel_id=channel_id, team_id=team_id,
                auth_user_id=auth_user_id, parameters=params)
        except HTTPError as exc:
            if 'archived' in exc.args[0] and archived_channel_handle:
                slack_managers = self._get_managers_connected_to_slack(
                    organization_id, pool_id)
                for manager in slack_managers:
                    params['warning'] = 'is_archived'
                    if warning_params:
                        params['warning_params'] = warning_params
                    self.slacker_cl.send_message(
                        type_=type_,
                        auth_user_id=manager['auth_user_id'],
                        parameters=params)
            else:
                raise

    def get_consumers(self, consumer, channel):
        return [consumer(queues=[TASK_QUEUE], accept=['json'],
                         callbacks=[self.process_task], prefetch_count=10)]

    @staticmethod
    def ts_to_slacker_time_format(timestamp):
        if timestamp:
            date = datetime.utcfromtimestamp(timestamp)
            return datetime.strftime(date, "%m/%d/%Y %H:%M UTC")
        else:
            return 'Not set'

    def get_pool_slack_channels_map(self, alerts):
        """
        Gets a map of alerts ids and slack contacts
        :param alerts: list of dictionary alerts
        :return: dict: {pool_id: {'alert_id': [(slack_channel_id, slack_team_id)]}}
        """
        pool_channels_map = {}
        for alert in alerts:
            contacts = [(x['slack_channel_id'], x['slack_team_id'])
                        for x in alert['contacts'] if x.get('slack_channel_id')]
            if not pool_channels_map.get(alert['pool_id']):
                pool_channels_map[alert['pool_id']] = {}
            if not pool_channels_map[alert['pool_id']].get(alert['id']):
                pool_channels_map[alert['pool_id']][alert['id']] = set()
            pool_channels_map[alert['pool_id']][alert['id']].update(contacts)
            if alert['include_children']:
                _, pool = self.rest_cl.pool_get(alert['pool_id'],
                                                children=True)
                children_pools = [x['id'] for x in pool['children']]
                for child in children_pools:
                    if not pool_channels_map.get(child):
                        pool_channels_map[child] = {alert['id']: set()}
                    if not pool_channels_map[child].get(alert['id']):
                        pool_channels_map[child][alert['id']] = set()
                    pool_channels_map[child][alert['id']].update(contacts)
        return pool_channels_map

    def resource_booking_status(self, current_booking):
        if not current_booking:
            booking_status = 'available'
        elif current_booking['released_at'] != 0:
            booking_status = 'occupied by {0} until {1}'.format(
                current_booking['acquired_by']['name'],
                self.ts_to_slacker_time_format(
                    current_booking['released_at']))
        else:
            booking_status = 'occupied by {0}'.format(
                current_booking['acquired_by']['name'])
        return booking_status

    @staticmethod
    def get_current_booking(bookings):
        now_ts = int(datetime.utcnow().timestamp())
        for booking in bookings:
            if booking['acquired_since'] <= now_ts and (
                    booking['released_at'] == 0 or
                    booking['released_at'] > now_ts):
                return booking

    @staticmethod
    def get_upcoming_booking(bookings, current_booking=None):
        acquired_since = int(datetime.utcnow().timestamp())
        if current_booking and current_booking.get('released_at'):
            acquired_since = current_booking['released_at']
        future_bookings = [x for x in bookings
                           if x['acquired_since'] > acquired_since]
        if future_bookings:
            return min(future_bookings, key=lambda x: x['acquired_since'])

    def get_resource_booking_info(self, resource_id):
        _, bookings = self.rest_cl.resource_bookings_get(resource_id)
        current_booking = self.get_current_booking(bookings['bookings'])
        booking_status = self.resource_booking_status(current_booking)
        upcoming_booking = self.get_upcoming_booking(bookings['bookings'],
                                                     current_booking)
        if upcoming_booking:
            upcoming_booking[
                'acquired_since'] = self.ts_to_slacker_time_format(
                upcoming_booking['acquired_since'])
            upcoming_booking['released_at'] = self.ts_to_slacker_time_format(
                upcoming_booking['released_at'])
        return current_booking, booking_status, upcoming_booking

    @staticmethod
    def get_resource_name(resource):
        return resource.get('name') or resource.get('cloud_resource_id')

    @staticmethod
    def check_action_object_type(action, object_type):
        action_objects_map = {
            'expenses_alert': ['pool'],
            'booking_acquire': ['booking'],
            'booking_release': ['booking'],
            'constraint_violated': ['pool', 'user'],
            'env_property_updated': ['resource'],
            'env_active_state_changed': ['resource'],
            'alert_added': ['pool_alert'],
            'alert_removed': ['pool_alert']
        }
        if object_type not in action_objects_map.get(action, []):
            raise InvalidExecutorTask('Invalid object type %s for task %s' % (
                object_type, action))

    def _get_managers_connected_to_slack(self, organization_id, pool_id):
        pool_permission = ['MANAGE_POOLS']
        _, pool_managers = self.rest_cl.authorized_employee_list(
            organization_id, 'pool', pool_id, pool_permission)
        _, users = self.auth_cl.user_list([x['auth_user_id']
                                           for x in pool_managers['employees']])
        slack_users = [x['id'] for x in users if x['slack_connected']]
        slack_managers = list(filter(lambda x: x['auth_user_id'] in slack_users,
                                     pool_managers['employees']))
        if not slack_managers:
            org_permission = ['EDIT_PARTNER']
            _, org_managers = self.rest_cl.authorized_employee_list(
                organization_id, 'organization', organization_id,
                org_permission)
            _, users = self.auth_cl.user_list(
                [x['auth_user_id'] for x in org_managers['employees']])
            slack_users = [x['id'] for x in users if x['slack_connected']]
            slack_managers = list(
                filter(lambda x: x['auth_user_id'] in slack_users,
                       org_managers['employees']))
        return slack_managers

    def get_warning_params(self, alert, pool, organization, channel_id):
        return {
            'organization_id': organization.get('id'),
            'public_ip': self.config_cl.public_ip(),
            'channel_id': channel_id,
            'based': alert.get('based'),
            'limit': pool.get('limit'),
            'threshold': alert.get('threshold'),
            'threshold_type': alert.get('threshold_type'),
            'include_children': alert.get('include_children'),
            'pool_id': pool.get('id'),
            'pool_name': pool.get('name'),
            'currency': organization.get('currency')
        }

    def execute_booking_acquire_release(self, organization_id, booking_id,
                                        action, object_type, meta=None):
        _, pool_alerts = self.rest_cl.alert_list(organization_id)
        slack_alerts = {x['id']: x for x in pool_alerts['alerts']
                        if x['based'] == 'env_change' and
                        any(contact.get('slack_channel_id')
                            for contact in x['contacts'])}
        if not slack_alerts:
            return
        _, booking = self.rest_cl.shareable_book_get(booking_id)

        resource_id = booking['resource_id']
        _, organization = self.rest_cl.organization_get(organization_id)
        current_booking, booking_status, upcoming_booking = \
            self.get_resource_booking_info(resource_id)
        _, resource = self.rest_cl.cloud_resource_get(resource_id)
        params = {'resource_id': resource_id,
                  'resource_name': self.get_resource_name(resource),
                  'public_ip': self.config_cl.public_ip(),
                  'org_id': organization_id,
                  'org_name': organization['name'],
                  'upcoming_booking': upcoming_booking,
                  'booking_status': booking_status}
        pool_channels_map = self.get_pool_slack_channels_map(
            slack_alerts.values())
        for alert_id, contacts in pool_channels_map.get(
                resource['pool_id']).items():
            _, alert = self.rest_cl.alert_get(alert_id)
            _, pool = self.rest_cl.pool_get(alert['pool_id'])
            for contact in contacts:
                warning_params = self.get_warning_params(
                    slack_alerts.get(alert_id, {}), pool, organization,
                    contact[0])
                self.send(
                    ACTION_MSG_MAP.get(action), params, contact[0], contact[1],
                    archived_channel_handle=True,
                    organization_id=organization_id, pool_id=pool['id'],
                    warning_params=warning_params)

    def execute_expense_alert(self, organization_id, pool_id, action,
                              object_type, meta):
        alert_id = meta['alert_id']
        pool_limit = meta.get('limit', 0)
        cost = meta.get('cost', 0)
        _, alert = self.rest_cl.alert_get(alert_id)
        _, organization = self.rest_cl.organization_get(organization_id)
        _, pool = self.rest_cl.pool_get(pool_id)
        params = {
            'pool_name': pool['name'],
            'organization_name': organization['name'],
            'organization_id': organization_id,
            'public_ip': self.config_cl.public_ip(),
            'pool_id': pool_id,
            'limit': pool_limit,
            'cost': cost,
            'based': alert['based'],
            'threshold': alert['threshold'],
            'threshold_type': alert['threshold_type'],
            'currency': organization['currency']
        }
        contacts = alert['contacts']
        alert_pool = pool
        if alert['pool_id'] != pool_id:
            _, alert_pool = self.rest_cl.pool_get(alert['pool_id'])
        for contact in contacts:
            if contact.get('slack_channel_id'):
                warning_params = self.get_warning_params(
                    alert, alert_pool, organization,
                    contact['slack_channel_id'])
                self.send(
                    ACTION_MSG_MAP.get(action), params,
                    contact['slack_channel_id'], contact['slack_team_id'],
                    archived_channel_handle=True,
                    organization_id=organization_id, pool_id=pool_id,
                    warning_params=warning_params)

    def _env_active_state_changed_params(self, resource, meta):
        return {
            'previous_state': meta.get('previous_state'),
            'new_state': meta.get('new_state')
        }

    def _env_property_updated_params(self, resource, meta):
        _, booking_status, _ = self.get_resource_booking_info(resource['id'])
        _, bookings = self.rest_cl.resource_bookings_get(resource['id'])

        return {
            'env_properties': meta.get('env_properties'),
            'current_properties': resource.get('env_properties'),
            'booking_status': booking_status
        }

    def execute_env_change_alert(self, organization_id, resource_id, action,
                                 object_type, meta):
        alert_id = meta['alert_id']
        _, alert = self.rest_cl.alert_get(alert_id)
        _, organization = self.rest_cl.organization_get(organization_id)
        _, resource = self.rest_cl.cloud_resource_get(resource_id)

        msg_type_func_map = {
            'env_active_state_changed': self._env_active_state_changed_params,
            'env_property_updated': self._env_property_updated_params
        }
        params = msg_type_func_map[action](resource, meta)
        params.update({
            'resource_id': resource_id,
            'resource_name': self.get_resource_name(resource),
            'public_ip': self.config_cl.public_ip(),
            'org_name': organization['name'],
            'org_id': organization_id,
        })

        contacts = alert['contacts']
        pool_id = alert['pool_id']
        _, alert_pool = self.rest_cl.pool_get(alert['pool_id'])
        for contact in contacts:
            if contact.get('slack_channel_id'):
                warning_params = self.get_warning_params(
                    alert, alert_pool, organization,
                    contact['slack_channel_id'])
                self.send(
                    ACTION_MSG_MAP.get(action), params,
                    contact['slack_channel_id'], contact['slack_team_id'],
                    archived_channel_handle=True,
                    organization_id=organization_id, pool_id=pool_id,
                    warning_params=warning_params)

    def execute_constraint_violated(self, organization_id, object_id,
                                    action, object_type, meta):
        _, organization = self.rest_cl.organization_get(organization_id)
        params = {
            'violations': meta.get('violations'),
            'public_ip': self.config_cl.public_ip(),
            'org_name': organization['name'],
            'org_id': organization_id,
        }
        if object_type == 'user':
            self.send(ACTION_MSG_MAP.get(action), params,
                      auth_user_id=object_id)
        elif object_type == 'pool':
            alert_id = meta.get('alert_id')
            if not alert_id:
                pass
            _, alert = self.rest_cl.alert_get(alert_id)
            for contact in alert['contacts']:
                if contact.get('slack_channel_id'):
                    _, pool = self.rest_cl.pool_get(alert['pool_id'])
                    warning_params = self.get_warning_params(
                        alert, pool, organization, contact['slack_channel_id'])
                    self.send(
                        ACTION_MSG_MAP.get(action), params,
                        contact['slack_channel_id'], contact['slack_team_id'],
                        archived_channel_handle=True,
                        organization_id=organization_id, pool_id=pool['id'],
                        warning_params=warning_params)
        else:
            raise InvalidExecutorTask(
                'Unsupported object_type %s for task type %s' % (object_type,
                                                                 action))

    def execute_alert_added_removed(self, organization_id, alert_id, action,
                                    object_type, meta):
        _, organization = self.rest_cl.organization_get(organization_id)
        alert = meta.get('alert', {})
        pool_id = meta.get('alert', {}).get('pool_id')
        _, pool = self.rest_cl.pool_get(pool_id)
        params = {
            'pool_name': pool['name'],
            'pool_id': pool['id'],
            'limit': pool['limit'],
            'initiator_name': meta.get('initiator_name'),
            'initiator_email': meta.get('initiator_email'),
            'public_ip': self.config_cl.public_ip(),
            'organization_id': organization_id,
            'currency': organization['currency']
        }
        for p in ['based', 'threshold', 'threshold_type', 'include_children']:
            params[p] = alert.get(p)

        for contact in alert['contacts']:
            if contact.get('slack_channel_id'):
                warning_params = self.get_warning_params(
                    alert, pool, organization, contact['slack_channel_id'])
                self.send(
                    ACTION_MSG_MAP.get(action), params,
                    contact['slack_channel_id'], contact['slack_team_id'],
                    archived_channel_handle=True,
                    organization_id=organization_id, pool_id=pool['id'],
                    warning_params=warning_params)

    def execute(self, task):
        organization_id = task.get('organization_id')
        object_id = task.get('object_id')
        object_type = task.get('object_type')
        action = task.get('action')
        meta = task.get('meta')
        LOG.info('Started processing for object %s task type for %s '
                 'for organization %s' % (object_id, action, organization_id))
        task_params = {
            'organization_id': organization_id,
            'object_type': object_type,
            'object_id': object_id,
            'action': action,
        }
        if any(map(lambda x: x is None, task_params.values())):
            raise InvalidExecutorTask(
                'Invalid task received: {}'.format(task))
        self.check_action_object_type(action, object_type)

        action_func_map = {
            'expenses_alert': self.execute_expense_alert,
            'booking_acquire': self.execute_booking_acquire_release,
            'booking_release': self.execute_booking_acquire_release,
            'constraint_violated': self.execute_constraint_violated,
            'env_property_updated': self.execute_env_change_alert,
            'env_active_state_changed': self.execute_env_change_alert,
            'alert_added': self.execute_alert_added_removed,
            'alert_removed': self.execute_alert_added_removed
        }
        try:
            func = action_func_map[action]
        except KeyError:
            raise InvalidExecutorTask(
                'Unknown action type: %s' % action)
        func(organization_id, object_id, action, object_type, meta)

    def process_task(self, body, message):
        try:
            self.execute(body)
        except Exception as exc:
            LOG.exception('Processing task failed: %s', str(exc))
        message.ack()

    def heartbeat(self):
        while self.running:
            self.connection.heartbeat_check()
            time.sleep(1)


if __name__ == '__main__':
    urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)
    debug = os.environ.get('DEBUG', False)
    log_level = 'DEBUG' if debug else 'INFO'
    setup_logging(loglevel=log_level, loggers=[''])

    config_cl = ConfigClient(
        host=os.environ.get('HX_ETCD_HOST'),
        port=int(os.environ.get('HX_ETCD_PORT')),
    )
    config_cl.wait_configured()
    conn_str = 'amqp://{user}:{pass}@{host}:{port}'.format(
        **config_cl.read_branch('/rabbit'))
    with Connection(conn_str) as conn:
        try:
            worker = SlackerExecutorWorker(conn, config_cl)
            worker.run()
        except KeyboardInterrupt:
            worker.running = False
            worker.thread.join()
            LOG.info('Shutdown received')
