from collections import defaultdict
from datetime import datetime
from requests.exceptions import HTTPError
from sqlalchemy import and_

from rest_api.rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api.rest_api_server.controllers.employee import EmployeeController
from rest_api.rest_api_server.controllers.infrastructure.base import (
    BaseInfraController, is_run_succeeded, format_cloud_account,
    format_task, format_instance_size, format_region, format_owner)
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.models.models import Employee

from tools.optscale_exceptions.common_exc import (
    NotFoundException, WrongArgumentsException, ConflictException)


MIN_CPU_COUNT = 4
STOP_ACTION = 'stop'
STOPPED_STATE = 6


def load_hyperparameters(
        dumped_parameters: dict[str, str]
) -> dict[str, list]:
    res = defaultdict(list)
    for k, v in dumped_parameters.items():
        res[k] = list(map(lambda x: x.strip(), v.split(',')))
    return dict(res)


def dump_hyperparameters(
        loaded_parameters: dict[str, list]
) -> dict[str, str]:
    return {k: ','.join(v) for k, v in loaded_parameters.items()}


def format_template(template: dict) -> dict:
    return {
        'id': template['_id'],
        'name': template['name']
    }


def get_runners_duration(runners: list[dict]) -> int:
    min_started_at = 0
    max_destroyed_at = 0
    now = int(datetime.utcnow().timestamp())
    for runner in runners:
        if not runner.get('started_at'):
            # we need start point to calculate something
            continue
        if not min_started_at:
            min_started_at = runner['started_at']
        else:
            min_started_at = min(min_started_at, runner['started_at'])
        if not max_destroyed_at:
            max_destroyed_at = runner.get('destroyed_at') or now
        else:
            max_destroyed_at = max(
                max_destroyed_at, runner.get('destroyed_at', now))
    return max_destroyed_at - min_started_at


