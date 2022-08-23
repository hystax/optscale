from unittest.mock import patch
import insider_client.client as insider_client
from insider_api.tests.unittests.test_api_base import TestBase


class TestInstancesApi(TestBase):
    def setUp(self):
        self.valid_params = {
            'cloud_type': 'aws_cnr',
            'product_description': 'Linux/UNIX',
            'tenancy': 'default',
            'flavor': 'a1.2xlarge',
            'min_duration': 31536000,
            'max_duration': 31536000,
            'include_marketplace': False
        }
        return_value = [{
            'scope': 'Region', 'offering_class': 'standard',
            'offering_type': 'All Upfront', 'fixed_price': 1199.0,
            'recurring_charges': [{'Amount': 0.0, 'Frequency': 'Hourly'}]}]
        self.find_reserved_instances = patch(
            'insider_api.controllers.instance.'
            'InstanceController.find_reserved_instances',
            return_value=return_value
        ).start()
        super().setUp()

    def test_valid_params(self):
        code, _ = self.client.find_reserved_instances_offerings(
            **self.valid_params)
        self.assertEqual(code, 200)

    def test_flavors_bad_secret(self):
        http_provider = insider_client.FetchMethodHttpProvider(
            self.fetch, rethrow=False, secret='123')
        client = insider_client.Client(http_provider=http_provider)
        code, resp = client.find_reserved_instances_offerings(
            **self.valid_params)
        self.assertEqual(code, 403)
        self.verify_error_code(resp, 'OI0005')

    def test_invalid_parameters(self):
        for k, v in self.valid_params.items():
            body = self.valid_params.copy()
            body[k] = None
            code, resp = self.client.find_reserved_instances_offerings(**body)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OI0011')

        body = self.valid_params.copy()
        body['product_description'] = 123
        code, resp = self.client.find_reserved_instances_offerings(**body)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OI0008')

        body = self.valid_params.copy()
        body['tenancy'] = 453
        code, resp = self.client.find_reserved_instances_offerings(**body)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OI0008')

        body = self.valid_params.copy()
        body['flavor'] = False
        code, resp = self.client.find_reserved_instances_offerings(**body)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OI0008')

        body = self.valid_params.copy()
        body['min_duration'] = 'test'
        code, resp = self.client.find_reserved_instances_offerings(**body)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OI0008')

        body = self.valid_params.copy()
        body['max_duration'] = 'test'
        code, resp = self.client.find_reserved_instances_offerings(**body)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OI0008')

        body = self.valid_params.copy()
        body['include_marketplace'] = 'test'
        code, resp = self.client.find_reserved_instances_offerings(**body)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OI0008')
