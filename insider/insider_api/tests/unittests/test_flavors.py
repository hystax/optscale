import uuid
from unittest.mock import patch
from datetime import datetime
import mongomock
import insider_client.client as insider_client
from insider_api.tests.unittests.test_api_base import TestBase


class TestFlavorsApi(TestBase):
    def setUp(self):
        self.valid_params = {
            'cloud_type': 'aws_cnr',
            'resource_type': 'instance',
            'cpu': 2,
            'region': 'test',
            'mode': 'search_no_relevant',
            'family_specs': {'source_flavor_id': 't4.small'},
        }
        self.find_aws_flavor = patch(
            'insider_api.controllers.flavor.'
            'FlavorController.find_aws_flavor',
            return_value=('eu-central-1', 't2.small', 'eu-central-1a', [])
        ).start()
        self.find_azure_flavor = patch(
            'insider_api.controllers.flavor.'
            'FlavorController.find_azure_flavor',
            return_value=('eu-central-1', 't2.small', 'eu-central-1a', [])
        )
        self.find_azure_flavor.start()
        self.alibaba_rds_params = {
              "cloud_type": "alibaba_cnr",
              "cpu": 1,
              "family_specs": {
                  "zone_id": "",
                  "category": "",
                  "engine": "",
                  "engine_version": "",
                  "storage_type": "",
                  "source_flavor_id": "",
              },
              "region": "test",
              "resource_type": "rds_instance",
              "mode": "search_no_relevant",
        }
        self.find_alibaba_flavor = patch(
            'insider_api.controllers.flavor.'
            'FlavorController.find_alibaba_flavor',
            return_value=('eu-central-1', 't2.small', 'eu-central-1a', [])
        ).start()
        self.find_alibaba_rds_flavor = patch(
            'insider_api.controllers.flavor.'
            'FlavorController.find_alibaba_rds_flavor',
            return_value=('eu-central-1', 't2.small', 'eu-central-1a', [])
        ).start()
        super().setUp()

    def test_invalid_parameters(self):
        for k, v in self.valid_params.items():
            body = self.valid_params.copy()
            body[k] = None
            code, resp = self.client.find_flavor(**body)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OI0011')

        body = self.valid_params.copy()
        body['cpu'] = 'asd'
        code, resp = self.client.find_flavor(**body)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OI0008')

        body = self.valid_params.copy()
        body['mode'] = 'test'
        code, resp = self.client.find_flavor(**body)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OI0008')

        body = self.alibaba_rds_params.copy()
        body['family_specs']['invalid_param'] = 'ecs.t5-c1m1.xlarge'
        code, resp = self.client.find_flavor(**body)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OI0014')

        body['resource_type'] = 'instance'
        code, resp = self.client.find_flavor(**body)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OI0014')

        body = self.valid_params.copy()
        body['preinstalled'] = 3
        code, resp = self.client.find_flavor(**body)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OI0008')

        # preinstalled param can be used only for aws_cnr cloud
        body = self.valid_params.copy()
        body['cloud_type'] = 'azure_cnr'
        body['preinstalled'] = 'NA'
        code, resp = self.client.find_flavor(**body)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OI0016')

    def test_flavors_bad_secret(self):
        http_provider = insider_client.FetchMethodHttpProvider(
            self.fetch, rethrow=False, secret='123')
        client = insider_client.Client(http_provider=http_provider)
        code, resp = client.find_flavor(**self.valid_params)
        self.assertEqual(code, 403)
        self.verify_error_code(resp, 'OI0005')

    def test_flavors_no_secret(self):
        http_provider = insider_client.FetchMethodHttpProvider(
            self.fetch, rethrow=False)
        client = insider_client.Client(http_provider=http_provider)
        code, resp = client.find_flavor(**self.valid_params)
        self.assertEqual(code, 401)
        self.verify_error_code(resp, 'OI0007')

    def test_not_supported_cloud(self):
        self.valid_params['cloud_type'] = 'test'
        code, resp = self.client.find_flavor(**self.valid_params)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OI0010')

    def test_valid_params(self):
        code, _ = self.client.find_flavor(**self.valid_params)
        self.assertEqual(code, 200)

        self.valid_params['family_specs'] = {'source_flavor_id': 't4.small'}
        code, _ = self.client.find_flavor(**self.valid_params)
        self.assertEqual(code, 200)

        self.valid_params['relevant'] = True
        code, _ = self.client.find_flavor(**self.valid_params)
        self.assertEqual(code, 200)

        code, _ = self.client.find_flavor(**self.alibaba_rds_params)
        self.assertEqual(code, 200)

        self.alibaba_rds_params['family_specs'] = {
            'source_flavor_id': 'ecs.t5-c1m1.xlarge'}
        self.alibaba_rds_params['resource_type'] = 'instance'
        code, _ = self.client.find_flavor(**self.alibaba_rds_params)
        self.assertEqual(code, 200)

    def test_gcp(self):
        gcp = patch("insider_api.controllers.flavor.FlavorController.gcp").start()
        gcp.get_instance_types_priced.return_value = {
            "e2-micro": {
                "cpu_cores": 2,
                "family": "e2",
                "price": 0.052426890000000004,
                "ram_gb": 1.0,
            },
            "e2-small": {
                "cpu_cores": 2,
                "family": "e2",
                "price": 0.05571888,
                "ram_gb": 2.0,
            },
            "e2-standard-16": {
                "cpu_cores": 16,
                "family": "e2",
                "price": 0.60376656,
                "ram_gb": 64.0,
            },
        }
        gcp.get_instance_types_priced.__name__ = "get_instance_types_priced"
        gcp_params = {
            "cloud_type": "gcp_cnr",
            "resource_type": "instance",
            "cpu": 2,
            "region": "test",
            "mode": "current",
            "family_specs": {"source_flavor_id": "e2-small"},
        }
        code, resp = self.client.find_flavor(**gcp_params)
        self.assertEqual(code, 200)
        self.assertEqual(resp, {
                "cpu": 2,
                "flavor": "e2-small",
                "price": 0.05571888,
                "ram": 2.0,
            })

        gcp_params = {
            "cloud_type": "gcp_cnr",
            "resource_type": "instance",
            "cpu": 16,
            "region": "test",
            "mode": "search_relevant",
            "family_specs": {"source_flavor_id": "e2-small"},
        }
        code, resp = self.client.find_flavor(**gcp_params)
        self.assertEqual(code, 200)
        self.assertEqual(resp, {
                "cpu": 16,
                "flavor": "e2-standard-16",
                "price": 0.60376656,
                "ram": 64.0,
            })

    def test_find_azure_flavor_currency(self):
        code, resp = self.client.find_flavor(
            currency=0, **self.valid_params)
        self.assertEqual(code, 400)

        code, resp = self.client.find_flavor(
            currency='BRL', **self.valid_params)

    def test_cloud_account_id(self):
        params = self.valid_params.copy()
        params['cloud_account_id'] = '123'
        code, _ = self.client.find_flavor(**params)
        self.assertEqual(code, 200)

    def patch_nebius(self):
        platforms = {'s1': {'name': 'Intel Cascade Lake',
                            'core_fraction': {
                                '20': [{
                                    'cpu': [2, 4],
                                    'ram_per_core': [1, 2]
                                }],
                                '100': [{
                                    'cpu': [2, 4],
                                    'ram_per_core': [1, 2]
                                }]}},
                     's2': {'name': 'Intel Ice Lake',
                            'core_fraction': {
                                '20': [{
                                    'cpu': [2, 4],
                                    'ram_per_core': [1, 2]
                                }],
                                '100': [{
                                    'cpu': [2, 4],
                                    'ram_per_core': [1, 2]
                                }]}}
                     }
        patch(
            "insider_api.controllers.flavor.FlavorController.get_cloud_account",
            return_value={
                'type': 'nebius',
                'config': {'platforms': platforms}
            }).start()
        nebius = patch(
            "insider_api.controllers.flavor.FlavorController.nebius").start()
        nebius.get_prices.return_value = [
            {
                'id': '1',
                'name': 'Intel Cascade Lake. 100% vCPU',
                'pricingVersions': [{
                    'pricingExpressions': [{'rates': [{'unitPrice': 0.5}]}]
                }]
            },
            {
                'id': '2',
                'name': 'Intel Cascade Lake. 20% vCPU',
                'pricingVersions': [{
                    'pricingExpressions': [{'rates': [{'unitPrice': 1.1}]}]
                }]
            },
            {
                'id': '3',
                'name': 'Intel Cascade Lake. 20% vCPU - preemptible instances',
                'pricingVersions': [{
                    'pricingExpressions': [{'rates': [{'unitPrice': 0.001}]}]
                }]
            },
            {
                'id': '4',
                'name': 'Intel Ice Lake. 20% vCPU',
                'pricingVersions': [{
                    'pricingExpressions': [{'rates': [{'unitPrice': 11}]}]
                }]
            },
        ]
        nebius.get_prices.__name__ = "get_prices"

    def test_nebius(self):
        self.patch_nebius()
        nebius_params = {
            "cloud_type": "nebius",
            "resource_type": "instance",
            "cpu": 2,
            "region": "test_region",
            "mode": "current",
            "family_specs": {"source_flavor_id": "Intel Cascade Lake",
                             "ram": 4,
                             "cpu_fraction": 20},
        }
        code, resp = self.client.find_flavor(**nebius_params)
        self.assertEqual(code, 200)
        self.assertDictEqual(resp, {
                "cpu": 2,
                "flavor": "Intel Cascade Lake",
                "price": 2.2,  # 2 cores * price
                "ram": 4,
            })

        # not supported cpu
        nebius_params = {
            "cloud_type": "nebius",
            "resource_type": "instance",
            "cpu": 1,
            "region": "test",
            "mode": "current",
            "family_specs": {"source_flavor_id": "Intel Cascade Lake",
                             "ram": 4,
                             "cpu_fraction": 20},
        }
        code, resp = self.client.find_flavor(**nebius_params)
        self.assertEqual(code, 200)
        self.assertEqual(resp, {})

        # not supported source_flavor_id
        nebius_params = {
            "cloud_type": "nebius",
            "resource_type": "instance",
            "cpu": 2,
            "region": "test",
            "mode": "current",
            "family_specs": {"source_flavor_id": "Intel",
                             "ram": 4,
                             "cpu_fraction": 20},
        }
        code, resp = self.client.find_flavor(**nebius_params)
        self.assertEqual(code, 200)
        self.assertEqual(resp, {})

    def test_nebius_optional_region(self):
        self.patch_nebius()
        nebius_params = {
            "cloud_type": "nebius",
            "resource_type": "instance",
            "cpu": 2,
            "region": None,
            "mode": "current",
            "family_specs": {"source_flavor_id": "Intel Cascade Lake",
                             "ram": 4,
                             "cpu_fraction": 20},
        }
        code, _ = self.client.find_flavor(**nebius_params)
        self.assertEqual(code, 200)
