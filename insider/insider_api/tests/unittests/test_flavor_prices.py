import os

from datetime import datetime
from unittest.mock import patch, PropertyMock

import optscale_client.insider_client.client as insider_client

from insider.insider_api.tests.unittests.test_api_base import TestBase


class TestFlavorPricesApi(TestBase):
    def setUp(self):
        os.environ['ASYNC_TEST_TIMEOUT'] = '30'
        self.aws_valid_params = {
            'cloud_type': 'aws',
            'region': 'us-west-2',
            'flavor': 't3.medium',
            'os_type': 'linux'
        }
        self.azure_valid_params = {
            'cloud_type': 'azure',
            'region': 'uaecentral',
            'flavor': 'Standard_B1ms',
            'os_type': 'windows'
        }
        self.alibaba_valid_params = {
            'cloud_type': 'alibaba',
            'region': 'Singapore',
            'flavor': 'cs.t5-lc1m2.large',
            'os_type': 'linux'
        }
        self.valid_aws_family_params = {
            'cloud_type': 'aws',
            'region': 'us-west-2',
            'instance_family': 't3'
        }
        self.azure_cad = patch(
            'insider.insider_api.controllers.flavor_price.'
            'AzureProvider.cloud_adapter').start()
        self.aws_cad = patch(
            'insider.insider_api.controllers.flavor_price.'
            'AwsProvider.cloud_adapter').start()
        self.alibaba_cad = patch(
            'insider.insider_api.controllers.flavor_price.'
            'AlibabaProvider.cloud_adapter').start()
        super().setUp()
        patch('insider.insider_api.controllers.flavor_price.'
              'BaseProvider.mongo_client',
              new_callable=PropertyMock, return_value=self.mongo_client).start()

    def insert_azure_pricing(self, ts):
        discovery = {
            "started_at": ts - 1,
            "completed_at": ts,
            "cloud_type": "azure_cnr"
        }
        self.mongo_client.insider.discoveries.insert_one(discovery)
        pricings = [
            {
                'serviceFamily': 'Compute',
                'productId': 'DZH318Z0BQ4C',
                'tierMinimumUnits': 0.0,
                'created_at': 1623287688,
                'unitPrice': 0.14,
                'meterId': 'd5a81ebd-6435-4b0f-9ab1-6c0d0dd6eed0',
                'location': 'UAE Central',
                'skuId': 'DZH318Z0BQ4C/01C7',
                'isPrimaryMeterRegion': False,
                'serviceName': 'Virtual Machines',
                'meterName': 'DS2 v2',
                'last_seen': ts,
                'productName': 'Virtual Machines DSv2 Series for Windows',
                'serviceId': 'DZH313Z7MMC8',
                'currencyCode': 'USD',
                'skuName': 'DS2 v2',
                'armSkuName': 'Standard_B1ms',
                'armRegionName': 'uaecentral',
                'unitOfMeasure': '1 Hour',
                'retailPrice': 0.14,
                'effectiveStartDate': '2016-09-01T00:00:00Z',
                'type': 'Consumption'
            },
            {
                'serviceFamily': 'Compute',
                'productId': 'DZH318Z0BQ4C',
                'tierMinimumUnits': 0.0,
                'created_at': 1623287688,
                'unitPrice': 0.15,
                'meterId': 'd5a81ebd-6435-4b0f-9ab1-6c0d0dd6eed0',
                'location': 'UAE Central',
                'skuId': 'DZH318Z0BQ4C/01C7',
                'isPrimaryMeterRegion': False,
                'serviceName': 'Virtual Machines',
                'meterName': 'DS2 v2',
                'last_seen': ts,
                'productName': 'Virtual Machines DSv2 Series',
                'serviceId': 'DZH313Z7MMC8',
                'currencyCode': 'USD',
                'skuName': 'DS2 v2',
                'armSkuName': 'Standard_B1ms',
                'armRegionName': 'uaecentral',
                'unitOfMeasure': '1 Hour',
                'retailPrice': 0.15,
                'effectiveStartDate': '2016-09-01T00:00:00Z',
                'type': 'Consumption'
            },
            {
                'serviceFamily': 'Compute',
                'productId': 'DZH318Z0BQ4C',
                'tierMinimumUnits': 0.0,
                'created_at': 1623287688,
                'unitPrice': 0.16,
                'meterId': 'd5a81ebd-6435-4b0f-9ab1-6c0d0dd6eed0',
                'location': 'UAE Central',
                'skuId': 'DZH318Z0BQ4C/01C7',
                'isPrimaryMeterRegion': False,
                'serviceName': 'Virtual Machines',
                'meterName': 'DS2 v2',
                'last_seen': ts - 100500,
                'productName': 'Virtual Machines DSv2 Series',
                'serviceId': 'DZH313Z7MMC8',
                'currencyCode': 'USD',
                'skuName': 'DS2 v2',
                'armSkuName': 'Standard_B1ms',
                'armRegionName': 'uaecentral',
                'unitOfMeasure': '1 Hour',
                'retailPrice': 0.16,
                'effectiveStartDate': '2016-09-01T00:00:00Z',
                'type': 'Consumption'
            },
            {
                'serviceFamily': 'Compute',
                'productId': 'DZH318Z0BQ4C',
                'tierMinimumUnits': 0.0,
                'created_at': 1623287688,
                'unitPrice': 0.17,
                'meterId': 'd5a81ebd-6435-4b0f-9ab1-6c0d0dd6eed0',
                'location': 'UAE Central',
                'skuId': 'DZH318Z0BQ4C/01C7',
                'isPrimaryMeterRegion': False,
                'serviceName': 'Virtual Machines',
                'meterName': 'DS2 v2',
                'last_seen': ts,
                'productName': 'Virtual Machines DSv2 Series',
                'serviceId': 'DZH313Z7MMC8',
                'currencyCode': 'USD',
                'skuName': 'DS2 v2',
                'armSkuName': 'Standard_B1ms',
                'armRegionName': 'uaecentral',
                'unitOfMeasure': '1 Hour',
                'retailPrice': 0.17,
                'effectiveStartDate': '2016-09-01T00:00:00Z',
                'effectiveEndDate': '2016-09-01T00:00:00Z',
                'type': 'Consumption'
            }
        ]
        bulk = []
        for pricing in pricings:
            brl_pricing = pricing.copy()
            brl_pricing['currencyCode'] = 'BRL'
            for k in ['retailPrice', 'unitPrice']:
                brl_pricing[k] = pricing[k] * 2
            bulk.extend([pricing, brl_pricing])
        self.mongo_client.insider.azure_prices.insert_many(bulk)

    def insert_aws_pricing(self, ts):
        pricings = [
            {
                "sku": "2Y2V5UBKTCGHE4AP",
                "capacitystatus": "Used",
                "clockSpeed": "3.1 GHz",
                "currentGeneration": "Yes",
                "dedicatedEbsThroughput": "Up to 2085 Mbps",
                "ecu": "Variable",
                "enhancedNetworkingSupported": "No",
                "instanceFamily": "General purpose",
                "instanceType": "t3.medium",
                "intelAvx2Available": "Yes",
                "intelAvxAvailable": "Yes",
                "intelTurboAvailable": "Yes",
                "licenseModel": "No License required",
                "location": "US West (Oregon)",
                "locationType": "AWS Region",
                "memory": "0.5 GiB",
                "networkPerformance": "Up to 5 Gigabit",
                "normalizationSizeFactor": "0.25",
                "operatingSystem": "Linux",
                "operation": "RunInstances",
                "physicalProcessor": "Intel Skylake E5 2686 v5",
                "preInstalledSw": "NA",
                "price": {"USD": "0.0073000000"},
                "price_unit": "Hrs",
                "processorArchitecture": "64-bit",
                "processorFeatures": "AVX; AVX2; Intel AVX; Intel AVX2; "
                                     "Intel AVX512; Intel Turbo",
                "servicecode": "AmazonEC2",
                "servicename": "Amazon Elastic Compute Cloud",
                "storage": "EBS only",
                "tenancy": "Shared",
                "updated_at": datetime.utcfromtimestamp(ts),
                "usagetype": "APE1-BoxUsage:t3.nano", "vcpu": "2"
            },
            {
                "sku": "2Y2V5UBKTCGHE4AP",
                "capacitystatus": "Used",
                "clockSpeed": "3.1 GHz",
                "currentGeneration": "Yes",
                "dedicatedEbsThroughput": "Up to 2085 Mbps",
                "ecu": "Variable",
                "enhancedNetworkingSupported": "No",
                "instanceFamily": "General purpose",
                "instanceType": "t3.medium",
                "intelAvx2Available": "Yes",
                "intelAvxAvailable": "Yes",
                "intelTurboAvailable": "Yes",
                "licenseModel": "No License required",
                "location": "US West (Oregon)",
                "locationType": "AWS Region",
                "memory": "0.5 GiB",
                "networkPerformance": "Up to 5 Gigabit",
                "normalizationSizeFactor": "0.25",
                "operatingSystem": "Windows",
                "operation": "RunInstances",
                "physicalProcessor": "Intel Skylake E5 2686 v5",
                "preInstalledSw": "NA",
                "price": {"USD": "0.0083000000"},
                "price_unit": "Hrs",
                "processorArchitecture": "64-bit",
                "processorFeatures": "AVX; AVX2; Intel AVX; Intel AVX2; "
                                     "Intel AVX512; Intel Turbo",
                "servicecode": "AmazonEC2",
                "servicename": "Amazon Elastic Compute Cloud",
                "storage": "EBS only",
                "tenancy": "Shared",
                "updated_at": datetime.utcfromtimestamp(ts),
                "usagetype": "APE1-BoxUsage:t3.nano", "vcpu": "2"
            },
            {
                "sku": "2Y2V5UBKTCGHE4AP",
                "capacitystatus": "Used",
                "clockSpeed": "3.1 GHz",
                "currentGeneration": "Yes",
                "dedicatedEbsThroughput": "Up to 2085 Mbps",
                "ecu": "Variable",
                "enhancedNetworkingSupported": "No",
                "instanceFamily": "General purpose",
                "instanceType": "t3.medium",
                "intelAvx2Available": "Yes",
                "intelAvxAvailable": "Yes",
                "intelTurboAvailable": "Yes",
                "licenseModel": "No License required",
                "location": "US West (Oregon)",
                "locationType": "AWS Region",
                "memory": "0.5 GiB",
                "networkPerformance": "Up to 5 Gigabit",
                "normalizationSizeFactor": "0.25",
                "operatingSystem": "Windows",
                "operation": "RunInstances",
                "physicalProcessor": "Intel Skylake E5 2686 v5",
                "preInstalledSw": "SQL Std",
                "price": {"USD": "0.1000000000"},
                "price_unit": "Hrs",
                "processorArchitecture": "64-bit",
                "processorFeatures": "AVX; AVX2; Intel AVX; Intel AVX2; "
                                     "Intel AVX512; Intel Turbo",
                "servicecode": "AmazonEC2",
                "servicename": "Amazon Elastic Compute Cloud",
                "storage": "EBS only",
                "tenancy": "Shared",
                "updated_at": datetime.utcfromtimestamp(ts),
                "usagetype": "APE1-BoxUsage:t3.nano", "vcpu": "2"
            },
            {
                "sku": "2Y2V5UBKTCGHE4AP",
                "capacitystatus": "Used",
                "clockSpeed": "3.1 GHz",
                "currentGeneration": "Yes",
                "dedicatedEbsThroughput": "Up to 2085 Mbps",
                "ecu": "Variable",
                "enhancedNetworkingSupported": "No",
                "instanceFamily": "General purpose",
                "instanceType": "t3.medium",
                "intelAvx2Available": "Yes",
                "intelAvxAvailable": "Yes",
                "intelTurboAvailable": "Yes",
                "licenseModel": "No License required",
                "location": "US West (Oregon)",
                "locationType": "AWS Region",
                "memory": "0.5 GiB",
                "networkPerformance": "Up to 5 Gigabit",
                "normalizationSizeFactor": "0.25",
                "operatingSystem": "Windows",
                "operation": "RunInstances",
                "physicalProcessor": "Intel Skylake E5 2686 v5",
                "preInstalledSw": "NA",
                "price": {"USD": "0.0093000000"},
                "price_unit": "Hrs",
                "processorArchitecture": "64-bit",
                "processorFeatures": "AVX; AVX2; Intel AVX; Intel AVX2; "
                                     "Intel AVX512; Intel Turbo",
                "servicecode": "AmazonEC2",
                "servicename": "Amazon Elastic Compute Cloud",
                "storage": "EBS only",
                "tenancy": "Shared",
                "updated_at": datetime(year=2021, month=6, day=10),
                "usagetype": "APE1-BoxUsage:t3.nano", "vcpu": "2"
            },
            {
                "sku": "2Y2V5UBKTCGHE4AP",
                "capacitystatus": "Used",
                "clockSpeed": "3.1 GHz",
                "currentGeneration": "Yes",
                "dedicatedEbsThroughput": "Up to 2085 Mbps",
                "ecu": "Variable",
                "enhancedNetworkingSupported": "No",
                "instanceFamily": "General purpose",
                "instanceType": "t4.medium",
                "intelAvx2Available": "Yes",
                "intelAvxAvailable": "Yes",
                "intelTurboAvailable": "Yes",
                "licenseModel": "No License required",
                "location": "US West (Oregon)",
                "locationType": "AWS Region",
                "memory": "0.5 GiB",
                "networkPerformance": "Up to 5 Gigabit",
                "normalizationSizeFactor": "0.25",
                "operatingSystem": "Windows",
                "operation": "RunInstances",
                "physicalProcessor": "Intel Skylake E5 2686 v5",
                "preInstalledSw": "NA",
                "price": {"USD": "0.0083000000"},
                "price_unit": "Hrs",
                "processorArchitecture": "64-bit",
                "processorFeatures": "AVX; AVX2; Intel AVX; Intel AVX2; "
                                     "Intel AVX512; Intel Turbo",
                "servicecode": "AmazonEC2",
                "servicename": "Amazon Elastic Compute Cloud",
                "storage": "EBS only",
                "tenancy": "Shared",
                "updated_at": datetime.utcfromtimestamp(ts),
                "usagetype": "APE1-BoxUsage:t3.nano", "vcpu": "2"
            },
            {
                "sku": "2Y2V5UBKTCGHE5AP",
                "capacitystatus": "Used",
                "clockSpeed": "3.1 GHz",
                "currentGeneration": "Yes",
                "dedicatedEbsThroughput": "Up to 2085 Mbps",
                "ecu": "Variable",
                "enhancedNetworkingSupported": "No",
                "instanceFamily": "General purpose",
                "instanceType": "t4.large",
                "intelAvx2Available": "Yes",
                "intelAvxAvailable": "Yes",
                "intelTurboAvailable": "Yes",
                "licenseModel": "No License required",
                "location": "US West (Oregon)",
                "locationType": "AWS Region",
                "memory": "0.5 GiB",
                "networkPerformance": "Up to 5 Gigabit",
                "normalizationSizeFactor": "0.25",
                "operatingSystem": "Windows",
                "operation": "RunInstances",
                "physicalProcessor": "Intel Skylake E5 2686 v5",
                "preInstalledSw": "NA",
                "price": {"USD": "0.0083000000"},
                "price_unit": "Hrs",
                "processorArchitecture": "64-bit",
                "processorFeatures": "AVX; AVX2; Intel AVX; Intel AVX2; "
                                     "Intel AVX512; Intel Turbo",
                "servicecode": "AmazonEC2",
                "servicename": "Amazon Elastic Compute Cloud",
                "storage": "EBS only",
                "tenancy": "Shared",
                "updated_at": datetime.utcfromtimestamp(ts),
                "usagetype": "APE1-BoxUsage:t3.nano", "vcpu": "2"
            },
        ]
        for pricing in pricings:
            self.mongo_client.restapi.aws_prices.insert_one(pricing)

    def insert_alibaba_pricing(self, ts):
        pricings = [
            {
                'UnitPrice': 0.0,
                'ModuleCode': 'InstanceType',
                'CostAfterDiscount': 18.55,
                'OriginalCost': 18.55,
                'InvoiceDiscount': 0.0,
                'billing_method': 'subscription',
                'region': 'Singapore',
                'flavor': 'cs.t5-lc1m2.large',
                'quantity': 1,
                'updated_at': datetime.utcfromtimestamp(ts)
            },
            {
                'UnitPrice': 0.0,
                'ModuleCode': 'InstanceType',
                'CostAfterDiscount': 189.21,
                'OriginalCost': 222.6,
                'InvoiceDiscount': 33.39,
                'billing_method': 'subscription',
                'region': 'Singapore',
                'flavor': 'cs.t5-lc1m2.large',
                'quantity': 12,
                'updated_at': datetime.utcfromtimestamp(ts)
            },
            {
                'UnitPrice': 0.0,
                'ModuleCode': 'InstanceType',
                'CostAfterDiscount': 19.53,
                'OriginalCost': 19.53,
                'InvoiceDiscount': 0.0,
                'billing_method': 'subscription',
                'region': 'Germany (Frankfurt)',
                'flavor': 'cs.t5-lc1m2.large',
                'quantity': 1,
                'updated_at': datetime.utcfromtimestamp(ts)
            },
        ]
        for pricing in pricings:
            self.mongo_client.insider.alibaba_prices.insert_one(pricing)

    def test_invalid_parameters(self):
        for params in [self.aws_valid_params, self.azure_valid_params,
                       self.alibaba_valid_params]:
            for k, v in params.items():
                if k == 'cloud_type':
                    continue
                body = params.copy()
                body[k] = None
                code, resp = self.client.get_flavor_prices(**body)
                self.assertEqual(code, 400)
                self.verify_error_code(resp, 'OI0011')

        for k, v in self.valid_aws_family_params.items():
            if k == 'cloud_type':
                continue
            body = self.valid_aws_family_params.copy()
            body[k] = None
            code, resp = self.client.get_family_prices(**body)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OI0011')

    def test_flavors_bad_secret(self):
        http_provider = insider_client.FetchMethodHttpProvider(
            self.fetch, rethrow=False, secret='123')
        client = insider_client.Client(http_provider=http_provider)
        code, resp = client.get_flavor_prices(**self.aws_valid_params)
        self.assertEqual(code, 403)
        self.verify_error_code(resp, 'OI0005')

    def test_flavors_no_secret(self):
        http_provider = insider_client.FetchMethodHttpProvider(
            self.fetch, rethrow=False)
        client = insider_client.Client(http_provider=http_provider)
        code, resp = client.get_flavor_prices(**self.aws_valid_params)
        self.assertEqual(code, 401)
        self.verify_error_code(resp, 'OI0007')

    def test_not_supported_cloud(self):
        valid_params = self.aws_valid_params.copy()
        valid_params['cloud_type'] = 'test'
        code, resp = self.client.get_flavor_prices(**valid_params)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OI0010')

        valid_params = self.valid_aws_family_params.copy()
        valid_params['cloud_type'] = 'test'
        code, resp = self.client.get_family_prices(**valid_params)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OI0010')

    def test_not_supported_os_type(self):
        self.azure_cad.get_regions_coordinates.return_value = {
            self.azure_valid_params['region']: 2
        }
        for params in [self.aws_valid_params, self.azure_valid_params]:
            valid_params = params.copy()
            valid_params['os_type'] = 'test'
            code, resp = self.client.get_flavor_prices(**valid_params)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OI0015')

        params = self.valid_aws_family_params.copy()
        params['os_type'] = 'test'
        code, resp = self.client.get_family_prices(**params)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OI0015')

    def test_not_supported_region(self):
        for params in [self.aws_valid_params, self.azure_valid_params]:
            valid_params = params.copy()
            valid_params['region'] = 'test'
            code, resp = self.client.get_flavor_prices(**valid_params)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OI0012')

        params = self.valid_aws_family_params.copy()
        params['region'] = 'test'
        code, resp = self.client.get_family_prices(**params)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OI0012')

    def test_azure_valid_params(self):
        now = int(datetime.utcnow().timestamp())
        self.insert_azure_pricing(now)
        self.azure_cad.get_regions_coordinates.return_value = {
            self.azure_valid_params['region']: 2
        }
        code, res = self.client.get_flavor_prices(**self.azure_valid_params)
        self.assertEqual(code, 200)
        self.assertEqual(len(res.get('prices', [])), 1)
        price = res['prices'][0]
        self.assertEqual(price['flavor'], self.azure_valid_params['flavor'])
        self.assertEqual(price['region'], self.azure_valid_params['region'])
        self.assertEqual(price['operating_system'],
                         self.azure_valid_params['os_type'])
        self.assertEqual(price['price'], 0.14)
        for k in ['price_unit', 'currency']:
            self.assertIsNotNone(price.get(k))

        self.azure_valid_params['os_type'] = 'linux'
        code, res = self.client.get_flavor_prices(**self.azure_valid_params)
        self.assertEqual(code, 200)
        self.assertEqual(len(res.get('prices', [])), 1)
        price = res['prices'][0]
        self.assertEqual(price['price'], 0.15)
        self.assertEqual(price['currency'], 'USD')

        code, res = self.client.get_flavor_prices(
            currency='BRL', **self.azure_valid_params)
        self.assertEqual(code, 200)
        self.assertEqual(len(res.get('prices', [])), 1)
        price = res['prices'][0]
        self.assertEqual(price['price'], 0.3)
        self.assertEqual(price['currency'], 'BRL')

        code, res = self.client.get_flavor_prices(
            currency='EU', **self.azure_valid_params)
        self.assertEqual(code, 200)
        self.assertEqual(len(res.get('prices', [])), 0)

    def test_aws_valid_params(self):
        now = int(datetime.utcnow().timestamp())
        self.insert_aws_pricing(now)
        code, res = self.client.get_flavor_prices(**self.aws_valid_params)
        self.assertEqual(code, 200)
        self.assertEqual(len(res.get('prices', [])), 1)
        price = res['prices'][0]
        self.assertEqual(price['flavor'], self.aws_valid_params['flavor'])
        self.assertEqual(price['region'], self.aws_valid_params['region'])
        self.assertEqual(price['operating_system'],
                         self.aws_valid_params['os_type'])
        self.assertEqual(price['price'], 0.0073)
        for k in ['price_unit', 'currency']:
            self.assertIsNotNone(price.get(k))
        aws_preinstalled_params = self.aws_valid_params.copy()
        aws_preinstalled_params['os_type'] = 'windows'
        aws_preinstalled_params['preinstalled'] = 'sql STD'
        code, res = self.client.get_flavor_prices(**aws_preinstalled_params)
        self.assertEqual(code, 200)
        self.assertEqual(len(res.get('prices', [])), 1)
        price = res['prices'][0]
        self.assertEqual(price['operating_system'],
                         aws_preinstalled_params['os_type'])
        self.assertEqual(price['price'], 0.1)

    def test_alibaba_valid_params(self):
        now = int(datetime.utcnow().timestamp())
        self.insert_alibaba_pricing(now)
        self.alibaba_valid_params['quantity'] = 1
        self.alibaba_valid_params['billing_method'] = 'subscription'
        code, res = self.client.get_flavor_prices(**self.alibaba_valid_params)
        self.assertEqual(code, 200)
        self.assertEqual(len(res.get('prices', [])), 1)
        price = res['prices'][0]
        self.assertEqual(price['flavor'], self.alibaba_valid_params['flavor'])
        self.assertEqual(price['region'], self.alibaba_valid_params['region'])
        self.assertEqual(price['operating_system'],
                         self.alibaba_valid_params['os_type'])
        self.assertEqual(price['price'], 18.55)
        for k in ['price_unit', 'currency']:
            self.assertIsNotNone(price.get(k))
        alibaba_valid_params = self.alibaba_valid_params.copy()
        alibaba_valid_params['region'] = 'Germany (Frankfurt)'
        code, res = self.client.get_flavor_prices(**alibaba_valid_params)
        self.assertEqual(code, 200)
        self.assertEqual(len(res.get('prices', [])), 1)
        price = res['prices'][0]
        self.assertEqual(price['operating_system'],
                         alibaba_valid_params['os_type'])
        self.assertEqual(price['price'], 19.53)

    def test_aws_valid_params_empty(self):
        with patch('insider.insider_api.controllers.flavor_price.AwsProvider.'
                   'cloud_adapter.get_prices', return_value=[]):
            code, res = self.client.get_flavor_prices(**self.aws_valid_params)
            self.assertEqual(code, 200)
            self.assertListEqual(res.get('prices'), [])

            code, res = self.client.get_family_prices(
                **self.valid_aws_family_params)
            self.assertEqual(code, 200)
            self.assertListEqual(res.get('prices'), [])

    def test_azure_valid_params_empty(self):
        self.azure_cad.get_regions_coordinates.return_value = {
            self.azure_valid_params['region']: 2
        }
        code, res = self.client.get_flavor_prices(**self.azure_valid_params)
        self.assertEqual(code, 200)
        self.assertListEqual(res.get('prices'), [])

    def test_alibaba_valid_params_empty(self):
        code, res = self.client.get_flavor_prices(**self.alibaba_valid_params)
        self.assertEqual(code, 200)
        self.assertListEqual(res.get('prices'), [])

    def test_aws_family_valid_params(self):
        now = int(datetime.utcnow().timestamp())
        self.insert_aws_pricing(now)
        code, res = self.client.get_family_prices(
            **self.valid_aws_family_params)
        self.assertEqual(code, 200)
        self.assertEqual(len(res.get('prices', [])), 1)
        price = res['prices'][0]
        self.assertEqual(price['instance_family'],
                         self.valid_aws_family_params['instance_family'])
        self.assertEqual(price['region'],
                         self.valid_aws_family_params['region'])
        self.assertEqual(price['operating_system'], 'linux')
        self.assertEqual(price['instance_type'], 't3.medium')
        self.assertEqual(price['price'], 0.0073)
        self.assertEqual(price['cpu'], 2)
        self.assertEqual(price['ram'], 512)
        self.assertIsNone(price['gpu'])
        for k in ['price_unit', 'currency']:
            self.assertIsNotNone(price.get(k))

        params = self.valid_aws_family_params.copy()
        params['os_type'] = 'Windows'
        code, res = self.client.get_family_prices(**params)
        self.assertEqual(code, 200)
        self.assertEqual(len(res.get('prices', [])), 1)
        for p in res.get('prices'):
            self.assertTrue(p['instance_type'] in ['t3.medium'])
        params['instance_family'] = 't4'
        code, res = self.client.get_family_prices(**params)
        self.assertEqual(code, 200)
        self.assertEqual(len(res.get('prices', [])), 2)
        for p in res.get('prices'):
            self.assertTrue(p['instance_type'] in ['t4.medium', 't4.large'])
