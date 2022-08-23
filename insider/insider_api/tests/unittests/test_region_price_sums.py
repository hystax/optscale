import uuid
from unittest.mock import patch
from datetime import datetime
import insider_client.client as insider_client
from insider_api.tests.unittests.test_api_base import TestBase


class TestRegionPriceSumsAPI(TestBase):
    def setUp(self):
        super().setUp()
        self.core_pricing_ids = [
            '1b286734-7784-4f96-b497-d9ad9b935e99',
            '3727475e-e0c1-460b-80b0-be4ad439ba8b',
            '4d1bb254-aaf7-40e8-99d3-65a628cdd037'
        ]
        self.regions_price_map = {
            'westus': 3,
            'southcentralus': 5
        }
        # pricing_id, sku, region
        self.pricing_map = [
            (self.core_pricing_ids[0], 'sku_1', 'westus'),
            (str(uuid.uuid4()), 'sku_1', 'southcentralus'),
            (self.core_pricing_ids[1], 'sku_2', 'westus'),
            (str(uuid.uuid4()), 'sku_2', 'southcentralus'),
            (str(uuid.uuid4()), 'some', 'westus'),
        ]

    def _discovery(self):
        now = int(datetime.utcnow().timestamp())
        discoveries = [
            {
                'cloud_type': 'azure_cnr',
                'started_at': now - 100,
                'completed_at': now - 50
            },
            {
                'cloud_type': 'azure_cnr',
                'started_at': now,
                'completed_at': 0
            },
            {
                'cloud_type': 'aws_cnr',
                'started_at': now,
                'completed_at': now
            }
        ]
        for d in discoveries:
            self.mongo_client.insider.discoveries.insert_one(d)
        d_time = now - 100
        pricings = []
        for pricing_id, sku, region in self.pricing_map:
            price = self.regions_price_map[region]
            pricings.append({
                'meterId': pricing_id, 'unitPrice': price,
                'type': 'Consumption', 'skuName': sku, 'meterName': sku,
                'productName': sku, 'armRegionName': region,
                'serviceName': 'Virtual Machines', 'isPrimaryMeterRegion': True
            })
        for i, p in enumerate(pricings):
            p['last_seen'] = d_time + i
            self.mongo_client.insider.azure_prices.insert_one(p)
        return pricings

    def test_region_price_sums_without_discovery(self):
        code, resp = self.client.get_region_price_sums('azure_cnr')
        self.assertEqual(code, 404)
        self.verify_error_code(resp, 'OI0009')

    def test_region_price_sums_not_supported_cloud(self):
        code, resp = self.client.get_region_price_sums('some_cloud')
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OI0010')

    def test_region_price_sums_without_secret(self):
        http_provider = insider_client.FetchMethodHttpProvider(
            self.fetch, rethrow=False)
        client = insider_client.Client(http_provider=http_provider)
        code, resp = client.get_region_price_sums('azure_cnr')
        self.assertEqual(code, 401)
        self.verify_error_code(resp, 'OI0007')

    def test_region_price_sums_bad_secret(self):
        http_provider = insider_client.FetchMethodHttpProvider(
            self.fetch, rethrow=False, secret='123')
        client = insider_client.Client(http_provider=http_provider)
        code, resp = client.get_region_price_sums('azure_cnr')
        self.assertEqual(code, 403)
        self.verify_error_code(resp, 'OI0005')

    def test_region_price_sums(self):
        self._discovery()
        code, resp = self.client.get_region_price_sums('azure_cnr')
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['price_sums']), 2)
        for region, price in self.regions_price_map.items():
            self.assertEqual(resp['price_sums'][region], price * 2)

    def test_private_region(self):
        pricings = self._discovery()
        code, resp = self.client.get_similar_pricings(
            'azure_cnr', pricings[0]['meterId'])
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['similar_prices']), 2)
        # similar but government
        pr = {
            'meterId': self.core_pricing_ids[2], 'unitPrice': 0,
            'type': 'Consumption', 'skuName': 'some',
            'meterName': pricings[0]['meterName'],
            'productName': pricings[0]['productName'],
            'armRegionName': 'westgovtest',
            'serviceName': 'Virtual Machines'
        }
        self.mongo_client.insider.azure_prices.insert_one(pr)
        code, resp = self.client.get_region_price_sums('azure_cnr')
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['price_sums']), 2)
        self.assertFalse('westgovtest' in resp['price_sums'])

    def test_not_exists_in_region(self):
        pricings = self._discovery()
        pr = {
            'meterId': self.core_pricing_ids[2], 'unitPrice': 0,
            'type': 'Consumption', 'skuName': pricings[0]['skuName'],
            'meterName': pricings[0]['meterName'],
            'productName': pricings[0]['productName'],
            'armRegionName': 'westus2',
            'serviceName': 'Virtual Machines'
        }
        self.mongo_client.insider.azure_prices.insert_one(pr)
        code, resp = self.client.get_region_price_sums('azure_cnr')
        self.assertEqual(code, 200)
        self.assertTrue(pr['armRegionName'] not in resp['price_sums'])
