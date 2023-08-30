from unittest.mock import patch

from rest_api.rest_api_server.tests.unittests.test_api_base import TestApiBase


class TestCleanupScriptsApi(TestApiBase):

    def setUp(self, version='v2'):
        super().setUp(version)

        _, self.org = self.client.organization_create({'name': "partner"})
        self.org_id = self.org['id']
        self.valid_aws_creds = {
            'name': 'my creds',
            'type': 'aws_cnr',
            'config': {
                'access_key_id': 'key',
                'secret_access_key': 'secret',
                'config_scheme': 'create_report'
            }
        }
        patch('tools.cloud_adapter.clouds.aws.Aws.configure_report').start()
        patch('tools.cloud_adapter.clouds.aws.Aws.validate_credentials',
              return_value={'account_id': '1', 'warnings': []}).start()
        patch('tools.cloud_adapter.clouds.azure.Azure.configure_report').start()
        self.auth_user_1 = self.gen_id()
        _, self.employee = self.client.employee_create(
            self.org_id, {'name': 'employee',
                          'auth_user_id': self.auth_user_1})
        code, self.aws = self.create_cloud_account(
            self.org_id, self.valid_aws_creds, auth_user_id=self.auth_user_1)
        self.cloud_acc_aws_id = self.aws['id']

        self.valid_azure_cloud_acc = {
            'name': 'azure cloud_acc',
            'type': 'azure_cnr',
            'config': {
                'subscription_id': 'id',
                'secret': 'secret',
                'client_id': 'id',
                'tenant': 't'
            }
        }
        code, cloud_acc_azure = self.create_cloud_account(
            self.org_id, self.valid_azure_cloud_acc)
        self.assertEqual(code, 201)
        self.cloud_acc_azure_id = cloud_acc_azure['id']

    def test_script_get(self):
        code, script = self.client.get_cleanup_script(self.cloud_acc_aws_id,
                                                      'obsolete_images')
        self.assertEqual(code, 200)
        self.assertIn(self.cloud_acc_aws_id, script)

    def test_script_get_invalid_cloud(self):
        code, resp = self.client.get_cleanup_script(self.gen_id(),
                                                    'obsolete_images')
        self.assertEqual(code, 404)
        self.verify_error_code(resp, 'OE0002')

    def test_script_get_invalid_module(self):
        code, resp = self.client.get_cleanup_script(self.cloud_acc_aws_id,
                                                    'fakemodulename')
        self.assertEqual(code, 404)
        self.verify_error_code(resp, 'OE0002')

    def test_script_get_invalid_cloud_type(self):
        code, resp = self.client.get_cleanup_script(self.cloud_acc_azure_id,
                                                    'obsolete_images')
        self.assertEqual(code, 404)
        self.verify_error_code(resp, 'OE0002')
