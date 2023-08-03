import os
from datetime import datetime
from unittest.mock import patch, PropertyMock
from insider_api.tests.unittests.test_api_base import TestBase
from botocore.exceptions import ClientError


class TestRelevantFlavorsApi(TestBase):
    def setUp(self):
        os.environ['ASYNC_TEST_TIMEOUT'] = '30'
        self.azure_cad = patch(
            'insider_api.controllers.relevant_flavor.'
            'AzureProvider.cloud_adapter').start()
        self.aws_cad = patch(
            'insider_api.controllers.relevant_flavor.'
            'AwsProvider.cloud_adapter').start()
        self.nebius_cad = patch(
            'insider_api.controllers.relevant_flavor.'
            'NebiusProvider.cloud_adapter').start()
        super().setUp()
        patch('insider_api.controllers.relevant_flavor.BaseProvider.mongo_client',
              new_callable=PropertyMock, return_value=self.mongo_client
              ).start()

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
                'location': 'US West',
                'skuId': 'DZH318Z0BQ4C/01C7',
                'isPrimaryMeterRegion': False,
                'serviceName': 'Virtual Machines',
                'meterName': 'DS2 v2',
                'last_seen': ts,
                'productName': 'Virtual Machines DSv2 Series',
                'serviceId': 'DZH313Z7MMC8',
                'currencyCode': 'USD',
                'skuName': 'DS2 v2',
                'armSkuName': 'Standard_B1s',
                'armRegionName': 'westus',
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
                'unitPrice': 1.15,
                'meterId': 'd5a81ebd-6435-4b0f-9ab1-6c0d0dd6eed0',
                'location': 'US West 2',
                'skuId': 'DZH318Z0BQ4C/01C7',
                'isPrimaryMeterRegion': False,
                'serviceName': 'Virtual Machines',
                'meterName': 'DS2 v2',
                'last_seen': ts,
                'productName': 'Virtual Machines DSv2 Series',
                'serviceId': 'DZH313Z7MMC8',
                'currencyCode': 'USD',
                'skuName': 'DS2 v2',
                'armSkuName': 'Standard_B4s',
                'armRegionName': 'westus2',
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
                'location': 'UK South',
                'skuId': 'DZH318Z0BQ4C/01C7',
                'isPrimaryMeterRegion': False,
                'serviceName': 'Virtual Machines',
                'meterName': 'DS2 v2',
                'last_seen': ts - 100500,
                'productName': 'Virtual Machines DSv2 Series',
                'serviceId': 'DZH313Z7MMC8',
                'currencyCode': 'USD',
                'skuName': 'DS2 v2',
                'armSkuName': 'Standard_B1s',
                'armRegionName': 'uksouth',
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
                'armSkuName': 'Standard_B1s',
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

    def test_invalid_region(self):
        code, resp = self.client.get_relevant_flavors('aws_cnr', 'ss')
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OI0012')

    def test_invalid_cloud_type(self):
        code, resp = self.client.get_relevant_flavors('invalid', 'af')
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OI0010')

    def test_invalid_params(self):
        for p in ['min_cpu', 'max_cpu', 'min_ram', 'max_ram']:
            body = {p: 'test'}
            code, resp = self.client.get_relevant_flavors(
                'aws_cnr', 'af', **body)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OI0008')

    def test_missed_region(self):
        code, resp = self.client.get_relevant_flavors(
            'aws_cnr', None)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OI0011')

    def test_azure_flavors(self):
        self.azure_cad.location_map = {
            'westus': 'West US', 'westus2': 'West US 2', 'uksouth': 'UK South'
        }
        self.azure_cad.get_flavors_info.return_value = {
            'Standard_B1s': {
                'vcpus': 1, 'name': 'Standard_B1s', 'ram': 1024,
                'family': 'family1'
            },
            'Standard_B4s': {
                'vcpus': 4, 'name': 'Standard_B4s', 'ram': 8192,
                'family': 'family2'
            }
        }
        self.insert_azure_pricing(int(datetime.utcnow().timestamp()))
        code, resp = self.client.get_relevant_flavors('azure_cnr', 'us')
        self.assertEqual(resp, {
            'azure_cnr': [
                {'cpu': 1, 'memory': 1.0,
                 'instance_family': 'Virtual Machines DSv2 Series',
                 'name': 'Standard_B1s', 'location': 'US West',
                 'cost': 0.14, 'currency': 'USD'},
                {'cpu': 4, 'memory': 8.0, 'instance_family':
                    'Virtual Machines DSv2 Series', 'name': 'Standard_B4s',
                 'location': 'US West 2', 'cost': 1.15, 'currency': 'USD'}
            ]
        })

        code, resp = self.client.get_relevant_flavors(
            'azure_cnr', 'us', min_cpu=8)
        self.assertEqual(code, 200)
        self.assertEqual(resp, {'azure_cnr': []})

        code, resp = self.client.get_relevant_flavors(
            'azure_cnr', 'me')
        self.assertEqual(code, 200)
        self.assertEqual(resp, {'azure_cnr': []})

        code, resp = self.client.get_relevant_flavors(
            'azure_cnr', 'us', max_ram=6)
        self.assertEqual(code, 200)
        self.assertEqual(resp, {
            'azure_cnr': [
                {'cpu': 1, 'memory': 1.0,
                 'instance_family': 'Virtual Machines DSv2 Series',
                 'name': 'Standard_B1s', 'location': 'US West', 'cost': 0.14,
                 'currency': 'USD'}
            ]})

    def test_aws_flavors(self):
        self.aws_cad.list_regions.return_value = ['us-east-1']
        self.aws_cad.get_prices.return_value = [
            {'memory': '8 GiB', 'vcpu': '2', 'locationType': 'AWS Region',
             'instanceFamily': 'General purpose', 'operatingSystem': 'Linux',
             'regionCode': 'us-east-1', 'instanceType': 'm2a.16xlarge',
             'location': 'US East (N. Virginia)',
             'price': {'USD': '2.9190000000'},
             'sku': '24HHMFHS8G927VDR'},
            {'memory': '4 GiB', 'vcpu': '1', 'locationType': 'AWS Region',
             'instanceFamily': 'General purpose', 'operatingSystem': 'Linux',
             'regionCode': 'us-east-1', 'instanceType': 'm4a.16xlarge',
             'location': 'US East (N. Virginia)',
             'price': {'USD': '2.9190000000'},
             'sku': '24HHMFHS8G927VDR'}
        ]
        code, resp = self.client.get_relevant_flavors(
            'aws_cnr', 'af')
        self.assertEqual(code, 200)
        self.assertEqual(resp, {'aws_cnr': []})

        code, resp = self.client.get_relevant_flavors(
            'aws_cnr', 'us')
        self.assertEqual(code, 200)
        self.assertEqual(resp, {'aws_cnr': [
            {'cost': '2.9190000000', 'cpu': 2, 'currency': 'USD',
             'instance_family': 'General purpose',
             'location': 'US East (N. Virginia)', 'memory': 8.0,
             'name': 'm2a.16xlarge'},
            {'cost': '2.9190000000', 'cpu': 1, 'currency': 'USD',
             'instance_family': 'General purpose',
             'location': 'US East (N. Virginia)', 'memory': 4.0,
             'name': 'm4a.16xlarge'}
        ]})
        code, resp = self.client.get_relevant_flavors(
            'aws_cnr', 'us', min_cpu=2)
        self.assertEqual(code, 200)
        self.assertEqual(resp, {'aws_cnr': [
            {'cost': '2.9190000000', 'cpu': 2, 'currency': 'USD',
             'instance_family': 'General purpose',
             'location': 'US East (N. Virginia)', 'memory': 8.0,
             'name': 'm2a.16xlarge'}
        ]})

    def test_nebius_flavors(self):
        self.nebius_cad.get_prices.return_value = [
            {'id': 'dihk3vqlk9snp1jv351u', 'name': 'Intel Ice Lake. 100% vCPU',
             'serviceId': 'dih2pas77ftg9h3f2djj', 'pricingUnit': 'core*hour',
             'pricingVersions': [{'type': 'STREET_PRICE',
                                  'effectiveTime': '2022-06-07T21:00:00Z',
                                  'pricingExpressions': [{'rates': [
                                      {'startPricingQuantity': '0',
                                       'unitPrice': '2',
                                       'currency': 'USD'}]}]},
                                 ]},
            {'id': 'dihf0q0d6gtpcom4b1p6', 'name': 'Intel Ice Lake. 50% vCPU',
             'serviceId': 'dih2pas77ftg9h3f2djj', 'pricingUnit': 'core*hour',
             'pricingVersions': [{'type': 'STREET_PRICE',
                                  'effectiveTime': '2022-06-07T21:00:00Z',
                                  'pricingExpressions': [{'rates': [
                                      {'startPricingQuantity': '0',
                                       'unitPrice': '0.001',
                                       'currency': 'USD'}]}]},
                                 ]},
            {'id': 'dihilq72mjc3bej6j74p', 'name': 'Intel Ice Lake. RAM',
             'serviceId': 'dih2pas77ftg9h3f2djj', 'pricingUnit': 'gbyte*hour',
             'pricingVersions': [{'type': 'STREET_PRICE',
                                  'effectiveTime': '2022-06-07T21:00:00Z',
                                  'pricingExpressions': [{'rates': [
                                      {'startPricingQuantity': '0',
                                       'unitPrice': '1',
                                       'currency': 'USD'}]}]},
                                 ]},
            {'id': 'dihfh95rpff4gf6ejhnu',
             'name': 'MySQL. Intel Ice Lake. RAM, committed usage for 1 year',
             'serviceId': 'dih8hpu626uudbq0j8mk', 'pricingUnit': 'gbyte*hour',
             'pricingVersions': [{'type': 'STREET_PRICE',
                                  'effectiveTime': '2022-06-07T21:00:00Z',
                                  'pricingExpressions': [{'rates': [
                                      {'startPricingQuantity': '0',
                                       'unitPrice': '0.004',
                                       'currency': 'USD'}]}]}]}
        ]
        code, resp = self.client.get_relevant_flavors('nebius', 'us')
        self.assertEqual(code, 200)

        code, resp = self.client.get_relevant_flavors(
            'nebius', 'me', min_cpu=4, max_cpu=8, max_ram=12)
        self.assertEqual(code, 200)
        self.assertEqual(resp, {
            'nebius': [
                {'cpu': 4, 'memory': 4, 'cost': 12.0, 'currency': 'USD',
                 'name': 'Intel Ice Lake', 'instance_family': 'standard-v3',
                 'location': 'Israel'},
                {'cpu': 4, 'memory': 8, 'cost': 16.0, 'currency': 'USD',
                 'name': 'Intel Ice Lake', 'instance_family': 'standard-v3',
                 'location': 'Israel'},
                {'cpu': 4, 'memory': 12, 'cost': 20.0, 'currency': 'USD',
                 'name': 'Intel Ice Lake', 'instance_family': 'standard-v3',
                 'location': 'Israel'},
                {'cpu': 6, 'memory': 6, 'cost': 18.0, 'currency': 'USD',
                 'name': 'Intel Ice Lake', 'instance_family': 'standard-v3',
                 'location': 'Israel'},
                {'cpu': 6, 'memory': 12, 'cost': 24.0, 'currency': 'USD',
                 'name': 'Intel Ice Lake', 'instance_family': 'standard-v3',
                 'location': 'Israel'},
                {'cpu': 8, 'memory': 8, 'cost': 24.0, 'currency': 'USD',
                 'name': 'Intel Ice Lake', 'instance_family': 'standard-v3',
                 'location': 'Israel'},
            ]
        })

    def test_credentials_exception(self):
        error_message = 'test message'
        patch('insider_api.controllers.relevant_flavor.'
              'AwsProvider.cloud_adapter.list_regions',
              side_effect=ClientError(
                  {'Error': {'Message': error_message}}, '')).start()
        code, resp = self.client.get_relevant_flavors('aws_cnr', 'us')
        self.assertEqual(code, 401)
        self.verify_error_code(resp, 'OI0019')
        self.assertEqual(resp['error']['reason'],
                         'Invalid credentials: %s' % error_message)
