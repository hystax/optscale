import logging
import re
import json
from collections import OrderedDict, defaultdict
from datetime import datetime, timedelta
from optscale_client.insider_client.client import Client as InsiderClient
from tools.cloud_adapter.clouds.nebius import Nebius, PLATFORMS
from concurrent.futures.thread import ThreadPoolExecutor
from bumiworker.bumiworker.modules.base import ModuleBase

LOG = logging.getLogger(__name__)
DEFAULT_DAYS_THRESHOLD = 30
DAYS_IN_MONTH = 30
DAY_IN_SEC = 86400


class NebiusMigration(ModuleBase):
    def __init__(self, organization_id, config_client, created_at):
        super().__init__(organization_id, config_client, created_at)
        self.option_ordered_map = OrderedDict({
            'days_threshold': {'default': DEFAULT_DAYS_THRESHOLD},
            'skip_cloud_accounts': {'default': []}
        })
        self._insider_cl = None
        self._nebius = None

    @property
    def unique_record_keys(self):
        return 'cloud_account_id', 'region', 'flavor',

    @property
    def insider_cl(self):
        if self._insider_cl is None:
            self._insider_cl = InsiderClient(
                url=self.config_cl.insider_url(),
                secret=self.config_cl.cluster_secret())
        return self._insider_cl

    @property
    def nebius(self):
        if self._nebius is None:
            config = self.config_cl.read_branch('/service_credentials/nebius')
            self._nebius = Nebius(config)
        return self._nebius

    def _get_gcp_usages(self, cloud_account_id, dt, resources):
        cloud_resource_ids, cloud_resource_hashes = [], []
        for r in resources:
            if 'cloud_resource_hash' in r:
                cloud_resource_hashes.append(r['cloud_resource_hash'])
            if 'cloud_resource_id' in r:
                cloud_resource_ids.append(r['cloud_resource_id'])
        expenses = self.mongo_client.restapi.raw_expenses.aggregate([
            {'$match': {
                'cloud_account_id': cloud_account_id,
                'sku': {'$regex': 'Core running'},
                'start_date': {'$gte': dt},
                '$or': [
                    {'resource_id': {'$in': cloud_resource_ids}},
                    {'resource_hash': {'$in': cloud_resource_hashes}},
                ]
            }},
            {'$group': {
                '_id': {'system_tags': '$system_tags', 'region': '$region'},
                'usage': {'$sum': '$usage_amount_in_pricing_units'},
            }}
        ])
        result = []
        for e in expenses:
            system_tags = e['_id']['system_tags']
            cores = int(system_tags['compute.googleapis.com/cores'])
            result.append({
                'usage': e['usage'] / cores,
                'flavor': system_tags['compute.googleapis.com/machine_spec'],
                'region': e['_id']['region'],
            })
        return result

    def _get_aws_usages(self, cloud_account_id, dt, resources):
        cloud_resource_ids = list(map(lambda x: x['cloud_resource_id'], resources))
        expenses = self.mongo_client.restapi.raw_expenses.aggregate([
            {'$match': {
                'cloud_account_id': cloud_account_id,
                'start_date': {'$gte': dt},
                'box_usage': True,
                'resource_id': {'$in': cloud_resource_ids},
            }},
            {'$group': {
                '_id': {
                    'region': '$product/regionCode',
                    'flavor': '$product/instanceType',
                },
                'usages': {'$push': '$lineItem/UsageAmount'},
            }}
        ])
        result = []
        for e in expenses:
            _id = e['_id']
            if not _id:
                continue
            result.append({
                'usage': sum([float(x) for x in e['usages']]),
                'flavor': _id['flavor'],
                'region': _id['region'],
            })
        return result

    def _get_azure_usages(self, cloud_account_id, dt, resources):
        resource_map = {}
        for r in resources:
            resource_map[r['cloud_resource_id']] = {
                'flavor': r.get('meta', {}).get('flavor'),
                'region': r.get('region')
            }

        expenses = self.mongo_client.restapi.raw_expenses.aggregate([
            {'$match': {
                'cloud_account_id': cloud_account_id,
                'start_date': {'$gte': dt},
                'box_usage': True,
                'resource_id': {'$in': list(resource_map.keys())},
            }},
            {'$group': {
                '_id': '$resource_id',
                'usage': {'$sum': '$usage_quantity'},
            }}
        ])
        result = {}
        for e in expenses:
            cloud_resource_id = e['_id']
            flavor = resource_map.get(cloud_resource_id, {})
            flavor_name = flavor['flavor']
            if flavor_name not in result:
                result[flavor_name] = {
                    'usage': 0,
                    'flavor': flavor_name,
                    'region': flavor.get('region')
                }
            result[flavor_name]['usage'] += e['usage']
        return list(result.values())

    def _get_alibaba_usages(self, cloud_account_id, dt, resources):
        resource_ids = list(map(lambda x: x['cloud_resource_id'], resources))
        expenses = self.mongo_client.restapi.raw_expenses.aggregate([
            {'$match': {
                'cloud_account_id': cloud_account_id,
                'start_date': {'$gte': dt},
                'box_usage': True,
                'resource_id': {'$in': resource_ids},
            }},
            {'$group': {
                '_id': {
                    'region': '$Region',
                    'flavor': '$InstanceSpec',
                },
                'usages': {'$push': '$Usage'},
            }}
        ])
        result = []
        for e in expenses:
            _id = e['_id']
            result.append({
                'usage': sum([float(x) for x in e['usages']]),
                'flavor': _id['flavor'],
                'region': _id['region'],
            })
        return result

    def _get_nebius_pricing(self):
        def _get_sku_price_by_pattern(sku_pattern):
            sku_regex = re.compile(sku_pattern)
            res = [sku for sku in skus if re.search(sku_regex, sku['name'])]
            if not res:
                return 0, None
            price_rate = res[0]['pricingVersions'][-1][
                'pricingExpressions'][0]['rates'][0]
            return float(price_rate['unitPrice'])
        skus = self.nebius.get_prices()
        for family, platform in PLATFORMS.items():
            if not platform.get('core_fraction'):
                continue
            name = platform.get('name')
            supported_fractions = [100]
            for fraction in supported_fractions:
                price_per_cpu = _get_sku_price_by_pattern(
                    '^{0}. {1}% vCPU$'.format(name, fraction))
                price_per_ram = _get_sku_price_by_pattern(
                    '^{0}. RAM$'.format(name))
                return name, price_per_cpu, price_per_ram

    def _find_flavor(self, cloud_type, region, flavor):
        _, resp = self.insider_cl.find_flavor(
            cloud_type=cloud_type, resource_type='instance',
            region=region, family_specs={'source_flavor_id': flavor},
            mode='current'
        )
        return resp

    def _is_nebius_option_enabled(self):
        _, response = self.rest_client.organization_option_get(
            self.organization_id, 'features')
        feature_options = json.loads(response['value'])
        return feature_options.get('nebius_connection_enabled', 0)

    def get_cloud_funcs_map(self):
        return {
            'aws_cnr': self._get_aws_usages,
            'azure_cnr': self._get_azure_usages,
            'alibaba_cnr': self._get_alibaba_usages,
            'gcp_cnr': self._get_gcp_usages
        }

    def _get(self):
        if not self._is_nebius_option_enabled():
            return []
        (days_threshold, skip_cloud_accounts) = self.get_options_values()
        cloud_func_map = self.get_cloud_funcs_map()
        cloud_account_map = self.get_cloud_accounts(
            supported_cloud_types=list(cloud_func_map.keys()),
            skip_cloud_accounts=skip_cloud_accounts)
        cloud_account_ids = list(cloud_account_map.keys())
        dt = datetime.utcnow() - timedelta(seconds=days_threshold * DAY_IN_SEC)
        month_multiplier = DAYS_IN_MONTH / days_threshold
        last_seen = int(dt.timestamp())
        instances = self.mongo_client.restapi.resources.find({
            '$and': [
                {'cloud_account_id': {'$in': cloud_account_ids}},
                {'resource_type': {'$in': ['Instance', 'RDS Instance']}},
                {'_last_seen_date': {
                    '$gte': self.timestamp_to_day_start(last_seen)}},
                {'last_seen': {'$gte': last_seen}},
            ]}, ['cloud_account_id', 'cloud_resource_id',
                 'cloud_resource_hash', 'region', 'meta']
        )
        instances_map = defaultdict(list)
        for i in instances:
            instances_map[i['cloud_account_id']].append(i)

        nebius_pr = self._get_nebius_pricing()
        result = []
        for k, v in cloud_account_map.items():
            instances = instances_map[k]
            if not instances:
                continue
            cloud_usages = cloud_func_map[v['type']](k, dt, instances)
            flavor_map = {}
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = []
                for cu in cloud_usages:
                    futures.append(executor.submit(
                        self._find_flavor,
                        v['type'], cu['region'], cu['flavor']
                    ))
                for i, f in enumerate(futures):
                    try:
                        res = f.result()
                        if res:
                            flavor_map.update({res['flavor']: res})
                    except Exception as ex:
                        LOG.warning('Error processing flavor %s: %s' % (
                            cloud_usages[i], str(ex)))
            for cu in cloud_usages:
                flavor = flavor_map.get(cu['flavor'])
                if not flavor:
                    continue
                cpu = flavor['cpu']
                ram = flavor['ram']
                if v['type'] in ['aws_cnr', 'azure_cnr']:
                    ram /= 1024
                usage = cu['usage'] * month_multiplier
                cost = round(usage * flavor['price'], 3)
                nebius_cost = round(
                    usage * (cpu * nebius_pr[1] + ram * nebius_pr[2]), 3)
                saving = round(cost - nebius_cost, 3)
                if saving <= 0:
                    continue
                result.append({
                    'cloud_account_id': k,
                    'cloud_type': v['type'],
                    'cloud_account_name': v['name'],
                    'region': cu['region'],
                    'flavor': cu['flavor'],
                    'cpu': cpu,
                    'ram': ram,
                    'usage': usage,
                    'cost': cost,
                    'saving': saving,
                    'recommended_flavor': {
                        'flavor': nebius_pr[0],
                        'cpu': cpu,
                        'ram': ram,
                        'cost': nebius_cost
                    }
                })
        return result


def main(organization_id, config_client, created_at, **kwargs):
    return NebiusMigration(
        organization_id, config_client, created_at).get()


def get_module_email_name():
    return 'Nebius migration opportunities'
