import logging
import re
from datetime import datetime, timedelta
from pymongo import MongoClient, UpdateOne

from insider.insider_api.controllers.base import (
    BaseController, BaseAsyncControllerWrapper)
from insider.insider_api.exceptions import Err

from tools.cloud_adapter.clouds.alibaba import Alibaba
from tools.cloud_adapter.clouds.aws import Aws
from tools.cloud_adapter.clouds.azure import Azure
from tools.optscale_exceptions.common_exc import WrongArgumentsException


LOG = logging.getLogger(__name__)


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
    def prices_collection(self):
        raise NotImplementedError()

    @property
    def cloud_adapter(self):
        raise NotImplementedError()

    def _load_flavor_prices(self, region, flavor, os_type, preinstalled,
                            quantity, billing_method, currency='USD'):
        raise NotImplementedError()

    def _load_family_prices(self, instance_family, region, os_type, currency):
        raise NotImplementedError()

    def _flavor_format(self, price_infos, region, os_type):
        raise NotImplementedError()

    def _flavor_family_format(self, price_infos, instance_family, region,
                              os_type):
        raise NotImplementedError()

    def get_flavor_prices(self, region, flavor, os_type, preinstalled=None,
                          billing_method=None, quantity=None, currency='USD'):
        price_infos = self._load_flavor_prices(region, flavor, os_type,
                                               preinstalled, billing_method,
                                               quantity, currency)
        return self._flavor_format(price_infos, region, os_type)

    def get_family_prices(self, instance_family, region, os_type, currency):
        price_infos = self._load_family_prices(
            instance_family, region, os_type, currency)
        return self._flavor_family_format(
            price_infos, instance_family, region, os_type)


class AwsProvider(BaseProvider):
    def __init__(self, config_cl):
        super().__init__(config_cl)
        self.os_map = {
            'rhel': 'RHEL',
            'windows': 'Windows',
            'suse': 'SUSE',
            'linux': 'Linux'
        }
        self.preinstalled_map = {
            'sql std': 'SQL Std',
            'sql web': 'SQL Web',
            'sql ent': 'SQL Ent'
        }
        self.region_map = {
            'ap-northeast-2': 'Asia Pacific (Seoul)',
            'eu-north-1': 'EU (Stockholm)',
            'eu-central-1': 'EU (Frankfurt)',
            'us-east-1': 'US East (N. Virginia)',
            'eu-west-1': 'EU (Ireland)',
            'me-south-1': 'Middle East (Bahrain)',
            'us-west-1': 'US West (N. California)',
            'ap-northeast-3': 'Asia Pacific (Osaka-Local)',
            'ca-central-1': 'Canada (Central)',
            'us-west-2': 'US West (Oregon)',
            'ap-southeast-2': 'Asia Pacific (Sydney)',
            'us-east-2': 'US East (Ohio)',
            'ap-northeast-1': 'Asia Pacific (Tokyo)',
            'eu-west-3': 'EU (Paris)',
            'ap-southeast-1': 'Asia Pacific (Singapore)',
            'eu-west-2': 'EU (London)',
            'af-south-1': 'Africa (Cape Town)',
            'ap-east-1': 'Asia Pacific (Hong Kong)',
            'eu-south-1': 'EU (Milan)',
            'ap-south-1': 'Asia Pacific (Mumbai)',
            'sa-east-1': 'South America (Sao Paulo)'
        }

    @property
    def cloud_adapter(self):
        if self._cloud_adapter is None:
            config = self._config_cl.read_branch('/service_credentials/aws')
            self._cloud_adapter = Aws(config)
        return self._cloud_adapter

    @property
    def prices_collection(self):
        return self.mongo_client.restapi.aws_prices

    def _load_flavor_prices(self, region, flavor, os_type, preinstalled=None,
                            billing_method=None, quantity=None, currency='USD'):
        location = self.region_map.get(region)
        if not location:
            raise WrongArgumentsException(Err.OI0012, [region])
        operating_system = self.os_map.get(os_type.lower())
        if not operating_system:
            raise WrongArgumentsException(Err.OI0015, [os_type])
        software = self.preinstalled_map.get(
            preinstalled.lower(), 'NA') if preinstalled else 'NA'

        now = datetime.utcnow()
        query = {
            'instanceType': flavor,
            'location': location,
            'operatingSystem': operating_system,
            'tenancy': 'Shared',
            'preInstalledSw': software,
            'capacitystatus': 'Used',
            'licenseModel': 'No License required',
            'updated_at': {'$gte': now - timedelta(days=60)}
        }
        price_infos = list(self.prices_collection.find(query))
        if not price_infos:
            query.pop('updated_at', None)
            price_infos = self.cloud_adapter.get_prices(query)
            updates = []
            for price_info in price_infos:
                price_info['updated_at'] = now
                updates.append(UpdateOne(
                    filter={'sku': price_info['sku']},
                    update={'$set': price_info},
                    upsert=True,
                ))
            if updates:
                self.prices_collection.bulk_write(updates)
        return price_infos

    def _load_family_prices(self, instance_family, region, os_type, currency):
        location = self.region_map.get(region)
        if not location:
            raise WrongArgumentsException(Err.OI0012, [region])
        operating_system = self.os_map.get(os_type.lower())
        if not operating_system:
            raise WrongArgumentsException(Err.OI0015, [os_type])

        # TODO: Add currency support
        now = datetime.utcnow()
        regex = re.compile(f"{instance_family}\.", re.IGNORECASE)
        query = {
            'instanceType': regex,
            'location': location,
            'operatingSystem': operating_system,
            'tenancy': 'Shared',
            'preInstalledSw': 'NA',
            'capacitystatus': 'Used',
            'licenseModel': 'No License required',
            'updated_at': {'$gte': now - timedelta(days=60)}
        }
        price_infos = list(self.prices_collection.find(query))
        if not price_infos:
            query.pop('updated_at', None)
            query.pop('instanceType', None)
            res = self.cloud_adapter.get_prices(query)
            updates = []
            for price_info in res:
                price_info['updated_at'] = now
                if regex.match(price_info.get('instanceType')):
                    price_infos.append(price_info)
                updates.append(UpdateOne(
                    filter={'sku': price_info['sku']},
                    update={'$set': price_info},
                    upsert=True,
                ))
            if updates:
                self.prices_collection.bulk_write(updates)
        return price_infos

    def _validate_price_info(self, price_info):
        if price_info['price_unit'].lower() not in {'hours', 'hrs'}:
            LOG.warning('Unusual price unit found. Price - %s', price_info)
            return False
        return True

    def _flavor_format(self, price_infos, region, os_type):
        res = []
        price_unit = '1 hour'
        for price_info in price_infos:
            if not self._validate_price_info(price_info):
                continue
            currency, price = next(iter(price_info['price'].items()))
            res.append({
                'price': float(price),
                'region': region,
                'flavor': price_info['instanceType'],
                'operating_system': os_type.lower(),
                'price_unit': price_unit,
                'currency': currency
            })
        return res

    def _flavor_family_format(self, price_infos, instance_family, region,
                              os_type):
        res = []
        price_unit = '1 hour'
        for price_info in price_infos:
            if not self._validate_price_info(price_info):
                continue
            currency, price = next(iter(price_info['price'].items()))
            cpu = price_info.get('vcpu')
            if cpu is not None:
                cpu = int(cpu)
            ram = price_info.get('memory')
            if ram is not None:
                ram = int(float(ram.split(' ')[0]) * 1024)
            gpu = price_info.get('gpu')
            if gpu is not None:
                gpu = int(gpu)
            res.append({
                'price': float(price),
                'region': region,
                'instance_family': instance_family,
                'instance_type': price_info['instanceType'],
                'operating_system': os_type.lower(),
                'price_unit': price_unit,
                'currency': currency,
                'cpu': cpu,
                'ram': ram,
                'gpu': gpu
            })
        return res


