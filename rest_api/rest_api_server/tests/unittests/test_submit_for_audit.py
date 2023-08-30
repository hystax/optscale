from rest_api.rest_api_server.tests.unittests.test_api_base import TestApiBase
from unittest.mock import ANY, patch, call


class TestReportImportsApi(TestApiBase):

    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.org = self.client.organization_create(
            {'name': "organization"})
        self.org_id = self.org['id']
        self.auth_user = self.gen_id()
        _, self.employee = self.client.employee_create(
            self.org_id, {'name': 'employee',
                          'auth_user_id': self.auth_user})
        patch('rest_api.rest_api_server.controllers.base.BaseController.'
              'get_user_id', return_value=self.auth_user).start()
        patch('rest_api.rest_api_server.controllers.base.'
              'BaseController.publish_activities_task').start()

    def test_service_email_send(self):
        p_email_send = self.mock_email_send_enable()
        code, _ = self.client.submit_for_audit(self.org_id)
        self.assertEqual(code, 204)
        p_email_send.assert_called_once_with(
            ANY, ANY, template_type='organization_audit_submit',
            template_params=ANY)

    def test_event_created(self):
        patch('rest_api.rest_api_server.controllers.submit_for_audit.'
              'AuditSubmitController.send_submit_audit_service_email').start()
        p_activities_publish = patch(
            'rest_api.rest_api_server.controllers.base.'
            'BaseController.publish_activities_task').start()
        code, _ = self.client.submit_for_audit(self.org_id)
        self.assertEqual(code, 204)
        p_activities_publish.assert_has_calls([
            call(self.org_id, self.org_id, 'organization',
                 'technical_audit_submit', ANY,
                 'organization.technical_audit_submit', add_token=True)])

    def test_submit_invalid_org(self):
        code, deleted_org = self.client.organization_create(
            {'name': 'deleted_org'})
        self.assertEqual(code, 201)
        self.delete_organization(deleted_org['id'])

        org_ids = ['impostor', deleted_org['id']]
        for org_id in org_ids:
            code, data = self.client.submit_for_audit(org_id)
            self.assertEqual(code, 404)
            self.assertEqual(data['error']['error_code'], 'OE0002')
