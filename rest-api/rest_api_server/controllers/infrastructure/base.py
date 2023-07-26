import logging
from collections import defaultdict
from datetime import datetime, timedelta
from requests.exceptions import HTTPError
from sqlalchemy import and_
from uuid import uuid4

from sqlalchemy.exc import IntegrityError

from rest_api_server.controllers.base import (
    BaseProfilingTokenController, MongoMixin)
from rest_api_server.exceptions import Err
from rest_api_server.models.enums import RunStates
from rest_api_server.models.models import CloudAccount, Employee
from rest_api_server.utils import Config, handle_http_exc

from insider_client.client import Client as InsiderClient
from optscale_exceptions.common_exc import (
    NotFoundException, WrongArgumentsException)

CLOUD_TYPE_TO_CLOUD_MAP = {
    'aws_cnr': 'aws'
}
HOUR_IN_SEC = 3600
LOG = logging.getLogger(__name__)


def format_application(application: dict):
    if application is None:
        return {}
    return {
        'id': application['_id'],
        'name': application['name'],
        'deleted': application['deleted_at'] != 0
    }


def format_cloud_account(cloud_account: CloudAccount):
    if cloud_account is None:
        return {}
    return {
        'id': cloud_account.id,
        'name': cloud_account.name,
        'type': cloud_account.type.value,
        'deleted': cloud_account.deleted
    }


def format_region(region_id):
    # TODO: (am) hardcoded and mocked. Rewrite
    return {
        'id': region_id,
        'name': region_id,
        'cloud_type': 'aws_cnr'
    }


def format_instance_type(instance_type):
    # TODO: (am) hardcoded and mocked. Rewrite
    return {
        'name': instance_type,
        'cloud_type': 'aws_cnr'
    }


def format_instance_size(instance_size):
    # TODO: (am) hardcoded and mocked. Rewrite
    type_ = instance_size_to_type(instance_size)
    res = format_instance_type(instance_size)
    res['type'] = type_
    return res


def format_owner(owner: Employee):
    return {
        'id': owner.id,
        'name': owner.name,
        'deleted': owner.deleted
    }


def get_cost(hourly_price, duration):
    return round(hourly_price * duration / HOUR_IN_SEC, 4)


def is_run_succeeded(run: dict) -> bool:
    return run['state'] == RunStates.completed


def instance_size_to_type(instance_size: str) -> str:
    # For example m1.xlarge to m1
    return instance_size.rsplit('.', 1)[0]


