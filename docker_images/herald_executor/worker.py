#!/usr/bin/env python
import calendar
import os
import time
import uuid
from enum import Enum
from collections import defaultdict, OrderedDict
from datetime import datetime, timedelta, timezone
from threading import Thread
from kombu.mixins import ConsumerMixin
from kombu.log import get_logger
from kombu import Connection
from kombu.utils.debug import setup_logging
from kombu import Exchange, Queue, binding
import urllib3

from optscale_client.config_client.client import Client as ConfigClient
from optscale_client.rest_api_client.client_v2 import Client as RestClient
from optscale_client.herald_client.client_v2 import Client as HeraldClient
from optscale_client.auth_client.client_v2 import Client as AuthClient

LOG = get_logger(__name__)

EXCHANGE_NAME = 'activities-tasks'
QUEUE_NAME = 'herald-task'

ENTITY_FIELD_MAP = {
    'pool': 'pool_id',
    'owner': 'owner_id',
    'cloud_account': 'cloud_account_id'
}
CONSTRAINT_TYPES = ['resource_count_anomaly', 'expense_anomaly',
                    'resource_quota', 'recurring_budget', 'expiring_budget',
                    'tagging_policy']
NOT_SET = 'Not set'
MANAGER_ROLE = 'optscale_manager'
REGULAR_IDENTITY = 'regular'
SECONDS_IN_DAY = 24 * 60 * 60

TASK_EXCHANGE = Exchange(EXCHANGE_NAME, type='topic')
TASK_QUEUE = Queue(QUEUE_NAME, TASK_EXCHANGE, bindings=[
    binding(TASK_EXCHANGE, routing_key='booking.action.#'),
    binding(TASK_EXCHANGE, routing_key='alert.violation.#'),
    binding(TASK_EXCHANGE, routing_key='constraint.violation.#'),
    binding(
        TASK_EXCHANGE,
        routing_key='organization.recommendation.new_security_recommendation'),
    binding(TASK_EXCHANGE,
            routing_key='organization.recommendation.saving_spike'),
    binding(TASK_EXCHANGE, routing_key='organization.report_import.passed'),
    binding(TASK_EXCHANGE, routing_key='insider.error.sslerror')
])


