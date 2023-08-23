#!/usr/bin/env python
import calendar
import os
import requests
import time
import uuid
from copy import deepcopy
from datetime import datetime, timedelta
from threading import Thread
from kombu.mixins import ConsumerMixin
from kombu.log import get_logger
from kombu import Connection
from kombu.utils.debug import setup_logging
from kombu import Connection as QConnection
from kombu import Exchange, Queue
from kombu.pools import producers
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from optscale_client.config_client.client import Client as ConfigClient
from optscale_client.rest_api_client.client_v2 import Client as RestClient


LOG = get_logger(__name__)
EXPENSE_ANOMALY = 'expense_anomaly'
EXPIRING_BUDGET = 'expiring_budget'
RECURRING_BUDGET = 'recurring_budget'
RESOURCE_COUNT_ANOMALY = 'resource_count_anomaly'
RESOURCE_QUOTA = 'resource_quota'
TAGGING_POLICY = 'tagging_policy'
ENTITY_FIELD_MAP = {
    'pool': 'pool_id',
    'owner': 'owner_id',
    'cloud_account': 'cloud_account_id'
}
DAYS_IN_YEAR = 365
SECONDS_IN_DAY = 24 * 60 * 60
REGULAR_IDENTITY = 'regular'

ACTIVITIES_EXCHANGE_NAME = 'activities-tasks'
ACTIVITIES_EXCHANGE = Exchange(ACTIVITIES_EXCHANGE_NAME, type='topic')

WORKER_EXCHANGE_NAME = 'organization-violations'
WORKER_QUEUE_NAME = 'organization-violation'
WORKER_TASK_EXCHANGE = Exchange(WORKER_EXCHANGE_NAME, type='direct')
WORKER_TASK_QUEUE = Queue(WORKER_QUEUE_NAME, WORKER_TASK_EXCHANGE,
                          routing_key=WORKER_QUEUE_NAME)


