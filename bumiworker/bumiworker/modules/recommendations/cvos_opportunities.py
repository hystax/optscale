import logging
from datetime import timedelta

from bumiworker.bumiworker.modules.reserved_instances_base import ReservedInstancesBase

LOG = logging.getLogger(__name__)
BULK_SIZE = 500
SECS_IN_YEAR = 365 * 24 * 60 * 60
HRS_IN_MONTH = 24 * 30
CPU_FRACTION = 100


class CVoSOpportunities(ReservedInstancesBase):
    SUPPORTED_CLOUD_TYPES = ['nebius']

    @property
    def cloud_type(self):
        return 'nebius'

    def get_raw_expenses(self, cloud_account_ids, cloud_resource_ids, now):
        raw_expenses = []
        for i in range(0, len(cloud_resource_ids), BULK_SIZE):
            bulk_ids = cloud_resource_ids[i:i + BULK_SIZE]
            resp = self.mongo_client.restapi.raw_expenses.aggregate([
                {'$match': {
                    '$and': [
                        {'resource_id': {'$in': bulk_ids}},
                        {'start_date': {'$gte': now - timedelta(days=7)}},
                        {'cloud_account_id': {'$in': cloud_account_ids}},
                        # reservations are supported for 100% core fraction
                        {'sku_name': {'$regex': '(.*)100% vCPU(.*)'}}
                    ]
                }},
                {'$group': {
                    '_id': '$resource_id',
                    'sku_names': {'$addToSet': '$sku_name'},
                    'daily_cost': {'$max': '$cost'},
                    'cloud_account_id': {'$first': '$cloud_account_id'}
                }},
            ])
            raw_expenses.extend(list(resp))
        return raw_expenses

    def _is_instance_reserved(self, raw_info):
        sku_names = raw_info['sku_names']
        if any(x for x in sku_names if 'committed usage' in x):
            return True

    def get_offer_key(self, raw_info, resource):
        platform_name = resource.get('meta', {}).get('platform_name')
        flavor = f'{platform_name}. 100% vCPU'
        return (flavor, raw_info['cloud_account_id'])

    def _offer_key_to_insider_params(self, offer_key):
        (flavor, cloud_account_id) = offer_key
        return {
            'cloud_type': self.cloud_type,
            'flavor': flavor,
            'min_duration': SECS_IN_YEAR // 2,
            'max_duration': SECS_IN_YEAR,
            'currency': self.currency,
            'cloud_account_id': cloud_account_id
        }

    def get_flavor_key(self, raw_info, resource):
        return ('instance', resource['meta'].get('ram', 0),
                resource['meta']['platform_name'], CPU_FRACTION, 'current',
                resource.get('region'), raw_info['cloud_account_id'],
                resource['meta']['cpu_count'])

    def _flavor_key_to_insider_params(self, flavor_key):
        (resource_type, ram, source_flavor_id, cpu_fraction, mode,
         region, cloud_account_id, cpu_count) = flavor_key
        family_specs = {
            'ram': ram,
            'source_flavor_id': source_flavor_id,
            'cpu_fraction': cpu_fraction
        }
        return {
            'cloud_type': self.cloud_type,
            'resource_type': resource_type,
            'family_specs': family_specs,
            'mode': mode,
            'currency': self.currency,
            'cpu_count': cpu_count,
            'region': region,
            'cloud_account_id': cloud_account_id
        }

    def get_offers_monthly_costs(self, insider_offerings, resource):
        six_months_offer_monthly_cost = None
        one_year_offer_monthly_cost = None
        cpu_count = resource.get('meta', {}).get('cpu_count', 0)
        for offer in insider_offerings:
            offer_type = offer.get('offering_type')
            if not offer_type:
                LOG.warning('Invalid offering: %s. Will skip it!', offer)
                continue
            offer_hourly_price = float(offer['recurring_charges'][0]['Amount']) * cpu_count
            if offer_type == '6 months':
                six_months_offer_monthly_cost = offer_hourly_price * HRS_IN_MONTH
            elif offer_type == '1 year':
                one_year_offer_monthly_cost = offer_hourly_price * HRS_IN_MONTH
            else:
                LOG.warning('Found not standard offering: %s. Will skip it!', offer)
        return six_months_offer_monthly_cost, one_year_offer_monthly_cost

    def get_current_flavor_hourly_price(self, flavor_key):
        params = self._flavor_key_to_insider_params(flavor_key)
        _, flavor = self.insider_cl.find_flavor(**params)
        return flavor.get('price', 0)

    def format_result(self, saving1, saving2, raw_info, instance, excluded_pools):
        platform_name = instance['meta'].get('platform_name')
        platform = f'{platform_name}. 100% vCPU'
        return {
            'saving': saving1,
            'saving_1_year': saving2,
            'flavor': platform,
            'region': instance.get('region') or instance['meta'].get('zone_id'),
            'cloud_resource_id': instance['cloud_resource_id'],
            'resource_name': instance.get('name'),
            'resource_id': instance['_id'],
            'cloud_account_id': instance['cloud_account_id'],
            "cloud_type": self.cloud_type,
            'is_excluded': instance.get('pool_id') in excluded_pools,
        }


def main(organization_id, config_client, created_at, **kwargs):
    return CVoSOpportunities(
        organization_id, config_client, created_at).get()


def get_module_email_name():
    return 'CVoS opportunities'
