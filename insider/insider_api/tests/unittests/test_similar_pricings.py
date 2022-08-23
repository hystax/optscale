import uuid
from datetime import datetime
import insider_client.client as insider_client
from insider_api.tests.unittests.test_api_base import TestBase


class TestSimilarPricingsAPI(TestBase):
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
        pricings = [{
            'meterId': 'e39695b9-bcf3-465a-ab67-4527699a34c6',
            'unitOfMeasure': '1 Hour', 'retailPrice': 0.19,
            'type': 'Consumption', 'serviceFamily': 'Compute',
            'effectiveStartDate': '2019-10-16T00:00:00Z',
            'skuName': 'A3 Spot', 'location': 'UK North',
            'meterName': 'A3 Spot', 'skuId': 'DZH318Z0BPVJ/018M',
            'serviceName': 'Virtual Machines',
            'productName': 'Virtual Machines A Series Windows',
            'currencyCode': 'USD', 'unitPrice': 0.19,
            'serviceId': 'DZH313Z7MMC8', 'created_at': 1608907516,
            'armSkuName': 'Standard_A3', 'isPrimaryMeterRegion': True,
            'armRegionName': 'southcentralus', 'tierMinimumUnits': 0.0,
            'productId': 'DZH318Z0BPVJ'
        }, {
            'meterId': '001caea7-ff8a-5957-8480-7f1121cc1976',
            'unitOfMeasure': '1 Hour', 'retailPrice': 0.043704,
            'type': 'Consumption', 'serviceFamily': 'Compute',
            'effectiveStartDate': '2021-01-01T00:00:00Z',
            'skuName': 'A3 Spot', 'location': 'US Central',
            'meterName': 'A3 Spot', 'skuId': 'DZH318Z0BPVJ/017Q',
            'serviceName': 'Virtual Machines',
            'effectiveEndDate': '2020-12-31T23:59:00Z',
            'productName': 'Virtual Machines A Series Windows',
            'currencyCode': 'USD', 'unitPrice': 0.043704,
            'serviceId': 'DZH313Z7MMC8', 'created_at': 1608907516,
            'armSkuName': 'Standard_A3', 'isPrimaryMeterRegion': True,
            'armRegionName': 'centralus', 'tierMinimumUnits': 0.0,
            'productId': 'DZH318Z0BPVJ'
        }, {
            'productName': 'Virtual Machines Dv2 promo Series',
            'created_at': 1608907516, 'meterName': 'D14 v2/DS14 v2 - Expired',
            'meterId': '0008a792-d49f-4f13-a461-9c9f24e92ccf',
            'serviceId': 'DZH313Z7MMC8', 'location': 'US North Central',
            'skuId': 'DZH318Z0BPSP/001D', 'serviceName': 'Virtual Machines',
            'isPrimaryMeterRegion': True, 'retailPrice': 1.482,
            'unitOfMeasure': '1 Hour', 'currencyCode': 'USD',
            'armSkuName': 'Standard_D14_v2_Promo', 'skuName': 'D14 v2',
            'effectiveStartDate': '2018-09-01T00:00:00Z', 'unitPrice': 1.482,
            'tierMinimumUnits': 0.0, 'type': 'Consumption',
            'serviceFamily': 'Compute', 'productId': 'DZH318Z0BPSP',
            'armRegionName': 'northcentralus'
        }]
        for i, p in enumerate(pricings):
            p['last_seen'] = d_time + i
            self.mongo_client.insider.azure_prices.insert_one(p)
        return pricings

    def test_similar_pricings_without_discovery(self):
        code, resp = self.client.get_similar_pricings('azure_cnr',
                                                      str(uuid.uuid4()))
        self.assertEqual(code, 404)
        self.verify_error_code(resp, 'OI0009')

    def test_similar_pricings_not_supported_cloud(self):
        code, resp = self.client.get_similar_pricings('some_cloud',
                                                      str(uuid.uuid4()))
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OI0010')

    def test_similar_pricings_without_secret(self):
        http_provider = insider_client.FetchMethodHttpProvider(
            self.fetch, rethrow=False)
        client = insider_client.Client(http_provider=http_provider)
        code, resp = client.get_similar_pricings(
            'azure_cnr', str(uuid.uuid4()))
        self.assertEqual(code, 401)
        self.verify_error_code(resp, 'OI0007')

    def test_similar_pricings_bad_secret(self):
        http_provider = insider_client.FetchMethodHttpProvider(
            self.fetch, rethrow=False, secret='123')
        client = insider_client.Client(http_provider=http_provider)
        code, resp = client.get_similar_pricings(
            'azure_cnr', str(uuid.uuid4()))
        self.assertEqual(code, 403)
        self.verify_error_code(resp, 'OI0005')

    def test_similar_pricings(self):
        pricings = self._discovery()
        code, resp = self.client.get_similar_pricings(
            'azure_cnr', pricings[0]['meterId'])
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['similar_prices']), 2)
        for p in resp['similar_prices']:
            self.assertTrue(p['meterId'] in [
                pricings[0]['meterId'], pricings[1]['meterId']
            ])

        code, resp = self.client.get_similar_pricings(
            'azure_cnr', pricings[2]['meterId'])
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['similar_prices']), 1)

    def test_similar_pricings_fake_id(self):
        self._discovery()
        code, resp = self.client.get_similar_pricings(
            'azure_cnr', str(uuid.uuid4()))
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['similar_prices']), 0)

    def test_private_region(self):
        pricings = self._discovery()
        private_meter_id = 'ba97ea7b-f85a-44f0-b6f2-ffffe1f136cb'
        code, resp = self.client.get_similar_pricings(
            'azure_cnr', pricings[0]['meterId'])
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['similar_prices']), 2)
        pr = {
            'meterId': private_meter_id,
            'unitOfMeasure': '1 Hour', 'retailPrice': 0.19,
            'type': 'Consumption', 'serviceFamily': 'Compute',
            'effectiveStartDate': '2019-10-16T00:00:00Z',
            'skuName': 'A3 Spot', 'location': 'UK North',
            'meterName': 'A3 Spot', 'skuId': 'DZH318Z0BPVJ/018M',
            'serviceName': 'Virtual Machines',
            'productName': 'Virtual Machines A Series Windows',
            'currencyCode': 'USD', 'unitPrice': 0.19,
            'serviceId': 'DZH313Z7MMC8', 'created_at': 1608907516,
            'armSkuName': 'Standard_A3', 'isPrimaryMeterRegion': True,
            'armRegionName': 'uknorth', 'tierMinimumUnits': 0.0,
            'productId': 'DZH318Z0BPVJ',
            'last_seen': int(datetime.utcnow().timestamp())
        }
        self.mongo_client.insider.azure_prices.insert_one(pr)
        code, resp = self.client.get_similar_pricings(
            'azure_cnr', pricings[0]['meterId'])
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['similar_prices']), 2)
        for p in resp['similar_prices']:
            self.assertNotEqual(p['meterId'], private_meter_id)
