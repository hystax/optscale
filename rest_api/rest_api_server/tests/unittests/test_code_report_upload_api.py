from rest_api.rest_api_server.tests.unittests.test_api_base import TestApiBase
from unittest.mock import patch


class TestReportImportsApi(TestApiBase):

    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.org = self.client.organization_create(
            {'name': "organization"})
        self.org_id = self.org['id']
        patch('rest_api.rest_api_server.controllers.code_report_upload.'
              'CodeReportFileController.s3_client').start()
        patch('rest_api.rest_api_server.controllers.code_report_upload.'
              'CodeReportFileController.s3_client.'
              'create_multipart_upload').start()
        patch('rest_api.rest_api_server.controllers.code_report_upload.'
              'CodeReportFileController.s3_client.'
              'complete_multipart_upload').start()
        patch('rest_api.rest_api_server.handlers.v2.code_report_uploads.'
              'CodeReportAsyncHandler.check_file').start()

    def test_upload(self):
        code, data = self.client.post(
            self.client.code_report_upload_url(self.org_id), body={})
        self.assertEqual(code, 204)

    def test_upload_invalid_org(self):
        code, deleted_org = self.client.organization_create(
            {'name': 'deleted_org'})
        self.assertEqual(code, 201)
        self.delete_organization(deleted_org['id'])

        org_ids = ['impostor', deleted_org['id']]
        for org_id in org_ids:
            code, data = self.client.post(
                self.client.code_report_upload_url(org_id), {})
            self.assertEqual(code, 404)
            self.assertEqual(data['error']['error_code'], 'OE0002')
