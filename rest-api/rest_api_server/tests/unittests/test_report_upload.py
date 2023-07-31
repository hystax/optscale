from rest_api_server.tests.unittests.test_api_base import TestApiBase
from unittest.mock import patch


class TestReportImportsApi(TestApiBase):

    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.org = self.client.organization_create(
            {'name': "organization"})
        self.org_id = self.org['id']
        cloud_acc1 = {
            'name': 'cloud_acc1',
            'type': 'aws_cnr',
            'config': {
                'access_key_id': 'key',
                'secret_access_key': 'secret',
                'config_scheme': 'create_report'
            }
        }
        self.auth_user_id = self.gen_id()
        code, self.employee = self.client.employee_create(
            self.org_id, {'name': 'John Smith', 'auth_user_id': self.auth_user_id})
        patch('cloud_adapter.clouds.aws.Aws.configure_report').start()
        _, self.cloud_acc = self.create_cloud_account(
            self.org_id, cloud_acc1, auth_user_id=self.auth_user_id)
        patch('rest_api_server.controllers.report_import.'
              'ReportImportFileController.s3_client').start()
        patch('rest_api_server.controllers.report_import.'
              'ReportImportFileController.s3_client.'
              'create_multipart_upload').start()
        patch('rest_api_server.controllers.report_import.'
              'ReportImportFileController.s3_client.'
              'complete_multipart_upload').start()

    def test_upload(self):
        code, data = self.client.post(
            self.client.report_upload_url(self.cloud_acc['id']), body={})
        self.assertEqual(code, 201)

    def test_upload_invalid_cacc(self):
        cloud_acc2 = {
            'name': 'cloud_acc2',
            'type': 'aws_cnr',
            'config': {
                'access_key_id': 'key',
                'secret_access_key': 'secret',
                'config_scheme': 'create_report'
            }
        }
        _, deleted_acc = self.create_cloud_account(
            self.org_id, cloud_acc2, auth_user_id=self.auth_user_id)
        code, _ = self.client.cloud_account_delete(deleted_acc['id'])
        self.assertEqual(code, 204)

        acc_ids = ['impostor', deleted_acc['id']]
        for acc_id in acc_ids:
            code, data = self.client.post(
                self.client.report_upload_url(acc_id), {})
            self.assertEqual(code, 404)
            self.assertEqual(data['error']['error_code'], 'OE0002')
