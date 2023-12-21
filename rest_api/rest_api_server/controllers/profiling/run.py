import math
from collections import defaultdict
from datetime import datetime
from requests.exceptions import HTTPError

from rest_api.rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api.rest_api_server.controllers.profiling.base import (
    BaseProfilingController, RunCostsMixin)
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.models.enums import RunStates

from tools.optscale_exceptions.common_exc import NotFoundException

DAY_IN_HOURS = 24
BYTES_IN_MB = 1024 * 1024


class RunController(BaseProfilingController, RunCostsMixin):

    def get(self, organization_id, run_id, profiling_token):
        try:
            run = self.get_run(profiling_token, run_id)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(Err.OE0002, ['Run', run_id])
            raise
        cloud_accounts_ids = self.get_cloud_account_ids(organization_id)
        run_costs = self._get_run_costs(cloud_accounts_ids, [run])
        goals = self.__get_application_goals(
            run['application_id'], profiling_token)
        return self.formatted_run(run, goals, run_costs)

    def formatted_run(self, run, application_goals, run_costs):
        state = run['state']
        run['status'] = RunStates(state).name
        finish = run.get('finish')
        if not finish and state == RunStates.running:
            finish = datetime.utcnow().timestamp()
        run['duration'] = finish - run.get('start') if finish else None
        run['cost'] = run_costs.get(run['id'], 0)
        run['goals'] = application_goals
        if run.get('runset_id'):
            run['runset'] = {
                'id': run.pop('runset_id'),
                'name': run.pop('runset_name', None)
            }
        return run

    def list(self, organization_id, application_id, profiling_token, **kwargs):
        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')
        try:
            data = self.list_application_runs(profiling_token, application_id)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(
                    Err.OE0002, ['Application', application_id])
            raise
        runs = []
        for run in data:
            run_start = run['start']
            if start_date and start_date > run_start:
                continue
            if end_date and end_date < run_start:
                continue
            runs.append(run)
        cloud_accounts_ids = self.get_cloud_account_ids(organization_id)
        run_costs = self._get_run_costs(cloud_accounts_ids, runs)
        goals = self.__get_application_goals(application_id, profiling_token)
        return sorted([
            self.formatted_run(run, goals, run_costs) for run in runs
        ], key=lambda d: d['start'])

    def __get_application_goals(self, app_id, profiling_token):
        try:
            application = self.get_application(profiling_token, app_id)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(Err.OE0002, ['Application', app_id])
            raise
        return application['goals']

    def get_cloud_account_ids(self, organization_id):
        return list(self._get_cloud_accounts(organization_id).keys())

    def breakdown_get(self, organization_id, run_id, profiling_token):
        def _aggregate(values, func_name):
            functions = {
                'avg': lambda x: sum(x) / len(x),
                'max': lambda x: max(x),
                'sum': lambda x: sum(x),
                'last': lambda x: x[-1]
            }
            return functions.get(func_name)(values)

        try:
            run = self.get_run(profiling_token, run_id)
            logs = self.list_logs(profiling_token, run_id)
            milestones = self.list_milestones(profiling_token, run_id)
            stages = self.list_stages(profiling_token, run_id)
            proc_data = self.list_proc_data(profiling_token, run_id)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(Err.OE0002, ['Run', run_id])
            raise
        goals = self.__get_application_goals(
            run['application_id'], profiling_token)
        executors = run.get('executors', [])
        log_times = list(map(lambda x: x['time'], logs)) or [run['start']]
        min_time = math.ceil(min([min(log_times), run['start']]))
        max_time = math.ceil(max([max(log_times), run.get('finish') or 0]))
        goal_function_map = {g['key']: g.get('func') for g in goals}
        result = {}
        for p in proc_data:
            t = math.ceil(p['timestamp'])
            if t not in result:
                result[t] = defaultdict(lambda: defaultdict(list))
            instance_id = p.get('instance_id')
            if instance_id:
                result[t]['metrics']['executors_count'].append(instance_id)
            proc_stats = p.get('proc_stats', {})
            for stats_key, fields_map in {
                'ps_stats': {
                    'ram': 'used_ram_mb',
                    'cpu': 'cpu_percent'
                },
                'gpu_stats': {
                    'gpu_load': 'avg_gpu_load',
                    'gpu_memory_free': 'avg_gpu_memory_free',
                    'gpu_memory_total': 'avg_gpu_memory_total',
                    'gpu_memory_used': 'avg_gpu_memory_used'
                }
            }.items():
                stats = proc_stats.get(stats_key, {})
                for k, v in fields_map.items():
                    value = stats.get(v)
                    if value is not None:
                        result[t]['metrics'][k].append(value)
            proc = proc_stats.get('proc', {})
            process_cpu = proc.get('cpu')
            if process_cpu is not None:
                result[t]['metrics']['process_cpu'].append(process_cpu)
            process_ram = proc.get('mem', {}).get('vms', {}).get('t')
            if process_ram is not None:
                result[t]['metrics']['process_ram'].append(
                    process_ram / BYTES_IN_MB)
        for log in logs:
            t = math.ceil(log['time'])
            if t not in result:
                result[t] = defaultdict(lambda: defaultdict(list))
            for k, v in log.get('data', {}).items():
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