class RunsetController(BaseInfraController):
    def format_runset(
            self, runset, template: dict, runners: list[dict],
            runs: list[dict], cloud_accounts: dict, tasks: dict,
            owners: dict
    ) -> dict:
        runset.pop('token', None)
        runset['id'] = runset.pop('_id')
        runset.pop('template_id')
        cloud_account = cloud_accounts[runset.pop('cloud_account_id')]
        costs, _ = self._get_usage(runners, cloud_account)
        duration = get_runners_duration(runners)
        runset['cloud_account'] = format_cloud_account(cloud_account)
        runset['task'] = format_task(tasks[runset.pop('task_id')])
        owner_id = runset.pop('owner_id', None)
        if owner_id:
            runset['owner'] = format_owner(owners[owner_id])
        runset['instance_size'] = format_instance_size(
            runset.pop('instance_type'))
        runset['region'] = format_region(runset.pop('region_id'))
        runset['template'] = format_template(template)
        runset['hyperparameters'] = dump_hyperparameters(
            runset['hyperparameters'])
        runset['duration'] = duration
        runset['cost'] = sum(costs.values())
        runset['runs_count'] = len(runs)
        runset['succeeded_runs'] = len(
            [r for r in runs if is_run_succeeded(r)])
        return runset

    def _get_employee(self, organization_id: str, user_id: str) -> Employee:
        return EmployeeController(
            self.session, self._config, self.token
        ).get_employee_by_user_and_organization(
            user_id, organization_id)

    def __get_template(self, infrastructure_token, template_id) -> dict:
        try:
            template = self.get_template(infrastructure_token, template_id)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(
                    Err.OE0002, ['Template', template_id])
            raise
        return template

    @staticmethod
    def _check_is_template_based(template, **data):
        for template_k, runset_k in [
            ('cloud_account_ids', 'cloud_account_id'),
            ('region_ids', 'region_id'),
            ('instance_types', 'instance_type'),
            ('task_ids', 'task_id')
        ]:
            if data.get(runset_k) not in template.get(template_k):
                raise WrongArgumentsException(Err.OE0538, [runset_k, ', '.join(
                    template.get(template_k))])
        if data.get('name_prefix') != template.get('name_prefix'):
            raise WrongArgumentsException(
                Err.OE0539, ['name_prefix', template.get('name_prefix')])
        runset_budget = data.get('destroy_conditions', {}).get('max_budget')
        if runset_budget is not None:
            if runset_budget > template.get('budget'):
                raise WrongArgumentsException(
                    Err.OE0541, ['max_budget', template.get('budget')])
        for k, v in template.get('tags', {}).items():
            if data.get('tags', {}).get(k) != v:
                raise WrongArgumentsException(
                    Err.OE0539, [f'tags.{k}', v])

    @staticmethod
    def _check_hyperparameters(template_params: dict, runset_params: dict):
        unmatched_params = set(template_params.values()) ^ set(
            runset_params.keys())
        if unmatched_params:
            raise WrongArgumentsException(
                Err.OE0540, [', '.join(unmatched_params)])

    @staticmethod
    def _build_destroy_conditions(
            runset_conditions: dict, budget: float
    ) -> dict:
        res = runset_conditions
        if 'max_budget' not in res:
            res['max_budget'] = budget
        return res

    def _find_instance_size(
            self, template_id: str, infrastructure_token: str,
            cloud_type: str, instance_type: str, region_id: str
    ) -> dict:
        price_infos = list(self._get_flavor_prices(
            cloud_type, instance_type, region_id).values())
        price_infos = sorted(price_infos, key=lambda r: r['price'])
        # trying to select something with "MIN_CPU_COUNT" CPUs
        suitable_price_infos = list(filter(
            lambda pi: pi['cpu'] >= MIN_CPU_COUNT, price_infos))
        if not suitable_price_infos:
            # return max available instance size if nothing suitable found
            return price_infos[-1]
        prev_runsets = self.__list(infrastructure_token, template_id)
        if not prev_runsets:
            # take intermediate size in instance family scope (upper bound)
            pos = len(suitable_price_infos) // 2
            return suitable_price_infos[pos]
        # TODO: re-implement me
        # here we should select instance size based on previous runset runs
        # it must be covered by separate design
        # taking minimum instance size with 4 CPU for now (based on price)
        return suitable_price_infos[0]

    def __create(self, infrastructure_token, template_id, **kwargs) -> dict:
        try:
            runset = self.create_runset(
                infrastructure_token, template_id=template_id, **kwargs)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(
                    Err.OE0002, ['Template', template_id])
            raise
        return runset

    def create(self, organization_id, template_id,
               infrastructure_token, **kwargs):
        template = self.__get_template(infrastructure_token, template_id)
        self._check_is_template_based(template, **kwargs)
        cloud_accounts = self._get_cloud_accounts(
            organization_id, [kwargs.get('cloud_account_id')],
            exclude_deleted=True)
        tasks = self._get_tasks(
            organization_id, [kwargs.get('task_id')],
            exclude_deleted=True)
        owner = self._get_employee(organization_id, kwargs.pop('user_id'))
        owners = {owner.id: owner}
        kwargs['owner_id'] = owner.id
        price_info = self._find_instance_size(
            template_id, infrastructure_token,
            cloud_accounts[kwargs.get('cloud_account_id')].type.value,
            kwargs['instance_type'], kwargs['region_id'])
        kwargs['instance_type'] = price_info['instance_type']
        self._check_hyperparameters(
            template.get('hyperparameters', {}), kwargs['hyperparameters'])
        kwargs['hyperparameters'] = load_hyperparameters(
            kwargs['hyperparameters'])
        kwargs['destroy_conditions'] = self._build_destroy_conditions(
            kwargs.pop('destroy_conditions', {}), template['budget'])
        runset = self.__create(
            infrastructure_token, template_id=template_id, **kwargs)
        return self.format_runset(
            runset, template, list(), list(), cloud_accounts, tasks,
            owners)

    def __edit(self, infrastructure_token, runset_id, **kwargs) -> dict:
        try:
            runset = self.update_runset(
                infrastructure_token, runset_id, **kwargs)
        except HTTPError as ex:
            if ex.response.status_code == 409:
                raise ConflictException(
                    Err.OE0544, [runset_id, kwargs.get('state')])
            elif ex.response.status_code == 404:
                raise NotFoundException(
                    Err.OE0002, ['Runset', runset_id])
            raise
        return runset

    def edit(self, organization_id, runset_id,
             infrastructure_token, **kwargs):
        if kwargs['action'] != STOP_ACTION:
            raise WrongArgumentsException(
                Err.OE0545, [kwargs['action']])
        runset = self.__edit(
            infrastructure_token, runset_id, state=STOPPED_STATE)
        template = self.__get_template(
            infrastructure_token, runset['template_id'])
        cloud_accounts = self._get_cloud_accounts(
            organization_id, [runset.get('cloud_account_id')])
        tasks = self._get_tasks(organization_id, [runset.get('task_id')])
        owners = self._get_owners(organization_id, [runset.get('owner_id')])
        runners = self.__list_runners(infrastructure_token, runset_id)
        runs = self.__list_runs(organization_id, runset_id)
        return self.format_runset(
            runset, template, runners, runs, cloud_accounts, tasks,
            owners)

    def __get(self, infrastructure_token, runset_id) -> dict:
        try:
            runset = self.get_runset(infrastructure_token, runset_id)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(
                    Err.OE0002, ['Runset', runset_id])
            raise
        return runset

    def __list(self, infrastructure_token, template_id) -> list[dict]:
        runsets = self.list_runsets(infrastructure_token, template_id)
        runsets = sorted(runsets, key=lambda r: r['number'])
        return runsets

    def __list_runners(self, infrastructure_token, runset_id) -> list:
        return self.list_runners(infrastructure_token, runset_id)

    def __list_runs(self, organization_id: str, runset_id: str) -> list[dict]:
        runs_dict = self._bulk_get_runs(organization_id, [runset_id])
        return runs_dict.get(runset_id, [])

    def _get_owners(
            self, organization_id: str,
            owner_ids: list[str]
    ) -> dict[str, Employee]:
        # is used only in display purposes. No need to filter deleted entities
        owner_ids = list(filter(None, owner_ids))
        owners_q = self.session.query(Employee).filter(and_(
            Employee.organization_id == organization_id,
            Employee.id.in_(owner_ids),
        ))
        owners_dict = {o.id: o for o in owners_q.all()}
        if len(owner_ids) != len(owners_dict):
            not_found = list(filter(
                lambda x: x not in owners_dict.keys(),
                owner_ids))
            raise NotFoundException(
                Err.OE0002, [Employee.__name__, ', '.join(not_found)])
        return owners_dict

    def get(self, organization_id, runset_id, infrastructure_token):
        runset = self.__get(infrastructure_token, runset_id)
        template = self.__get_template(
            infrastructure_token, runset['template_id'])
        cloud_accounts = self._get_cloud_accounts(
            organization_id, [runset.get('cloud_account_id')])
        tasks = self._get_tasks(organization_id, [runset.get('task_id')])
        owners = self._get_owners(organization_id, [runset.get('owner_id')])
        runners = self.__list_runners(infrastructure_token, runset_id)
        runs = self.__list_runs(organization_id, runset_id)
        return self.format_runset(
            runset, template, runners, runs, cloud_accounts, tasks,
            owners)

    def list(self, organization_id, template_id, infrastructure_token):
        template = self.__get_template(infrastructure_token, template_id)
        runsets = self.__list(infrastructure_token, template_id)
        if not runsets:
            return []
        task_ids = set()
        cloud_account_ids = set()
        owner_ids = set()
        runset_ids = list()
        instance_types = set()
        region_ids = set()
        for runset in runsets:
            task_ids.add(runset['task_id'])
            cloud_account_ids.add(runset['cloud_account_id'])
            owner_ids.add(runset['owner_id'])
            instance_types.add(runset['instance_type'])
            region_ids.add(runset['region_id'])
            runset_ids.append(runset['_id'])
        tasks = self._get_tasks(organization_id, list(task_ids))
        cloud_accounts = self._get_cloud_accounts(
            organization_id, list(cloud_account_ids))
        owners = self._get_owners(organization_id, list(owner_ids))
        runs = self._bulk_get_runs(organization_id, runset_ids)
        runners = self._bulk_get_runners(runset_ids, infrastructure_token)
        res = []
        total_runs = 0
        total_cost = 0
        for runset in runsets:
            formatted_runset = self.format_runset(
                runset, template, runners.get(runset['_id'], []),
                runs.get(runset['_id'], []), cloud_accounts, tasks,
                owners)
            total_runs += formatted_runset['runs_count']
            total_cost += formatted_runset['cost']
            res.append(formatted_runset)
        return {
            'runsets': res,
            'total_runs': total_runs,
            'total_cost': total_cost,
            'last_runset_cost': res[-1]['cost'] if res else 0
        }


class RunsetAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return RunsetController
