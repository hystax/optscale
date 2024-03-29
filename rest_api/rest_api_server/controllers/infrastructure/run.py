from collections import defaultdict
from datetime import datetime, timedelta
from requests import HTTPError

from rest_api.rest_api_server.controllers.base_async import (
    BaseAsyncControllerWrapper)
from rest_api.rest_api_server.controllers.infrastructure.base import (
    BaseInfraController, get_cost)
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.models.enums import RunStates
from rest_api.rest_api_server.models.models import CloudAccount

from tools.optscale_exceptions.common_exc import NotFoundException


class RunController(BaseInfraController):
    def format_metric(self, metric: dict) -> dict:
        metric['id'] = metric.pop('_id')
        metric.pop('token', None)
        return metric

    def format_executor(self, executor: dict, cost: float) -> dict:
        executor['id'] = executor.pop('_id')
        executor.pop('token', None)
        executor['total_cost'] = cost
        return executor

    def format_runset(self, id_: str, name: str) -> dict:
        return {
            'id': id_,
            'name': name
        }

    def format_dataset(self, dataset: dict) -> dict:
        return {
            'id': dataset['_id'],
            'name': dataset['name'],
            'deleted': dataset['deleted_at'] != 0,
            'path': dataset['path'],
            'labels': dataset['labels'],
            'training_set': dataset['training_set'],
            'validation_set': dataset['validation_set'],
        }

    def format_run(
            self, run: dict, task_metrics: list[dict],
            executors: dict[str, dict], datasets: dict[str, dict]
    ) -> dict:
        run['id'] = run.pop('_id')
        run.pop('token', None)
        if run.get('hyperparameters') is None:
            run['hyperparameters'] = {}
        state = run.get('state')
        run['status'] = RunStates(state).name
        finish = run.get('finish')
        if not finish and state == RunStates.running:
            finish = datetime.utcnow().timestamp()
        duration = finish - run.get('start')
        run['runset'] = self.format_runset(
            run.pop('runset_id'), run.pop('runset_name', None))
        run['duration'] = duration
        run['metrics'] = task_metrics
        execs = []
        for e in run.get('executors', []):
            executor_object = executors.get(e)
            if not executor_object:
                continue
            execs.append(executor_object)
        run['executors'] = execs
        run['dataset'] = datasets.get(run.pop('dataset_id', None))
        return run

    def _get_executors_usage(
            self, runset: dict, runs: dict[str, dict],
            executors: dict[str, dict], cloud_account: CloudAccount
    ) -> dict[str, float]:
        if not runset.get('started_at'):
            # runset wasn't started. Nothing to count
            return {}
        if not executors:
            # no executors created. Nothing to count
            return {}
        now = int(datetime.utcnow().timestamp())
        started_at = runset['started_at']
        destroyed_at = runset.get('destroyed_at') or now
        started_at = datetime.fromtimestamp(started_at).replace(
            hour=0, minute=0, second=0, microsecond=0)
        destroyed_at = datetime.fromtimestamp(destroyed_at).replace(
            hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        raw_expenses = self.raw_expenses_collection.find({
            'cloud_account_id': runset['cloud_account_id'],
            'start_date': {'$gte': started_at, '$lt': destroyed_at},
            'end_date': {'$lte': destroyed_at},
            'resource_id': {'$in': [i_id for i_id in executors.keys()]}
        })
        cost_map = defaultdict(float)
        for exp in raw_expenses:
            cost_map[exp['resource_id']] += exp['cost']
        # get rid of delay in expenses occurrence
        hourly_price = None
        for instance_id in executors.keys():
            if instance_id not in cost_map:
                if hourly_price is None:
                    price_info = self._get_flavor_price(
                        cloud_account.type.value, runset['instance_type'],
                        runset['region_id'])
                    hourly_price = price_info.get('price', 0)
                run = runs[instance_id]
                if not run['start']:
                    duration = 0
                else:
                    duration = (run.get('finish') or now) - run['start']
                cost_map[instance_id] = get_cost(hourly_price, duration)
        return cost_map

    def __get_runset(self, infrastructure_token, runset_id) -> dict:
        try:
            runset = self.get_runset(infrastructure_token, runset_id)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(
                    Err.OE0002, ['Runset', runset_id])
            raise
        return runset

    def _bulk_get_runs(self, organization_id: str,
                       runset_id: str) -> list[dict]:
        profiling_token = self.get_profiling_token(organization_id)
        return self.bulk_get_runs(profiling_token, [runset_id])

    def _get_task_metrics(
            self, organization_id: str, task_id: str
    ) -> list[dict]:
        tasks = self._get_tasks(
            organization_id, [task_id])
        if not tasks:
            raise NotFoundException(
                Err.OE0002, ['Task', task_id])
        return tasks[task_id]['taskMetrics']

    def _get_executors(
            self, organization_id: str, run_ids: list[str]
    ) -> dict[str, dict]:
        profiling_token = self.get_profiling_token(organization_id)
        executors = self.get_executors(profiling_token, run_ids)
        return {e['instance_id']: e for e in executors}

    def _get_datasets(
            self, organization_id: str, dataset_ids: set[str]
    ) -> dict[str, dict]:
        if not dataset_ids:
            return {}
        profiling_token = self.get_profiling_token(organization_id)
        datasets = self.list_datasets(profiling_token, include_deleted=True)
        return {d['_id']: d for d in datasets if d['_id'] in dataset_ids}

    def list(self, organization_id, runset_id, infrastructure_token, **kwargs):
        runset = self.__get_runset(infrastructure_token, runset_id)
        runs = self._bulk_get_runs(organization_id, runset_id)
        if not runs:
            return []
        # infra executors are directly binded to runs, mapping them
        runs_map = {}
        run_ids = []
        dataset_ids = set()
        for run in runs:
            run_ids.append(run['_id'])
            if run.get('dataset_id'):
                dataset_ids.add(run['dataset_id'])
            for executor in run.get('executors', []):
                runs_map[executor] = run
        metrics = self._get_task_metrics(
            organization_id, runset['task_id'])
        executors = self._get_executors(organization_id, run_ids)
        cloud_accounts = self._get_cloud_accounts(
            organization_id, [runset.get('cloud_account_id')])
        cloud_account = cloud_accounts[runset.get('cloud_account_id')]
        costs = self._get_executors_usage(
            runset, runs_map, executors, cloud_account)
        executors = {i_id: self.format_executor(e, costs.get(i_id))
                     for i_id, e in executors.items()}
        metrics = [self.format_metric(g) for g in metrics]
        datasets = {d_id: self.format_dataset(d)
                    for d_id, d in self._get_datasets(
                organization_id, dataset_ids).items()}
        return sorted([
            self.format_run(run, metrics, executors, datasets)
            for run in runs
        ], key=lambda d: d['start'])


class RunAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return RunController
