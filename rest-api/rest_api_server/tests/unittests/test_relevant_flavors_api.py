import uuid
from unittest.mock import patch
from rest_api_server.tests.unittests.test_api_base import TestApiBase


class TestRelevantFlavorsApi(TestApiBase):

    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.org = self.client.organization_create({'name': "organization"})

    def test_invalid_region(self):
        code, resp = self.client.get_relevant_flavors(
            self.org['id'], 'ss')
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0217')

    def test_invalid_cloud_type(self):
        code, resp = self.client.get_relevant_flavors(
            self.org['id'], 'af', cloud_type='ss')
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0436')

        code, resp = self.client.get_relevant_flavors(
            self.org['id'], 'af', cloud_type=['aws_cnr', 'ss'])
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0436')

    def test_invalid_params(self):
        for p in ['min_cpu', 'max_cpu', 'min_ram', 'max_ram']:
            body = {p: 'test'}
            code, resp = self.client.get_relevant_flavors(
                self.org['id'], 'af', cloud_type='aws_cnr', **body)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0217')

    def test_missed_region(self):
        code, resp = self.client.get_relevant_flavors(
            self.org['id'], None)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0216')

    def test_invalid_filters(self):
        code, resp = self.client.get_relevant_flavors(
            self.org['id'], 'me', min_cpu=4, max_cpu=2)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0446')

        code, resp = self.client.get_relevant_flavors(
            self.org['id'], 'me', min_ram=4, max_ram=2)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0446')

    def test_not_existing_organization(self):
        code, resp = self.client.get_relevant_flavors(
            str(uuid.uuid4()), 'af', cloud_type='aws_cnr')
        self.assertEqual(code, 404)
        self.verify_error_code(resp, 'OE0002')

    def test_grouping(self):
        relevant_flavors = [
            {'nebius': [
                {'cpu': 2, 'memory': 2, 'cost': 1, 'name': 'nebius1',
                 'location': 'l1'},
                {'cpu': 2, 'memory': 4, 'cost': 2, 'name': 'nebius2',
                 'location': 'l1'},
                {'cpu': 1, 'memory': 2, 'cost': 2, 'name': 'nebius3',
                 'location': 'l1'}
            ]},
            {'azure_cnr': [
                {'cpu': 2, 'memory': 4, 'name': 'azure1', 'location': 'l1',
                 'cost': 1},
                {'cpu': 2, 'memory': 4, 'name': 'azure2', 'location': 'l2',
                 'cost': 2},
            ]},
            {'aws_cnr': [
                {'cpu': 2, 'memory': 4, 'name': 'aws2', 'location': 'l2',
                 'cost': 2},
                {'cpu': 2, 'memory': 2, 'name': 'aws1', 'location': 'l1',
                 'cost': 1},
            ]},
        ]
        patch('rest_api_server.controllers.relevant_flavor.'
              'RelevantFlavorController.get_relevant_flavors',
              return_value=(relevant_flavors, [])).start()
        code, resp = self.client.get_relevant_flavors(
            self.org['id'], 'af', cloud_type=['aws_cnr', 'azure_cnr'])
        self.assertEqual(code, 200)
        expected_result = {
            'flavors': [
                {
                    'cpu': 1,
                    'ram': 2,
                    'nebius': [
                        {'cost': 2, 'name': 'nebius3', 'location': 'l1'}
                    ],
                },
                {
                    'cpu': 2,
                    'ram': 2,
                    'nebius': [
                        {'cost': 1, 'name': 'nebius1', 'location': 'l1'}
                    ],
                    'aws_cnr': [
                        {'name': 'aws1', 'location': 'l1', 'cost': 1}
                    ]
                },
                {
                    'cpu': 2,
                    'ram': 4,
                    'nebius': [
                        {'cost': 2, 'name': 'nebius2', 'location': 'l1'}
                    ],
                    'azure_cnr': [
                        {'name': 'azure1', 'location': 'l1', 'cost': 1},
                        {'name': 'azure2', 'location': 'l2', 'cost': 2}
                    ],
                    'aws_cnr': [
                        {'name': 'aws2', 'location': 'l2', 'cost': 2}
                    ]
                }
            ],
            'errors': []
        }
        self.assertEqual(resp, expected_result)
