from collections import defaultdict
from datetime import datetime, timedelta
from functools import reduce
from requests.exceptions import HTTPError
from sqlalchemy.sql import and_
from typing import Union

from rest_api.rest_api_server.controllers.base_async import (
    BaseAsyncControllerWrapper)
from rest_api.rest_api_server.controllers.employee import EmployeeController
from rest_api.rest_api_server.controllers.profiling.base import (
    BaseProfilingController, RunCostsMixin)
from rest_api.rest_api_server.controllers.profiling.leaderboard_dataset import (
    LeaderboardDatasetController)
from rest_api.rest_api_server.controllers.profiling.leaderboard import (
    LeaderboardController)
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.models.enums import RunStates
from rest_api.rest_api_server.models.models import Employee

from tools.optscale_exceptions.common_exc import (
    NotFoundException, ConflictException)

HOUR_IN_SEC = 3600
DAY_IN_HOURS = 24


def format_employee(employee: Employee) -> dict:
    return {'id': employee.id, 'name': employee.name}


def format_resource(resource: dict, cloud_account: dict) -> dict:
    return {
        '_id': resource['_id'],
        'cloud_resource_id': resource.get('cloud_resource_id'),
        'name': resource.get('name'),
        'resource_type': resource.get('resource_type'),
        'first_seen': resource.get('first_seen'),
        'last_seen': resource.get('last_seen'),
        'region': resource.get('region'),
        'service_name': resource.get('service_name'),
        'cloud_account': cloud_account
    }


