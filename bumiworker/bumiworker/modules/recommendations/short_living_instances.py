from collections import OrderedDict
from datetime import datetime, timedelta

from bumiworker.bumiworker.modules.base import ModuleBase

DAYS_RANGE = 3
LIVE_HRS_THRESHOLD = 6
NEBIUS_MIN_CPU = 2
HOUR_IN_SECONDS = 3600
SPOT_SAVING_COEFFICIENT = 0.72
BULK_SIZE = 1000
SUPPORTED_CLOUD_TYPES = ['aws_cnr', 'alibaba_cnr', 'azure_cnr', 'nebius']


class ShortLivingInstances(ModuleBase):
    def __init__(self, organization_id, config_client, created_at):
        super().__init__(organization_id, config_client, created_at)
        self.option_ordered_map = OrderedDict({
            'days_threshold': {'default': DAYS_RANGE},
            'excluded_pools': {
                'default': {},
                'clean_func': self.clean_excluded_pools,
            },
            'skip_cloud_accounts': {'default': []}
        })

    @staticmethod
    def _is_flavor_cost(exp):
        # AWS
        if (exp.get('lineItem/UsageType') and
                'BoxUsage' in exp['lineItem/UsageType']):
            return True
        # Azure
        elif (exp.get('meter_details', {}).get(
                'meter_category') == 'Virtual Machines'):
            return True
        # Alibaba
        elif (exp.get('BillingItem') == 'Cloud server configuration' and
              'key:acs:ecs:payType value:spot' not in exp.get('Tags', [])):
            return True
        # Nebius
        elif (exp.get('service_name') == 'Compute Cloud' and
              ('RAM' not in exp.get('sku_name')) and
              ('Intel' in exp.get('sku_name') or 'AMD' in exp.get('sku_name'))):
            return True

    @staticmethod
    def _get_work_hrs(exp, cpu_count=None):
        # Azure
        if exp.get('usage_quantity'):
            return float(exp['usage_quantity'])
        # Alibaba
        elif exp.get('Usage'):
            return float(exp['Usage'])
        # Nebius
        elif exp.get('pricing_quantity'):
            # pricing_quantity measurement unit is core*hour
            cpu_count = cpu_count or NEBIUS_MIN_CPU
            return float(exp['pricing_quantity']) / cpu_count
        return 0

    def _get(self):
        (days_threshold, excluded_pools,
         skip_cloud_accounts) = self.get_options_values()
        cloud_account_map = self.get_cloud_accounts(
            supported_cloud_types=SUPPORTED_CLOUD_TYPES,
            skip_cloud_accounts=skip_cloud_accounts)
        now = datetime.utcnow()
        start_datetime = datetime.utcfromtimestamp(0)
        start_date = now - timedelta(days=days_threshold)
        first_seen = start_date.replace(hour=0, minute=0, second=0,
                                        microsecond=0).timestamp()
        resources = self.mongo_client.restapi.resources.find({
            '$and': [
                {'cloud_account_id': {
                    '$in': list(cloud_account_map.keys())}},
                {'resource_type': 'Instance'},
                {'_first_seen_date': {
                    '$gte': self.timestamp_to_day_start(first_seen)}},
                {'first_seen': {'$gte': first_seen}}
            ]
        }, ['cloud_resource_id', 'meta.cpu_count'])
        cloud_res_id_cpu_map = {
            x['cloud_resource_id']: x.get('meta', {}).get('cpu_count')
            for x in resources}
        resource_ids = cloud_res_id_cpu_map.keys()
        _, response = self.rest_client.cloud_resources_discover(
            self.organization_id, 'instance')
        existing_instance_ids = list(set(
            map(lambda x: x['cloud_resource_id'], response.get('data', []))))
        short_living_instance_candidates = list(
            filter(lambda x: x not in existing_instance_ids, resource_ids))
        short_living_instances_map = {}

        for r_ind in range(0, len(short_living_instance_candidates), BULK_SIZE):
            bulk_ids = short_living_instance_candidates[r_ind:r_ind + BULK_SIZE]
            raw_expenses = self.mongo_client.restapi.raw_expenses.find(
                {'$and': [{'cloud_account_id': {
                    '$in': list(cloud_account_map.keys())}},
                    {'resource_id': {'$in': bulk_ids}}]},
                ['_id', 'resource_id', 'cloud_account_id', 'cost', 'start_date',
                 'end_date', 'lineItem/UsageType', 'meter_details.meter_category',
                 'BillingItem', 'usage_quantity', 'Usage', 'Tags',
                 'lineItem/UsageStartDate', 'service_name', 'sku_name',
                 'pricing_quantity'])

            inst_map = {}
            inst_to_remove = set()
            for exp in raw_expenses:
                r_id = exp['resource_id']
                if r_id in inst_to_remove:
                    continue
                if exp.get('lineItem/UsageStartDate'):
                    exp_start_date = datetime.strptime(
                        exp['lineItem/UsageStartDate'], '%Y-%m-%dT%H:%M:%SZ')
                else:
                    exp_start_date = exp['start_date']
                if exp_start_date < start_date:
                    inst_to_remove.add(r_id)
                    continue
                if not inst_map.get(r_id):
                    inst_map[r_id] = {
                        'flavor_cost': 0,
                        'other_cost': 0,
                        'work_hrs': 0,
                        'start_date': start_datetime,
                        'end_date': start_date,
                        'cloud_account_id': exp['cloud_account_id']
                    }
                if self._is_flavor_cost(exp):
                    cpu_count = cloud_res_id_cpu_map.get(r_id)
                    inst_map[r_id]['flavor_cost'] += exp['cost']
                    inst_map[r_id]['work_hrs'] += self._get_work_hrs(
                        exp, cpu_count)
                else:
                    inst_map[r_id]['other_cost'] += exp['cost']
                if (inst_map[r_id]['start_date'] == start_datetime or
                        inst_map[r_id]['start_date'] > exp_start_date):
                    inst_map[r_id]['start_date'] = exp_start_date
                if inst_map[r_id]['end_date'] < exp['end_date']:
                    inst_map[r_id]['end_date'] = exp['end_date']
            for res_id, values in inst_map.items():
                if res_id in inst_to_remove:
                    continue
                if not values['flavor_cost']:
                    continue
                date_difference = values['end_date'] - values['start_date']
                if not values['work_hrs']:
                    values['work_hrs'] = int(
                        date_difference.total_seconds() / HOUR_IN_SECONDS)
                if values['work_hrs'] >= LIVE_HRS_THRESHOLD:
                    continue
                short_living_instances_map.update({res_id: values})

        result = []
        for sli_id in short_living_instances_map:
            resource_exp = short_living_instances_map.get(sli_id, {})
            flavor_cost = resource_exp.get('flavor_cost', 0)
            other_cost = resource_exp.get('other_cost', 0)
            cloud_account_id = resource_exp.get('cloud_account_id')
            cloud_account = cloud_account_map.get(cloud_account_id, {})
            _, resources = self.rest_client.cloud_resource_list(
                cloud_account_id, cloud_resource_id=sli_id)
            resources = resources.get('resources', [])
            if not resources:
                continue
            resource = resources[0]
            meta = resource.get('meta') or {}
            if meta.get('spotted', False):
                continue
            saving = flavor_cost * SPOT_SAVING_COEFFICIENT
            if saving > 0:
                result.append({
                    'cloud_resource_id': sli_id,
                    'resource_name': resource.get('name'),
                    'resource_id': resource.get('id'),
                    'cloud_account_id': cloud_account_id,
                    'cloud_type': cloud_account.get('type'),
                    'total_cost': flavor_cost + other_cost,
                    'first_seen': int(resource_exp.get('start_date').timestamp()),
                    'last_seen': int(resource_exp.get('end_date').timestamp()),
                    'saving': saving,
                    'region': resource.get('region'),
                    'is_excluded': resource.get('pool_id') in excluded_pools,
                })
        return result


def main(organization_id, config_client, created_at, **kwargs):
    return ShortLivingInstances(
        organization_id, config_client, created_at).get()


def get_module_email_name():
    return 'Instances with Spot (Preemptible) opportunities'
