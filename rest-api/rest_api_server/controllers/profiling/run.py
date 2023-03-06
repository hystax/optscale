import math
from datetime import datetime, timedelta
from optscale_exceptions.common_exc import NotFoundException, ForbiddenException
from rest_api_server.controllers.profiling.base import BaseProfilingController
from rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api_server.controllers.base import MongoMixin
from rest_api_server.models.models import CloudAccount
from rest_api_server.exceptions import Err
from requests.exceptions import HTTPError
from collections import defaultdict

HOUR_IN_SEC = 3600
DAY_IN_HOURS = 24
RUN_STATUS_RUNNING = 1
RUN_STATUS_COMPLETED = 2
RUN_STATUS_FAILED = 3
RUN_STATUSES_MAP = {
    RUN_STATUS_RUNNING: 'running',
    RUN_STATUS_COMPLETED: 'completed',
    RUN_STATUS_FAILED: 'failed'
}
BYTES_IN_MB = 1024 * 1024


class RunController(BaseProfilingController, MongoMixin):

    def get(self, organization_id, run_id, profiling_token):
        try:
            run = self.get_run(profiling_token, run_id)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(Err.OE0002, ['Run', run_id])
            elif ex.response.status_code == 403:
                raise ForbiddenException(Err.OE0234, [])
            raise
        run_costs = self.get_run_costs(organization_id, [run])
        goals = self.get_application_goals(
            run['application_id'], profiling_token)
        return self.formatted_run(run, goals, run_costs)

    def formatted_run(self, run, application_goals, run_costs):
        state = run['state']
        run['status'] = RUN_STATUSES_MAP.get(state)
        finish = run.get('finish')
        if not finish and state == RUN_STATUS_RUNNING:
            finish = datetime.utcnow().timestamp()
        run['duration'] = finish - run.get('start') if finish else None
        run['cost'] = run_costs.get(run['id'], 0)
        run['goals'] = application_goals
        return run

    def list(self, organization_id, application_id, profiling_token, **kwargs):
        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')
        data = self.list_runs(profiling_token, application_id)
        runs = []
        for run in data:
            run_start = run['start']
            if start_date and start_date > run_start:
                continue
            if end_date and end_date < run_start:
                continue
            runs.append(run)
        run_costs = self.get_run_costs(organization_id, runs)
        goals = self.get_application_goals(application_id, profiling_token)
        return [self.formatted_run(run, goals, run_costs) for run in runs]

    def get_application_goals(self, app_id, profiling_token):
        application = self.get_application(profiling_token, app_id)
        return application['goals']

    def get_run_costs(self, organization_id, runs):
        if not runs:
            return {}
        cloud_account_ids = self.get_cloud_account_ids(organization_id)
        executor_run_duration_map = defaultdict(dict)
        filters = []
        min_dt, max_dt = None, None
        for r in runs:
            r_start = r.get('start') or 0
            r_finish = r.get('finish') or 0
            if not r_finish and r['state'] == RUN_STATUS_RUNNING:
                r_finish = datetime.utcnow().timestamp()
            duration = r_finish - r_start
            for executor in r['executors']:
                if isinstance(executor, dict):
                    executor = executor['id']
                executor_run_duration_map[r['id']][executor] = duration
            r_start = datetime.utcfromtimestamp(r_start).replace(
                hour=0, minute=0, second=0, microsecond=0)
            r_finish = datetime.utcfromtimestamp(r_finish).replace(
                hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            if not min_dt or min_dt > r_start:
                min_dt = r_start
            if not max_dt or max_dt < r_finish:
                max_dt = r_finish
            filters.append({
                'resource_id': {'$in': r['executors']},
                'start_date': {'$gte': r_start, '$lt': r_finish},
                'end_date': {'$lte': r_finish}
            })
        raw_expenses = self.raw_expenses_collection.find({
            'cloud_account_id': {'$in': cloud_account_ids},
            'start_date': {'$gte': min_dt, '$lt': max_dt},
            'end_date': {'$lte': max_dt},
            '$or': filters
        })
        raw_expenses = list(raw_expenses)
        exp_map = defaultdict(list)
        for exp in raw_expenses:
            exp_map[exp['resource_id']].append(exp)
        result = {}
        executor_work_map = {}
        for r_id, expenses in exp_map.items():
            executor_work_map[r_id] = self.calculate_work(expenses)
        for run in runs:
            run_id = run['id']
            executors_durations = executor_run_duration_map.get(run_id, {})
            cost = 0
            for r_id, duration in executors_durations.items():
                working_hours, day_cost = executor_work_map.get(
                    r_id, (DAY_IN_HOURS, 0))
                w_time = working_hours * HOUR_IN_SEC
                cost += day_cost * duration / w_time
            result[run_id] = cost
        return result

    def calculate_work(self, expenses):
        working_hours_set = set()
        total_cost = 0
        working_hours = 0
        for e in expenses:
            total_cost += e['cost']
            if self._is_flavor_cost(e):
                time_interval = e.get('identity/TimeInterval')
                if time_interval:
                    working_hours_set.add(time_interval.split('/')[0])
                elif e.get('usage_quantity'):
                    working_hours += float(e['usage_quantity'])
                elif e.get('Usage'):
                    working_hours += float(e['Usage'])
        if working_hours_set:
            working_hours = len(working_hours_set)
        return working_hours or DAY_IN_HOURS, total_cost

    @staticmethod
    def _is_flavor_cost(exp):
        if (exp.get('lineItem/UsageType') and
                'BoxUsage' in exp['lineItem/UsageType']):
            return True
        elif (exp.get('meter_details', {}).get(
                'meter_category') == 'Virtual Machines'):
            return True
        elif (exp.get('BillingItem') == 'Cloud server configuration' and
              'key:acs:ecs:payType value:spot' not in exp.get('Tags', [])):
            return True
        return False

    def get_cloud_account_ids(self, organization_id):
        cloud_accounts = self.session.query(CloudAccount.id).filter(
            CloudAccount.deleted.is_(False),
            CloudAccount.organization_id == organization_id
        ).all()
        return [ca_id for ca_id, in cloud_accounts]

    def breakdown_get(self, organization_id, run_id, profiling_token):
        def _aggregate(values, func):
            functions = {
                'avg': lambda x: sum(x) / len(x),
                'max': lambda x: max(x),
                'sum': lambda x: sum(x),
                'last': lambda x: x[-1]
            }
            return functions.get(func)(values)

        try:
            run = self.get_run(profiling_token, run_id)
            logs = self.list_logs(profiling_token, run_id)
            milestones = self.list_milestones(profiling_token, run_id)
            stages = self.list_stages(profiling_token, run_id)
            proc_data = self.list_proc_data(profiling_token, run_id)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(Err.OE0002, ['Run', run_id])
            elif ex.response.status_code == 403:
                raise ForbiddenException(Err.OE0234, [])
            raise
        goals = self.get_application_goals(
            run['application_id'], profiling_token)
        executors = run.get('executors', [])
        log_times = list(map(lambda x: x['time'], logs)) or [run['start']]
        min_time = math.ceil(min([min(log_times), run['start']]))
        max_time = math.ceil(max([max(log_times), run.get('finish') or 0]))
        goal_function_map = {g['key']: g.get('function') for g in goals}
        result = {}
        for p in proc_data:
            t = math.ceil(p['timestamp'])
            if t not in result:
                result[t] = defaultdict(lambda: defaultdict(list))
            instance_id = p.get('instance_id')
            if instance_id:
                result[t]['metrics']['executors_count'].append(instance_id)
            proc_stats = p.get('proc_stats', {})
            ps_stats = proc_stats.get('ps_stats', {})
            fields_map = {
                'ram': 'used_ram_mb',
                'cpu': 'cpu_percent'
            }
            for k, v in fields_map.items():
                value = ps_stats.get(v)
                if value:
                    result[t]['metrics'][k].append(value)
            proc = proc_stats.get('proc', {})
            process_cpu = proc.get('cpu')
            if process_cpu is not None:
                result[t]['metrics']['process_cpu'].append(process_cpu)
            process_ram = proc.get('mem', {}).get('vms', {}).get('t')
            if process_ram is not None:
                result[t]['metrics']['process_ram'].append(
                    process_ram / BYTES_IN_MB)
        for l in logs:
            t = math.ceil(l['time'])
            if t not in result:
                result[t] = defaultdict(lambda: defaultdict(list))
            for k, v in l.get('data', {}).items():
                if k not in goal_function_map:
                    continue
                if isinstance(v, str):
                    v = float(v)
                result[t]['data'][k].append(v)
        for i in range(min_time, max_time + 1):
            breakdown = result.get(i)
            if not breakdown:
                result[i] = dict(metrics={}, data={})
                continue
            count = result[i]['metrics'].pop('executors_count', [])
            for key in ['metrics', 'data']:
                fields = list(result[i][key].keys())
                for k in fields:
                    objects = result[i][key].get(k)
                    if objects:
                        func = goal_function_map.get(k) or 'avg'
                        result[i][key][k] = _aggregate(objects, func)
            result[i]['metrics']['executors_count'] = len(set(count))
        return {
            'executors': executors,
            'breakdown': result,
            'milestones': milestones,
            'stages': stages,
        }


class RunAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return RunController