class TaskController(BaseProfilingController, RunCostsMixin):
    @staticmethod
    def format_task(
            task: 'dict', owner: 'Union[dict, None]',
            runs: 'list', run_costs: 'dict', executors: 'dict'
    ) -> 'dict':
        status = None
        last_run_reached_goals = dict()
        last_run_start, last_successful_run, last_run_duration = 0, 0, 0
        last_run_cost, last_30_days_cost, total_cost = 0, 0, 0
        last_run_executor = None
        run_metrics = {}
        last_30_days_start = int(
            (datetime.utcnow() - timedelta(days=30)).timestamp())
        if runs:
            for r in runs:
                run_cost = run_costs.get(r['id'], 0)
                total_cost += run_cost
                if r['start'] > last_30_days_start:
                    last_30_days_cost += run_cost
                if r.get('state') == RunStates.completed:
                    last_successful_run = r['start']
                for metric in task.get('metrics', []):
                    metric_id = metric['id']
                    value = r.get('data', {}).get(metric['key'])
                    if metric_id not in run_metrics:
                        run_metrics[metric_id] = metric.copy()
                        run_metrics[metric_id]['history'] = list()
                    if value is not None:
                        run_metrics[metric_id]['history'].append(value)
                        run_metrics[metric_id]['last_run_value'] = value
            last = runs[-1]

            last_run_start = last['start']
            last_run_reached_goals = last.get('reached_goals', {})
            status = RunStates(last['state']).name

            finish = last.get('finish')
            if not finish and last['state'] == RunStates.running:
                finish = datetime.utcnow().timestamp()

            last_run_duration = finish - last.get('start') if finish else None
            last_run_cost = run_costs.get(last['id'], 0)
            executor_ids = last.get('executors', [])
            if executor_ids:
                executor = executors.get(executor_ids[-1])
                if executor:
                    last_run_executor = executor
        if owner:
            task['owner'] = owner
        task.update({
            'status': status or 'created',
            'last_run': last_run_start,
            'last_run_duration': last_run_duration,
            'last_successful_run': last_successful_run,
            'runs_count': len(runs),
            'last_run_executor': last_run_executor,
            'last_run_cost': last_run_cost,
            'total_cost': total_cost,
            'run_metrics': list(run_metrics.values()),
            'last_30_days_cost': last_30_days_cost,
            'last_run_reached_goals': last_run_reached_goals,
        })
        return task

    @staticmethod
    def merge_metrics(task_metrics, kwargs):
        attach = kwargs.pop('attach', [])
        detach = kwargs.pop('detach', [])
        task_metrics.update(attach)
        return list(task_metrics.difference(detach))

    def _get_employee_by_user(self, user_id, organization_id):
        employee_ctrl = EmployeeController(
            self.session, self._config, self.token)
        return format_employee(
            employee_ctrl.get_employee_by_user_and_organization(
                user_id, organization_id))

    def _get_employee(self, employee_id, organization_id) -> dict:
        employee = self.session.query(Employee).filter(
            and_(
                Employee.deleted.is_(False),
                Employee.id == employee_id,
                Employee.organization_id == organization_id
            )
        ).one_or_none()
        if not employee:
            raise NotFoundException(Err.OE0002, ['Employee', employee_id])
        return format_employee(employee)

    def create(self, organization_id, profiling_token, **kwargs):
        owner_id = kwargs.get('owner_id')
        if not owner_id:
            auth_user_id = self.get_user_id()
            employee = self._get_employee_by_user(
                auth_user_id, organization_id)
            kwargs['owner_id'] = employee['id']
        else:
            employee = self._get_employee(owner_id, organization_id)
        task_key = kwargs.pop('key')
        try:
            task = self.create_task(
                profiling_token, task_key=task_key, **kwargs)
        except HTTPError as ex:
            if ex.response.status_code == 409:
                raise ConflictException(
                    Err.OE0534, ['Task', task_key])
            raise
        return self.format_task(task, employee, [], {}, {})

    def get(self, organization_id, task_id, profiling_token,
            last_runs=0, last_leaderboards=0):
        try:
            task = self.get_task(profiling_token, task_id)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(
                    Err.OE0002, ['Task', task_id])
            raise
        employees = self._get_employees(organization_id)
        cloud_accounts = self._get_cloud_accounts(organization_id)
        task_id = task['id']
        runs = list(self._get_runs(profiling_token, task_id).get(
            task_id, []))
        run_costs = self._get_run_costs(list(cloud_accounts.keys()), runs)
        executors = self._get_last_runs_executors(
            profiling_token, cloud_accounts, {task_id: runs})
        if last_runs:
            task.update({
                'last_runs': sorted(
                    runs, key=lambda x: x['start'], reverse=True)[:last_runs]
            })
        if last_leaderboards:
            leaderboard = LeaderboardController(
                self.session, self._config, self.token
            ).get(task_id, profiling_token)
            leaderboards_datasets = []
            if leaderboard:
                leaderboards_datasets = sorted(
                    LeaderboardDatasetController(
                        self.session, self._config, self.token
                    ).list(
                        leaderboard['id'], profiling_token
                    ), key=lambda x: x['created_at'], reverse=True
                )[:last_leaderboards]
            task.update({'last_leaderboards': leaderboards_datasets})
        return self.format_task(
            task, employees.get(task.get('owner_id')),
            runs, run_costs, executors)

    def _get_runs(
            self, profiling_token, task_id=None) -> dict[str, list[dict]]:
        if task_id:
            try:
                runs = self.list_task_runs(
                    profiling_token, task_id)
            except HTTPError as ex:
                if ex.response.status_code == 404:
                    raise NotFoundException(
                        Err.OE0002, ['Task', task_id])
                raise
        else:
            runs = self.list_runs(profiling_token)
        res = defaultdict(list)
        # further logic relies on sorted runs
        for run in sorted(runs, key=lambda r: r.get('start', 0)):
            res[run['task_id']].append(run)
        return res

    def _get_employees(self, organization_id) -> dict[str, dict]:
        employees_q = self.session.query(Employee).filter(
            Employee.deleted.is_(False),
            Employee.organization_id == organization_id
        )
        return {e.id: format_employee(e) for e in employees_q.all()}

    def _get_resources(
            self, resource_ids: list, cloud_accounts: dict[str, dict]
    ) -> dict[str, dict]:
        if not resource_ids:
            return {}
        res = self.resources_collection.find({
            'cloud_account_id': {'$in': list(cloud_accounts.keys())},
            'cloud_resource_id': {'$in': resource_ids}
        })
        return {r['cloud_resource_id']: format_resource(
            r, cloud_accounts.get(r.get('cloud_account_id'), {})) for r in res}

    def _get_last_runs_executors(self,
                                 profiling_token,
                                 cloud_accounts: dict[str, dict],
                                 task_runs: dict[str, list]
                                 ) -> dict[str, dict]:
        last_runs_ids = []
        for runs in task_runs.values():
            if runs:
                last_runs_ids.append(runs[-1]['id'])
        if not last_runs_ids:
            return {}
        executors = self.get_executors(profiling_token, run_ids=last_runs_ids)
        if not executors:
            return {}
        resources = self._get_resources(
            list(map(lambda x: x['instance_id'], executors)), cloud_accounts)
        res = {}
        for executor in executors:
            resource = resources.get(executor['instance_id'])
            executor.update({
                'discovered': True if resource else False,
                'resource': resource
            })
            res[executor['instance_id']] = executor
        return res

    def list(self, organization_id, profiling_token):
        tasks = self.list_tasks(profiling_token)
        runs = self._get_runs(profiling_token)
        employees = self._get_employees(organization_id)
        cloud_accounts = self._get_cloud_accounts(organization_id)
        run_costs = self._get_run_costs(
            list(cloud_accounts.keys()),
            list(reduce(lambda x, y: x + y, runs.values())) if runs else [])
        executors = self._get_last_runs_executors(
            profiling_token, cloud_accounts, runs)
        return [
            self.format_task(
                task, employees.get(task.get('owner_id')),
                runs.get(task['id'], []), run_costs, executors)
            for task in tasks
        ]

    def edit(self, organization_id, task_id, profiling_token, **kwargs):
        metrics = None
        if 'attach' in kwargs or 'detach' in kwargs:
            task = self.get(organization_id, task_id, profiling_token)
            task_metrics = set(map(lambda x: x['id'], task['metrics']))
            metrics = self.merge_metrics(task_metrics, kwargs)
        if metrics is not None:
            kwargs['metrics'] = metrics
        owner_id = kwargs.get('owner_id')
        if owner_id is not None:
            self._get_employee(owner_id, organization_id)
        try:
            self.update_task(profiling_token, task_id, **kwargs)
        except HTTPError as exc:
            if exc.response.status_code == 409:
                raise ConflictException(Err.OE0556, [])
            raise
        return self.get(organization_id, task_id, profiling_token)

    def delete(self, task_id, profiling_token):
        try:
            self.delete_task(profiling_token, task_id)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(
                    Err.OE0002, ['Task', task_id])
            raise


class TaskAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return TaskController