class OrganizationViolationsWorker(ConsumerMixin):
    def __init__(self, connection, config_cl):
        self.connection = connection
        self.config_cl = config_cl
        self._rest_cl = None
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

    def get_consumers(self, consumer, channel):
        return [consumer(queues=[WORKER_TASK_QUEUE], accept=['json'],
                         callbacks=[self.process_task])]

    def publish_activities_tasks(self, tasks):
        queue_conn = QConnection('amqp://{user}:{pass}@{host}:{port}'.format(
            **self.config_cl.read_branch('/rabbit')))
        with producers[queue_conn].acquire(block=True) as producer:
            for task_data in tasks:
                routing_key, task = task_data
                producer.publish(
                    task,
                    serializer='json',
                    exchange=ACTIVITIES_EXCHANGE,
                    declare=[ACTIVITIES_EXCHANGE],
                    routing_key=routing_key,
                    retry=True
                )

    @staticmethod
    def today_start(date):
        return date.replace(hour=0, minute=0, second=0, microsecond=0)

    def today_start_ts(self, date):
        return int(self.today_start(date).timestamp())

    def yesterday_end(self, date):
        return self.today_start(date) - timedelta(seconds=1)

    def yesterday_end_ts(self, date):
        return int(self.yesterday_end(date).timestamp())

    def today_end(self, date):
        return self.yesterday_end(date) + timedelta(days=1)

    def today_end_ts(self, date):
        return int(self.today_end(date).timestamp())

    def period_start_ts(self, date, threshold_days):
        period_start = self.today_start(date) - timedelta(days=threshold_days)
        return int(period_start.timestamp())

    @staticmethod
    def month_start(date):
        return date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    def month_start_ts(self, date):
        return int(self.month_start(date).timestamp())

    @staticmethod
    def month_end(date):
        last_day = calendar.monthrange(date.year, date.month)
        return datetime.combine(date.replace(day=last_day), date.time().max)

    def month_end_ts(self, date):
        return int(self.month_end(date).timestamp())

    def _get_todays_resource_count(self, constraint_id, organization_id, date,
                                   filters):
        start_date = self.today_start_ts(date)
        end_date = self.today_end_ts(date)
        LOG.info(f'Getting resource count today\'s value for constraint '
                 f'{constraint_id} for period start: {start_date}, '
                 f'end: {end_date}')
        _, res_count = self.rest_cl.resources_count_get(
            organization_id, start_date, end_date,
            breakdown_by='resource_type', params=filters)
        return res_count['count']

    def _get_resource_count_info(self, constraint_id, organization_id, date,
                                 threshold_days, filters):
        todays = self._get_todays_resource_count(
            constraint_id, organization_id, date, filters)

        start_date = self.period_start_ts(date, threshold_days)
        end_date = self.yesterday_end_ts(date)
        LOG.info(f'Getting resource count average value for constraint '
                 f'{constraint_id} for period start: {start_date}, '
                 f'end: {end_date}')
        _, res_count = self.rest_cl.resources_count_get(
            organization_id, start_date, end_date, breakdown_by='resource_type',
            params=filters)
        threshold_breakdown = {ts: sum([x['count'] for x in val.values()])
                               for ts, val in res_count['breakdown'].items()}
        average = sum([x['average'] for x in res_count['counts'].values()])
        return todays, average, threshold_breakdown

    def _get_expense_info(self, constraint_id, organization_id, date,
                          threshold_days, filters):
        start_date = self.period_start_ts(date, threshold_days)
        end_date = self.today_end_ts(date)
        yesterday_end_date = self.yesterday_end_ts(date)

        LOG.info(f'Getting expenses for constraint {constraint_id} for period'
                 f' start: {start_date}, end: {end_date}')
        _, expenses = self.rest_cl.breakdown_expenses_get(
            organization_id, start_date, end_date,
            breakdown_by='resource_type', params=filters)

        threshold_total = 0
        threshold_breakdown = {}
        todays = 0
        for ts, val in expenses['breakdown'].items():
            ts_cost = sum([x.get('cost', 0) for x in val.values()])
            if int(ts) > yesterday_end_date:
                todays = ts_cost
                continue
            threshold_breakdown[ts] = ts_cost
            threshold_total += threshold_breakdown[ts]
        average = (threshold_total / len(threshold_breakdown)
                   if len(threshold_breakdown) else 0)
        return todays, average, threshold_breakdown

    @staticmethod
    def get_nil_uuid():
        return str(uuid.UUID(int=0))

    def _collapsed_filters(self, filters):
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
                    elif filter_key in ['traffic_from', 'traffic_to']:
                        filter_val[i] = f"{v['name']}:{v['cloud_type']}"
                    else:
                        filter_val[i] = v['name']
                if v is None:
                    filter_val[i] = self.get_nil_uuid()
        return filters

    def get_max_last_import_at(self, organization_id):
        _, resp = self.rest_cl.cloud_account_list(organization_id)
        if not resp.get('cloud_accounts'):
            return 0
        return max([x['last_import_at'] for x in resp['cloud_accounts']])

    @staticmethod
    def _generate_activities_task(organization_id, constraint):
        routing_key = 'constraint.violation.{}'.format(
            constraint['type'])
        task = {
            'organization_id': organization_id,
            'object_id': constraint['id'],
            'object_type': 'organization_constraint',
            'action': 'organization_constraint_violated',
        }
        return routing_key, task

    def _update_limit_hit(self, organization_id, constraint, notifications,
                          min_created_at_ts, max_created_at_ts,
                          constraint_limit, value, run_result):
        notif_task = None
        limit_hits = [x for x in constraint['limit_hits']
                      if min_created_at_ts < x['created_at'] <= max_created_at_ts]
        if limit_hits:
            hit = max(limit_hits, key=lambda x: x['created_at'])
            hit_params = {
                'constraint_limit': constraint_limit,
                'value': value,
                'run_result': run_result
            }
            self.rest_cl.organization_limit_hit_update(
                hit['id'], hit_params)
        else:
            hit_params = {
                'constraint_id': constraint['id'],
                'constraint_limit': constraint_limit,
                'value': value,
                'run_result': run_result,
                'created_at': max_created_at_ts
            }
            self.rest_cl.organization_limit_hit_create(
                organization_id, hit_params)
            if notifications:
                notif_task = self._generate_activities_task(
                    organization_id, constraint)
        return notif_task

    @staticmethod
    def _slice_time_period_by_years(start_date, end_date):
        result = []
        current_date = start_date
        while current_date <= end_date:
            next_date = current_date + timedelta(days=DAYS_IN_YEAR)
            if next_date > end_date:
                result.append((int(current_date.timestamp()),
                               int(end_date.timestamp())))
                break
            result.append((int(current_date.timestamp()),
                           int(next_date.timestamp()) - 1))
            current_date = next_date
        return result

    @staticmethod
    def _get_anomaly_run_result(today, average, breakdown):
        if not average:
            breakdown.clear()
        return {
            "average": average,
            "today": today,
            "breakdown": breakdown
        }

    @staticmethod
    def _get_budget_and_quota_run_result(current, limit):
        return {'limit': limit, 'current': current}

    @staticmethod
    def _get_tagging_run_result(value):
        return {'value': value}

    def process_resource_quota(self, constraint, organization_id, date,
                               notifications, execution_start_ts):
        start_date = self.today_start_ts(date)
        end_date = execution_start_ts
        filters = self._collapsed_filters(constraint['filters'])
        todays_value = self._get_todays_resource_count(
            constraint['id'], organization_id, date, filters)
        max_value = constraint['definition']['max_value']
        run_result = self._get_budget_and_quota_run_result(
            current=todays_value, limit=max_value)
        result = [run_result]
        if todays_value > constraint['definition']['max_value']:
            result.append(self._update_limit_hit(
                organization_id, constraint, notifications, start_date,
                end_date, constraint_limit=max_value,
                value=todays_value, run_result=run_result))
        return result

    def process_recurring_budget(self, constraint, organization_id, date,
                                 notifications, execution_start_ts):
        last_import_at = self.get_max_last_import_at(organization_id)
        last_run = constraint['last_run']
        if last_run > last_import_at:
            return []
        monthly_budget = constraint['definition']['monthly_budget']
        start_date = self.month_start_ts(date)
        end_date = self.today_end_ts(date)
        filters = self._collapsed_filters(constraint['filters'])
        c_id = constraint['id']
        _, resp = self.rest_cl.breakdown_expenses_get(
            organization_id, start_date, end_date, params=filters)
        LOG.info(f'Getting expenses value for constraint '
                 f'{c_id} for period start: {start_date}, end: {end_date}')
        run_result = self._get_budget_and_quota_run_result(
            current=resp['total'], limit=monthly_budget)
        result = [run_result]
        if resp['total'] > monthly_budget:
            result.append(self._update_limit_hit(
                organization_id, constraint, notifications, start_date,
                int(date.timestamp()), constraint_limit=monthly_budget,
                value=resp['total'], run_result=run_result))
        return result

    def process_expiring_budget(self, constraint, organization_id, date,
                                notifications, execution_start_ts):
        last_import_at = self.get_max_last_import_at(organization_id)
        last_run = constraint['last_run']
        if last_run > last_import_at:
            return []
        c_id = constraint['id']
        total_budget = constraint['definition']['total_budget']
        start_date_ts = constraint['definition']['start_date']
        start_date = datetime.fromtimestamp(start_date_ts)
        end_date = self.today_end(date)
        filters = self._collapsed_filters(constraint['filters'])

        # breakdown_expenses api doesn't return expenses for more than 365 days
        time_periods = self._slice_time_period_by_years(start_date, end_date)
        total_expenses = 0
        for start_ts, end_ts in time_periods:
            _, resp = self.rest_cl.breakdown_expenses_get(
                organization_id, start_ts, end_ts, params=filters)
            LOG.info(f'Getting expenses value for constraint '
                     f'{c_id} for period start: {start_ts}, end: {end_ts}')
            total_expenses += resp['total']
        run_result = self._get_budget_and_quota_run_result(
            current=total_expenses, limit=total_budget)
        result = [run_result]
        if total_expenses > total_budget:
            if not constraint['limit_hits']:
                _, hits = self.rest_cl.organization_limit_hit_list(
                    organization_id, constraint_id=constraint['id'])
                constraint['limit_hits'] = hits['organization_limit_hits']
            result.append(self._update_limit_hit(
                organization_id, constraint, notifications, 0,
                execution_start_ts, total_budget, total_expenses, run_result))
        return result

    def _filter_resources_by_tags(self, constraint, resources):
        """Filter out resources that don't suit to AND-ed conditions 'tag',
        'without_tag' from constraint definition or OR-ed conditions 'tag',
        'without_tag' from constraint filters"""
        tag_and = constraint['definition']['conditions'].get('tag')
        without_tag_and = constraint['definition']['conditions'].get(
            'without_tag')
        tag_or = constraint['filters'].get('tag', [])
        without_tag_or = constraint['filters'].get('without_tag', [])
        nil_uuid_tag = self.get_nil_uuid()
        if tag_and == nil_uuid_tag:
            resources = [x for x in resources if not x.get('tags')]
        elif tag_and:
            resources = [x for x in resources if tag_and in x.get('tags', {})]
        if without_tag_and:
            resources = [x for x in resources
                         if without_tag_and not in x.get('tags', {})]
        if tag_or and nil_uuid_tag in tag_or:
            tag_or.remove(nil_uuid_tag)
            resources = [x for x in resources
                         if (any(t in x.get('tags', {}) for t in tag_or) or
                             not x.get('tags'))]
        elif tag_or:
            resources = [x for x in resources
                         if any(t in x.get('tags', {}) for t in tag_or)]
        if without_tag_or:
            resources = [x for x in resources
                         if not all(t in x.get('tags', {})
                                    for t in without_tag_or)]
        return resources

    def process_tagging_policy(self, constraint, organization_id, date,
                               notifications, execution_start_ts):
        c_id = constraint['id']
        start_date = constraint['definition']['start_date']
        if datetime.fromtimestamp(start_date) > datetime.utcnow():
            LOG.info(f'Constraint {c_id} is skipped due to start_date')
            return []
        today_date = datetime.fromtimestamp(execution_start_ts)
        start_ts = self.today_start_ts(today_date)
        end_ts = self.today_end_ts(today_date)
        filters = self._collapsed_filters(constraint['filters'])
        exp_filters = deepcopy(filters)
        tag = constraint['definition']['conditions'].get('tag')
        without_tag = constraint['definition']['conditions'].get('without_tag')
        for f in ['tag', 'without_tag']:
            if not exp_filters.get(f):
                exp_filters[f] = []
            if isinstance(exp_filters[f], str):
                exp_filters[f] = [exp_filters[f]]
        if tag:
            exp_filters['tag'].append(tag)
        if without_tag:
            exp_filters['without_tag'].append(without_tag)
        _, resp = self.rest_cl.clean_expenses_get(
            organization_id, start_ts, end_ts, exp_filters)
        LOG.info(f'Getting expenses value for constraint '
                 f'{c_id} for period start: {start_ts}, end: {end_ts}')
        resources = resp['clean_expenses']

        # resources are returned for OR-ed tags conditions, so need filtering
        filtered_resources = self._filter_resources_by_tags(
            constraint, resources)
        run_result = self._get_tagging_run_result(len(filtered_resources))
        result = [run_result]
        if filtered_resources:
            result.append(self._update_limit_hit(
                organization_id, constraint, notifications, start_ts,
                execution_start_ts, constraint_limit=0,
                value=len(filtered_resources), run_result=run_result))
        return result

    def process_anomaly(self, constraint, organization_id, date, notifications,
                        execution_start_ts):
        c_id = constraint['id']
        last_run = constraint['last_run']
        threshold = constraint['definition']['threshold']
        threshold_days = constraint['definition']['threshold_days']
        filters = self._collapsed_filters(constraint['filters'])
        type_ = constraint['type']
        if type_ == EXPENSE_ANOMALY:
            last_import_at = self.get_max_last_import_at(organization_id)
            if last_run > last_import_at:
                return []
            todays_value, average_value, breakdown_value = self._get_expense_info(
                c_id, organization_id, date, threshold_days, filters)
        elif type_ == RESOURCE_COUNT_ANOMALY:
            todays_value, average_value, breakdown_value = self._get_resource_count_info(
                c_id, organization_id, date, threshold_days, filters)
        run_result = self._get_anomaly_run_result(
            todays_value, average_value, breakdown_value)
        result = [run_result]
        if todays_value is None and average_value is None:
            return []
        elif todays_value > average_value + average_value * threshold / 100:
            min_created_at = date - timedelta(days=1)
            min_created_at_ts = int(min_created_at.timestamp())
            result.append(self._update_limit_hit(
                organization_id, constraint, notifications, min_created_at_ts,
                int(date.timestamp()), constraint_limit=average_value,
                value=todays_value, run_result=run_result))
        return result

    def process_organization_constraint(self, constraint, organization_id,
                                        start_ts, date, notifications):
        type_ = constraint['type']
        process_func_map = {
            EXPENSE_ANOMALY: self.process_anomaly,
            EXPIRING_BUDGET: self.process_expiring_budget,
            RECURRING_BUDGET: self.process_recurring_budget,
            RESOURCE_COUNT_ANOMALY: self.process_anomaly,
            RESOURCE_QUOTA: self.process_resource_quota,
            TAGGING_POLICY: self.process_tagging_policy
        }
        try:
            func = process_func_map[type_]
        except KeyError:
            raise Exception('Unsupported constraint type: %s' % type_)

        # each func must return up to 2 objects in predicted order:
        # last run result & notification task
        result = func(constraint, organization_id, date,
                      notifications, start_ts)
        payload = {'last_run': start_ts}
        try:
            payload['last_run_result'] = result.pop(0)
        except IndexError:
            pass
        self.rest_cl.organization_constraint_update(
            constraint['id'], payload)

        try:
            return result.pop(0)
        except IndexError:
            pass

    def process_organization_constraints(self, task):
        start = datetime.utcnow()
        start_ts = int(start.timestamp())
        org_id = task.get('organization_id')
        date_ts = task.get('date')
        if not org_id or not date_ts or not isinstance(date_ts, int):
            raise Exception('Invalid task received: {}'.format(task))
        date = datetime.fromtimestamp(date_ts)
        notifications = task.get('notifications')
        hit_days = [
            # hit_days for recurring_budget constraint
            (start - datetime.combine(
                self.month_start(date), start.time())).days + 1,
            # hit_days for resource_quota and anomalies constraints
            (start - datetime.combine(
                        date - timedelta(days=1), start.time())).days + 1]
        _, response = self.rest_cl.organization_constraint_list(
            org_id, hit_days=max(hit_days))
        constraints = response.get('organization_constraints')
        if not constraints:
            LOG.info('No constraints found for organization %s' % org_id)
            return
        notif_tasks = []
        for constr in constraints:
            try:
                notif_task = self.process_organization_constraint(
                    constr, org_id, start_ts, date, notifications)
                if notif_task:
                    notif_tasks.append(notif_task)
            except Exception as exc:
                LOG.exception('Processing organization constraint %s failed. '
                              'Error: %s' % (constr['id'], str(exc)))
        self.publish_activities_tasks(notif_tasks)
        LOG.info('Organization violation process for organization %s completed'
                 ' in %s seconds' % (
                    org_id, int(datetime.utcnow().timestamp()) - start_ts))

    def process_task(self, body, message):
        try:
            self.process_organization_constraints(body)
        except Exception as exc:
            LOG.exception('Organization violations failed: %s', str(exc))
        message.ack()

    def heartbeat(self):
        while self.running:
            self.connection.heartbeat_check()
            time.sleep(1)


if __name__ == '__main__':
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    debug = os.environ.get('DEBUG', False)
    log_level = 'INFO' if not debug else 'DEBUG'
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
            worker = OrganizationViolationsWorker(conn, config_cl)
            worker.run()
        except KeyboardInterrupt:
            worker.running = False
            worker.thread.join()
            LOG.info('Shutdown received')