CURRENCY_MAP = {
    "AED": "د.إ",
    "AFN": "؋",
    "ALL": "L",
    "AMD": "֏",
    "ANG": "ƒ",
    "AOA": "Kz",
    "ARS": "$",
    "AUD": "$",
    "AWG": "ƒ",
    "AZN": "₼",
    "BAM": "KM",
    "BBD": "$",
    "BDT": "৳",
    "BGN": "лв",
    "BHD": ".د.ب",
    "BIF": "FBu",
    "BMD": "$",
    "BND": "$",
    "BOB": "$b",
    "BRL": "R$",
    "BSD": "$",
    "BTC": "฿",
    "BTN": "Nu.",
    "BWP": "P",
    "BYR": "Br",
    "BYN": "Br",
    "BZD": "BZ$",
    "CAD": "CA$",
    "CDF": "FC",
    "CHF": "CHF",
    "CLP": "$",
    "CNY": "¥",
    "COP": "$",
    "CRC": "₡",
    "CUC": "$",
    "CUP": "₱",
    "CVE": "$",
    "CZK": "Kč",
    "DJF": "Fdj",
    "DKK": "kr",
    "DOP": "RD$",
    "DZD": "دج",
    "EEK": "kr",
    "EGP": "£",
    "ERN": "Nfk",
    "ETB": "Br",
    "ETH": "Ξ",
    "EUR": "€",
    "FJD": "$",
    "FKP": "£",
    "GBP": "£",
    "GEL": "₾",
    "GGP": "£",
    "GHC": "₵",
    "GHS": "GH₵",
    "GIP": "£",
    "GMD": "D",
    "GNF": "FG",
    "GTQ": "Q",
    "GYD": "$",
    "HKD": "$",
    "HNL": "L",
    "HRK": "kn",
    "HTG": "G",
    "HUF": "Ft",
    "IDR": "Rp",
    "ILS": "₪",
    "IMP": "£",
    "INR": "₹",
    "IQD": "ع.د",
    "IRR": "﷼",
    "ISK": "kr",
    "JEP": "£",
    "JMD": "J$",
    "JOD": "JD",
    "JPY": "¥",
    "KES": "KSh",
    "KGS": "лв",
    "KHR": "៛",
    "KMF": "CF",
    "KPW": "₩",
    "KRW": "₩",
    "KWD": "KD",
    "KYD": "$",
    "KZT": "лв",
    "LAK": "₭",
    "LBP": "£",
    "LKR": "₨",
    "LRD": "$",
    "LSL": "M",
    "LTC": "Ł",
    "LTL": "Lt",
    "LVL": "Ls",
    "LYD": "LD",
    "MAD": "MAD",
    "MDL": "lei",
    "MGA": "Ar",
    "MKD": "ден",
    "MMK": "K",
    "MNT": "₮",
    "MOP": "MOP$",
    "MRO": "UM",
    "MRU": "UM",
    "MUR": "₨",
    "MVR": "Rf",
    "MWK": "MK",
    "MXN": "$",
    "MYR": "RM",
    "MZN": "MT",
    "NAD": "$",
    "NGN": "₦",
    "NIO": "C$",
    "NOK": "kr",
    "NPR": "₨",
    "NZD": "$",
    "OMR": "﷼",
    "PAB": "B/.",
    "PEN": "S/.",
    "PGK": "K",
    "PHP": "₱",
    "PKR": "₨",
    "PLN": "zł",
    "PYG": "Gs",
    "QAR": "﷼",
    "RMB": "￥",
    "RON": "lei",
    "RSD": "Дин.",
    "RUB": "₽",
    "RWF": "R₣",
    "SAR": "﷼",
    "SBD": "$",
    "SCR": "₨",
    "SDG": "ج.س.",
    "SEK": "kr",
    "SGD": "$",
    "SHP": "£",
    "SLL": "Le",
    "SOS": "S",
    "SRD": "$",
    "SSP": "£",
    "STD": "Db",
    "STN": "Db",
    "SVC": "$",
    "SYP": "£",
    "SZL": "E",
    "THB": "฿",
    "TJS": "SM",
    "TMT": "T",
    "TND": "د.ت",
    "TOP": "T$",
    "TRL": "₤",
    "TRY": "₺",
    "TTD": "TT$",
    "TVD": "$",
    "TWD": "NT$",
    "TZS": "TSh",
    "UAH": "₴",
    "UGX": "USh",
    "USD": "$",
    "UYU": "$U",
    "UZS": "лв",
    "VEF": "Bs",
    "VND": "₫",
    "VUV": "VT",
    "WST": "WS$",
    "XAF": "FCFA",
    "XBT": "Ƀ",
    "XCD": "$",
    "XOF": "CFA",
    "XPF": "₣",
    "YER": "﷼",
    "ZAR": "R",
    "ZWD": "Z$",
}


def get_nil_uuid():
    return str(uuid.UUID(int=0))


class HeraldTemplates(Enum):
    ANOMALY_DETECTION = 'anomaly_detection_alert'
    EXPIRING_BUDGET = 'organization_policy_expiring_budget'
    RECURRING_BUDGET = 'organization_policy_recurring_budget'
    RESOURCE_QUOTA = 'organization_policy_quota'
    ENVIRONMENT_CHANGES = 'environment_changes'
    NEW_SECURITY_RECOMMENDATION = 'new_security_recommendation'
    POOL_ALERT = 'alert'
    SAVING_SPIKE = 'saving_spike'
    RESOURCE_OWNER_VIOLATION_ALERT = 'resource_owner_violation_alert'
    TAGGING_POLICY = 'organization_policy_tagging'
    REPORT_IMPORT_PASSED = 'report_imports_passed_for_org'
    INSIDER_SSLERROR = 'insider_prices_sslerror'


