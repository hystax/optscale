from unittest.mock import patch
import optscale_client.insider_client.client as insider_client
from insider.insider_api.tests.unittests.test_api_base import TestBase


class TestInstancesApi(TestBase):
    def setUp(self):
        self.required_params = {
            'cloud_type': 'aws_cnr',
            'flavor': 'a1.2xlarge',
            'min_duration': 31536000,
            'max_duration': 31536000,
        }
        return_value = [{
            'scope': 'Region', 'offering_class': 'standard',
            'offering_type': 'All Upfront', 'fixed_price': 1199.0,
            'recurring_charges': [{'Amount': 0.0, 'Frequency': 'Hourly'}]}]
        self.find_reserved_instances = patch(
            'insider.insider_api.controllers.instance.'
            'InstanceController.find_reserved_instances',
            return_value=return_value
        ).start()
        super().setUp()

    def test_valid_params(self):
        code, resp = self.client.find_reserved_instances_offerings(
            **self.required_params)
        self.assertEqual(code, 200)

    def test_unexpected_parameters(self):
        body = self.required_params.copy()
        body['unexpected'] = 'param'
        code, resp = self.client.find_reserved_instances_offerings(**body)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OI0014')

    def test_flavors_bad_secret(self):
        http_provider = insider_client.FetchMethodHttpProvider(
            self.fetch, rethrow=False, secret='123')
        client = insider_client.Client(http_provider=http_provider)
        code, resp = client.find_reserved_instances_offerings(**self.required_params)
        self.assertEqual(code, 403)
        self.verify_error_code(resp, 'OI0005')

    def test_invalid_parameters(self):
        for k, v in self.required_params.items():
            body = self.required_params.copy()
            body[k] = None
            code, resp = self.client.find_reserved_instances_offerings(**body)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OI0011')

        body = self.required_params.copy()
        body['product_description'] = 123
        code, resp = self.client.find_reserved_instances_offerings(**body)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OI0008')

        body = self.required_params.copy()
        body['tenancy'] = 453
        code, resp = self.client.find_reserved_instances_offerings(**body)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OI0008')

        body = self.required_params.copy()
        body['flavor'] = False
        code, resp = self.client.find_reserved_instances_offerings(**body)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OI0008')

        body = self.required_params.copy()
        body['min_duration'] = 'test'
        code, resp = self.client.find_reserved_instances_offerings(**body)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OI0008')

        body = self.required_params.copy()
        body['max_duration'] = 'test'
        code, resp = self.client.find_reserved_instances_offerings(**body)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OI0008')

        body = self.required_params.copy()
        body['include_marketplace'] = 'test'
        code, resp = self.client.find_reserved_instances_offerings(**body)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OI0008')

        body = self.required_params.copy()
        body['currency'] = 123
        code, resp = self.client.find_reserved_instances_offerings(**body)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OI0008')

        body = self.required_params.copy()
        body['cloud_account_id'] = 123
        code, resp = self.client.find_reserved_instances_offerings(**body)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OI0008')

    def test_optional_params(self):
        body = self.required_params.copy()
        for param, value in [('currency', 'USD'), ('tenancy', 'dedicated'),
                             ('include_marketplace', False),
                             ('cloud_account_id', 'account_id'),
                             ('product_description', 'Linux')]:
            body[param] = value
            code, resp = self.client.find_reserved_instances_offerings(**body)
            self.assertEqual(code, 200)

    def test_cloud_required_params(self):
        body = self.required_params.copy()
        body['cloud_type'] = 'aws_cnr'
        code, resp = self.client.find_reserved_instances_offerings(**body)
        self.assertEqual(code, 200)

        body['cloud_type'] = 'nebius'
        code, resp = self.client.find_reserved_instances_offerings(**body)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OI0011')
