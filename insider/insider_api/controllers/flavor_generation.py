import re
from cloud_adapter.exceptions import RegionNotFoundException
from insider_api.exceptions import Err
from insider_api.controllers.base import (BaseAsyncControllerWrapper,
                                          CachedThreadPoolExecutor)
from insider_api.controllers.flavor import FlavorController
from optscale_exceptions.common_exc import WrongArgumentsException

AZURE_FAMILY_GENERATION_MAP = {
    'standardDASFamily': 'standardDASv5Family',
    'standardDASv2Family': 'standardDASv5Family',
    'standardDASv3Family': 'standardDASv5Family',
    'standardDASv4Family': 'standardDASv5Family',
    'standardDCSFamily': 'standardDCSv3Family',
    'standardDCSv2Family': 'standardDCSv3Family',
    'standardDDSFamily': 'standardDDSv5Family',
    'standardDDSv2Family': 'standardDDSv5Family',
    'standardDDSv3Family': 'standardDDSv5Family',
    'standardDDSv4Family': 'standardDDSv5Family',
    'standardDDFamily': 'standardDDv5Family',
    'standardDDv2Family': 'standardDDv5Family',
    'standardDDv3Family': 'standardDDv5Family',
    'standardDDv4Family': 'standardDDv5Family',
    'standardDFamily': 'standardDv5Family',
    'standardDv2Family': 'standardDv5Family',
    'standardDv3Family': 'standardDv5Family',
    'standardDv4Family': 'standardDv5Family',
    'standardDSFamily': 'standardDSv5Family',
    'standardDSv2Family': 'standardDSv5Family',
    'standardDSv3Family': 'standardDSv5Family',
    'standardDSv4Family': 'standardDSv5Family',
    'standardEASFamily': 'standardEASv5Family',
    'standardEASv2Family': 'standardEASv5Family',
    'standardEASv3Family': 'standardEASv5Family',
    'standardEASv4Family': 'standardEASv5Family',
    'standardEDSFamily': 'standardEDSv5Family',
    'standardEDSv2Family': 'standardEDSv5Family',
    'standardEDSv3Family': 'standardEDSv5Family',
    'standardEDSv4Family': 'standardEDSv5Family',
    'standardEDFamily': 'standardEDv5Family',
    'standardEDv2Family': 'standardEDv5Family',
    'standardEDv3Family': 'standardEDv5Family',
    'standardEDv4Family': 'standardEDv5Family',
    'standardEIASFamily': 'standardEIASv5Family',
    'standardEIASv2Family': 'standardEIASv5Family',
    'standardEIASv3Family': 'standardEIASv5Family',
    'standardEIASv4Family': 'standardEIASv5Family',
    'standardEISFamily': 'standardEISv5Family',
    'standardEISv2Family': 'standardEISv5Family',
    'standardEISv3Family': 'standardEISv5Family',
    'standardEISv4Family': 'standardEISv5Family',
    'standardEIFamily': 'standardEIv5Family',
    'standardEIv2Family': 'standardEIv5Family',
    'standardEIv3Family': 'standardEIv5Family',
    'standardEIv4Family': 'standardEIv5Family',
    'standardESFamily': 'standardESv5Family',
    'standardESv2Family': 'standardESv5Family',
    'standardESv3Family': 'standardESv5Family',
    'standardESv4Family': 'standardESv5Family',
    'standardEFamily': 'standardEv5Family',
    'standardEv2Family': 'standardEv5Family',
    'standardEv3Family': 'standardEv5Family',
    'standardEv4Family': 'standardEv5Family',
    'standardFSFamily': 'standardFSv2Family',
    'standardLSFamily': 'standardLSv2Family',
    'standardMSFamily': 'standardMSv2Family',
    'standardNCSFamily': 'standardNCSv3Family',
    'standardNCSv2Family': 'standardNCSv3Family',
    'standardNDSFamily': 'standardNDSv3Family',
    'standardNDSv2Family': 'standardNDSv3Family',
    'standardNVSFamily': 'standardNVSv4Family',
    'standardNVSv2Family': 'standardNVSv4Family',
    'standardNVSv3Family': 'standardNVSv4Family'
}


