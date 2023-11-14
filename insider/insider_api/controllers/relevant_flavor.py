import re
from botocore.exceptions import ClientError as AwsClientError
from grpc._channel import _InactiveRpcError
from pymongo import MongoClient
from tools.optscale_exceptions.common_exc import (
    NotFoundException, UnauthorizedException, WrongArgumentsException)
from tools.cloud_adapter.clouds.azure import Azure
from tools.cloud_adapter.exceptions import AuthorizationException
from tools.cloud_adapter.clouds.aws import Aws
from tools.cloud_adapter.clouds.nebius import Nebius, PLATFORMS
from insider.insider_api.exceptions import Err
from insider.insider_api.controllers.flavor import FlavorController
from insider.insider_api.controllers.base import (BaseAsyncControllerWrapper,
                                                  CachedThreadPoolExecutor)
from insider.insider_api.utils import handle_credentials_error


def extract_substring_between(string, sub_1, sub_2):
    substring = string[(string.index(sub_1) + len(sub_1)):]
    return substring[:substring.index(sub_2)]


class BaseProvider:
    def __init__(self, config_cl):
        self._config_cl = config_cl
        self._mongo_client = None
        self._cloud_adapter = None

    @property
    def mongo_client(self):
        if not self._mongo_client:
            mongo_params = self._config_cl.mongo_params()
            mongo_conn_string = "mongodb://%s:%s@%s:%s" % mongo_params[:-1]
            self._mongo_client = MongoClient(mongo_conn_string)
        return self._mongo_client

    @property
    def cloud_adapter(self):
        raise NotImplementedError()

    def get_relevant_flavors(self, **kwargs):
        raise NotImplementedError()

    def _extract_cpu(self, flavor):
        raise NotImplementedError()

    def _extract_memory(self, flavor):
        raise NotImplementedError()

    @staticmethod
    def _extract_credentials_error_message(exc):
        raise NotImplementedError()

    def _check_flavor(self, flavor, **kwargs):
        cpu = self._extract_cpu(flavor)
        min_cpu = kwargs.get('min_cpu')
        if min_cpu and min_cpu > cpu:
            return False
        max_cpu = kwargs.get('max_cpu')
        if max_cpu and max_cpu < cpu:
            return False
        ram = self._extract_memory(flavor)
        min_ram = kwargs.get('min_ram')
        if min_ram and min_ram > ram:
            return False
        max_ram = kwargs.get('max_ram')
        if max_ram and max_ram < ram:
            return False
        return True


class AzureProvider(BaseProvider):
    region_map = {
        'ap': ['Australia', 'India', 'Asia', 'Japan', 'Korea'],
        'eu': ['France', 'Germany', 'Europe', 'Norway', 'Poland', 'Sweden',
               'Switzerland'],
        'ca': ['Canada'], 'sa': ['Brazil'], 'us': ['US'], 'af': ['Africa'],
        'me': ['Qatar', 'UAE', 'UK']
    }

    @property
    def cloud_adapter(self):
        if self._cloud_adapter is None:
            config = self._config_cl.read_branch('/service_credentials/azure')
            self._cloud_adapter = Azure(config)
        return self._cloud_adapter

    @staticmethod
    def _extract_credentials_error_message(exc):
        s = str(exc)
        try:
            return extract_substring_between(s, ': ', '.')
        except Exception:
            return s

    def _format_flavor(self, obj):
        return {
            'cpu': self._extract_cpu(obj),
            'memory': self._extract_memory(obj),
            'instance_family': obj['productName'],
            'name': obj.get('name'),
            'location': obj['location'],
            'cost': obj.get('unitPrice', 0),
            'currency': obj.get('currencyCode')
        }

    def _extract_cpu(self, flavor):
        return flavor['vcpus']

    def _extract_memory(self, flavor):
        return flavor['ram'] / 1024

    def get_azure_flavors(self):
        return self.cloud_adapter.get_flavors_info()

    @handle_credentials_error(AuthorizationException)
    def get_relevant_flavors(self, **kwargs):
        regions = self.get_regions(kwargs['region'])
        with CachedThreadPoolExecutor(self.mongo_client) as executor:
            flavors_future = executor.submit(self.get_azure_flavors)
        flavors_info = flavors_future.result()
        flavors = {}
        for k, v in flavors_info.items():
            if self._check_flavor(v, **kwargs):
                flavors[k] = v
        discoveries = self.mongo_client.insider.discoveries.find(
            {'cloud_type': 'azure_cnr'}
        ).sort(
            [('completed_at', -1)]).limit(1)
        try:
            last_discovery = next(discoveries)
        except StopIteration:
            raise NotFoundException(Err.OI0009, ['azure_cnr'])
        currency = kwargs.get('preferred_currency')
        currencies = self.get_discovered_currencies(
            last_discovery['started_at'])
        if currency not in currencies:
            currency = 'USD'
        pricing = self.mongo_client.insider.azure_prices.aggregate([
            {
                '$match': {
                    '$and': [
                        {'type': 'Consumption'},
                        {'serviceName': 'Virtual Machines'},
                        {'last_seen': {'$gte': last_discovery['started_at']}},
                        {'armSkuName': {'$in': list(flavors.keys())}},
                        {'armRegionName': {'$in': regions}},
                        {'productName': {'$regex': '.*(?<!Windows)$'}},
                        {'meterName': {'$regex': '.*(?<!Spot)$'}},
                        {'meterName': {'$regex': '.*(?<!Low Priority)$'}},
                        {'currencyCode': currency}
                    ]
                }
            }
        ])
        result = []
        for p in pricing:
            p.update(flavors.get(p['armSkuName'], {}))
            result.append(self._format_flavor(p))
        return result

    def get_discovered_currencies(self, last_seen):
        return self.mongo_client.insider.azure_prices.distinct(
            'currencyCode', {'last_seen': {'$gte': last_seen}})

    def get_regions(self, global_region):
        locations = self.region_map.get(global_region, [])
        regions = []
        for k, v in self.cloud_adapter.location_map.items():
            if any(filter(lambda x: x in v, locations)):
                regions.append(k)
        return regions


