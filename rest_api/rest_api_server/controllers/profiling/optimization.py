from rest_api.rest_api_server.controllers.optimization import (
    OptimizationController, ACTIVE_STATUS)
from rest_api.rest_api_server.controllers.profiling.base import BaseProfilingController
from rest_api.rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api.rest_api_server.controllers.checklist import ChecklistController
from tools.optscale_exceptions.common_exc import NotFoundException
from rest_api.rest_api_server.exceptions import Err
from requests.exceptions import HTTPError
from datetime import datetime

LAST_RUNS_THRESHOLD = 7 * 86400  # 7 days


class TaskOptimizationsController(BaseProfilingController,
                                  OptimizationController):

    @staticmethod
    def get_basic_response(checklist):
        return {
            'total_saving': 0,
            'total_count': 0,
            'optimizations': {},
            'dismissed_optimizations': {},
            'excluded_optimizations': {},
        }

    @staticmethod
    def collect_executor_ids(runs):
        executor_ids = set()
        for r in runs:
            executor_ids.update(r.get('executors', []))
        return list(executor_ids)

    def _get_optimizations_data(self, checklist, instance_ids):
        res = super()._get_optimizations_data(checklist)
        optimization_data = []
        for r in res:
            data = []
            for d in r.get('data', []):
                if d.get('cloud_resource_id') not in instance_ids:
                    continue
                data.append(d)
            r['data'] = data
            optimization_data.append(r)
        return optimization_data

    def get_last_task_runs(self, task_id, profiling_token):
        try:
            runs = self.list_task_runs(profiling_token, task_id)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(
                    Err.OE0002, ['Task', task_id])
            raise
        now = int(datetime.utcnow().timestamp())
        return list(filter(
            lambda x: x['start'] >= now - LAST_RUNS_THRESHOLD, runs))

    def get_optimizations(
            self, organization_id, task_id, profiling_token,
            types, status):
        runs = self.get_last_task_runs(task_id, profiling_token)
        executor_ids = self.collect_executor_ids(runs)
        checklist = ChecklistController(
            self.session, self._config).get_by_organization(organization_id)
        res = self.get_basic_response(checklist)
        optimization_groups = list(self._get_optimizations_data(
            checklist, executor_ids))
        for group in optimization_groups:
            module = group.get('module')
            res_map = self.fill_optimization_group(
                group, [], module in types if types else True, 0,
                status or ACTIVE_STATUS)
            self._process_optimization_statuses(res, res_map, module)
        res['total_count'] = sum(list(map(
            lambda x: x.get('count', 0), res['optimizations'].values())))
        return res


class TaskOptimizationAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return TaskOptimizationsController