class FlavorGenerationController(FlavorController):
    def find_flavor_generation(self, cloud_type, region, current_flavor,
                               **kwargs):
        find_flavor_function_map = {
            'aws_cnr': self.find_aws_flavor_generation,
            'azure_cnr': self.find_azure_flavor_generation,
            'alibaba_cnr': self.find_alibaba_flavor_generation
        }
        params = {
            'region': region,
            'current_flavor': current_flavor,
            'os_type': kwargs.get('os_type'),
            'preinstalled': kwargs.get('preinstalled'),
            'meter_id': kwargs.get('meter_id')
        }
        return find_flavor_function_map[cloud_type](**params)

    def find_aws_flavor_generation(self, region, current_flavor, os_type=None,
                                   preinstalled=None, meter_id=None):
        if not os_type or os_type == 'NA':
            os_type = 'Linux'
        preinstalled = preinstalled or 'NA'
        with CachedThreadPoolExecutor(self.mongo_client) as executor:
            names_to_codes_map = executor.submit(
                self.aws.get_region_name_code_map).result()
            if region not in names_to_codes_map.values():
                raise WrongArgumentsException(Err.OI0012, [region])
            all_instance_types = self.get_aws_all_instance_types(
                executor, region)
            current_flavor_info = next(
                (t for t in all_instance_types
                 if t['InstanceType'] == current_flavor), None)
            if (not current_flavor_info or
                    current_flavor_info['CurrentGeneration']):
                return {}
            vcpu = current_flavor_info['VCpuInfo']['DefaultVCpus']
            ram = int(current_flavor_info['MemoryInfo']['SizeInMiB'])
            arch = current_flavor_info['ProcessorInfo']['SupportedArchitectures']
            region_flavors = [
                t['InstanceType'] for t in all_instance_types
                if (t['VCpuInfo']['DefaultVCpus'] == vcpu and
                    t['MemoryInfo']['SizeInMiB'] == ram and
                    'on-demand' in t['SupportedUsageClasses'] and
                    arch == t['ProcessorInfo']['SupportedArchitectures'] and
                    t['CurrentGeneration'])
            ]
            skus = self.get_aws_skus(executor, region_flavors, preinstalled,
                                     os_type)
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
            prices.append({
                'flavor': attributes['instanceType'],
                'price': float(price['USD']) * 24
            })
        if not prices:
            return {}
        proposed_value = min(prices, key=lambda x: x['price'])
        return {
            'proposed_flavor': proposed_value['flavor'],
            'proposed_daily_price': proposed_value['price']
        }

    def find_azure_flavor_generation(self, region, current_flavor, os_type=None,
                                     preinstalled=None, meter_id=None):
        windows_key = 'Windows'
        linux_key = 'Linux'
        if not os_type or os_type == 'NA':
            os_type = linux_key
        if os_type not in [linux_key, windows_key]:
            return {}
        proposed_prices = []
        with CachedThreadPoolExecutor(self.mongo_client) as executor:
            flavor_map = executor.submit(self.get_azure_flavors).result()
            flavor_info = flavor_map.get(current_flavor, {})
            flavor_family = flavor_info.get('family')
            if flavor_family not in AZURE_FAMILY_GENERATION_MAP:
                return {}
            proposed_flavor_family = AZURE_FAMILY_GENERATION_MAP.get(
                flavor_family)
            vcpu = flavor_info.get('vcpus', 0)
            ram = flavor_info.get('ram', 0)
            proposed_flavor_map = {
                flavor_name: flavor for flavor_name, flavor in
                flavor_map.items()
                if (flavor.get('family') == proposed_flavor_family and
                    flavor.get('vcpus') == vcpu and
                    flavor.get('ram') == ram)
            }
            locations_future = executor.submit(self.get_azure_locations)
            locations = locations_future.result()
            location = locations.get(region)
            if not location:
                raise WrongArgumentsException(Err.OI0012, [region])
            current_prices = executor.submit(
                self.get_azure_prices, location,
                re.sub(r'[0-9]+', '[0-9]+', current_flavor, 1)).result()
            for flavor_name in proposed_flavor_map:
                instance_family = re.sub(r'[0-9]+', '[0-9]+', flavor_name, 1)
                flavor_prices = executor.submit(self.get_azure_prices, location,
                                                instance_family).result()
                if flavor_prices:
                    proposed_prices.extend(flavor_prices)

        flavors = []
        meter_name = self._set_meter_name(meter_id, current_prices)
        for price in proposed_prices:
            price_meter_name = price.get('meterName')
            if meter_id:
                if meter_name and not self._contains_same_meter_family(
                        meter_name, price_meter_name):
                    continue
            flavor = proposed_flavor_map.get(price['armSkuName'])
            if not flavor:
                continue
            product_name = price['productName']
            # according to azure pricing api we have 'windows'
            # in productName as os type, and don't have it for others
            if os_type == windows_key:
                if windows_key not in product_name:
                    continue
            else:
                if windows_key in product_name:
                    continue
            flavors.append({
                'flavor': flavor['name'],
                'price': float(price['unitPrice']) * 24
            })
        if not flavors:
            return {}
        proposed_value = min(flavors, key=lambda x: x['price'])
        return {
            'proposed_flavor': proposed_value['flavor'],
            'proposed_daily_price': proposed_value['price']
        }

    @staticmethod
    def _select_suitable_family(flavor_family, all_families, available_families):
        prefix, number, postfix = '[a-z]+', '[0-9]+', '[a-z]*'
        family_template_base = r"ecs\.({prefix})({number})"
        family_template_postfix = family_template_base + r"({postfix})"
        flavor_family_search = re.search(family_template_postfix.format(
            prefix=prefix, number=number, postfix=postfix), flavor_family)
        if not flavor_family_search:
            return []
        family_prefix = flavor_family_search.group(1)
        family_number = flavor_family_search.group(2)
        family_postfix = flavor_family_search.group(3)
        if family_postfix:
            family_template = family_template_postfix.format(
                prefix=family_prefix, number=number, postfix=family_postfix)
        else:
            family_template = family_template_base.format(
                prefix=family_prefix, number=number)
        suitable_family = None
        generation_version = 1
        generation_template = r"ecs-({number})"
        for family, generation in all_families.items():
            if family not in available_families:
                continue
            family_search = re.search(family_template, family)
            if family_search:
                if family_number == family_search.group(2):
                    continue
                generation_search = re.search(generation_template.format(
                    number=number), generation)
                if not generation_search:
                    continue
                generation_number = int(generation_search.group(1))
                if generation_number <= generation_version:
                    continue
                generation_version = generation_number
                suitable_family = family
        return suitable_family

    def find_alibaba_flavor_generation(self, region, current_flavor,
                                       os_type=None, preinstalled=None,
                                       meter_id=None):
        with CachedThreadPoolExecutor(self.mongo_client) as executor:
            try:
                all_flavors = executor.submit(
                    self.alibaba.get_all_flavors, region).result()
                if current_flavor not in all_flavors:
                    return {}
                all_families = executor.submit(
                    self.alibaba.get_all_families, region).result()
                available_flavors = executor.submit(
                    self.alibaba.get_available_flavors, region).result()
                available_prices = executor.submit(
                    self.alibaba.get_flavor_prices,
                    available_flavors, region).result()
            except RegionNotFoundException:
                raise WrongArgumentsException(Err.OI0012, [region])
            except ValueError as exc:
                raise WrongArgumentsException(Err.OI0017, [str(exc)])
        flavor_info = all_flavors.get(current_flavor)
        available_families = {
            flavor['InstanceTypeFamily'] for flavor_name, flavor in
            all_flavors.items() if flavor_name in available_flavors}
        vcpu = flavor_info.get('CpuCoreCount', 0)
        ram = flavor_info.get('MemorySize', 0)
        flavor_family = flavor_info.get('InstanceTypeFamily')
        suitable_family = self._select_suitable_family(
            flavor_family, all_families, list(available_families))
        if not suitable_family:
            return {}
        flavors = []
        for flavor_id, flavor_details in all_flavors.items():
            if flavor_details['InstanceTypeFamily'] != suitable_family:
                continue
            price = available_prices.get(flavor_id)
            if price is None:
                continue
            flavor_cpu = flavor_details['CpuCoreCount']
            flavor_ram = flavor_details['MemorySize']
            flavor_result = {
                'flavor': flavor_id,
                'price': price * 24,
            }
            if flavor_cpu == vcpu and flavor_ram == ram:
                flavors.append(flavor_result)
        if not flavors:
            return {}
        proposed_value = min(flavors, key=lambda x: x['price'])
        return {
            'proposed_flavor': proposed_value['flavor'],
            'proposed_daily_price': proposed_value['price']
        }


class FlavorGenerationAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return FlavorGenerationController
