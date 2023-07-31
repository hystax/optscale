import logging
from datetime import timedelta

from bumi_worker.modules.reserved_instances_base import ReservedInstancesBase

LOG = logging.getLogger(__name__)
BULK_SIZE = 500
SECS_IN_YEAR = 365 * 24 * 60 * 60
HRS_IN_MONTH = 24 * 30


class ReservedInstances(ReservedInstancesBase):
    SUPPORTED_CLOUD_TYPES = ['aws_cnr']

    @property
    def cloud_type(self):
        return 'aws_cnr'

    def get_raw_expenses(self, cloud_account_ids, cloud_resource_ids, now):
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
        return raw_expenses

    def _is_instance_reserved(self, raw_info):
        line_types = raw_info['line_types']
        if any(True for x in line_types if x in ['SavingsPlanCoveredUsage',
                                                 'DiscountedUsage']):
            return True

    @staticmethod
    def _get_product_description(raw_info):
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

    def get_offer_key(self, raw_info, resource):
        try:
            pd = self._get_product_description(raw_info)
        except KeyError as ex:
            LOG.warning('Instance %s skipped due to inability to find '
                        'product description - %s',
                        raw_info['_id'], str(ex))
            return None
        tenancy = 'dedicated' if raw_info['tenancy'] == 'dedicated' else 'default'
        return (self.cloud_type, pd, tenancy, raw_info['flavor'],
                SECS_IN_YEAR, SECS_IN_YEAR, False)

    def _offer_key_to_insider_params(self, offer_key):
        (cloud_type, pd, tenancy, flavor,
         min_duration, max_duration, include_marketplace) = offer_key
        return {
            'cloud_type': cloud_type,
            'product_description': pd,
            'tenancy': tenancy,
            'flavor': flavor,
            'min_duration': min_duration,
            'max_duration': max_duration,
            'include_marketplace': include_marketplace
        }

    def get_flavor_key(self, raw_info, resource):
        return ('aws', raw_info['flavor'], resource['region'],
                raw_info['os'], raw_info['software'])

    def _flavor_key_to_insider_params(self, flavor_key):
        (cloud_type, flavor, region, os, preinstalled) = flavor_key
        return {
            'cloud_type': cloud_type,
            'flavor': flavor,
            'region': region,
            'os_type': os,
            'preinstalled': preinstalled
        }

    def get_offers_monthly_costs(self, insider_offerings, resource):
        s_all_up_cost = None
        c_no_up_cost = None
        for offer in insider_offerings:
            if offer['scope'] != 'Region':
                continue
            if (offer['offering_class'] == 'standard' and
                    offer['offering_type'] == 'All Upfront'):
                s_all_up_cost = offer['fixed_price'] / 12
            elif (offer['offering_class'] == 'convertible' and
                  offer['offering_type'] == 'No Upfront'):
                c_no_up_cost = (
                        offer['recurring_charges'][0]['Amount'] * HRS_IN_MONTH)
        return s_all_up_cost, c_no_up_cost

    def get_current_flavor_hourly_price(self, flavor_key):
        price = 0
        params = self._flavor_key_to_insider_params(flavor_key)
        _, resp = self.insider_cl.get_flavor_prices(**params)
        prices = resp.get('prices', [])
        # only the hourly price is supported now for AWS
        if prices and prices[0]['price_unit'] == '1 hour':
            price = prices[0]['price']
        return price

    def format_result(self, saving1, saving2, raw_info, instance, excluded_pools):
        return {
            'saving': saving1,
            'average_saving': saving2,
            'flavor': raw_info['flavor'],
            'region': instance['region'],
            'cloud_resource_id': instance['cloud_resource_id'],
            'resource_name': instance.get('name'),
            'resource_id': instance['_id'],
            'cloud_account_id': instance['cloud_account_id'],
            "cloud_type": self.cloud_type,
            'is_excluded': instance.get('pool_id') in excluded_pools,
        }


def main(organization_id, config_client, created_at, **kwargs):
    return ReservedInstances(
        organization_id, config_client, created_at).get()


def get_module_email_name():
    return 'Reserved Instances opportunities'
