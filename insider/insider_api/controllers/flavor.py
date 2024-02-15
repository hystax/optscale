from functools import cached_property
import logging
import re
from datetime import datetime
from insider.insider_api.exceptions import Err
from tools.cloud_adapter.clouds.alibaba import Alibaba
from tools.cloud_adapter.clouds.aws import Aws
from tools.cloud_adapter.clouds.azure import Azure
from tools.cloud_adapter.clouds.nebius import Nebius
from tools.cloud_adapter.clouds.gcp import Gcp
from tools.cloud_adapter.exceptions import (RegionNotFoundException,
                                            ForbiddenException)
from tools.optscale_exceptions.common_exc import (
    WrongArgumentsException, ForbiddenException as OptForbidden)
from insider.insider_api.controllers.base import (BaseController,
                                                  BaseAsyncControllerWrapper,
                                                  CachedThreadPoolExecutor,
                                                  CachedCloudCaller)
from botocore.exceptions import ClientError as AwsClientError
from insider.insider_api.utils import handle_credentials_error

LOG = logging.getLogger(__name__)   # 12 hours by default


class TypeNotMatchedException(Exception):
    pass


class FlavorController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.caller = CachedCloudCaller(self.mongo_client)
        self._aws = None
        self._azure = None
        self._alibaba = None
        self.cloud_account_id = None

    @property
    def aws(self):
        if self._aws is None:
            config = self.get_service_credentials('aws')
            if self.cloud_account_id:
                cloud_acc = self.get_cloud_account(self.cloud_account_id)
                config = cloud_acc['config']
            self._aws = Aws(config)
        return self._aws

    @property
    def azure(self):
        if self._azure is None:
            config = self.get_service_credentials('azure')
            if self.cloud_account_id:
                cloud_acc = self.get_cloud_account(self.cloud_account_id)
                config = cloud_acc['config']
            self._azure = Azure(config)
        return self._azure

    @property
    def alibaba(self):
        if self._alibaba is None:
            config = self.get_service_credentials('alibaba')
            if self.cloud_account_id:
                cloud_acc = self.get_cloud_account(self.cloud_account_id)
                config = cloud_acc['config']
            self._alibaba = Alibaba(config)
        return self._alibaba

    @cached_property
    def gcp(self):
        config = self.get_service_credentials('gcp')
        if self.cloud_account_id:
            cloud_acc = self.get_cloud_account(self.cloud_account_id)
            config = cloud_acc['config']
        return Gcp(config)

    @cached_property
    def nebius(self):
        cloud_acc = self.get_cloud_account(self.cloud_account_id)
        config = cloud_acc.get('config')
        if not config:
            raise ValueError('Cloud account %s is not found' % self.cloud_account_id)
        return Nebius(config)

    def find_flavor(self, cloud_type, resource_type, region,
                    family_specs, mode, cloud_account_id=None, **kwargs):
        if cloud_account_id:
            self.cloud_account_id = cloud_account_id
        find_flavor_function_map = {
            'aws_cnr': {
                'instance': self.find_aws_flavor,
            },
            'azure_cnr': {
                'instance': self.find_azure_flavor,
            },
            'gcp_cnr': {
                'instance': self.find_gcp_flavor,
            },
            'alibaba_cnr': {
                'instance': self.find_alibaba_flavor,
                'rds_instance': self.find_alibaba_rds_flavor
            },
            'nebius': {
                'instance': self.find_nebius_flavor,
                'rds_instance': self.find_nebius_rds_flavor,
            },
        }
        try:
            params = {
                'family_specs': family_specs,
                'region': region,
                'mode': mode,
                'additional_params': kwargs if kwargs else {}
            }
            return find_flavor_function_map[cloud_type][resource_type](**params)
        except TypeNotMatchedException:
            return {}

    def get_azure_prices(self, region, instance_family, currency='USD',
                         meter_id=None):
        discoveries = self.discoveries_collection.find(
            {'cloud_type': 'azure_cnr'}
        ).sort(
            [('completed_at', -1)])
        pricing_query = {
            'armSkuName': {'$regex': instance_family},
            'type': 'Consumption',
            'serviceName': 'Virtual Machines',
            'armRegionName': region,
            'currencyCode': currency
        }
        if meter_id:
            pricing_query['meterId'] = meter_id
        pricings = list()
        next_start = int(datetime.now().timestamp())
        for discovery in discoveries:
            discovery_started_at = discovery['started_at']
            pricing_query['last_seen'] = {'$gte': discovery_started_at,
                                          '$lt': next_start}
            next_start = discovery_started_at
            pricing_count = self.azure_prices_collection.count_documents(
                pricing_query)
            if pricing_count:
                pricings = list(self.azure_prices_collection.find(
                    pricing_query))
                break
        return pricings

    def get_azure_locations(self):
        location_map = self.azure.location_map
        return {v: k for k, v in location_map.items()}

    def get_azure_flavors(self):
        return self.azure.get_flavors_info()

    @staticmethod
    def _set_meter_name(meter_id, prices):
        meter_name = None
        if meter_id:
            # if meter_id exists, get the first meter_name from prices for it
            meter_name = next((
                p.get('meterName') for p in prices
                if p.get('meterId') == meter_id), None)
        return meter_name

    @staticmethod
    def _contains_same_meter_family(meter_name, price_meter_name):
        spot_key = 'Spot'
        low_priority_key = 'Low Priority'
        for key in [spot_key, low_priority_key]:
            if key in meter_name and key in price_meter_name:
                return True
        if (spot_key not in meter_name and spot_key not in
                price_meter_name and low_priority_key not in
                meter_name and low_priority_key not in
                price_meter_name):
            return True
        return False

    def find_azure_flavor(self, region, family_specs, mode,
                          additional_params=None):
        additional_params = additional_params or {}
        vcpu = additional_params.get('cpu', 0)
        os_type = additional_params.get('os_type')
        meter_id = additional_params.get('meter_id')
        currency = additional_params.get('currency') or 'USD'
        windows_key = 'Windows'
        linux_key = 'Linux'
        if not os_type or os_type == 'NA':
            os_type = linux_key
        if os_type not in [linux_key, windows_key]:
            return {}
        source_flavor_id = family_specs['source_flavor_id']
        instance_family = re.sub(r'[0-9]+', '[0-9]+', source_flavor_id, 1)
        with CachedThreadPoolExecutor(self.mongo_client) as executor:
            locations_future = executor.submit(self.get_azure_locations)
            locations = locations_future.result()
            location = locations.get(region)
            if not location:
                raise WrongArgumentsException(Err.OI0012, [region])
            flavors_future = executor.submit(self.get_azure_flavors)
            m_id = meter_id if mode == 'current' else None
            prices_future = executor.submit(
                self.get_azure_prices, location, instance_family, currency, m_id)
        flavors_info = flavors_future.result()
        prices = prices_future.result()

        flavors = []
        relevant_flavor = None
        meter_name = self._set_meter_name(meter_id, prices)
        for p in prices:
            price_meter_id = p.get('meterId')
            price_meter_name = p.get('meterName')
            if meter_id:
                if mode == 'current':
                    if price_meter_id != meter_id:
                        continue
                else:
                    if meter_name and not self._contains_same_meter_family(
                            meter_name, price_meter_name):
                        continue
            flavor = flavors_info.get(p['armSkuName'])
            if not flavor:
                continue
            product_name = p['productName']
            # according to azure pricing api we have 'windows'
            # in productName as os type, and don't have it for others
            if os_type == windows_key:
                if windows_key not in product_name:
                    continue
            else:
                if windows_key in product_name:
                    continue
            flavor_name = flavor['name']
            fl = {
                'cpu': flavor['vcpus'],
                'ram': flavor['ram'],
                'flavor': flavor_name,
                'price': p['unitPrice']
            }
            if mode == 'current':
                if flavor_name == source_flavor_id:
                    flavors.append(fl)
                    break
            else:
                if flavor['vcpus'] < vcpu:
                    continue
                if flavor['vcpus'] == vcpu:
                    flavors.append(fl)
                    continue
                if not relevant_flavor:
                    relevant_flavor = fl
                    continue
                if relevant_flavor['cpu'] > fl['cpu']:
                    relevant_flavor = fl
        if not flavors and mode == 'search_relevant' and relevant_flavor:
            flavors = [relevant_flavor]
        if not flavors:
            raise TypeNotMatchedException()
        return min(flavors, key=lambda x: x['price'])

    @handle_credentials_error(AwsClientError)
    def find_aws_flavor(self, region, family_specs, mode,
                        additional_params=None):
        source_flavor_id = family_specs['source_flavor_id']
        instance_family = source_flavor_id.split('.')[0]
        additional_params = additional_params or {}
        vcpu = additional_params.get('cpu', 0)
        os_type = additional_params.get('os_type')
        if not os_type or os_type == 'NA':
            os_type = 'Linux'
        preinstalled = additional_params.get('preinstalled') or 'NA'
        with CachedThreadPoolExecutor(self.mongo_client) as executor:
            regions_future = executor.submit(
                self.aws.get_region_name_code_map)
            names_to_codes_map = regions_future.result()
            if region not in names_to_codes_map.values():
                raise WrongArgumentsException(Err.OI0012, [region])
            if mode == 'current':
                skus = self.get_aws_skus(executor, [source_flavor_id],
                                         preinstalled, os_type)
            else:
                region_flavors, relevant_flavor = (
                    self.get_matched_instance_types(
                        executor, region, vcpu, instance_family))
                skus = self.get_aws_skus(executor, region_flavors,
                                         preinstalled, os_type)
                if not skus and mode == 'search_relevant' and relevant_flavor:
                    skus = self.get_aws_skus(executor, [relevant_flavor],
                                             preinstalled, os_type)

        prices = []
        for sku_info in skus:
            region_code = names_to_codes_map.get(
                sku_info['product']['attributes']['location'])
            if not region_code or region_code != region:
                continue
            price = list(list(
                sku_info['terms']['OnDemand'].values()
            )[0]['priceDimensions'].values())[0]['pricePerUnit']
            if 'USD' not in price or float(price['USD']) == 0:
                continue
            attributes = sku_info['product']['attributes']
            ram = float(attributes['memory'].split()[0])
            prices.append({
                'cpu': int(attributes['vcpu']),
                'ram': int(ram * 1024),
                'flavor': attributes['instanceType'],
                'price': float(price['USD']),
            })
        if not prices:
            raise TypeNotMatchedException()
        else:
            return max(prices, key=lambda x: x['price'])

    def find_alibaba_flavor(self, region, family_specs, mode,
                            additional_params=None):
        additional_params = additional_params or {}
        vcpu = additional_params.get('cpu', 0)
        source_flavor_id = family_specs['source_flavor_id']
        with CachedThreadPoolExecutor(self.mongo_client) as executor:
            try:
                all_flavors = executor.submit(
                    self.alibaba.get_all_flavors, region).result()
                available_flavors = executor.submit(
                    self.alibaba.get_available_flavors, region).result()
                available_prices = executor.submit(
                    self.alibaba.get_flavor_prices,
                    available_flavors, region).result()
            except RegionNotFoundException:
                raise WrongArgumentsException(Err.OI0012, [region])
            except ValueError as exc:
                raise WrongArgumentsException(Err.OI0017, [str(exc)])

        source_flavor_family = all_flavors.get(
            source_flavor_id, {}).get('InstanceTypeFamily')
        flavors = []
        relevant_flavor = None
        for flavor_id, flavor_details in all_flavors.items():
            if flavor_details['InstanceTypeFamily'] != source_flavor_family:
                continue
            flavor_cpu = flavor_details['CpuCoreCount']
            flavor_ram = flavor_details['MemorySize']
            price = available_prices.get(flavor_id)
            if price is None:
                continue
            flavor_result = {
                'cpu': flavor_cpu,
                'ram': flavor_ram,
                'flavor': flavor_id,
                'price': price,
            }
            if mode == 'current':
                if flavor_id == source_flavor_id:
                    flavors.append(flavor_result)
                    break
            else:
                if flavor_cpu < vcpu:
                    continue
                if flavor_cpu == vcpu:
                    flavors.append(flavor_result)
                    continue
                if not relevant_flavor:
                    relevant_flavor = flavor_result
                    continue
                if relevant_flavor['cpu'] > flavor_result['cpu']:
                    relevant_flavor = flavor_result
        if not flavors and mode == 'search_relevant' and relevant_flavor:
            flavors = [relevant_flavor]
        if not flavors:
            raise TypeNotMatchedException()
        return min(flavors, key=lambda x: x['price'])

    def find_gcp_flavor(self, region, family_specs, mode,
                        additional_params=None):
        additional_params = additional_params or {}
        vcpu = additional_params.get('cpu', 0)
        source_flavor_id = family_specs['source_flavor_id']
        with CachedThreadPoolExecutor(self.mongo_client) as executor:
            try:
                instance_types = executor.submit(
                    self.gcp.get_instance_types_priced, region).result()
            except RegionNotFoundException:
                raise WrongArgumentsException(Err.OI0012, [region])
            except ValueError as ex:
                raise WrongArgumentsException(Err.OI0017, [str(ex)])
            except ForbiddenException:
                raise OptForbidden(Err.OI0020, [])

        source_flavor_family = source_flavor_id.split("-")[0]
        flavors = []
        relevant_flavor = None
        for flavor_id, flavor_details in instance_types.items():
            if flavor_details['family'] != source_flavor_family:
                continue
            flavor_cpu = flavor_details['cpu_cores']
            flavor_ram = flavor_details['ram_gb']
            price = flavor_details.get("price")
            if price is None:
                continue
            flavor_result = {
                'cpu': flavor_cpu,
                'ram': flavor_ram,
                'flavor': flavor_id,
                'price': price,
            }
            if mode == 'current':
                if flavor_id == source_flavor_id:
                    flavors.append(flavor_result)
                    break
            else:
                if flavor_cpu < vcpu:
                    continue
                if flavor_cpu == vcpu:
                    flavors.append(flavor_result)
                    continue
                if not relevant_flavor:
                    relevant_flavor = flavor_result
                    continue
                if relevant_flavor['cpu'] > flavor_result['cpu']:
                    relevant_flavor = flavor_result
        if not flavors and mode == 'search_relevant' and relevant_flavor:
            flavors = [relevant_flavor]
        if not flavors:
            raise TypeNotMatchedException()
        return min(flavors, key=lambda x: x['price'])

    def find_nebius_flavor(self, region, family_specs, mode,
                           additional_params=None):

        def round_to_half_int(num):
            return round(num * 2) / 2

        additional_params = additional_params or {}
        vcpu = additional_params.get('cpu', 1)
        ram = family_specs.get('ram', 0)
        platform_name = family_specs['source_flavor_id']
        cpu_fraction = family_specs['cpu_fraction']
        currency = additional_params.get('currency', 'USD')
        with CachedThreadPoolExecutor(self.mongo_client) as executor:
            # add cloud_account_id to not use cached prices for
            # other nebius cloud accounts
            skus = executor.submit(
                self.nebius.get_prices, currency=currency,
                cloud_account_id=self.cloud_account_id).result()

        cloud_acc = self.get_cloud_account(self.cloud_account_id)
        platform = [
            x for x in cloud_acc['config']['platforms'].values()
            if x['name'] == platform_name]
        sku_pattern = '^{0}. {1}% vCPU$'.format(
            platform_name, cpu_fraction)
        sku_regex = re.compile(sku_pattern)
        family_skus = [
            sku for sku in skus if re.search(sku_regex, sku['name'])]
        flavors = []
        for sku in family_skus:
            price_per_core = sku['pricingVersions'][-1][
                'pricingExpressions'][0]['rates'][0]['unitPrice']
            if platform:
                ram_cpu_list = platform[0]['core_fraction'].get(
                    str(cpu_fraction), [])
                for el in ram_cpu_list:
                    if vcpu in el['cpu']:
                        ram_per_core = round_to_half_int(ram / vcpu)
                        available_ram = el['ram_per_core']
                        if ram_per_core in available_ram:
                            expected_ram = ram
                        else:
                            # find nearest available down ram value which
                            # is not the maximum ram value for this sku
                            nearest = min(available_ram,
                                          key=lambda x: x - ram)
                            if nearest == max(available_ram):
                                LOG.warning(
                                    'Expected nearest RAM value %s is'
                                    ' maximum for platform %s',
                                    nearest, platform_name)
                                continue
                            else:
                                expected_ram = nearest * vcpu
                        flavor_result = {
                            'cpu': vcpu,
                            'ram': expected_ram,
                            'flavor': platform_name,
                            'price': float(price_per_core) * vcpu,
                        }
                        flavors.append(flavor_result)
                        if mode == 'current':
                            break
                else:
                    LOG.warning('Expected vCPU value %s is not '
                                'available for platform %s', vcpu, platform_name)
        if not flavors:
            raise TypeNotMatchedException()
        return min(flavors, key=lambda x: x['price'])

    def find_nebius_rds_flavor(self, region, family_specs, mode,
                               additional_params=None):

        def bytes_to_gb(ram):
            return ram / 2 ** 30

        additional_params = additional_params or {}
        vcpu = additional_params.get('cpu', 1)
        currency = additional_params.get('currency', 'USD')
        category = family_specs.get('category')
        platform_name = family_specs.get('platform_name')
        source_flavor_id = family_specs['source_flavor_id']
        if '.' in source_flavor_id:
            flavor_family = source_flavor_id.split('.')[0]
        else:
            flavor_family = source_flavor_id.split('-')[0]

        all_flavors = self.nebius.get_rds_flavors(service_name=category.lower())
        source_flavor_info = [x for x in all_flavors if x.id == source_flavor_id]
        family_flavors = [x for x in all_flavors
                          if x.id.startswith(flavor_family) and x.cores == vcpu]

        with CachedThreadPoolExecutor(self.mongo_client) as executor:
            skus = executor.submit(
                self.nebius.get_prices, currency=currency,
                cloud_account_id=self.cloud_account_id).result()
        sku_pattern = '^{0}. {1}. 100% vCPU$'.format(category, platform_name)
        sku_regex = re.compile(sku_pattern, flags=re.IGNORECASE)
        family_skus = [
            sku for sku in skus if re.search(sku_regex, sku['name'])]
        flavors = []
        if family_skus:
            price_per_core = family_skus[0]['pricingVersions'][-1][
                'pricingExpressions'][0]['rates'][0]['unitPrice']
            if mode == 'current':
                if source_flavor_info:
                    flavor_result = {
                        'cpu': source_flavor_info[0].cores,
                        'ram': bytes_to_gb(source_flavor_info[0].memory),
                        'flavor': source_flavor_id,
                        'price': float(price_per_core) * source_flavor_info[0].cores,
                    }
                    flavors.append(flavor_result)
            else:
                for fl in family_flavors:
                    flavor_result = {
                        'cpu': fl.cores,
                        'ram': bytes_to_gb(fl.memory),
                        'flavor': fl.id,
                        'price': float(price_per_core) * fl.cores,
                    }
                    flavors.append(flavor_result)
        if not flavors:
            raise TypeNotMatchedException()
        return min(flavors, key=lambda x: x['price'])

    def find_alibaba_rds_flavor(
            self, region, family_specs, mode, additional_params=None):
        additional_params = additional_params or {}
        vcpu = additional_params.get('cpu', 0)
        source_flavor_id = family_specs.pop('source_flavor_id')
        with CachedThreadPoolExecutor(self.mongo_client) as executor:
            try:
                all_flavors_future = executor.submit(
                    self.alibaba.get_all_rds_flavors, region)
                family_flavors_future = executor.submit(
                    self.alibaba.get_available_rds_flavors, region=region,
                    **family_specs)
                all_flavors = all_flavors_future.result()
                family_flavors = family_flavors_future.result()
            except RegionNotFoundException:
                raise WrongArgumentsException(Err.OI0012, [region])

        source_flavor_info = all_flavors.get(source_flavor_id)
        if not source_flavor_info or 'ClassGroup' not in source_flavor_info:
            LOG.warning('Could not find flavor group for flavor %s',
                        source_flavor_id)
            raise TypeNotMatchedException()
        source_flavor_group = source_flavor_info['ClassGroup']

        flavors = []
        relevant_flavor = None
        for flavor_id in family_flavors:
            flavor_details = all_flavors.get(flavor_id)
            if not flavor_details:
                continue
            if flavor_details['ClassGroup'] != source_flavor_group:
                continue
            price = float(flavor_details['ReferencePrice']) / 100  # Cent to $
            flavor_cpu = int(flavor_details['Cpu'])
            flavor_ram = self._parse_alibaba_rds_ram(
                flavor_details['MemoryClass'])
            flavor_result = {
                'cpu': flavor_cpu,
                'ram': flavor_ram,
                'flavor': flavor_id,
                'price': price,
            }
            if mode == 'current':
                if flavor_id == source_flavor_id:
                    flavors.append(flavor_result)
                    break
            else:
                if flavor_cpu < vcpu:
                    continue
                if flavor_cpu == vcpu:
                    flavors.append(flavor_result)
                    continue
                if not relevant_flavor:
                    relevant_flavor = flavor_result
                    continue
                if relevant_flavor['cpu'] > flavor_result['cpu']:
                    relevant_flavor = flavor_result
        if not flavors and mode == 'search_relevant' and relevant_flavor:
            flavors = [relevant_flavor]
        if not flavors:
            raise TypeNotMatchedException()
        return min(flavors, key=lambda x: x['price'])

    @staticmethod
    def _parse_alibaba_rds_ram(ram_string):
        flavor_ram_match = re.match(r'^\s*(\d+)G.*$', ram_string)
        if flavor_ram_match:
            return int(flavor_ram_match.group(1))
        else:
            LOG.warning('Could not parse RAM from `%s`', ram_string)

    def get_aws_all_instance_types(self, executor, region):
        return executor.submit(self.aws.get_all_instance_types, region).result()

    def get_matched_instance_types(self, executor, region, vcpu,
                                   instance_family):
        types = self.get_aws_all_instance_types(executor, region)
        flavors, relevant_flavor = self.find_instance_types(
            vcpu, types, instance_family)
        return flavors, relevant_flavor

    def get_aws_skus(self, executor, flavors, preinstalled, os_type):
        pricing_futures = []
        for flavor in flavors:
            pricing_futures.append(executor.submit(
                self.aws.get_pricing,
                {'instanceType': flavor,
                 'preInstalledSw': preinstalled,
                 'operatingSystem': os_type, 'capacitystatus': 'Used'}
            ))

        skus = []
        for f in pricing_futures:
            skus.extend(f.result())
        return skus

    def find_instance_types(self, vcpu, types, instance_family):
        def is_matches(type_):
            if 'on-demand' not in type_['SupportedUsageClasses']:
                return False
            if type_['VCpuInfo']['DefaultVCpus'] < vcpu:
                return False
            instance_type = type_['InstanceType'].split('.')[0]
            if instance_family != instance_type:
                return False
            return True

        instance_types = []
        relevant_inst_type = None
        for t in types:
            if not is_matches(t):
                continue
            type_cpu = t['VCpuInfo']['DefaultVCpus']
            if type_cpu == vcpu:
                instance_types.append(t['InstanceType'])
                continue
            if not relevant_inst_type:
                relevant_inst_type = t
                continue
            rel_cpu = relevant_inst_type['VCpuInfo']['DefaultVCpus']
            if rel_cpu > type_cpu:
                relevant_inst_type = t
        relevant_flavor = relevant_inst_type['InstanceType'] if (
            relevant_inst_type) else None
        return instance_types, relevant_flavor


class FlavorAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return FlavorController
