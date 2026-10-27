import os
from unittest.mock import patch
from rest_api.rest_api_server.tests.unittests.test_api_base import TestApiBase

EXT_ID = 'my-unique-id'


class TestCloudPolicyGeneratorApi(TestApiBase):

    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.org = self.client.organization_create({'name': "organization"})
        self.org_id = self.org['id']
        patch('rest_api.rest_api_server.controllers.policy_gen.PolicyGeneratorController.'
              'get_aws_account_id',
              return_value=5555555555555551).start()

    def test_generate_policy_ok(self):
        code, result = self.client.cloud_policy_get(self.org_id, "aws_cnr",
                                                    "test", external_id=EXT_ID)
        self.assertEqual(code, 200)
        self.assertTrue(result.get("role_policy", {}).get("Statement"))
        # 6 statements in the regular role policy
        self.assertEqual(len(result.get("role_policy", {}).get("Statement")),
                         6)
        self.assertTrue(result.get("trust_policy", {}).get("Statement"))

    def test_generate_policy_linked_ok(self):
        code, result = self.client.cloud_policy_get(
            self.org_id, "aws_cnr", linked=True, bucket_name=None,
            external_id=EXT_ID)
        self.assertEqual(code, 200)
        self.assertTrue(result.get("role_policy", {}).get("Statement"))
        # 3 statements in the linked role policy
        self.assertEqual(len(result.get("role_policy", {}).get("Statement")),
                         3)
        self.assertTrue(result.get("trust_policy", {}).get("Statement"))

    def test_invalid_cloud(self):
        code, result = self.client.cloud_policy_get(self.org_id, "invalid",
                                                    "test", external_id=EXT_ID)
        self.assertEqual(code, 400)
        self.assertEqual(result["error"]["error_code"], "OE0436")

    def test_missing_cloud_type(self):
        url = self.client.cloud_policy_url(self.org_id) + self.client.query_url(
            bucket_name="test", external_id=EXT_ID
        )
        code, result = self.client.get(url)
        self.assertEqual(code, 400)
        self.assertEqual(result["error"]["error_code"], "OE0548")

    def test_missing_bucket_non_linked(self):
        url = self.client.cloud_policy_url(self.org_id) + self.client.query_url(
            cloud_type="aws_cnr", external_id=EXT_ID
        )
        code, result = self.client.get(url)
        self.assertEqual(code, 400)
        self.assertEqual(result["error"]["error_code"], "OE0548")

    def test_unexpected_arg(self):
        url = self.client.cloud_policy_url(self.org_id) + self.client.query_url(
            cloud_type="aws_cnr", bucket_name="my_bucket",
            external_id=EXT_ID, unexpected="test"
        )
        code, result = self.client.get(url)
        self.assertEqual(code, 400)
        self.assertEqual(result["error"]["error_code"], "OE0212")

    def test_bucket_provided_for_linked_acc(self):
        url = self.client.cloud_policy_url(self.org_id) + self.client.query_url(
            cloud_type="aws_cnr", bucket_name="test",
            external_id=EXT_ID, linked=True,
        )
        code, result = self.client.get(url)
        self.assertEqual(code, 400)
        self.assertEqual(result["error"]["error_code"], "OE0212")

    def test_generate_policy_without_external_id(self):
        code, resp = self.client.cloud_policy_get(
            self.org_id, "aws_cnr", linked=True, bucket_name=None)
        self.assertEqual(code, 200)
        self.assertTrue(resp.get("trust_policy", {}).get("Statement"))
        statement = resp["trust_policy"]["Statement"][0]
        self.assertNotIn("Condition", statement)

    def test_generate_policy_invalid_external_id(self):
        for value in ['x', 'a' * 1225]:
            url = self.client.cloud_policy_url(self.org_id) + \
                self.client.query_url(
                    cloud_type='aws_cnr', bucket_name='test',
                    external_id=value)
            code, resp = self.client.get(url)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0215')
        for value in ['bad value!', 'bad$value']:
            url = self.client.cloud_policy_url(self.org_id) + \
                self.client.query_url(
                    cloud_type='aws_cnr', bucket_name='test',
                    external_id=value)
            code, resp = self.client.get(url)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0218')

    def test_generate_policy_external_id_in_trust_policy(self):
        code, resp = self.client.cloud_policy_get(
            self.org_id, "aws_cnr", bucket_name="test", external_id=EXT_ID)
        self.assertEqual(code, 200)
        statement = resp.get("trust_policy", {}).get("Statement", [{}])[0]
        self.assertEqual(
            statement.get("Condition", {}).get(
                "StringEquals", {}).get("sts:ExternalId"),
            EXT_ID,
        )
