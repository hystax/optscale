from rest_api_server.tests.unittests.test_api_base import TestApiBase


class TestCloudHealthApi(TestApiBase):

    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.org = self.client.organization_create({'name': "organization"})
        self.org_id = self.org['id']

    def test_result_found(self):
        health_result = {'test_key': 'test_value'}
        self.mongo_client.restapi.health.insert_one({
            'organization_id': self.org_id,
            'created_at': 1,
            'health': health_result
        })
        code, result = self.client.cloud_health_get(self.org_id)
        self.assertEqual(code, 200)
        self.assertEqual(result, health_result)

    def test_result_not_found(self):
        code, result = self.client.cloud_health_get(self.org_id)
        self.assertEqual(code, 424)
        self.verify_error_code(result, 'OE0458')
