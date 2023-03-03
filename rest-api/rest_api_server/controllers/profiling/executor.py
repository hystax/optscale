import uuid
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from rest_api_server.controllers.base import MongoMixin
from rest_api_server.models.models import CloudAccount
from rest_api_server.controllers.profiling.base import BaseProfilingController
from rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from requests.exceptions import HTTPError

BYTES_IN_MB = 1024 * 1024


class ExecutorController(BaseProfilingController, MongoMixin):

    def list(self, organization_id, application_ids, profiling_token, **kwargs):
        run_ids = kwargs.get('run_ids')
        if not application_ids and not run_ids:
            applications = self.list_applications(profiling_token)
            application_ids = list(map(lambda x: x['id'], applications))
        response = self.get_executors(
            profiling_token, application_ids, run_ids)
        if response:
            cloud_resource_ids = list(map(
                lambda x: x['instance_id'], response))
            resources = self.get_executor_info(
                organization_id, cloud_resource_ids)
            for r in response:
                resource = resources.get(r['instance_id'])
                r.update({
                    'discovered': True if resource else False,
                    'resource': resource
                })
        return response

    def get_executor_info(self, organization_id, executor_ids):
        if not executor_ids:
            return {}
        cloud_accounts_map = self.get_cloud_accounts_map(organization_id)
        res = list(self.resources_collection.find({
            'cloud_account_id': {'$in': list(cloud_accounts_map.keys())},
            'cloud_resource_id': {'$in': executor_ids}
        }))
        resources = {r['cloud_resource_id']: r for r in res}
        for r_id, resource in resources.items():
            if resource:
                resource.update({
                    'cloud_account': cloud_accounts_map.get(
                        resource['cloud_account_id']),
                    'first_seen': resource.get('first_seen'),
                    'last_seen': resource.get('last_seen')
                })
        return resources

    def get_cloud_accounts_map(self, organization_id):
        cloud_accounts = self.session.query(CloudAccount).filter(
            CloudAccount.deleted.is_(False),
            CloudAccount.organization_id == organization_id
        ).all()
        return {
            ca.id: {'name': ca.name, 'type': ca.type.value, 'id': ca.id}
            for ca in cloud_accounts
        }

    def breakdown_get(self, breakdown_by, profiling_token):
        breakdowns_map = {
            'executors_count': lambda x: x['instance_id'],
            'cpu': lambda x: x.get(
                'proc_stats', {}).get('ps_stats', {}).get('cpu_percent', 0),
            'ram': lambda x: x.get(
                'proc_stats', {}).get('ps_stats', {}).get('used_ram_mb', 0),
            'process_cpu': lambda x: x.get(
                'proc_stats', {}).get('proc', {}).get('cpu', 0),
            'process_ram': lambda x: x.get(
                'proc_stats', {}).get('proc', {}).get('mem', {}).get(
                'vms', {}).get('t', 0) / BYTES_IN_MB

        }
        applications = self.list_applications(profiling_token)
        result = defaultdict(list)
        for app in applications:
            try:
                runs = self.list_runs(profiling_token, app['id'])
                for run in runs:
                    proc_data = self.list_proc_data(profiling_token, run['id'])
                    for p in proc_data:
                        dt = datetime.fromtimestamp(p['timestamp']).replace(
                            hour=0, minute=0, second=0, microsecond=0,
                            tzinfo=timezone.utc)
                        result[dt].append(breakdowns_map[breakdown_by](p))
            except HTTPError:
                continue
        breakdown = {}
        for dt, values in result.items():
            if breakdown_by == 'executors_count':
                breakdown[int(dt.timestamp())] = len(set(values))
            else:
                breakdown[int(dt.timestamp())] = sum(values) / len(values)
        return {
            'breakdown': breakdown,
            'breakdown_by': breakdown_by
        }


class ExecutorAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return ExecutorController