class AzureProvider(BaseProvider):
    @property
    def prices_collection(self):
        return self.mongo_client.insider.azure_prices

    @property
    def cloud_adapter(self):
        if self._cloud_adapter is None:
            config = self._config_cl.read_branch('/service_credentials/azure')
            self._cloud_adapter = Azure(config)
        return self._cloud_adapter

    @property
    def discoveries_collection(self):
        return self.mongo_client.insider.discoveries

    def _load_flavor_prices(self, region, flavor, os_type, preinstalled=None,
                            billing_method=None, quantity=None, currency='USD'):
        regions = set(self.cloud_adapter.get_regions_coordinates())
        if region not in regions:
            raise WrongArgumentsException(Err.OI0012, [region])
        operating_system = os_type.lower()
        if operating_system not in {'windows', 'linux'}:
            raise WrongArgumentsException(Err.OI0015, [os_type])

        now = datetime.utcnow()
        product_name_regex = "Windows$" if operating_system == 'windows' else ".*(?<!Windows)$"
        query = {
            'type': 'Consumption',
            'serviceName': 'Virtual Machines',
            'armSkuName': re.compile(flavor, re.IGNORECASE),
            'armRegionName': region,
            '$or': [
                {'effectiveEndDate': {'$gte': now}},
                {'effectiveEndDate': {'$exists': False}}
            ],
            'productName': {'$regex': product_name_regex},
            'skuName': {'$regex': ".*[^Spot][^Priority]$"},
            'currencyCode': currency
        }
        return list(self.prices_collection.find(query).sort(
            [('last_seen', -1)]).limit(1))

    def _flavor_format(self, price_infos, region, os_type):
        res = []
        for price_info in price_infos:
            res.append({
                'price': price_info['unitPrice'],
                'region': price_info['armRegionName'],
                'flavor': price_info['armSkuName'],
                'operating_system': os_type.lower(),
                'price_unit': price_info['unitOfMeasure'].lower(),
                'currency': price_info['currencyCode']
            })
        return res


