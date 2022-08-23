from unittest.mock import patch
import insider_client.client as insider_client
from insider_api.tests.unittests.test_api_base import TestBase


class TestFlavorGenerationsApi(TestBase):
    def setUp(self):
        self.valid_params = {
            'cloud_type': 'aws_cnr',
            'region': 'test',
            "current_flavor": "t2.small",
            "os_type": "Linux"
        }
        self.find_aws_flavor_generation = patch(
            'insider_api.controllers.flavor_generation.'
            'FlavorGenerationController.find_aws_flavor_generation',
            return_value=('t3.small', 't2.small', '2.5')
        ).start()
        self.find_azure_flavor_generation = patch(
            'insider_api.controllers.flavor_generation.'
            'FlavorGenerationController.find_azure_flavor_generation',
            return_value=('Standard_A2_v2', 'Standard_A2', '3.6')
        ).start()
        self.find_alibaba_flavor_generation = patch(
            'insider_api.controllers.flavor_generation.'
            'FlavorGenerationController.find_alibaba_flavor_generation',
            return_value=('ecs.n4.large', 'ecs.n1.medium', '4.7')
        ).start()
        super().setUp()

    def test_invalid_parameters(self):
        for param in ['cloud_type', 'region', 'current_flavor']:
            body = self.valid_params.copy()
            body[param] = None
            code, resp = self.client.find_flavor_generation(**body)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OI0011')

        body = self.valid_params.copy()
        body['region'] = 1
        code, resp = self.client.find_flavor_generation(**body)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OI0008')

        body = self.valid_params.copy()
        body['current_flavor'] = 2
        code, resp = self.client.find_flavor_generation(**body)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OI0008')

        body = self.valid_params.copy()
        body['os_type'] = 3
        code, resp = self.client.find_flavor_generation(**body)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OI0008')

        body = self.valid_params.copy()
        body['preinstalled'] = 4
        code, resp = self.client.find_flavor_generation(**body)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OI0008')

        body = self.valid_params.copy()
        body['meter_id'] = 'aefe2412-a457-472a-ac3c-4f1809c60fac'
        code, resp = self.client.find_flavor_generation(**body)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OI0016')

        body = self.valid_params.copy()
        body['cloud_type'] = 'azure_cnr'
        body['meter_id'] = 5
        code, resp = self.client.find_flavor_generation(**body)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OI0008')

        body = self.valid_params.copy()
        body['preinstalled'] = 3
        code, resp = self.client.find_flavor_generation(**body)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OI0008')

        # preinstalled param can be used only for aws_cnr cloud
        body = self.valid_params.copy()
        body['cloud_type'] = 'azure_cnr'
        body['preinstalled'] = 'NA'
        code, resp = self.client.find_flavor_generation(**body)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OI0016')

    def test_flavor_generation_bad_secret(self):
        http_provider = insider_client.FetchMethodHttpProvider(
            self.fetch, rethrow=False, secret='123')
        client = insider_client.Client(http_provider=http_provider)
        code, resp = client.find_flavor_generation(**self.valid_params)
        self.assertEqual(code, 403)
        self.verify_error_code(resp, 'OI0005')

    def test_flavor_generation_no_secret(self):
        http_provider = insider_client.FetchMethodHttpProvider(
            self.fetch, rethrow=False)
        client = insider_client.Client(http_provider=http_provider)
        code, resp = client.find_flavor_generation(**self.valid_params)
        self.assertEqual(code, 401)
        self.verify_error_code(resp, 'OI0007')

    def test_not_supported_cloud(self):
        self.valid_params['cloud_type'] = 'test'
        code, resp = self.client.find_flavor_generation(**self.valid_params)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OI0010')

    def test_valid_params(self):
        code, _ = self.client.find_flavor_generation(**self.valid_params)
        self.assertEqual(code, 200)

        valid_params = self.valid_params.copy()
        valid_params['cloud_type'] = 'azure_cnr'
        valid_params['current_flavor'] = 'Standard_A2'
        valid_params['os_type'] = 'Windows'
        valid_params['meter_id'] = 'aefe2412-a457-472a-ac3c-4f1809c60fac'
        code, _ = self.client.find_flavor_generation(**self.valid_params)
        self.assertEqual(code, 200)

        valid_params = self.valid_params.copy()
        valid_params['cloud_type'] = 'alibaba_cnr'
        valid_params['current_flavor'] = 'ecs.n1.medium'
        code, _ = self.client.find_flavor_generation(**self.valid_params)
        self.assertEqual(code, 200)

        valid_params = self.valid_params.copy()
        valid_params['cloud_type'] = 'aws_cnr'
        valid_params['os_type'] = 'Linux'
        valid_params['preinstalled'] = 'NA'
        code, _ = self.client.find_flavor_generation(**self.valid_params)
        self.assertEqual(code, 200)