class BaseInfraController(BaseProfilingTokenController, MongoMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._insider_client = None

    @property
    def insider_client(self):
        if self._insider_client is None:
            self._insider_client = InsiderClient(
                url=Config().insider_url)
            self._insider_client.secret = self.get_secret()
        return self._insider_client

    def _get_usage(
            self, runners: list[dict],
            cloud_account: CloudAccount
    ) -> tuple[dict[str, float], dict[str, int]]:
        now = int(datetime.utcnow().timestamp())
        filters = []
        min_dt, max_dt = None, None
        duration_map = {}
        cost_map = defaultdict(float)
        for runner in runners:
            if not runner.get('started_at'):
                # runner wasn't started. Nothing to count
                continue
            # set preliminary cost
            cost_map[runner['instance_id']] = runner.get('cost', 0)
            started_at = runner['started_at']
            destroyed_at = runner.get('destroyed_at') or now
            duration = destroyed_at - started_at
            duration_map[runner['instance_id']] = duration
            started_at = datetime.fromtimestamp(started_at).replace(
                hour=0, minute=0, second=0, microsecond=0)
            destroyed_at = datetime.fromtimestamp(destroyed_at).replace(
                hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            if not min_dt or min_dt > started_at:
                min_dt = started_at
            if not max_dt or max_dt < destroyed_at:
                max_dt = destroyed_at
            filters.append({
                'resource_id': runner['instance_id'],
                'start_date': {'$gte': started_at, '$lt': destroyed_at},
                'end_date': {'$lte': destroyed_at}
            })
        if not filters:
            return {}, duration_map
        raw_expenses = self.raw_expenses_collection.find({
            'cloud_account_id': cloud_account.id,
            'start_date': {'$gte': min_dt, '$lt': max_dt},
            'end_date': {'$lte': max_dt},
            '$or': filters
        })
        aggregated_cost_map = defaultdict(float)
        for exp in raw_expenses:
            aggregated_cost_map[exp['resource_id']] += exp['cost']
        cost_map.update(aggregated_cost_map)
        return cost_map, duration_map

    def _get_cloud_accounts(
            self, organization_id: str,
            cloud_account_ids: list[str],
            exclude_deleted: bool = False
    ) -> dict[str, CloudAccount]:
        cloud_accounts_q = self.session.query(CloudAccount).filter(and_(
            CloudAccount.organization_id == organization_id,
            CloudAccount.id.in_(cloud_account_ids)
        ))
        if exclude_deleted:
            cloud_accounts_q = cloud_accounts_q.filter(
                CloudAccount.deleted.is_(False))
        cloud_accounts_dict = {ca.id: ca for ca in cloud_accounts_q.all()}
        if len(cloud_account_ids) != len(cloud_accounts_dict):
            not_found = list(filter(
                lambda x: x not in cloud_accounts_dict.keys(),
                cloud_account_ids))
            raise NotFoundException(
                Err.OE0002, [CloudAccount.__name__, ', '.join(not_found)])
        return cloud_accounts_dict

    def _get_applications(
            self, organization_id: str,
            application_ids: list[str],
            exclude_deleted: bool = False
    ) -> dict[str, dict]:
        profiling_token = self.get_profiling_token(organization_id)
        applications = self.bulk_get_applications(
            profiling_token, application_ids, not exclude_deleted)
        applications_dict = {a['_id']: a for a in filter(
            lambda x: x['_id'] in application_ids, applications)}
        if len(application_ids) != len(applications_dict):
            not_found = list(filter(
                lambda x: x not in applications_dict.keys(), application_ids))
            raise NotFoundException(
                Err.OE0002, ['Application', ', '.join(not_found)])
        return applications_dict

    def _bulk_get_runs(self, organization_id: str,
                       runset_ids: list[str]) -> dict[str, list[dict]]:
        profiling_token = self.get_profiling_token(organization_id)
        runs = self.bulk_get_runs(profiling_token, runset_ids)
        runs_dict = defaultdict(list)
        for r in runs:
            runs_dict[r['runset_id']].append(r)
        return runs_dict

    def _bulk_get_runners(
            self, runset_ids, infrastructure_token
    ) -> dict[str, list[dict]]:
        runners = self.bulk_get_runners(infrastructure_token, runset_ids)
        res = defaultdict(list)
        for r in runners:
            res[r['runset_id']].append(r)
        return res

    def _get_flavor_price(
            self, cloud_type: str, instance_size: str, region_id: str
    ) -> dict:
        instance_type = instance_size_to_type(instance_size)
        flavor_prices = self._get_flavor_prices(
            cloud_type, instance_type, region_id)
        return flavor_prices.get((instance_size, region_id))

    def _get_flavor_prices(
            self, cloud_type: str, instance_type: str, region_id: str
    ) -> dict[tuple[str, str], dict]:
        type_ = CLOUD_TYPE_TO_CLOUD_MAP.get(cloud_type)
        if not type_:
            raise WrongArgumentsException(Err.OE0436, ['cloud_type'])
        try:
            _, price_info = self.insider_client.get_family_prices(
                cloud_type=type_,
                instance_family=instance_type,
                region=region_id,
                os_type='linux')
        except HTTPError as ex:
            if ex.response.status_code == 400:
                raise WrongArgumentsException(
                    Err.OE0005,
                    [f'Instance type {instance_type}',
                     f'in region {region_id}'])
            raise
        price_infos = price_info.get('prices', [])
        if not price_infos:
            raise WrongArgumentsException(
                Err.OE0005,
                [f'Instance type {instance_type}', f'in region {region_id}'])
        return {(pi['instance_type'], pi['region']): pi for pi in price_infos}

    def get_infrastructure_token(self, organization_id):
        token_obj = self.get_or_create_profiling_token(
            organization_id)
        if not token_obj.infrastructure_token:
            LOG.warning(
                'Infra token not found for organization %s. Trying to create',
                organization_id)
            token_obj.infrastructure_token = str(uuid4())
            self._create_bulldozer_token(token_obj.infrastructure_token)
            try:
                self.session.commit()
            except IntegrityError:
                self._delete_arcee_token(token_obj.infrastructure_token)
                raise
        return token_obj.infrastructure_token

    def get_profiling_token(self, organization_id):
        return self.get_or_create_profiling_token(
            organization_id).token

    # TODO: (am) possibly move methods below to appropriate providers
    @handle_http_exc
    def bulk_get_applications(self, profiling_token, application_ids,
                              include_deleted=False):
        arcee = self.get_arcee_client(profiling_token)
        _, applications = arcee.applications_bulk_get(
            application_ids, include_deleted)
        return applications

    @handle_http_exc
    def bulk_get_runs(self, profiling_token, runset_ids):
        arcee = self.get_arcee_client(profiling_token)
        _, runs = arcee.runs_bulk_get(runset_ids)
        return runs

    @handle_http_exc
    def get_executors(self, profiling_token, run_ids):
        arcee = self.get_arcee_client(profiling_token)
        _, executors = arcee.executors_get(run_ids=run_ids)
        return executors

    @handle_http_exc
    def create_template(self, infrastructure_token, **kwargs):
        bulldozer = self.get_bulldozer_client(infrastructure_token)
        _, template = bulldozer.template_create(**kwargs)
        return template

    @handle_http_exc
    def get_template(self, infrastructure_token, template_id):
        bulldozer = self.get_bulldozer_client(infrastructure_token)
        _, template = bulldozer.template_get(template_id)
        return template

    @handle_http_exc
    def delete_template(self, infrastructure_token, template_id):
        bulldozer = self.get_bulldozer_client(infrastructure_token)
        bulldozer.template_delete(template_id)

    @handle_http_exc
    def update_template(self, infrastructure_token, template_id, **kwargs):
        bulldozer = self.get_bulldozer_client(infrastructure_token)
        _, template = bulldozer.template_update(template_id, **kwargs)
        return template

    @handle_http_exc
    def list_templates(self, infrastructure_token):
        bulldozer = self.get_bulldozer_client(infrastructure_token)
        _, templates = bulldozer.templates_list()
        return templates

    @handle_http_exc
    def create_runset(self, infrastructure_token, **kwargs):
        bulldozer = self.get_bulldozer_client(infrastructure_token)
        _, runset = bulldozer.runset_create(**kwargs)
        return runset

    @handle_http_exc
    def update_runset(self, infrastructure_token, runset_id, **kwargs):
        bulldozer = self.get_bulldozer_client(infrastructure_token)
        _, runset = bulldozer.runset_update(runset_id, **kwargs)
        return runset

    @handle_http_exc
    def get_runset(self, infrastructure_token, runset_id):
        bulldozer = self.get_bulldozer_client(infrastructure_token)
        _, runset = bulldozer.runset_get(runset_id)
        return runset

    @handle_http_exc
    def list_runsets(self, infrastructure_token, template_id):
        bulldozer = self.get_bulldozer_client(infrastructure_token)
        _, runsets = bulldozer.runset_list(template_id)
        return runsets

    @handle_http_exc
    def list_runners(self, infrastructure_token, runset_id):
        bulldozer = self.get_bulldozer_client(infrastructure_token)
        _, runners = bulldozer.runners_list(runset_id)
        return runners

    @handle_http_exc
    def bulk_get_runners(self, infrastructure_token, runset_ids):
        bulldozer = self.get_bulldozer_client(infrastructure_token)
        _, runners = bulldozer.runners_bulk_get(runset_ids)
        return runners
