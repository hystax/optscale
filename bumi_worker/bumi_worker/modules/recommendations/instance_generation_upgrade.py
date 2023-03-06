import logging

from collections import OrderedDict, defaultdict
from datetime import datetime, timedelta
from insider_client.client import Client as InsiderClient

from bumi_worker.modules.base import ModuleBase

LOG = logging.getLogger(__name__)
SUPPORTED_CLOUD_TYPES = [
    'aws_cnr',
    'azure_cnr',
    'alibaba_cnr'
]
BULK_SIZE = 500


class InstanceGenerationUpgrade(ModuleBase):
    def __init__(self, organization_id, config_client, created_at):
        super().__init__(organization_id, config_client, created_at)
        self.option_ordered_map = OrderedDict({
            'excluded_pools': {
                'default': {},
                'clean_func': self.clean_excluded_pools,
            },
            'skip_cloud_accounts': {'default': []}
        })
        self._insider_cl = None

    @property
    def insider_cl(self):
        if self._insider_cl is None:
            self._insider_cl = InsiderClient(
                url=self.config_cl.insider_url(),
                secret=self.config_cl.cluster_secret(),
                verify=False)
        return self._insider_cl

    def get_organization_currency(self):
        _, organization = self.rest_client.organization_get(
            self.organization_id)
        return organization.get('currency', 'USD')

    def _get(self):
        (excluded_pools, skip_cloud_accounts) = self.get_options_values()
        cloud_account_map = self.get_cloud_accounts(
            supported_cloud_types=SUPPORTED_CLOUD_TYPES,
            skip_cloud_accounts=skip_cloud_accounts)
        cloud_account_ids = list(cloud_account_map.keys())
        now = datetime.utcnow()
        instances = self.mongo_client.restapi.resources.find({
            '$and': [
                {'resource_type': {'$in': ['Instance', 'RDS Instance']}},
                {'active': True},
                {'cloud_account_id': {'$in': cloud_account_ids}}
            ]})
        employees = self.get_employees()
        pools = self.get_pools()
        instance_map = {ins['cloud_resource_id']: ins for ins in instances}
        cloud_resource_ids = list(instance_map.keys())
        result = []
        stats_map = {}
        currency = self.get_organization_currency()
        for i in range(0, len(cloud_resource_ids), BULK_SIZE):
            bulk_ids = cloud_resource_ids[i:i + BULK_SIZE]
            raw_expenses = self.mongo_client.restapi.raw_expenses.aggregate([
                {'$match': {
                    '$and': [
                        {'box_usage': True},
                        {'resource_id': {'$in': bulk_ids}},
                        {'start_date': {'$gte': now - timedelta(days=7)}},
                        {'cloud_account_id': {'$in': cloud_account_ids}},
                    ]
                }},
                {'$group': {
                    '_id': '$resource_id',
                    'os': {'$last': '$product/operatingSystem'},
                    'software': {'$last': '$product/preInstalledSw'},
                    'daily_costs': {'$push': {
                        "date": "$start_date",
                        "cost": '$cost'
                    }},
                    'meter_id': {'$last': '$meter_id'},
                }},
            ])
            for raw_info in raw_expenses:
                instance = instance_map.get(raw_info['_id'])
                cloud_account_id = instance['cloud_account_id']
                if cloud_account_id not in stats_map:
                    stats_map[cloud_account_id] = {
                        'success': 0, 'not_found_recommended_flavors': 0,
                        'cheap_old_flavor': 0}
                pool_id = instance.get('pool_id')
                flavor = instance['meta']['flavor']
                ca = cloud_account_map[cloud_account_id]
                cloud_type = ca['type']
                meter_id = raw_info.get('meter_id')
                os_type = instance['meta'].get('os') or raw_info.get('os')
                preinstalled = raw_info.get('software')
                daily_cost_map = defaultdict(int)
                for daily_cost in raw_info.get('daily_costs', []):
                    raw_date = daily_cost['date']
                    daily_cost_map[raw_date] += daily_cost.get('cost', 0)
                current_daily_cost = max(daily_cost_map.values())
                generation_params = {
                    'cloud_type': cloud_type,
                    'region': instance['region'],
                    'current_flavor': flavor,
                    'os_type': os_type,
                }
                if preinstalled and cloud_type == 'aws_cnr':
                    generation_params['preinstalled'] = preinstalled
                if meter_id and cloud_type == 'azure_cnr':
                    generation_params['meter_id'] = meter_id
                _, gen_resp = self.insider_cl.find_flavor_generation(
                    **generation_params, currency=currency)
                if not gen_resp:
                    stats_map[cloud_account_id][
                        'not_found_recommended_flavors'] += 1
                    continue
                if gen_resp.get('proposed_daily_price') > current_daily_cost:
                    stats_map[cloud_account_id]['cheap_old_flavor'] += 1
                    continue
                result.append({
                    "cloud_resource_id": instance['cloud_resource_id'],
                    "resource_name": instance.get('name'),
                    "resource_id": instance['_id'],
                    "cloud_account_id": instance['cloud_account_id'],
                    "cloud_type": cloud_type,
                    "region": instance['region'],
                    "owner": self._extract_owner(instance.get('employee_id'),
                                                 employees),
                    "pool": self._extract_pool(pool_id, pools),
                    "saving": (current_daily_cost - gen_resp[
                        'proposed_daily_price']) * 30,
                    "recommended_flavor": gen_resp['proposed_flavor'],
                    "is_excluded": pool_id in excluded_pools,
                    "flavor": flavor
                })
                stats_map[cloud_account_id]['success'] += 1
        for cloud_acc_id, stat in stats_map.items():
            cloud_type = cloud_account_map[cloud_acc_id]['type']
            LOG.info('Instance_generation_upgrade statistics for %s (%s): %s',
                     self.organization_id, cloud_type, stat)
        return result


def main(organization_id, config_client, created_at, **kwargs):
    return InstanceGenerationUpgrade(
        organization_id, config_client, created_at).get()


def get_module_email_name():
    return 'Not last generation flavor Instance'