class AlibabaProvider(BaseProvider):
    @property
    def prices_collection(self):
        return self.mongo_client.insider.alibaba_prices

    @property
    def cloud_adapter(self):
        config = self._config_cl.read_branch('/service_credentials/alibaba')
        self._cloud_adapter = Alibaba(config)
        return self._cloud_adapter

    def _load_flavor_prices(self, region, flavor, os_type='linux',
                            preinstalled=None, billing_method='pay_as_you_go',
                            quantity=1, currency='USD'):
        now = datetime.utcnow()
        query = {
            'region': region,
            'flavor': flavor,
            'quantity': quantity,
            'billing_method': billing_method,
            'updated_at': {'$gte': now - timedelta(days=60)}
        }
        price_infos = list(self.prices_collection.find(query))
        if not price_infos:
            prices = self.cloud_adapter.get_flavor_prices(
                [flavor], region, os_type=os_type,
                billing_method=billing_method, quantity=quantity,
                price_only=False)
            updates = []
            for flavor, price_info in prices.items():
                price_info['updated_at'] = now
                price_info['flavor'] = flavor
                price_info['region'] = region
                price_info['quantity'] = quantity
                updates.append(UpdateOne(
                    filter={'flavor': flavor, 'region': region,
                            'quantity': quantity,
                            'billing_method': price_info['billing_method']},
                    update={'$set': price_info},
                    upsert=True,
                ))
                price_infos.append(price_info)
            if updates:
                self.prices_collection.bulk_write(updates)
        return price_infos

    def _flavor_format(self, price_infos, region, os_type):
        result = []
        currency = 'USD'
        price_unit = '1 hour'
        for price_info in price_infos:
            result.append({
                'price': float(price_info['CostAfterDiscount']),
                'region': region,
                'flavor': price_info['flavor'],
                'operating_system': os_type,
                'price_unit': price_unit,
                'currency': currency
            })
        return result


class PricesProvider:
    __modules__ = {
        'azure': AzureProvider,
        'aws': AwsProvider,
        'alibaba': AlibabaProvider
    }

    @staticmethod
    def get_provider(cloud_type):
        provider = PricesProvider.__modules__.get(cloud_type)
        if not provider:
            raise WrongArgumentsException(Err.OI0010, [cloud_type])
        return provider


class FlavorPriceController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def supported_cloud_types(self):
        return ['alibaba', 'azure', 'aws']

    @property
    def required_params(self):
        return [('cloud_type', str), ('region', str), ('flavor', str),
                ('os_type', str)]

    def validate_parameters(self, **params):
        missing_required = [
            p for p, _ in self.required_params if params.get(p) is None
        ]
        if missing_required:
            message = ', '.join(missing_required)
            raise WrongArgumentsException(Err.OI0011, [message])

        for param, param_type in self.required_params:
            value = params.get(param)
            if value is not None and not isinstance(value, param_type):
                raise WrongArgumentsException(Err.OI0008, [param])
        cloud_type = params.get('cloud_type')
        if cloud_type not in self.supported_cloud_types:
            raise WrongArgumentsException(Err.OI0010, [cloud_type])

    def get(self, **kwargs):
        self.validate_parameters(**kwargs)
        cloud_type = kwargs['cloud_type']
        region = kwargs['region']
        os_type = kwargs['os_type']
        flavor = kwargs['flavor']
        preinstalled = kwargs.get('preinstalled')
        quantity = kwargs.get('quantity')
        billing_method = kwargs.get('billing_method')
        currency = kwargs.get('currency')
        provider = PricesProvider.get_provider(cloud_type)
        return provider(self._config).get_flavor_prices(
            region, flavor, os_type, preinstalled, billing_method, quantity,
            currency)


class FlavorPriceAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return FlavorPriceController


class FamilyPriceController(FlavorPriceController):
    @property
    def supported_cloud_types(self):
        return ['aws']

    @property
    def required_params(self):
        return [('cloud_type', str), ('region', str), ('instance_family', str)]

    def get(self, **kwargs):
        self.validate_parameters(**kwargs)
        cloud_type = kwargs['cloud_type']
        instance_family = kwargs['instance_family']
        region = kwargs['region']
        os_type = kwargs.get('os_type') or 'Linux'
        currency = kwargs.get('currency') or 'USD'
        provider = PricesProvider.get_provider(cloud_type)
        return provider(self._config).get_family_prices(
            instance_family=instance_family, region=region, os_type=os_type,
            currency=currency
        )


class FamilyPriceAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return FamilyPriceController