class AwsProvider(BaseProvider):
    @property
    def cloud_adapter(self):
        if self._cloud_adapter is None:
            config = self._config_cl.read_branch('/service_credentials/aws')
            self._cloud_adapter = Aws(config)
        return self._cloud_adapter

    def _extract_cpu(self, flavor):
        return int(flavor['vcpu'])

    def _extract_memory(self, flavor):
        return float(flavor['memory'].split(' GiB')[0])

    @staticmethod
    def _extract_credentials_error_message(exc):
        try:
            message = exc.response['Error']['Message']
        except Exception:
            message = str(exc)
        return message

    def _format_flavor(self, obj, **kwargs):
        price_obj = obj['price']
        currency = kwargs.get('preferred_currency')
        price = price_obj.get(currency, 0)
        for k, v in price_obj.items():
            currency = k
            price = v
        return {
            'cpu': self._extract_cpu(obj),
            'memory': self._extract_memory(obj),
            'instance_family': obj['instanceFamily'],
            'name': obj['instanceType'],
            'location': obj['location'],
            'cost': price,
            'currency': currency
        }

    def get_aws_prices(self, body):
        return self.cloud_adapter.get_prices(body)

    @handle_credentials_error(AwsClientError)
    def get_relevant_flavors(self, **kwargs):
        regions = self.get_regions(kwargs['region'])
        result = []
        with CachedThreadPoolExecutor(self.mongo_client) as executor:
            futures = []
            for region in regions:
                body = {
                    'preInstalledSw': 'NA',
                    'tenancy': 'Shared',
                    'capacitystatus': 'Used',
                    'regionCode': region,
                    'operatingSystem': 'Linux',
                }
                futures.append(executor.submit(self.get_aws_prices, body))
            for f in futures:
                res = f.result()
                if not res:
                    continue
                for r in res:
                    if self._check_flavor(r, **kwargs):
                        result.append(self._format_flavor(r, **kwargs))
        return result

    def get_regions(self, global_region):
        regions = self.cloud_adapter.list_regions()
        return list(filter(lambda x: x.split('-')[0] == global_region, regions))


class NebiusProvider(BaseProvider):
    region_map = {'me': 'Israel'}

    @property
    def cloud_adapter(self):
        if self._cloud_adapter is None:
            config = self._config_cl.read_branch('/service_credentials/nebius')
            self._cloud_adapter = Nebius(config)
        return self._cloud_adapter

    @staticmethod
    def _extract_credentials_error_message(exc):
        try:
            s = exc.args[0].details
            return extract_substring_between(s, 'details = "', '"')
        except Exception:
            return str(exc)

    def _extract_cpu(self, flavor):
        return flavor['cpu']

    def _extract_memory(self, flavor):
        return flavor['memory']

    @handle_credentials_error(_InactiveRpcError)
    def get_relevant_flavors(self, **kwargs):
        def _get_sku_price_by_pattern(sku_pattern):
            sku_regex = re.compile(sku_pattern)
            res = [sku for sku in skus if re.search(sku_regex, sku['name'])]
            if not res:
                return 0, None
            price_rate = res[0]['pricingVersions'][-1][
                'pricingExpressions'][0]['rates'][0]
            return float(price_rate['unitPrice']), price_rate['currency']

        region = self.region_map.get(kwargs['region'])
        if not region:
            return []
        currency = kwargs.get('preferred_currency')
        try:
            skus = self.cloud_adapter.get_prices(currency=currency)
        except _InactiveRpcError:
            skus = self.cloud_adapter.get_prices(currency='USD')
        result = []
        for family, platform in PLATFORMS.items():
            if not platform.get('core_fraction'):
                continue
            supported_fractions = [100]
            for fraction in supported_fractions:
                price_per_cpu, currency = _get_sku_price_by_pattern(
                    '^{0}. {1}% vCPU$'.format(platform.get('name'), fraction))
                price_per_ram, _ = _get_sku_price_by_pattern(
                    '^{0}. RAM$'.format(platform.get('name')))
                core_fraction = platform['core_fraction'][fraction]
                base_flavor_info = {
                    'name': platform.get('name'),
                    'instance_family': family,
                    'location': region
                }
                for cf in core_fraction:
                    cpus = cf['cpu']
                    ram_per_core = cf['ram_per_core']
                    for cpu in cpus:
                        for r in ram_per_core:
                            ram = cpu * r
                            flavor = {'cpu': cpu, 'memory': ram}
                            if not self._check_flavor(flavor, **kwargs):
                                continue
                            flavor.update({
                                'cost': round(
                                    cpu * price_per_cpu + ram * price_per_ram,
                                    4),
                                'currency': currency,
                                **base_flavor_info
                            })
                            result.append(flavor)
        return result


class RelevantFlavorProvider:
    __modules__ = {
        'azure_cnr': AzureProvider,
        'aws_cnr': AwsProvider,
        'nebius': NebiusProvider
    }

    @staticmethod
    def get_provider(cloud_type):
        provider = RelevantFlavorProvider.__modules__.get(cloud_type)
        if not provider:
            raise WrongArgumentsException(Err.OI0010, [cloud_type])
        return provider


class RelevantFlavorController(FlavorController):
    def get(self, cloud_type, **kwargs):
        provider = RelevantFlavorProvider.get_provider(cloud_type)
        return provider(self._config).get_relevant_flavors(**kwargs)


class RelevantFlavorAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return RelevantFlavorController
