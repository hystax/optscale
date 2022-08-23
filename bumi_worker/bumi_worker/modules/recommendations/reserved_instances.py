import logging
from collections import OrderedDict
from datetime import datetime, timedelta

from cloud_adapter.cloud import Cloud
from insider_client.client import Client as InsiderClient

from bumi_worker.modules.base import ModuleBase

DEFAULT_DAYS_THRESHOLD = 90
SUPPORTED_CLOUD_TYPES = [
    'aws_cnr'
]
LOG = logging.getLogger(__name__)
BULK_SIZE = 500


class ReservedInstances(ModuleBase):
    def __init__(self, organization_id, config_client, created_at):
        super().__init__(organization_id, config_client, created_at)
        self.option_ordered_map = OrderedDict({
            'days_threshold': {'default': DEFAULT_DAYS_THRESHOLD},
            'excluded_pools': {
                'default': {},
                'clean_func': self.clean_excluded_pools,
            },
            'skip_cloud_accounts': {'default': []}
        })
        self._insider_cl = None

    @property
    def aws(self):
        config = self.config_cl.read_branch('/service_credentials/aws')
        config['type'] = SUPPORTED_CLOUD_TYPES[0]
        return Cloud.get_adapter(config)

    @property
    def insider_cl(self):
        if self._insider_cl is None:
            self._insider_cl = InsiderClient(
                url=self.config_cl.insider_url(),
                secret=self.config_cl.cluster_secret(),
                verify=False)
        return self._insider_cl

    def _get(self):
        (days_threshold, excluded_pools,
         skip_cloud_accounts) = self.get_options_values()
        cloud_account_map = self.get_cloud_accounts(
            SUPPORTED_CLOUD_TYPES, skip_cloud_accounts)
        cloud_account_ids = list(cloud_account_map.keys())
        now = datetime.utcnow()
        range_start_ts = int((now - timedelta(days=days_threshold)).timestamp())

        instances = list(self.mongo_client.restapi.resources.find({
            '$and': [
                {'resource_type': 'Instance'},
                {'active': True},
                {'cloud_account_id': {'$in': cloud_account_ids}},
                {'$or': [
                    {'first_seen': {'$lte': range_start_ts}},
                    {'cloud_created_at': {'$lte': range_start_ts}},
                ]}
            ]}, ['cloud_resource_id', 'region', 'cloud_account_id', 'name',
                 'pool_id']))
        instance_map = {i['cloud_resource_id']: i for i in instances}
        cloud_resource_ids = list(instance_map.keys())
        raw_expenses = []
        for i in range(0, len(cloud_resource_ids), BULK_SIZE):
            bulk_ids = cloud_resource_ids[i:i + BULK_SIZE]
            resp = self.mongo_client.restapi.raw_expenses.aggregate([
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
                    'line_types': {'$addToSet': '$lineItem/LineItemType'},
                    'software': {'$last': '$product/preInstalledSw'},
                    'os': {'$last': '$product/operatingSystem'},
                    'tenancy': {'$last': '$product/tenancy'},
                    'flavor': {'$last': '$product/instanceType'},
                    'daily_cost': {'$max': '$cost'},
                }},
            ])
            raw_expenses.extend(list(resp))
        results = []
        insider_offerings, insider_flavor_prices = {}, {}
        for raw_info in raw_expenses:
            line_types = raw_info['line_types']
            if 'DiscountedUsage' in line_types or 'SavingsPlanCoveredUsage' in line_types:
                LOG.info('Instance %s skipped due to discounts', raw_info['_id'])
                continue
            try:
                pd = self.get_product_description(raw_info)
            except KeyError as ex:
                LOG.warning('Instance %s skipped due to inability to find '
                            'product description - %s',
                            raw_info['_id'], str(ex))
                continue
            tenancy = 'dedicated' if raw_info['tenancy'] == 'dedicated' else 'default'
            offer_key = ('aws_cnr', pd, tenancy, raw_info['flavor'],
                         365*24*3600, 365*24*3600, False)
            if offer_key not in insider_offerings:
                _, offerings = self.insider_cl.find_reserved_instances_offerings(
                    *offer_key)
                insider_offerings[offer_key] = offerings
            s_all_up_cost = None
            c_no_up_cost = None
            for offer in insider_offerings[offer_key]:
                if offer['scope'] != 'Region':
                    continue
                if (offer['offering_class'] == 'standard' and
                        offer['offering_type'] == 'All Upfront'):
                    s_all_up_cost = offer['fixed_price'] / 12
                elif (offer['offering_class'] == 'convertible' and
                      offer['offering_type'] == 'No Upfront'):
                    c_no_up_cost = (
                            offer['recurring_charges'][0]['Amount'] * 24 * 30)
            if s_all_up_cost is None or c_no_up_cost is None:
                LOG.warning('Instance %s skipped due to inability to find '
                            'RI offers', raw_info['_id'])
                continue

            instance = instance_map.get(raw_info['_id'])
            flavor_key = ('aws', raw_info['flavor'], instance['region'],
                          raw_info['os'], raw_info['software'])
            if flavor_key not in insider_flavor_prices:
                _, resp = self.insider_cl.get_flavor_prices(*flavor_key)
                insider_flavor_prices[flavor_key] = resp
            prices = insider_flavor_prices[flavor_key].get('prices', [])
            # only the hourly price is supported now for AWS
            if prices and prices[0]['price_unit'] == '1 hour':
                monthly_cost = prices[0]['price'] * 24 * 30
            else:
                monthly_cost = raw_info['daily_cost'] * 30
            saving = monthly_cost - c_no_up_cost
            avg_saving = monthly_cost - s_all_up_cost
            if saving <= 0 or avg_saving <= 0:
                LOG.warning('Instance %s skipped due non-positive savings',
                            raw_info['_id'])
                continue

            ca = cloud_account_map[instance['cloud_account_id']]
            results.append({
                'saving': saving,
                'average_saving': avg_saving,
                'flavor': raw_info['flavor'],
                'region': instance['region'],
                'cloud_resource_id': instance['cloud_resource_id'],
                'resource_name': instance.get('name'),
                'resource_id': instance['_id'],
                'cloud_account_id': instance['cloud_account_id'],
                "cloud_type": ca['type'],
                'is_excluded': instance.get('pool_id') in excluded_pools,
            })
        return results

    def get_product_description(self, raw_info):
        linux_pd_map = {
            'Linux': 'Linux/UNIX',
            'RHEL': 'Red Hat Enterprise Linux',
            'SUSE': 'SUSE Linux',
        }
        windows_pd_map = {
            'NA': 'Windows',
            'SQL Std': 'Windows with SQL Server Standard',
            'SQL Web': 'Windows with SQL Server Web',
            'SQL Ent': 'Windows with SQL Server Enterprise',
        }
        if raw_info['os'] == 'Windows':
            result = windows_pd_map.get(raw_info['software'])
        else:
            result = linux_pd_map.get(raw_info['os'])
        if result is None:
            raise KeyError(
                'Operating system {} with software {} not found'.format(
                    raw_info['os'], raw_info['software']))
        return result


def main(organization_id, config_client, created_at, **kwargs):
    return ReservedInstances(
        organization_id, config_client, created_at).get()


def get_module_email_name():
    return 'Reserved Instances opportunities'
