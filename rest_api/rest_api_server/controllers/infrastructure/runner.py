from enum import Enum
from requests.exceptions import HTTPError

from rest_api.rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api.rest_api_server.controllers.infrastructure.base import (
    BaseInfraController, format_cloud_account, format_region,
    format_instance_size)
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.models.models import CloudAccount

from tools.optscale_exceptions.common_exc import NotFoundException


class RunnerStates(Enum):
    starting_preparing = 1
    starting = 2
    started = 3
    destroying_scheduled = 4
    destroy_preparing = 5
    destroying = 6
    destroyed = 7
    error = 9
    waiting_arcee = 10
    unknown = 99


class RunnerController(BaseInfraController):
    @staticmethod
    def format_runner(
            runner: dict, runset: dict,
            cloud_accounts: dict[str, CloudAccount],
            costs: dict[str, float], durations: dict[str, int]
    ) -> dict:
        runner.pop('token', None)
        runner['id'] = runner.pop('_id')
        try:
            runner['state'] = RunnerStates(
                runner.pop('state')).name.replace("_", " ")
        except ValueError:
            runner['state'] = RunnerStates.unknown.name
        runner['cloud_account'] = format_cloud_account(
            cloud_accounts[runner.pop('cloud_account_id')])
        runner['instance_size'] = format_instance_size(
            runset.get('instance_type'))
        runner['region'] = format_region(runset['region_id'])
        runner['duration'] = durations.get(runner.get('instance_id'), 0)
        runner['cost'] = costs.get(runner.get('instance_id'), 0)
        return runner

    def __get_runset(self, infrastructure_token, runset_id) -> dict:
        try:
            runset = self.get_runset(infrastructure_token, runset_id)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(
                    Err.OE0002, ['Runset', runset_id])
            raise
        return runset

    def __list(self, infrastructure_token, runset_id) -> list:
        return self.list_runners(infrastructure_token, runset_id)

    def list(self, organization_id, runset_id, infrastructure_token):
        runset = self.__get_runset(infrastructure_token, runset_id)
        cloud_accounts = self._get_cloud_accounts(
            organization_id, [runset['cloud_account_id']])
        cloud_account = cloud_accounts[runset['cloud_account_id']]
        runners = self.__list(infrastructure_token, runset_id)
        costs, durations = self._get_usage(runners, cloud_account)
        return [self.format_runner(r, runset, cloud_accounts, costs, durations)
                for r in runners]


class RunnerAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return RunnerController
