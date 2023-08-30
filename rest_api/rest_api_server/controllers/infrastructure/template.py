from functools import reduce
from itertools import product
from requests.exceptions import HTTPError
from typing import Iterable

from rest_api.rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api.rest_api_server.controllers.infrastructure.base import (
    BaseInfraController, format_cloud_account, format_application,
    format_instance_type, format_region)
from rest_api.rest_api_server.exceptions import Err

from tools.optscale_exceptions.common_exc import (
    NotFoundException, ConflictException, WrongArgumentsException)


def permutation(p):
    keys, values = zip(*p.items())
    exp = [dict(zip(keys, v)) for v in product(*values)]
    return exp


class TemplateController(BaseInfraController):
    @staticmethod
    def format_template(
            template: dict, cloud_accounts: dict, applications: dict
    ) -> dict:
        template.pop('token', None)
        template['id'] = template.pop('_id')
        template['cloud_accounts'] = [
            format_cloud_account(cloud_accounts[id_])
            for id_ in template.pop('cloud_account_ids')]
        template['applications'] = [
            format_application(applications[id_])
            for id_ in template.pop('application_ids')]
        template['instance_types'] = [
            format_instance_type(id_)
            for id_ in template.pop('instance_types')
        ]
        template['regions'] = [
            format_region(id_) for id_ in template.pop('region_ids')]
        return template

    def _check_instance_types(
            self, cloud_accounts: Iterable, instance_types: list,
            region_ids: list
    ):
        cloud_types = {ca.type.value for ca in cloud_accounts}
        params = {'instance_type': instance_types, 'region_id': region_ids}
        validation_passed = False
        # TODO: reduce API calls count
        for cloud_type in cloud_types:
            for combination in permutation(params):
                try:
                    self._get_flavor_prices(cloud_type, **combination)
                    validation_passed = True
                    break
                except Exception:
                    pass
        if not validation_passed:
            raise WrongArgumentsException(
                Err.OE0542, [', '.join(instance_types), ', '.join(region_ids)])

    def create(self, organization_id, infrastructure_token, **kwargs):
        cloud_accounts = self._get_cloud_accounts(
            organization_id, kwargs['cloud_account_ids'],
            exclude_deleted=True)
        applications = self._get_applications(
            organization_id, kwargs['application_ids'],
            exclude_deleted=True)
        self._check_instance_types(
            cloud_accounts.values(), kwargs['instance_types'],
            kwargs['region_ids'])
        template = self.__create(
            infrastructure_token, **kwargs)
        return self.format_template(
            template, cloud_accounts, applications)

    def __create(self, infrastructure_token, **kwargs) -> dict:
        try:
            template = self.create_template(infrastructure_token, **kwargs)
        except HTTPError as ex:
            if ex.response.status_code == 409:
                raise ConflictException(
                    Err.OE0149, ['Template', kwargs.get('name')])
            raise
        return template

    def __get(self, infrastructure_token, template_id) -> dict:
        try:
            template = self.get_template(infrastructure_token, template_id)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(
                    Err.OE0002, ['Template', template_id])
            raise
        return template

    def __edit(self, infrastructure_token, template_id, **kwargs) -> dict:
        try:
            template = self.update_template(
                infrastructure_token, template_id, **kwargs)
        except HTTPError as ex:
            if ex.response.status_code == 409:
                raise ConflictException(
                    Err.OE0149, ['Template', kwargs.get('name')])
            elif ex.response.status_code == 404:
                raise NotFoundException(
                    Err.OE0002, ['Template', template_id])
            raise
        return template

    def get(self, organization_id, template_id, infrastructure_token):
        template = self.__get(infrastructure_token, template_id)
        cloud_accounts = self._get_cloud_accounts(
            organization_id, template.get('cloud_account_ids'))
        applications = self._get_applications(
            organization_id, template.get('application_ids'))
        return self.format_template(
            template, cloud_accounts, applications)

    def edit(self, organization_id, template_id,
             infrastructure_token, **kwargs):
        template = self.__get(infrastructure_token, template_id)
        cloud_accounts = self._get_cloud_accounts(
            organization_id,
            kwargs.get('cloud_account_ids') or template['cloud_account_ids'],
            exclude_deleted=len(kwargs.get('cloud_account_ids', [])) > 0)
        applications = self._get_applications(
            organization_id,
            kwargs.get('application_ids') or template['application_ids'],
            exclude_deleted=len(kwargs.get('application_ids', [])) > 0)
        if any(map(lambda x: x in kwargs, ['instance_types', 'region_ids'])):
            self._check_instance_types(
                cloud_accounts.values(),
                kwargs.get('instance_types') or template['instance_types'],
                kwargs.get('region_ids') or template['region_ids'])
        template = self.__edit(
            infrastructure_token, template_id, **kwargs)
        return self.format_template(
            template, cloud_accounts, applications)

    def delete(self, template_id, infrastructure_token):
        try:
            self.delete_template(infrastructure_token, template_id)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFoundException(
                    Err.OE0002, ['Template', template_id])
            elif ex.response.status_code == 409:
                raise ConflictException(Err.OE0537, [template_id])
            raise

    def _bulk_get_runs(
            self, organization_id, runset_ids: list[str]
    ) -> list[dict]:
        runs = super()._bulk_get_runs(organization_id, runset_ids)
        if not runs:
            return []
        return reduce(lambda x, y: x + y, runs.values())

    def _count_runs(self, organization_id, runset_ids: list[str]) -> int:
        return len(self._bulk_get_runs(organization_id, runset_ids))

    def _get_runsets(
            self, template_id, infrastructure_token
    ) -> dict[str, dict]:
        runsets = self.list_runsets(infrastructure_token, template_id)
        return {r['_id']: r for r in runsets}

    def list_overview(self, organization_id, infrastructure_token):
        def _format_overview(t, runs_count_, total_cost_, last_runset_cost_):
            return {
                'id': t['_id'],
                'name': t['name'],
                'total_runs': runs_count_,
                'total_cost': total_cost_,
                'last_runset_cost': last_runset_cost_
            }

        templates = self.list_templates(infrastructure_token)
        if not templates:
            return []
        cloud_account_ids = list(set(reduce(
            lambda x, y: x + y,
            map(lambda z: z['cloud_account_ids'], templates))))
        cloud_accounts = self._get_cloud_accounts(
            organization_id, cloud_account_ids)
        res = []
        for template in templates:
            runs_count = 0
            total_cost = 0
            last_runset_cost = 0
            runsets = self._get_runsets(template['_id'], infrastructure_token)
            if runsets:
                runset_ids = list(runsets.keys())
                runs_count = self._count_runs(organization_id, runset_ids)
                runners = self._bulk_get_runners(
                    runset_ids, infrastructure_token)
                last_runset_id = runset_ids[0]
                for runset_id, runset in runsets.items():
                    costs, _ = self._get_usage(
                        runners.get(runset_id, []),
                        cloud_accounts[runset['cloud_account_id']])
                    runset_cost = sum(costs.values())
                    # set initial last_runset_id value or overwrite with
                    # fresher sample
                    if runset['created_at'] >= runsets[last_runset_id]['created_at']:
                        last_runset_cost = runset_cost
                        last_runset_id = runset_id
                    total_cost += runset_cost
            res.append(_format_overview(
                template, runs_count, total_cost, last_runset_cost))
        return res


class TemplateAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return TemplateController