class HeraldExecutorWorker(ConsumerMixin):
    def __init__(self, connection, config_cl):
        self.connection = connection
        self.config_cl = config_cl
        self._rest_cl = None
        self._herald_cl = None
        self._auth_cl = None
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
    def herald_cl(self):
        if not self._herald_cl:
            self._herald_cl = HeraldClient(
                url=self.config_cl.herald_url(),
                secret=self.config_cl.cluster_secret()
            )
        return self._herald_cl

    @property
    def auth_cl(self):
        if not self._auth_cl:
            self._auth_cl = AuthClient(
                url=self.config_cl.auth_url(),
                secret=self.config_cl.cluster_secret()
            )
        return self._auth_cl

    def get_consumers(self, consumer, channel):
        return [consumer(queues=[TASK_QUEUE], accept=['json'],
                         callbacks=[self.process_task], prefetch_count=10)]

    def get_auth_users(self, user_ids):
        _, response = self.auth_cl.user_list(user_ids)
        return response

    def get_owner_manager_infos(self, organization_id,
                                tenant_auth_user_ids=None):
        auth_users = []
        if tenant_auth_user_ids:
            auth_users = self.get_auth_users(tenant_auth_user_ids)
        all_user_info = {auth_user['id']: {
            'display_name': auth_user.get('display_name'),
            'email': auth_user.get('email')
        } for auth_user in auth_users}

        _, org_managers = self.auth_cl.user_roles_get(
            scope_ids=[organization_id],
            role_purposes=[MANAGER_ROLE])
        for manager in org_managers:
            user_id = manager['user_id']
            if not tenant_auth_user_ids or user_id not in tenant_auth_user_ids:
                all_user_info[user_id] = {
                    'display_name': manager.get('user_display_name'),
                    'email': manager.get('user_email')
                }
        return all_user_info

    def _get_service_emails(self):
        return self.config_cl.optscale_email_recipient()

    @staticmethod
    def _filter_bookings(shareable_bookings, resource_id, now_ts):
        result = []
        for booking in shareable_bookings:
            if (booking['resource_id'] != resource_id or (
                    booking['released_at'] != 0 and
                    booking['released_at'] <= now_ts)):
                continue
            result.append(booking)
        return result

    @staticmethod
    def _get_organization_params(organization):
        return {
            'id': organization['id'],
            'name': organization['name'],
            'currency_code': CURRENCY_MAP.get(organization['currency'], '$')
        }

    def send_environment_changes(self, resource, status_changed_info,
                                 organization_id):
        is_available = resource.get('active', False)
        cloud_account_id = resource.get('cloud_account_id')
        _, cloud_account = self.rest_cl.cloud_account_get(cloud_account_id)
        _, organization = self.rest_cl.organization_get(
            cloud_account['organization_id'])
        pool_id = resource.get('pool_id')
        _, pool = self.rest_cl.pool_get(pool_id)
        if cloud_account is None or pool is None:
            LOG.error('Resource cloud account %s or pool %s is not exists',
                      cloud_account, pool)
            return
        env_properties = OrderedDict(resource.get('env_properties', {}))
        resource_id = resource.get('_id') or resource.get('id')
        now_ts = int(datetime.utcnow().timestamp())
        _, shareable_bookings = self.rest_cl.shareable_book_list(
            organization_id, 0,
            int(datetime.max.replace(tzinfo=timezone.utc).timestamp()))
        if not shareable_bookings:
            LOG.error('Bookings are not found for the organization %s',
                      organization_id)
            return
        default_status_text = ('UNAVAILABLE' if is_available is False
                               else 'AVAILABLE')
        booking_status = {'Status': default_status_text}
        upcoming_bookings = [{'status_info': {'Status': '-'}}]
        resource_tenant_ids = []

        def format_utc_date(dt_timestamp):
            return str(datetime.fromtimestamp(dt_timestamp)) + ' UTC'

        def format_remained_time(start_date, end_date):
            dividers_map = OrderedDict({3600: ('hour', 'hours'),
                                        60: ('minute', 'minutes')})
            str_result = ''
            for divider, (one_value, many_values) in dividers_map.items():
                str_result = str(0) + ' {}'.format(many_values)
                result = int((end_date - start_date) / divider)
                if result == 0:
                    continue
                str_result = str(result)
                str_result += (' {}'.format(one_value)
                               if result == 1 else ' {}'.format(many_values))
                break
            return str_result

        shareable_booking_data = self._filter_bookings(
            shareable_bookings.get('data', []), resource_id, now_ts)
        for booking in shareable_booking_data:
            acquired_by_id = booking.get('acquired_by_id')
            if acquired_by_id:
                resource_tenant_ids.append(acquired_by_id)
        _, employees = self.rest_cl.employee_list(org_id=organization_id)
        employee_id_map = {
            employee['id']: employee for employee in employees['employees']
            if employee['id'] in resource_tenant_ids}
        tenant_auth_user_ids = [
            emp['auth_user_id'] for emp in list(employee_id_map.values())
        ]

        for booking in shareable_booking_data:
            acquired_since = booking['acquired_since']
            released_at = booking['released_at']
            acquired_by_id = booking.get('acquired_by_id')
            utc_acquired_since = int(
                datetime.utcfromtimestamp(acquired_since).timestamp())
            utc_released_at = int(
                datetime.utcfromtimestamp(released_at).timestamp())
            user_name = employee_id_map.get(acquired_by_id, {}).get('name')
            if not user_name:
                LOG.error('Could not detect employee name for booking %s',
                          booking['id'])
                continue
            if now_ts >= utc_acquired_since and (
                    now_ts <= utc_released_at or released_at == 0):
                if is_available:
                    remained = ('∞' if released_at == 0 else
                                format_remained_time(now_ts, utc_released_at))
                    booking_status = {
                        'Status': 'IN USE',
                        'details': {
                            'User': user_name,
                            'Since': format_utc_date(acquired_since),
                            'Until': ('∞' if released_at == 0 else
                                      format_utc_date(released_at)),
                            'Remained': remained
                        }
                    }
            else:
                duration = ('∞' if released_at == 0 else
                            format_remained_time(acquired_since, released_at))
                if upcoming_bookings[0].get('status_info', {}).get(
                        'Status') == '-':
                    upcoming_bookings = []
                upcoming_bookings.append({
                    'details': {
                        'User': user_name,
                        'Since': format_utc_date(acquired_since),
                        'Until': '∞' if released_at == 0 else format_utc_date(
                            released_at),
                        'Duration': duration
                    }})

        all_user_info = self.get_owner_manager_infos(
            cloud_account['organization_id'], tenant_auth_user_ids)
        env_properties_list = [
            {'env_key': env_prop_key, 'env_value': env_prop_value}
            for env_prop_key, env_prop_value in env_properties.items()
        ]
        for user_id, user_info in all_user_info.items():
            template_params = {
                'texts': {
                    'title': 'Environment changes',
                    'organization': self._get_organization_params(organization),
                    'user': {
                        'user_display_name': user_info.get('display_name')
                    },
                    'environments_infos': {
                        'resource_name': (resource.get('name') or
                                          resource.get('cloud_resource_id')),
                        'resource_type': resource.get('resource_type'),
                        'cloud_account_id': cloud_account['id'],
                        'cloud_account_name': cloud_account['name'],
                        'pool': pool['name'],
                        'resource_id': resource_id,
                        'status': booking_status,
                        'upcoming_bookings': upcoming_bookings,
                        'env_properties': env_properties_list,
                        'contains_envs': bool(env_properties_list)
                    }
                }
            }
            template_params['texts'].update(status_changed_info)
            self.herald_cl.email_send(
                [user_info.get('email')], 'Environment changed',
                template_type=HeraldTemplates.ENVIRONMENT_CHANGES.value,
                template_params=template_params)

    def execute_booking_acquire_release(self, booking_id, organization_id,
                                        action):

        def _prepare_acquire_release_data(booking_id, action):
            status_map = {
                'booking_acquire': 'acquired',
                'booking_release': 'released'
            }
            _, booking = self.rest_cl.shareable_book_get(booking_id)
            _, resource = self.rest_cl.cloud_resource_get(
                booking['resource_id'])
            updated_value = status_map.get(action)
            return resource, updated_value

        resource, updated_value = _prepare_acquire_release_data(
            booking_id, action)
        status_changed_info = {
            'environment_status_changed': {
                'changed_environment': {
                    'name': resource.get('name') or resource.get('cloud_resource_id'),
                    'id': resource['id'],
                    'status': updated_value
                }
            }
        }
        self.send_environment_changes(
            resource, status_changed_info, organization_id)

    @staticmethod
    def _merge_env_properties(old_value_map, new_value_map):
        merged_map = {k: {'name': k, 'previous_value': v, 'new_value': ''}
                      for k, v in old_value_map.items()
                      }
        for k, v in new_value_map.items():
            previous_value = old_value_map.get(k, '')
            merged_map[k] = {
                'name': k,
                'previous_value': previous_value,
                'new_value': v
            }
        return [val for val in merged_map.values()
                if val['previous_value'] != val['new_value']]

    def execute_env_property_changed(self, resource_id, organization_id,
                                     meta):
        _, resource = self.rest_cl.cloud_resource_get(resource_id)
        changed_properties_list = meta.get('env_properties')
        environment_prop_changed = {
            'environment_prop_changed': {
                'changed_environment': {
                    'name': (resource.get('name') or
                             resource.get('cloud_resource_id')),
                    'id': resource.get('id'),
                    'property_info': changed_properties_list
                }
            }
        }
        if changed_properties_list:
            self.send_environment_changes(resource, environment_prop_changed,
                                          organization_id)

    def execute_env_state_changed(self, resource_id, organization_id,
                                  meta):
        _, resource = self.rest_cl.cloud_resource_get(resource_id)
        res_name = resource.get('name') or resource.get('cloud_resource_id')
        environment_state_changed = {
            'environment_state_changed': {
                'changed_environment': {
                    'name': res_name,
                    'id': resource['id'],
                    'previous_value': meta.get('previous_state'),
                    'new_value': meta.get('new_state')
                }
            }
        }
        resource['active'] = meta.get('new_state')
        self.send_environment_changes(resource, environment_state_changed,
                                      organization_id)

    def send_expenses_alert(self, email, alert, pool_name, user_display_name,
                            organization):
        threshold_message = "%s%s" % (CURRENCY_MAP.get(organization['currency'], '$'),
                                      alert['threshold'])
        if alert['threshold_type'] == 'percentage':
            threshold_message = "%s%%" % alert['threshold']
        email_body = "Pool %s exceeded by alert base type %s with threshold " \
                     "value %s." % (pool_name, alert['based'],
                                    threshold_message)
        template_params = {
            'texts': {
                'user': {
                    'user_display_name': user_display_name
                },
                'organization': self._get_organization_params(organization),
                'title': "Pool Limit exceeded",
                'message': email_body
            }
        }
        self.herald_cl.email_send(
            [email], 'Optscale pool limit alert',
            template_type=HeraldTemplates.POOL_ALERT.value,
            template_params=template_params)
        LOG.info('sending email notification to user %s' % email)

    def execute_expense_alert(self, pool_id, organization_id, meta):
        _, organization = self.rest_cl.organization_get(organization_id)
        alert_id = meta.get('alert_id')
        _, alert = self.rest_cl.alert_get(alert_id)
        _, pool = self.rest_cl.pool_get(pool_id)
        for contact in alert['contacts']:
            employee_id = contact.get('employee_id')
            if employee_id:
                _, employee = self.rest_cl.employee_get(employee_id)
                _, user = self.auth_cl.user_get(employee['auth_user_id'])
                self.send_expenses_alert(
                    user['email'], alert, pool['name'], user['display_name'],
                    organization)

    def execute_constraint_violated(self, object_id, organization_id, meta,
                                    object_type):
        if object_type != 'user':
            return
        _, organization = self.rest_cl.organization_get(organization_id)
        _, user = self.auth_cl.user_get(object_id)

        if user.get('slack_connected'):
            return

        hit_list = meta.get('violations')
        resource_type_map = {
            'ttl': 'TTL',
            'total_expense_limit': 'Total expense limit',
            'daily_expense_limit': 'Daily expense limit'
        }
        for hit in hit_list:
            resource_type = hit.get('type')
            type_value_for_replace = resource_type_map.get(resource_type)
            if resource_type and type_value_for_replace:
                hit['type'] = type_value_for_replace
        params = {
            'email': [user['email']],
            'template_type': HeraldTemplates.RESOURCE_OWNER_VIOLATION_ALERT.value,
            'subject': 'Action required: Hystax OptScale Resource Constraint'
                       ' Violation Alert',
            'template_params': {
                'texts': {
                    'organization': self._get_organization_params(organization),
                    'user': user,
                    'total_violated': len(hit_list),
                    'violated_resources': hit_list,
                    'title': 'Resource Constraint Violation Alert',
                }
            }
        }
        self.herald_cl.email_send(**params)

    @staticmethod
    def _collapsed_filters(filters):
        for k, v in ENTITY_FIELD_MAP.items():
            if k in filters:
                filters[v] = [x['id'] if isinstance(x, dict) else x
                              for x in filters[k]]
                filters.pop(k, None)
        for filter_key, filter_val in filters.items():
            for i, v in enumerate(filter_val):
                if isinstance(v, dict):
                    if filter_key == 'resource_type':
                        filter_val[i] = '%s:%s' % (
                            v['name'], v['type'] or REGULAR_IDENTITY)
                    else:
                        filter_val[i] = v['name']
        return filters

    @staticmethod
    def _snake_to_camel_case(filter_name):
        if '_' in filter_name:
            parts = filter_name.split('_')
            filter_name = parts[0] + ''.join(x.title() for x in parts[1:])
        return filter_name

    def _get_org_constraint_link(self, constraint, created_at, filters):
        link_filters = defaultdict(list)
        for f, v in filters.items():
            f = self._snake_to_camel_case(f)
            for i, val in enumerate(v):
                if val is None:
                    v[i] = get_nil_uuid()
            link_filters[f] = v
        created = datetime.utcfromtimestamp(created_at)
        if constraint['type'] in ['expense_anomaly', 'resource_count_anomaly']:
            start_date = datetime.combine(created, created.time().min) - timedelta(
                days=constraint['definition']['threshold_days'])
            end_date = datetime.combine(created, created.time().max) + timedelta(
                days=1)
        elif constraint['type'] == 'expiring_budget':
            start_date = datetime.utcfromtimestamp(
                constraint['definition']['start_date'])
            end_date = None
        elif constraint['type'] == 'recurring_budget':
            start_date = created.replace(day=1, hour=0, minute=0, second=0)
            _, last_day = calendar.monthrange(start_date.year, start_date.month)
            end_date = datetime.combine(
                start_date.replace(day=last_day), start_date.time().max)
        elif constraint['type'] == 'resource_quota':
            start_date = created.replace(hour=0, minute=0, second=0)
            end_date = created.replace(hour=23, minute=59, second=59)
        elif constraint['type'] == 'tagging_policy':
            tag = constraint['definition']['conditions'].get('tag')
            without_tag = constraint['definition']['conditions'].get(
                'without_tag')
            if tag and tag not in link_filters.get('tag', []):
                link_filters['tag'].append(tag)
            if without_tag and without_tag not in link_filters.get(
                    'withoutTag', []):
                link_filters['withoutTag'].append(without_tag)
            start_date = created.replace(hour=0, minute=0, second=0)
            end_date = created.replace(hour=23, minute=59, second=59)
        else:
            raise Exception(
                'Unsupported constraint type: %s' % constraint['type'])
        link_filters['startDate'] = int(start_date.timestamp())
        if end_date:
            link_filters['endDate'] = int(end_date.timestamp())
        type_breakdown_by_map = {
            'expense_anomaly': 'expenses',
            'resource_count_anomaly': 'resourceCount',
            'expiring_budget': 'expenses',
            'recurring_budget': 'expenses',
            'resource_quota': 'resourceCount',
            'tagging_policy': 'expenses'
        }
        link_filters['breakdownBy'] = type_breakdown_by_map[constraint['type']]
        if link_filters.get('recommendations'):
            link_filters['availableSavings'] = link_filters['recommendations']
            link_filters.pop('recommendations')
        query = self.rest_cl.query_url(**link_filters)
        link = 'https://{0}/resources'.format(self.config_cl.public_ip())
        link += query
        return link

    def _get_org_constraint_template_params(self, organization, constraint,
                                            constraint_data, hit_date,
                                            latest_hit, link, user_info):
        constraint_template_map = {
            'expense_anomaly': HeraldTemplates.ANOMALY_DETECTION.value,
            'resource_count_anomaly': HeraldTemplates.ANOMALY_DETECTION.value,
            'expiring_budget': HeraldTemplates.EXPIRING_BUDGET.value,
            'recurring_budget': HeraldTemplates.RECURRING_BUDGET.value,
            'resource_quota': HeraldTemplates.RESOURCE_QUOTA.value,
            'tagging_policy': HeraldTemplates.TAGGING_POLICY.value
        }
        if 'anomaly' in constraint['type']:
            title = 'Anomaly detection alert'
        else:
            title = 'Organization policy violated'
        resource_types = ['resource_quota', 'resource_count_anomaly', 'tagging_policy']
        constraint_limit = (latest_hit['constraint_limit']
                            if constraint['type'] not in resource_types
                            else round(latest_hit['constraint_limit']))
        value = (latest_hit['value']
                 if constraint['type'] not in resource_types
                 else round(latest_hit['value']))
        params = {
            'texts': {
                'title': title,
                'organization': self._get_organization_params(organization),
                'organization_constraint': {**constraint_data},
                'limit_hit': {
                    'created_at': hit_date,
                    'value': value,
                    'link': link,
                    'constraint_limit': constraint_limit
                },
                'user': {
                    'user_display_name': user_info.get('display_name')
                },
            }
        }
        if constraint['type'] == 'tagging_policy':
            tag = constraint['definition']['conditions'].get('tag')
            without_tag = constraint['definition']['conditions'].get('without_tag')
            conditions = []
            if tag:
                if tag == get_nil_uuid():
                    tag = NOT_SET
                conditions.append(f'with tag "{tag}"')
            if without_tag:
                conditions.append(f'without tag "{without_tag}"')
            params['texts']['conditions'] = ', '.join(conditions)
        return params, title, constraint_template_map[constraint['type']]

    def execute_organization_constraint_violated(self, constraint_id,
                                                 organization_id):
        code, organization = self.rest_cl.organization_get(organization_id)
        if not organization:
            LOG.warning('Organization %s was not found, error code: %s' % (
                organization_id, code))
            return
        code, constraint = self.rest_cl.organization_constraint_get(constraint_id)
        if not constraint:
            LOG.warning(
                'Organization constraint %s was not found, error code: %s' % (
                    constraint_id, code))
            return
        c_filters = self._collapsed_filters(constraint['filters'])
        constraint_data = constraint.copy()
        code, hits = self.rest_cl.organization_limit_hit_list(
            organization_id, constraint_id=constraint_id)
        if not hits.get('organization_limit_hits'):
            raise Exception(
                'Limit hits for constraint %s were not found, '
                'error code: %s' % (constraint_id, code))
        latest_hit = max(hits['organization_limit_hits'],
                         key=lambda x: x['created_at'])
        hit_date = datetime.utcfromtimestamp(
            latest_hit['created_at']).strftime('%m/%d/%Y %I:%M %p UTC')
        if constraint['type'] not in CONSTRAINT_TYPES:
            raise Exception('Unknown organization constraint '
                            'type: %s' % constraint['type'])
        for constraint_type in CONSTRAINT_TYPES:
            constraint_data[constraint_type] = constraint_type == constraint['type']
        link = self._get_org_constraint_link(
            constraint, latest_hit['created_at'], c_filters)
        if constraint['type'] in ['expiring_budget', 'tagging_policy']:
            constraint_data['definition']['start_date'] = datetime.utcfromtimestamp(
                int(constraint_data['definition']['start_date'])).strftime(
                '%m/%d/%Y %I:%M %p UTC')
        managers = self.get_owner_manager_infos(organization_id)
        for user_id, user_info in managers.items():
            params, subject, template = self._get_org_constraint_template_params(
                organization, constraint, constraint_data, hit_date,
                latest_hit, link, user_info)
            self.herald_cl.email_send(
                [user_info.get('email')], subject,
                template_type=template, template_params=params)

    def execute_new_security_recommendation(self, organization_id,
                                            module_count_list):
        code, organization = self.rest_cl.organization_get(organization_id)
        if not organization:
            LOG.warning(f'Organization {organization_id} was not found, error '
                        f'code: {code}')
            return
        for i, data_dict in enumerate(module_count_list):
            module_count_list[i] = data_dict
        managers = self.get_owner_manager_infos(organization_id)
        for user_id, user_info in managers.items():
            template_params = {
                'texts': {
                    'title': 'New security recommendation detected',
                    'organization': self._get_organization_params(organization),
                    'user': {
                        'user_display_name': user_info.get('display_name')
                    },
                    'modules': module_count_list
                }
            }
            self.herald_cl.email_send(
                [user_info.get('email')], 'New security recommendation detected',
                template_type=HeraldTemplates.NEW_SECURITY_RECOMMENDATION.value,
                template_params=template_params)

    def execute_saving_spike(self, organization_id, meta):
        code, organization = self.rest_cl.organization_get(organization_id)
        if not organization:
            LOG.warning(f'Organization {organization_id} was not found, error '
                        f'code: {code}')
            return
        top3 = meta.get('top3')
        for i, opt in enumerate(top3):
            opt['saving'] = round(opt['saving'], 2)
            top3[i] = opt

        managers = self.get_owner_manager_infos(organization_id)
        for user_id, user_info in managers.items():
            template_params = {
                'texts': {
                    'title': 'Saving spike',
                    'organization': self._get_organization_params(organization),
                    'current_total': round(meta.get('current_total', 0), 2),
                    'previous_total': round(meta.get('previous_total', 0), 2),
                    'recommendations': top3,
                    'user': {
                        'user_display_name': user_info.get('display_name')
                    },
                }
            }
            self.herald_cl.email_send(
                [user_info.get('email')], 'Saving spike',
                template_type=HeraldTemplates.SAVING_SPIKE.value,
                template_params=template_params)

    def execute_report_imports_passed_for_org(self, organization_id):
        _, organization = self.rest_cl.organization_get(organization_id)
        managers = self.get_owner_manager_infos(organization_id)
        emails = [x['email'] for x in managers.values()]
        subject = 'Expenses initial processing completed'
        template_params = {
            'texts': {
                'organization': self._get_organization_params(organization),
                'title': subject
            }
        }
        self.herald_cl.email_send(
            emails, subject,
            template_type=HeraldTemplates.REPORT_IMPORT_PASSED.value,
            template_params=template_params)

    def execute_insider_prices(self):
        email = self._get_service_emails()
        if email:
            public_ip = self.config_cl.public_ip()
            title = 'Insider faced Azure SSLError'
            subject = f'[{public_ip}] {title}'
            template_params = {
                'texts': {
                    'title': title
                }
            }
            self.herald_cl.email_send(
                [email], subject,
                template_type=HeraldTemplates.INSIDER_SSLERROR.value,
                template_params=template_params)

    def execute(self, task):
        organization_id = task.get('organization_id')
        action = task.get('action')
        object_id = task.get('object_id')
        object_type = task.get('object_type')
        meta = task.get('meta')
        task_params = [
            object_id, organization_id
        ]
        action_param_required = {
            'booking_acquire': task_params + [action],
            'booking_release': task_params + [action],
            'env_property_updated': task_params + [meta],
            'env_active_state_changed': task_params + [meta],
            'expenses_alert': task_params + [meta],
            'constraint_violated': task_params + [meta, object_type],
            'organization_constraint_violated': task_params,
            'new_security_recommendation': [organization_id, meta],
            'saving_spike': [object_id, meta],
            'report_import_passed': [object_id],
            'insider_prices_sslerror': []
        }
        if action_param_required.get(action) is None or any(
                map(lambda x: x is None, action_param_required.get(action))):
            raise Exception('Invalid task received: {}'.format(task))

        action_func_map = {
            'booking_acquire': self.execute_booking_acquire_release,
            'booking_release': self.execute_booking_acquire_release,
            'env_property_updated': self.execute_env_property_changed,
            'env_active_state_changed': self.execute_env_state_changed,
            'expenses_alert': self.execute_expense_alert,
            'constraint_violated': self.execute_constraint_violated,
            'organization_constraint_violated':
                self.execute_organization_constraint_violated,
            'new_security_recommendation':
                self.execute_new_security_recommendation,
            'saving_spike': self.execute_saving_spike,
            'report_import_passed': self.execute_report_imports_passed_for_org,
            'insider_prices_sslerror': self.execute_insider_prices
        }
        LOG.info('Started processing for object %s task type for %s '
                 'for organization %s' % (object_id, action, organization_id))
        try:
            func = action_func_map[action]
        except KeyError:
            LOG.warning('Unknown action type: %s. Skipping' % action)
            return
        func(*action_param_required[action])

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
            worker = HeraldExecutorWorker(conn, config_cl)
            worker.run()
        except KeyboardInterrupt:
            worker.running = False
            worker.thread.join()
            LOG.info('Shutdown received')
