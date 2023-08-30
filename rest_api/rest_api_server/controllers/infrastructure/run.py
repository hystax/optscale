from collections import defaultdict
from datetime import datetime, timedelta
from requests import HTTPError

from rest_api.rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api.rest_api_server.controllers.infrastructure.base import (
    BaseInfraController, get_cost)
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.models.enums import RunStates
from rest_api.rest_api_server.models.models import CloudAccount

from tools.optscale_exceptions.common_exc import NotFoundException


class RunController(BaseInfraController):
    def format_goal(self, goal: dict) -> dict:
        goal['id'] = goal.pop('_id')
        goal.pop('token', None)
        return goal

    def format_executor(self, executor: dict, cost: float) -> dict:
        executor['id'] = executor.pop('_id')
        executor.pop('token', None)
        executor['total_cost'] = cost
        return executor

    def format_runset(self, id_, name):
        return {
            'id': id_,
            'name': name
        }

    def format_run(
            self, run: dict, application_goals: list[dict],
            executors: dict[str, dict]) -> dict:
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
        run['goals'] = application_goals
        execs = []
        for e in run.get('executors', []):
            executor_object = executors.get(e)
            if not executor_object:
                continue
            execs.append(executor_object)
        run['executors'] = execs
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

    def _get_application_goals(
            self, organization_id: str, application_id: str
    ) -> list[dict]:
        applications = self._get_applications(
            organization_id, [application_id])
        if not applications:
            raise NotFoundException(
                Err.OE0002, ['Application', application_id])
        return applications[application_id]['applicationGoals']

    def _get_executors(
            self, organization_id: str, run_ids: list[str]
    ) -> dict[str, dict]:
        profiling_token = self.get_profiling_token(organization_id)
        executors = self.get_executors(profiling_token, run_ids)
        return {e['instance_id']: e for e in executors}

    def list(self, organization_id, runset_id, infrastructure_token, **kwargs):
        runset = self.__get_runset(infrastructure_token, runset_id)
        runs = self._bulk_get_runs(organization_id, runset_id)
        if not runs:
            return []
        # infra executors are directly binded to runs, mapping them
        runs_map = {}
        run_ids = []
        for run in runs:
            run_ids.append(run['_id'])
            for executor in run.get('executors', []):
                runs_map[executor] = run
        goals = self._get_application_goals(
            organization_id, runset['application_id'])
        executors = self._get_executors(organization_id, run_ids)
        cloud_accounts = self._get_cloud_accounts(
            organization_id, [runset.get('cloud_account_id')])
        cloud_account = cloud_accounts[runset.get('cloud_account_id')]
        costs = self._get_executors_usage(
            runset, runs_map, executors, cloud_account)
        executors = {i_id: self.format_executor(e, costs.get(i_id))
                     for i_id, e in executors.items()}
        goals = [self.format_goal(g) for g in goals]
        return sorted([
            self.format_run(run, goals, executors)
            for run in runs
        ], key=lambda d: d['start'])


class RunAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return RunController
