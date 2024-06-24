import logging

from collections import defaultdict, OrderedDict
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime, timedelta
from requests import HTTPError

from optscale_client.insider_client.client import Client as InsiderClient

from bumiworker.bumiworker.modules.base import ModuleBase

LOG = logging.getLogger(__name__)
SUPPORTED_CLOUD_TYPES = [
    'alibaba_cnr'
]
ALIBABA_CLOUD_TYPE = 'alibaba'
DAYS_IN_MONTH = 30
MONTHS_IN_YEAR = 12
DEFAULT_DAYS_THRESHOLD = 90
PAY_AS_YOU_GO_ITEM = 'Cloud server configuration'
SUBSCRIPTION_ITEM = 'instance_type'


class InstanceSubscription(ModuleBase):
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
    def insider_cl(self):
        if self._insider_cl is None:
            self._insider_cl = InsiderClient(
                url=self.config_cl.insider_url(),
                secret=self.config_cl.cluster_secret(),
                verify=False)
        return self._insider_cl

    def get_raw_expenses(self, cloud_account_id, now, cloud_resource_ids):
        return self.mongo_client.restapi.raw_expenses.aggregate([
            {
                '$match': {
                    '$and': [
                        {'resource_id': {'$in': cloud_resource_ids}},
                        {'start_date': {
                            '$gte': now - timedelta(days=DAYS_IN_MONTH)}},
                        {'cloud_account_id': cloud_account_id},
                        {'BillingItem': {
                            '$in': [PAY_AS_YOU_GO_ITEM, SUBSCRIPTION_ITEM]}}
                    ]
                }
            },
            {
                '$group': {
                    '_id': '$resource_id',
                    "cost": {'$sum': '$cost'},
                    'billing_item': {'$addToSet': '$BillingItem'},
                    'daily_cost_without_discount': {
                        '$max': '$PretaxGrossAmount'
                    },
                    'invoice_discount': {'$max': '$InvoiceDiscount'},
                    'coupons_discount': {'$last': '$DeductedByCoupons'},
                    'resource_package_discount': {
                        '$last': '$DeductedByResourcePackage'
                    }
                },
            }
        ])

    def get_subscriptions_costs(self, cloud_resource_id, flavor, region):
        try:
            _, monthly_flavor_prices = self.insider_cl.get_flavor_prices(
                ALIBABA_CLOUD_TYPE, flavor, region, os_type='linux',
                billing_method='subscription', quantity=1)
            _, yearly_flavor_prices = self.insider_cl.get_flavor_prices(
                ALIBABA_CLOUD_TYPE, flavor, region, os_type='linux',
                billing_method='subscription', quantity=MONTHS_IN_YEAR)
            monthly_subscription_cost = monthly_flavor_prices['prices'][0].get(
                'price')
            yearly_subscription_cost = yearly_flavor_prices['prices'][0].get(
                'price')
        except (HTTPError, KeyError) as ex:
            LOG.info('Instance %s skipped due to inability to get '
                     'subscription price - %s', cloud_resource_id, str(ex))
            return None, None
        return monthly_subscription_cost, yearly_subscription_cost

    def handle_account(self, cloud_account, instance_map, now, excluded_pools):
        raw_expenses = self.get_raw_expenses(cloud_account['id'], now,
                                             list(instance_map.keys()))
        result = []
        for raw_info in raw_expenses:
            cloud_resource_id = raw_info['_id']
            if SUBSCRIPTION_ITEM in raw_info['billing_item']:
                LOG.warning('Instance %s skipped due to detected '
                            'subscription costs', raw_info['_id'])
                continue
            if raw_info['coupons_discount'] and float(
                    raw_info['coupons_discount']):
                LOG.info('Instance %s skipped due to coupons discounts',
                         cloud_resource_id)
                continue
            if raw_info['resource_package_discount'] and float(
                    raw_info['resource_package_discount']):
                LOG.info('Instance %s skipped due to package discounts',
                         cloud_resource_id)
                continue
            if raw_info['cost'] == 0:
                LOG.info('Instance %s skipped due to saving plan',
                         cloud_resource_id)
                continue

            instance = instance_map.get(cloud_resource_id)
            flavor = instance['meta']['flavor']
            region = instance['region']
            (monthly_subscription_cost,
             yearly_subscription_cost) = self.get_subscriptions_costs(
                cloud_resource_id, flavor, region)
            if not monthly_subscription_cost or not yearly_subscription_cost:
                continue
            raw_cost = float(raw_info['daily_cost_without_discount'])
            discount = float(raw_info['invoice_discount']) / raw_cost
            discounted_monthly_cost = raw_cost * DAYS_IN_MONTH * (1 - discount)
            saving_per_month = discounted_monthly_cost - monthly_subscription_cost
            yearly_subscription_cost_per_month = (
                    yearly_subscription_cost / MONTHS_IN_YEAR)
            yearly_saving_per_month = (
                    discounted_monthly_cost - yearly_subscription_cost_per_month)
            if saving_per_month <= 0 or yearly_saving_per_month <= 0:
                LOG.warning('Instance %s skipped due non-positive savings',
                            cloud_resource_id)
                continue
            result.append({
                'monthly_saving': saving_per_month,
                'annually_monthly_saving': yearly_saving_per_month,
                'saving': max(saving_per_month, yearly_saving_per_month),
                'invoice_discount': discount,
                'flavor': flavor,
                'region': region,
                'cloud_resource_id': instance['cloud_resource_id'],
                'resource_name': instance.get('name'),
                'resource_id': instance['_id'],
                'cloud_account_id': cloud_account['id'],
                'cloud_type': cloud_account['type'],
                'cloud_account_name': cloud_account['name'],
                'is_excluded': instance.get('pool_id') in excluded_pools,
            })
        return result

    def get_cloud_acc_instances_map(self, cloud_account_ids, range_start_ts):
        instances = list(self.mongo_client.restapi.resources.find({
            '$and': [
                {'resource_type': 'Instance'},
                {'active': True},
                {'cloud_account_id': {'$in': cloud_account_ids}},
                {'spotted': {'$ne': True}},
                {'$or': [
                    {'first_seen': {'$lte': range_start_ts}},
                    {'cloud_created_at': {'$lte': range_start_ts}},
                ]}
            ]}))
        cloud_acc_instance_map = defaultdict(dict)
        for instance in instances:
            cloud_acc_instance_map[
                instance['cloud_account_id']][
                instance['cloud_resource_id']] = instance
        return cloud_acc_instance_map

    def _get(self):
        (days_threshold, excluded_pools,
         skip_cloud_accounts) = self.get_options_values()

        cloud_account_map = self.get_cloud_accounts(
            SUPPORTED_CLOUD_TYPES, skip_cloud_accounts)
        cloud_account_ids = list(cloud_account_map.keys())
        now = datetime.utcnow()
        range_start_ts = int(
            (now - timedelta(days=days_threshold)).timestamp())
        cloud_acc_instance_map = self.get_cloud_acc_instances_map(
            cloud_account_ids, range_start_ts
        )

        result = []
        futures = []
        with ThreadPoolExecutor(max_workers=50) as executor:
            for cloud_acc_id, cloud_acc in cloud_account_map.items():
                instance_map = cloud_acc_instance_map.get(cloud_acc_id, {})
                if not instance_map:
                    continue
                futures.append(
                    executor.submit(self.handle_account, cloud_account=cloud_acc,
                                    instance_map=instance_map, now=now,
                                    excluded_pools=excluded_pools))
            for f in futures:
                res = f.result()
                if res:
                    result.extend(res)
        return result


def main(organization_id, config_client, created_at, **kwargs):
    return InstanceSubscription(
        organization_id, config_client, created_at).get()


def get_module_email_name():
    return 'Instances with Subscription opportunities'
