import logging
from collections import OrderedDict
from datetime import datetime, timedelta

from optscale_client.insider_client.client import Client as InsiderClient

from bumiworker.bumiworker.modules.base import ModuleBase

DEFAULT_DAYS_THRESHOLD = 90
LOG = logging.getLogger(__name__)
HRS_IN_MONTH = 24 * 30


class ReservedInstancesBase(ModuleBase):
    SUPPORTED_CLOUD_TYPES = []

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
        self.currency = self.get_organization_currency()

    @property
    def insider_cl(self):
        if self._insider_cl is None:
            self._insider_cl = InsiderClient(
                url=self.config_cl.insider_url(),
                secret=self.config_cl.cluster_secret(),
                verify=False)
        return self._insider_cl

    @property
    def cloud_type(self):
        raise NotImplementedError

    def get_instances_map(self, cloud_account_ids, range_start_ts):
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
                 'pool_id',  'meta.cpu_count', 'meta.cpu_fraction',
                 'meta.platform_name']))
        return {i['cloud_resource_id']: i for i in instances}

    def get_raw_expenses(self, cloud_account_ids, cloud_resource_ids, now):
        raise NotImplementedError

    def _is_instance_reserved(self, raw_info):
        raise NotImplementedError

    def get_offer_key(self, raw_info, resource):
        raise NotImplementedError

    def _offer_key_to_insider_params(self, offer_key):
        raise NotImplementedError

    def get_flavor_key(self, raw_info, resource):
        raise NotImplementedError

    def _flavor_key_to_insider_params(self, flavor_key):
        raise NotImplementedError

    def get_current_flavor_hourly_price(self, flavor_key):
        raise NotImplementedError

    def get_offers_monthly_costs(self, insider_offerings, resource):
        return NotImplementedError

    def format_result(self, saving1, saving2, raw_info, instance, excluded_pools):
        return NotImplementedError

    def _get(self):
        result = []
        (days_threshold, excluded_pools,
         skip_cloud_accounts) = self.get_options_values()
        cloud_account_map = self.get_cloud_accounts(
            self.SUPPORTED_CLOUD_TYPES, skip_cloud_accounts)
        cloud_account_ids = list(cloud_account_map.keys())
        now = datetime.utcnow()
        range_start_ts = int((now - timedelta(days=days_threshold)).timestamp())
        instance_map = self.get_instances_map(cloud_account_ids, range_start_ts)
        cloud_resource_ids = list(instance_map.keys())
        raw_expenses = self.get_raw_expenses(cloud_account_ids,
                                             cloud_resource_ids, now)
        raw_expenses_map = {}
        insider_flavor_prices, insider_offerings = {}, {}
        offer_keys = set()
        resource_id_keys_map = {}
        for raw_info in raw_expenses:
            resource_id = raw_info['_id']
            if self._is_instance_reserved(raw_info):
                LOG.warning('Instance %s skipped due to discounts',
                            resource_id)
                continue
            raw_expenses_map[resource_id] = raw_info
            instance = instance_map[resource_id]
            offer_key = self.get_offer_key(raw_info, instance)
            offer_keys.add(offer_key)
            flavor_key = self.get_flavor_key(raw_info, instance)
            resource_id_keys_map[resource_id] = (flavor_key, offer_key)

        for offer_key in offer_keys:
            params = self._offer_key_to_insider_params(offer_key)
            _, offerings = self.insider_cl.find_reserved_instances_offerings(
                **params)
            insider_offerings[offer_key] = offerings

        for resource_id in resource_id_keys_map:
            instance = instance_map[resource_id]
            res_flavor_key, res_offer_key = resource_id_keys_map[resource_id]
            raw_info = raw_expenses_map[resource_id]
            res_insider_offers = insider_offerings.get(res_offer_key)
            offer_1_monthly_cost, offer_2_monthly_cost = self.get_offers_monthly_costs(
                res_insider_offers, instance)
            if offer_1_monthly_cost is None or offer_2_monthly_cost is None:
                LOG.warning('Instance %s skipped due to inability to find '
                            'RI offers', resource_id)
                continue
            flavor_price = insider_flavor_prices.get(res_flavor_key)
            if not flavor_price:
                flavor_price = self.get_current_flavor_hourly_price(
                    res_flavor_key)
                insider_flavor_prices[res_flavor_key] = flavor_price
            if float(flavor_price) == 0:
                flavor_price = raw_info['daily_cost'] / 24
            monthly_flavor_price = flavor_price * HRS_IN_MONTH
            saving_1 = monthly_flavor_price - offer_1_monthly_cost
            saving_2 = monthly_flavor_price - offer_2_monthly_cost
            if saving_1 <= 0 or saving_2 <= 0:
                LOG.warning('Instance %s skipped due non-positive savings',
                            resource_id)
                continue
            resource_result = self.format_result(saving_1, saving_2, raw_info,
                                                 instance, excluded_pools)
            result.append(resource_result)
        return result
