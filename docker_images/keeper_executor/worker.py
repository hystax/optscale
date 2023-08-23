#!/usr/bin/env python
import hashlib
import os
import requests
import time
from threading import Thread
from kombu.mixins import ConsumerMixin
from kombu.log import get_logger
from kombu.utils.debug import setup_logging
from kombu import Exchange, Queue, binding, Connection
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from optscale_client.config_client.client import Client as ConfigClient
from optscale_client.rest_api_client.client_v2 import Client as RestClient
from optscale_client.report_client.client_v2 import Client as ReportClient
from optscale_client.auth_client.client_v2 import Client as AuthClient

LOG = get_logger(__name__)

EXCHANGE_NAME = 'activities-tasks'
QUEUE_NAME = 'keeper-task'

TASK_EXCHANGE = Exchange(EXCHANGE_NAME, type='topic')
ROUTING_KEYS = [
    'pool.#', 'employee.#', 'calendar_synchronization.#', 'cloud_account.#',
    'organization.*', 'cluster_type.#', 'report_import.#', 'resource.#',
    'alert.action.added', 'alert.action.removed', 'rule.#']
TASK_QUEUE = Queue(QUEUE_NAME, TASK_EXCHANGE, bindings=[
    binding(TASK_EXCHANGE, routing_key=routing_key)
    for routing_key in ROUTING_KEYS])


