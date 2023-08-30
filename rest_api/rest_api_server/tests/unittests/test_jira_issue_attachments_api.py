import uuid
from unittest.mock import patch
from rest_api.rest_api_server.tests.unittests.test_api_base import TestApiBase


class TestJiraIssueAttachmentsApi(TestApiBase):
    def setUp(self, version='v2'):
        super().setUp(version)
        patch('rest_api.rest_api_server.controllers.shareable_resource.'
              'ShareableBookingController.publish_task').start()
        patch('rest_api.rest_api_server.handlers.v2.jira_issue_attachments.'
              'JiraIssueAttachmentItemHandler.check_cluster_secret',
              return_value=False).start()
        _, self.organization = self.client.organization_create({
            'name': 'test organization'})
        self.organization_id = self.organization['id']
        self.auth_user = self.gen_id()
        _, self.employee = self.client.employee_create(
            self.organization['id'], {'name': 'employee',
                                      'auth_user_id': self.auth_user})
        _, self.pool = self.client.pool_create(self.organization_id, {
            'name': 'sub', 'parent_id': self.organization['pool_id']
        })
        self.pool_id = self.pool['id']
        self.auth_user_2 = self.gen_id()
        _, self.employee_2 = self.client.employee_create(
            self.organization['id'], {'name': 'employee_2',
                                      'auth_user_id': self.auth_user_2})
        patch('rest_api.rest_api_server.controllers.cloud_account.'
              'CloudAccountController._configure_report').start()
        self.cloud_acc_dict = {
            'name': 'my cloud_acc',
            'type': 'aws_cnr',
            'config': {
                'access_key_id': 'key',
                'secret_access_key': 'secret',
                'bucket_name': 'name',
                'config_scheme': 'create_report',
            }
        }
        self._mock_auth_user(self.auth_user)
        self.user = {
            'id': self.auth_user,
            'display_name': 'default',
            'email': 'email@email.com',
        }
        patch('rest_api.rest_api_server.handlers.v1.base.BaseAuthHandler._get_user_info',
              return_value=self.user).start()
        code, self.cloud_acc = self.create_cloud_account(
            self.organization_id, self.cloud_acc_dict,
            auth_user_id=self.auth_user)
        user_roles = [{
            "user_id": self.auth_user,
            "role_purpose": 'optscale_manager'
        }]
        self.p_get_roles_info = patch(
            'rest_api.rest_api_server.handlers.v1.base.BaseAuthHandler.get_roles_info',
            return_value=user_roles).start()

        self.resource_id = self._create_resource()['id']
        _, self.shareable_booking = self.client.shareable_book_create(
            self.organization_id, {
                'resource_id': self.resource_id,
                'acquired_by_id': self.employee['id']
            }
        )
        self.attachment_params = {
            'shareable_booking_id': self.shareable_booking['id'],
            'client_key': 'test_client', 'project_key': 'test_project',
            'issue_number': 123, 'issue_link': 'test_link', 'status': 'ok'
        }

    def _create_resource(self, employee_id=None, pool_id=None,
                         is_shareable=True, resource_type='Instance',
                         tags=None):
        if not employee_id:
            employee_id = self.employee['id']
        if not pool_id:
            pool_id = self.pool_id
        resource = {
            'cloud_resource_id': str(uuid.uuid4()),
            'name': 'resource',
            'resource_type': resource_type,
            'employee_id': employee_id,
            'region': 'us-west-1',
            'pool_id': pool_id
        }
        if tags:
            resource['tags'] = tags
        code, created_res = self.cloud_resource_create(self.cloud_acc['id'],
                                                       resource)
        if is_shareable:
            resource_id = created_res['id']
            self.resources_collection.update_one(
                filter={
                    '_id': resource_id
                },
                update={'$set': {
                    'shareable': True}}
            )
            created_res['shareable'] = True
        return created_res

    def test_create_jira_attachment(self):
        code, attachment = self.client.jira_issue_attachment_create(
            self.organization_id, self.attachment_params)
        self.assertEqual(code, 201)
        self.assertTrue(all(item in attachment.items()
                            for item in self.attachment_params.items()))
        self.assertIsNone(attachment['auto_detach_status'])

    def test_list_attachments(self):
        code, attachment = self.client.jira_issue_attachment_create(
            self.organization_id, self.attachment_params)
        code, resp = self.client.jira_issue_attachment_list(
            self.organization_id,
            client_key=self.attachment_params['client_key'],
            project_key=self.attachment_params['project_key'],
            issue_number=self.attachment_params['issue_number']
        )
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['jira_issue_attachments']), 1)
        self.assertEqual(resp['jira_issue_attachments'][0]['id'],
                         attachment['id'])

        code, resp = self.client.jira_issue_attachment_list(
            self.organization_id,
            client_key='another',
            project_key=self.attachment_params['project_key'],
            issue_number=self.attachment_params['issue_number']
        )
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['jira_issue_attachments']), 0)

    def test_patch_attachment(self):
        code, attachment = self.client.jira_issue_attachment_create(
            self.organization_id, self.attachment_params)
        upd_params = {'auto_detach_status': 'some', 'status': 'another'}
        code, resp = self.client.jira_issue_attachment_update(
            attachment['id'], upd_params)
        self.assertEqual(code, 200)
        self.assertTrue(all(p in resp.items() for p in upd_params.items()))

        upd_params = {'auto_detach_status': None}
        code, resp = self.client.jira_issue_attachment_update(
            attachment['id'], upd_params)
        self.assertEqual(code, 200)
        self.assertIsNone(resp['auto_detach_status'])

    def test_delete_attachment(self):
        code, attachment = self.client.jira_issue_attachment_create(
            self.organization_id, self.attachment_params)
        code, resp = self.client.jira_issue_attachment_delete(
            attachment['id'])
        self.assertEqual(code, 204)
        self.assertIsNone(resp)

    def test_list_empty(self):
        code, attachment = self.client.jira_issue_attachment_create(
            self.organization_id, self.attachment_params)
        code, resp = self.client.jira_issue_attachment_delete(
            attachment['id'])
        self.assertEqual(code, 204)
        code, resp = self.client.jira_issue_attachment_list(
            self.organization_id,
            client_key=self.attachment_params['client_key'],
            project_key=self.attachment_params['project_key'],
            issue_number=self.attachment_params['issue_number']
        )
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['jira_issue_attachments']), 0)

    def test_delete_not_existing(self):
        code, resp = self.client.jira_issue_attachment_delete(
            str(uuid.uuid4()))
        self.assertEqual(code, 404)
        self.verify_error_code(resp, 'OE0002')

    def test_patch_not_existing(self):
        code, attachment = self.client.jira_issue_attachment_create(
            self.organization_id, self.attachment_params)
        code, _ = self.client.jira_issue_attachment_delete(
            attachment['id'])
        self.assertEqual(code, 204)
        upd_params = {'auto_detach_status': 'some', 'status': 'another'}
        code, resp = self.client.jira_issue_attachment_update(
            attachment['id'], upd_params)
        self.assertEqual(code, 404)
        self.verify_error_code(resp, 'OE0002')

    def test_create_duplicate(self):
        code, _ = self.client.jira_issue_attachment_create(
            self.organization_id, self.attachment_params)
        self.assertEqual(code, 201)
        code, resp = self.client.jira_issue_attachment_create(
            self.organization_id, self.attachment_params)
        self.assertEqual(code, 409)
        self.verify_error_code(resp, 'OE0502')

    def test_create_invalid_parameters(self):
        params = self.attachment_params.copy()
        params['shareable_booking_id'] = str(uuid.uuid4())
        code, resp = self.client.jira_issue_attachment_create(
            self.organization_id, params)
        self.assertEqual(code, 404)
        self.verify_error_code(resp, 'OE0002')
        for k_str in ['client_key', 'project_key', 'status']:
            params = self.attachment_params.copy()
            params[k_str] = 123
            code, resp = self.client.jira_issue_attachment_create(
                self.organization_id, params)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0214')
            params[k_str] = ''
            code, resp = self.client.jira_issue_attachment_create(
                self.organization_id, params)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0215')
        params = self.attachment_params.copy()
        params['issue_number'] = 'asd'
        code, resp = self.client.jira_issue_attachment_create(
            self.organization_id, params)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0223')

    def test_create_not_provided(self):
        for k in self.attachment_params.keys():
            params = self.attachment_params.copy()
            params.pop(k)
            code, resp = self.client.jira_issue_attachment_create(
                self.organization_id, params)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0216')

    def test_unexpected_params(self):
        for k in ['deleted_at', 'unexpected']:
            params = self.attachment_params.copy()
            params[k] = 'test'
            code, resp = self.client.jira_issue_attachment_create(
                self.organization_id, params)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0212')
        code, attachment = self.client.jira_issue_attachment_create(
            self.organization_id, self.attachment_params)
        self.assertEqual(code, 201)
        for k in ['id', 'deleted_at', 'created_at', 'shareable_booking_id',
                  'client_key', 'project_key', 'issue_number', 'issue_link']:
            code, resp = self.client.jira_issue_attachment_update(
                attachment['id'], {k: 'test'})
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0211')
        code, resp = self.client.jira_issue_attachment_update(
            attachment['id'], {'not_ex': 'test'})
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0212')

    def test_create_for_another_user(self):
        self._mock_auth_user(str(uuid.uuid4()))
        code, resp = self.client.jira_issue_attachment_create(
            self.organization_id, self.attachment_params)
        self.assertEqual(code, 403)
        self.verify_error_code(resp, 'OE0378')

    def test_permissions_for_another_user(self):
        code, attachment = self.client.jira_issue_attachment_create(
            self.organization_id, self.attachment_params)
        self.assertEqual(code, 201)

        self._mock_auth_user(self.auth_user_2)
        code, resp = self.client.jira_issue_attachment_update(
            attachment['id'], {'status': 'test'})
        self.assertEqual(code, 403)
        self.verify_error_code(resp, 'OE0501')

        code, resp = self.client.jira_issue_attachment_delete(
            attachment['id'])
        self.assertEqual(code, 403)
        self.verify_error_code(resp, 'OE0501')

        code, resp = self.client.jira_issue_attachment_list(
            self.organization_id,
            client_key=self.attachment_params['client_key'],
            project_key=self.attachment_params['project_key'],
            issue_number=self.attachment_params['issue_number']
        )
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['jira_issue_attachments']), 1)
        self.assertEqual(resp['jira_issue_attachments'][0]['id'],
                         attachment['id'])

    def test_autodetach_status(self):
        self.attachment_params['auto_detach_status'] = 'Done'
        code, attachment = self.client.jira_issue_attachment_create(
            self.organization_id, self.attachment_params)
        self.assertEqual(code, 201)

        code, _ = self.client.jira_issue_attachment_update(
            attachment['id'], {'status': 'test'})
        self.assertEqual(code, 200)
        code, resp = self.client.jira_issue_attachment_list(
            self.organization_id,
            client_key=self.attachment_params['client_key'],
            project_key=self.attachment_params['project_key'],
            issue_number=self.attachment_params['issue_number']
        )
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['jira_issue_attachments']), 1)
        self.assertEqual(resp['jira_issue_attachments'][0]['id'],
                         attachment['id'])

        code, _ = self.client.jira_issue_attachment_update(
            attachment['id'], {'status': 'Done'})
        self.assertEqual(code, 200)
        code, resp = self.client.jira_issue_attachment_list(
            self.organization_id,
            client_key=self.attachment_params['client_key'],
            project_key=self.attachment_params['project_key'],
            issue_number=self.attachment_params['issue_number']
        )
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['jira_issue_attachments']), 0)