class KeeperExecutorWorker(ConsumerMixin):
    def __init__(self, connection, config_cl):
        self.connection = connection
        self.config_cl = config_cl
        self._auth_cl = None
        self._rest_cl = None
        self._report_cl = None
        self._action_func_details_map = {}
        self.running = True
        self.thread = Thread(target=self.heartbeat)
        self.thread.start()

    @property
    def rest_cl(self):
        if self._rest_cl is None:
            self._rest_cl = RestClient(
                url=self.config_cl.restapi_url(),
                secret=self.config_cl.cluster_secret(),
                verify=False)
        return self._rest_cl

    @property
    def report_cl(self):
        if not self._report_cl:
            self._report_cl = ReportClient(
                url=self.config_cl.keeper_url(),
                secret=self.config_cl.cluster_secret()
            )
        return self._report_cl

    @property
    def auth_cl(self):
        if not self._auth_cl:
            self._auth_cl = AuthClient(
                url=self.config_cl.auth_url(),
                secret=self.config_cl.cluster_secret()
            )
        return self._auth_cl

    @property
    def action_func_details_map(self):
        if not self._action_func_details_map:
            self._action_func_details_map = {
                'resource_assigned': (
                    self.execute_event_base,
                    ('{total_count} resources assigned to pool '
                     '{object_name} ({object_id}) to {employee_name} '
                     '({employee_id}) by {user_display_name} '
                     '({user_email})', 'N0089',
                     ['total_count', 'object_name', 'object_id',
                      'employee_name',
                      'employee_id', 'user_display_name', 'user_email'])),
                'assignment_request_accepted': (
                    self.execute_event_base,
                    ('Assignment request from {object_name} ({object_id}) to '
                     '{approver_name} ({approver_id}) for resource '
                     '{resource_name} ({resource_cloud_res_id}) was accepted',
                     'N0071', ['object_name', 'object_id', 'approver_name',
                               'approver_id', 'resource_name',
                               'resource_cloud_res_id'])),
                'assignment_request_declined': (
                    self.execute_event_base,
                    ('Assignment request from {object_name} ({object_id}) to '
                     '{approver_name} ({approver_id}) for resource '
                     '{resource_name} ({resource_cloud_res_id}) was declined',
                     'N0072', ['object_name', 'object_id', 'approver_name',
                               'approver_id', 'resource_name',
                               'resource_cloud_res_id'])),
                'calendar_warning': (self.execute_calendar_warning, None),
                'calendar_disconnected': (
                    self.execute_event_base,
                    ('Calendar {calendar_id} disconnected', 'N0118',
                     ['calendar_id'])),
                'calendar_connected': (
                    self.execute_event_base,
                    ('Calendar {calendar_id} connected', 'N0117',
                     ['calendar_id'])),
                'resources_discovered': (self.execute_resources_discovered,
                                         None),
                'pool_created': (
                    self.execute_event_base,
                    ('Pool {object_name} ({object_id}) created by '
                     '{user_display_name} ({user_email})', 'N0090',
                     ['object_name', 'object_id', 'user_display_name',
                      'user_email'])),
                'pool_deleted': (
                    self.execute_event_base,
                    ('Pool {object_name} has been deleted by '
                     '{user_display_name} ({user_email}). {res_count} '
                     'resources have been moved to pool {new_pool_name}. '
                     '{rules_cnt} rules have been redirected.', 'N0089',
                     ['object_name', 'user_display_name', 'user_email',
                      'res_count', 'new_pool_name', 'rules_cnt'])),
                'pool_updated': (
                    self.execute_event_base,
                    ('Pool {object_name} ({object_id}) updated with '
                     'parameters: {params} by {user_display_name} '
                     '({user_email})', 'N0091',
                     ['object_name', 'object_id', 'params', 'user_display_name',
                      'user_email'])),
                'rules_processing_started': (
                    self.execute_event_base,
                    ('Assignment Rules have been forced to run by '
                     '{user_display_name} ({user_email}). Target is {target}.',
                     'N0082', ['user_display_name', 'user_email', 'target'])),
                'rules_processing_completed': (
                    self.execute_event_base,
                    ('Assignment Rules processing for {target} completed. '
                     '{total} resources have been processed.',
                     'N0082', ['target', 'total'])),
                'root_assigned_resource': (
                    self.execute_event_base,
                    ('Invalid assignment tag detected. {resource_type} '
                     '{res_name} ({cloud_resource_id}) moved to organization '
                     'pool', 'N0076',
                     ['resource_type', 'res_name', 'cloud_resource_id'])),
                'rule_created': (
                    self.execute_event_base,
                    ('Rule {rule_name} ({rule_id}) created for pool '
                     '{pool_name} ({pool_id}) by {user_display_name} '
                     '({user_email}).', 'N0086',
                     ['rule_name', 'rule_id', 'pool_name', 'pool_id',
                      'user_display_name', 'user_email'])),
                'rule_updated': (
                    self.execute_event_base,
                    ('Rule {rule_name} ({rule_id}) updated by '
                     '{user_display_name} ({user_email}).',
                     'N0088', ['rule_name', 'rule_id', 'user_display_name',
                               'user_email'])),
                'rule_deleted': (
                    self.execute_event_base,
                    ('Rule {rule_name} ({rule_id}) deleted by '
                     '{user_display_name} ({user_email}).',
                     'N0087', ['rule_name', 'rule_id', 'user_display_name',
                               'user_email'])),
                'rule_applied': (
                    self.execute_event_base,
                    ('Rule applied: {rule_count} resources have been '
                     'automatically assigned to pool {pool_name} ({pool_id}) '
                     'according to rule {object_name} ({object_id})', 'N0081',
                     ['rule_count', 'pool_name', 'pool_id', 'object_name',
                      'object_id'])),
                'rule_deactivated': (
                    self.execute_event_base,
                    ('Rule is disabled: {object_name} ({object_id}) points to '
                     'the invalid pair of pool {pool_name} ({pool_id}) and '
                     'owner {owner_name} ({owner_id}). Rule has been disabled, '
                     'please fix and reenable it.', 'N0082',
                     ['object_name', 'object_id', 'pool_id', 'pool_name',
                      'owner_name', 'owner_id'])),
                'cluster_types_processing_started': (
                    self.execute_event_base,
                    ('Cluster types have been forced to run by '
                     '{user_display_name} ({user_email}).', 'N0104',
                     ['user_display_name', 'user_email'])),
                'cluster_types_processing_done': (
                    self.execute_event_base,
                    ('Cluster types reassignment completed. {total} resources '
                     'have been processed.', 'N0106',
                     ['total'])),
                'cluster_resources_deleted': (
                    self.execute_event_base,
                    ('Cluster Type {cluster_type_name} ({cluster_type_id}) '
                     'deleted, {modified_count} resources has been '
                     'automatically ungrouped.', 'N0107',
                     ['cluster_type_name', 'cluster_type_id',
                      'modified_count'])),
                'cluster_type_applied': (
                    self.execute_event_base,
                    ('Cluster type applied: {clustered_resources_count} '
                     'resources have been automatically grouped to '
                     '{clusters_count} clusters according to cluster type '
                     '{cluster_name} ({cluster_id})', 'N0105',
                     ['clustered_resources_count', 'clusters_count',
                      'cluster_name', 'cluster_id'])),
                'shareable_resource_deleted': (
                    self.execute_event_base,
                    ('Booking of the resource {object_name} ({object_id}) was '
                     'deleted by {user_display_name}',
                     'N0114',
                     ['object_name', 'object_id', 'user_display_name'])),
                'shareable_resource_changed': (
                    self.execute_event_base,
                    ('Booking of the resource {object_name} ({object_id}) was '
                     'changed by {user_display_name}',
                     'N0113',
                     ['object_name', 'object_id', 'user_display_name'])),
                'shareable_booking_released': (
                    self.execute_event_base,
                    ('Resource {object_name} ({object_id}) has been released',
                     'N0115',
                     ['object_name', 'object_id'])),
                'constraint_updated': (
                    self.execute_event_base,
                    ('{constraint_type} constraint for resource {object_name} '
                     '({object_id}) updated with parameters: {params} by '
                     '{user_display_name} ({user_email})',
                     'N0101',
                     ['constraint_type', 'object_name', 'object_id', 'params',
                      'user_display_name', 'user_email'])),
                'constraint_deleted': (
                    self.execute_event_base,
                    ('{constraint_type} constraint for resource {object_name} '
                     '({object_id}) deleted by {user_display_name} '
                     '({user_email})', 'N0100',
                     ['constraint_type', 'object_name', 'object_id',
                      'user_display_name', 'user_email'])),
                'constraint_created': (
                    self.execute_event_base,
                    ('{constraint_type} constraint for resource {object_name} '
                     '({object_id}) created by {user_display_name} '
                     '({user_email})', 'N0099',
                     ['constraint_type', 'object_name', 'object_id',
                      'user_display_name', 'user_email'])),
                'policy_updated': (
                    self.execute_event_base,
                    ('{policy_type} policy for pool {object_name} '
                     '({object_id}) updated with parameters: {params} by '
                     '{user_display_name} ({user_email})', 'N0096',
                     ['policy_type', 'object_name', 'object_id', 'params',
                      'user_display_name', 'user_email'])),
                'policy_enabled': (self.execute_policy_action, None),
                'policy_disabled': (self.execute_policy_action, None),
                'policy_created': (self.execute_policy_action, None),
                'policy_deleted': (self.execute_policy_action, None),
                'recommendations_dismissed': (
                    self.execute_event_base,
                    ('Recommendation {recommendation} dismissed for resource '
                     '{object_name} ({object_id}) by {user_display_name} '
                     '({user_email})', 'N0084',
                     ['recommendation', 'object_name', 'object_id',
                      'user_display_name', 'user_email'])),
                'recommendations_reactivated': (
                    self.execute_event_base,
                    ('Recommendation {recommendation} reactivated for resource '
                     '{object_name} ({object_id}) by {user_display_name} '
                     '({user_email})', 'N0085',
                     ['recommendation', 'object_name', 'object_id',
                      'user_display_name', 'user_email'])),
                'recalculation_started': (
                    self.execute_event_base,
                    ('Cost model changed. Expense recalculation for cloud '
                     'account {object_name} ({cloud_account_id}) started.',
                     'N0109', ['object_name', 'cloud_account_id'])),
                'recalculation_completed': (
                    self.execute_event_base,
                    ('Expense recalculation for cloud account {object_name} '
                     '({cloud_account_id}) completed successfully.', 'N0110',
                     ['object_name', 'cloud_account_id'])),
                'recalculation_failed': (
                    self.execute_event_base,
                    ('Expense recalculation for cloud account {object_name} '
                     '({cloud_account_id}) failed: {error_reason}', 'N0111',
                     ['object_name', 'cloud_account_id', 'error_reason'])),
                'report_import_completed': (
                    self.execute_event_base,
                    ('Billing data import for cloud account {object_name} '
                     '({cloud_account_id}) finished successfully', 'N0069',
                     ['object_name', 'cloud_account_id'])),
                'report_import_failed': (
                    self.execute_event_base,
                    ('Billing data import for cloud account {object_name} '
                     '({cloud_account_id}) failed: {error_reason}', 'N0070',
                     ['object_name', 'cloud_account_id', 'error_reason'])),
                'cloud_account_warning': (
                    self.execute_event_base,
                    ('Cloud account {object_name} ({object_id}) '
                     'capabilities may be degraded: {reason}', 'N0102',
                     ['object_name', 'object_id', 'reason'])),
                'cloud_account_created': (
                    self.execute_event_base,
                    ('Cloud account {object_name} ({object_id}) created',
                     'N0066', ['object_name', 'object_id'])),
                'cloud_account_updated': (
                    self.execute_event_base,
                    ('Cloud account {object_name} ({object_id}) updated',
                     'N0067', ['object_name', 'object_id'])),
                'cloud_account_deleted': (
                    self.execute_event_base,
                    ('Cloud account {object_name} ({object_id}) deleted',
                     'N0068', ['object_name', 'object_id'])),
                'employee_invited': (
                    self.execute_event_base,
                    ('Employee {email} invited by {user_display_name} '
                     '({user_email}) with roles: {scope_purposes}', 'N0097',
                     ['email', 'user_display_name', 'user_email',
                      'scope_purposes'])),
                'organization_updated': (
                    self.execute_event_base,
                    ('Organization {object_name} ({object_id}) updated',
                     'N0029', ['object_name', 'object_id'])),
                'organization_created': (
                    self.execute_event_base,
                    ('Organization {object_name} ({object_id}) created',
                     'N0027', ['object_name', 'object_id'])),
                'organization_deleted': (
                    self.execute_event_base,
                    ('Organization {object_name} ({object_id}) deleted',
                     'N0028', ['object_name', 'object_id'])),
                'alert_added': (self.execute_alert_added_removed, None),
                'alert_removed': (self.execute_alert_added_removed, None),
                'technical_audit_submit': (
                    self.execute_event_base,
                    ('Organization {object_name} ({object_id}) has been '
                     'submitted for technical audit by employee '
                     '{employee_name} ({employee_id})', 'N0120',
                     ['object_name', 'object_id', 'employee_name',
                      'employee_id']))
            }
        return self._action_func_details_map

    def get_consumers(self, consumer, channel):
        return [consumer(queues=[TASK_QUEUE], accept=['json'],
                         callbacks=[self.process_task])]

    def get_user_id(self, token):
        user_digest = hashlib.md5(token.encode('utf-8')).hexdigest()
        _, token_meta = self.auth_cl.token_meta_get([user_digest])
        return token_meta.get(user_digest, {}).get('user_id')

    def _get_user(self, token):
        user_id = self.get_user_id(token)
        if user_id is None:
            return {}
        self.auth_cl.token = token
        _, user = self.auth_cl.user_get(user_id)
        return user

    def _get_user_info(self, token):
        if not token:
            return None, None, None
        user_info = {}
        try:
            user_info = self._get_user(token)
        except requests.exceptions.HTTPError as ex:
            LOG.exception("Service call error: %s", str(ex))
        user_id = user_info.get('id', None)
        user_display_name = user_info.get('display_name', None)
        user_email = user_info.get('email', None)
        return user_id, user_display_name, user_email

    def _get_action_func_details_map(self, action):
        return self.action_func_details_map.get(action)

    def execute_event(
            self, evt_class, organization_id, level='INFO', object_id=None,
            object_type=None, object_name=None, description=None,
            localized=None, ack=False, token=None, user_display_name=None,
            user_id=None):
        if token and not user_id and not user_display_name:
            user_id, user_display_name, user_email = self._get_user_info(token)
        event = {
            'level': level,
            'evt_class': evt_class,
            'object_id': object_id,
            'object_type': object_type,
            'object_name': object_name,
            'organization_id': organization_id,
            'description': description,
            'localized': localized,
            'ack': ack,
            'initiator_id': user_id,
            'initiator_name': user_display_name,
        }
        self.report_cl.event_submit(**event)

    def execute_event_base(
            self, action, organization_id, level='INFO', object_id=None,
            object_type=None, object_name=None, ack=False, token=None,
            meta=None):
        action_value = self._get_action_func_details_map(action)
        if not action_value:
            LOG.error('Invalid action: %s', action)
            return
        _, (description_tmp, localized_code, param_list) = action_value
        user_id, user_display_name, user_email = self._get_user_info(token)
        if not meta:
            meta = {}
        meta['organization_id'] = organization_id
        meta['object_id'] = object_id
        meta['object_type'] = object_type
        meta['user_id'] = user_id
        meta['user_display_name'] = user_display_name
        meta['user_email'] = user_email
        params = {param: meta.get(param) for param in param_list}
        description = description_tmp.format(**params)
        localized_tmp = localized_code + '(' + ','.join(
            ['{' + param + '}' for param in param_list]) + ')'
        localized = localized_tmp.format(**params)
        self.execute_event(
            action.upper(), organization_id, object_id=object_id,
            object_type=object_type, object_name=object_name,
            description=description, localized=localized, level=level,
            token=token, user_id=user_id, user_display_name=user_display_name,
            ack=ack)

    def execute_resources_discovered(
            self, action, organization_id, level='INFO', object_id=None,
            object_type=None, object_name=None, ack=False, token=None,
            meta=None):
        stat = meta.get('stat')
        fmt_args = {
            'discovered': stat['total'],
            'cloud_acc_id': object_id,
            'cloud_acc_name': object_name
        }
        desc = ("{discovered} new resources discovered for cloud account "
                "{cloud_acc_name} ({cloud_acc_id})")
        localized = 'N0080({discovered},{cloud_acc_name},{cloud_acc_id})'
        if stat['clusters']:
            fmt_args.update({
                'clusters': len(stat['clusters']),
                'clustered': stat['clustered']
            })
            desc += ('. {clustered} of them were assembled into {clusters} '
                     'clusters')
            localized = ('N0080({discovered},{cloud_acc_name},{cloud_acc_id}'
                         ',{clustered},{clusters})')

        self.execute_event(
            action.upper(), organization_id, object_id=object_id,
            object_type=object_type, object_name=object_name,
            description=desc.format(**fmt_args),
            localized=localized.format(**fmt_args), ack=ack, token=token,
            level=level)

    def execute_calendar_warning(
            self, action, organization_id, level='WARNING', object_id=None,
            object_type=None, object_name=None, ack=False, token=None,
            meta=None):
        is_observer_message = meta.pop('is_observer', False)
        calendar_id = meta.pop('calendar_id', None)
        reason = meta.pop('reason', None)
        if is_observer_message:
            description = ('Calendar {calendar_id} synchronization warning: '
                           '{reason}'.format(calendar_id=calendar_id,
                                             reason=reason))
            localized = 'N0119({calendar_id}, {reason})'.format(
                calendar_id=calendar_id, reason=reason)
        else:
            description = ("Unable to clean up calendar %s "
                           "events during disconnection" % calendar_id)
            if reason is not None:
                description = '%s - %s' % (description, reason)
            localized = 'N0116({calendar_id})'.format(calendar_id=calendar_id)
        self.execute_event(
            action.upper(), organization_id, level=level, object_id=object_id,
            object_type=object_type, description=description,
            localized=localized, token=token, ack=ack)

    def execute_policy_action(
            self, action, organization_id, level='INFO', object_id=None,
            object_type=None, object_name=None, ack=False, token=None,
            meta=None):
        localized_code = {
            'policy_enabled': 'N0092',
            'policy_disabled': 'N0093',
            'policy_created': 'N0094',
            'policy_deleted': 'N0095'
        }.get(action)
        if not localized_code:
            LOG.error('Invalid action: %s', action)
            return
        action_type = action.split('_', 1)[1]
        policy_type = meta.pop('policy_type', None)
        user_id, user_display_name, user_email = self._get_user_info(token)
        description = ('{policy_type} policy for pool {pool_name} ({pool_id}) '
                       '{action_type} by {user_name} ({user_email})').format(
            policy_type=policy_type, pool_name=object_name, pool_id=object_id,
            action_type=action_type, user_name=user_display_name,
            user_email=user_email)
        localized = ('{localized_code}({policy_type},{pool_name},{pool_id},'
                     '{action_type},{user_name},{user_email})').format(
            localized_code=localized_code, policy_type=policy_type,
            pool_name=object_name, pool_id=object_id,
            action_type=action_type, user_name=user_display_name,
            user_email=user_email)
        self.execute_event(
            action.upper(), organization_id, level=level, object_id=object_id,
            object_type=object_type, object_name=object_name,
            description=description, localized=localized, token=token,
            user_id=user_id, user_display_name=user_display_name, ack=ack)

    def execute_alert_added_removed(
            self, action, organization_id, level='INFO', object_id=None,
            object_type=None, object_name=None, ack=False, token=None,
            meta=None):
        action_map = {
            'alert_added': 'created',
            'alert_removed': 'deleted'
        }
        alert = meta.pop('alert', None)
        pool_name = meta.pop('pool_name', None)
        with_subpools = meta.pop('with_subpools', None)
        warn_type = meta.pop('warn_type', None)
        threshold = str(alert['threshold'])
        if alert['threshold_type'] == 'percentage':
            threshold += '%'
        action_value = action_map.get(action)
        if not action_value:
            LOG.error('Invalid action: %s', action)
            return
        contact_type = []
        if any(bool(
                contact['slack_channel_id']) for contact in alert['contacts']):
            contact_type.append('slack')
        if any(bool(
                contact['employee_id']) for contact in alert['contacts']):
            contact_type.append('email')
        contact_type = "/".join(contact_type)
        user_id, user_display_name, user_email = self._get_user_info(token)
        params = {
            'username': user_display_name,
            'email': user_email,
            'action': action_value,
            'contact_type': contact_type,
            'pool_name': pool_name,
            'with_subpools': with_subpools,
            'warn_type': warn_type
        }
        if warn_type in ['constraint violation', 'environment changes']:
            description = (
                '{username}({email}) has {action} {contact_type} alert '
                'with {warn_type} type for pool {pool_name}{with_subpools}'
            ).format(**params)
            localized = (
                'N0121({username}, {email}, {action}, {contact_type},'
                '{warn_type}, {pool_name}, {with_subpools})').format(**params)
        elif warn_type in ['expenses', 'forecast']:
            params.update({'threshold': threshold})
            description = (
                '{username}({email}) has {action} {contact_type} alert '
                'for pool {pool_name}{with_subpools}, with {warn_type} '
                'threshold {threshold} of pool limit').format(**params)
            localized = (
                'N0103({username}, {email}, {action}, {contact_type},'
                '{pool_name}, {with_subpools}, {warn_type}, {threshold})'
            ).format(**params)
        else:
            LOG.error('Invalid warn_type: %s', warn_type)
            return
        self.execute_event(
            ('ALERT_' + action_value).upper(), organization_id, level=level,
            object_id=object_id, object_type=object_type,
            object_name=object_name, description=description,
            localized=localized, token=token, user_id=user_id,
            user_display_name=user_display_name, ack=ack)

    def execute(self, task):
        organization_id = task.get('organization_id')
        action = task.get('action')
        object_id = task.get('object_id')
        object_type = task.get('object_type')
        meta = task.get('meta', {})
        object_name = meta.get('object_name', None)
        level = meta.get('level', 'INFO')
        ack = meta.get('ack', False)
        token = meta.get('token', None)
        task_params = {
            'action': action,
            'organization_id': organization_id,
            'level': level,
            'object_id': object_id,
            'object_type': object_type,
            'object_name': object_name,
            'ack': ack,
            'token': token,
            'meta': meta
        }
        required_params = ['organization_id', 'object_id', 'object_type',
                           'action', 'level', 'ack']
        if any(map(lambda x: task_params.get(x) is None, required_params)):
            raise Exception('Invalid task received: {}'.format(task))
        action_func, _ = (self._get_action_func_details_map(action) or
                          (None, None))
        LOG.info('Started processing for object %s task type for %s '
                 'for organization %s' % (object_id, action, organization_id))
        if not action_func:
            LOG.warning('Unknown action type: %s. Skipping' % action)
            return
        action_func(**task_params)

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
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
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
            worker = KeeperExecutorWorker(conn, config_cl)
            worker.run()
        except KeyboardInterrupt:
            worker.running = False
            worker.thread.join()
            LOG.info('Shutdown received')
