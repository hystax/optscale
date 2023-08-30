import uuid
from unittest.mock import patch

from rest_api.rest_api_server.tests.unittests.test_api_base import TestApiBase


class TestLimitHitsApi(TestApiBase):

    def setUp(self, version='v2'):
        super().setUp(version)

        _, self.org = self.client.organization_create({'name': "partner"})
        _, pool = self.client.pool_update(self.org['id'], {'limit': 20})
        self.org_id = self.org['id']
        self.auth_user_1 = self.gen_id()
        _, self.employee = self.client.employee_create(
            self.org_id, {'name': 'employee',
                          'auth_user_id': self.auth_user_1})
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
        code, self.cloud_acc = self.create_cloud_account(self.org_id, self.valid_aws_creds,
                                                         auth_user_id=self.auth_user_1)
        self.cloud_acc_id = self.cloud_acc['id']

    def test_list(self):
        # create checklist
        code, res = self.client.checklist_list()
        self.assertEqual(code, 200)
        self.assertEqual(len(res['checklists']), 1)
        self.assertEqual(res['checklists'][0]['organization_id'], self.org_id)

        # reuse existing checklist
        code, res = self.client.checklist_list()
        self.assertEqual(code, 200)
        self.assertEqual(len(res['checklists']), 1)
        self.assertEqual(res['checklists'][0]['organization_id'], self.org_id)

    def test_patch(self):
        code, res = self.client.checklist_list()
        self.assertEqual(code, 200)
        base_checklist = res['checklists'][0]

        patch_val = 123
        for param in ['next_run', 'last_run', 'last_completed']:
            code, res = self.client.checklist_update(
                base_checklist['id'], {param: patch_val})
            self.assertEqual(code, 200)
            self.assertEqual(base_checklist['id'], res['id'])
            self.assertEqual(res[param], patch_val)

    def test_patch_unexpected_args(self):
        code, res = self.client.checklist_list()
        self.assertEqual(code, 200)
        base_checklist = res['checklists'][0]

        code, res = self.client.checklist_update(
            base_checklist['id'], {'previous_run': 123})
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0212')

    def test_patch_wrong_args(self):
        code, res = self.client.checklist_list()
        self.assertEqual(code, 200)
        base_checklist = res['checklists'][0]

        for param in ['next_run', 'last_run', 'last_completed']:
            code, res = self.client.checklist_update(
                base_checklist['id'], {param: -1})
            self.assertEqual(code, 400)
            self.assertEqual(res['error']['error_code'], 'OE0224')

            code, res = self.client.checklist_update(
                base_checklist['id'], {param: 'string_value'})
            self.assertEqual(code, 400)
            self.assertEqual(res['error']['error_code'], 'OE0223')

            code, res = self.client.checklist_update(
                base_checklist['id'], {param: 123456789123456789})
            self.assertEqual(code, 400)
            self.assertEqual(res['error']['error_code'], 'OE0224')

    def test_patch_organization(self):
        code, res = self.client.checklist_list()
        self.assertEqual(code, 200)
        base_checklist = res['checklists'][0]

        code, res = self.client.checklist_update(
            base_checklist['id'], {'organization_id': str(uuid.uuid4())})
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0212')

    def test_checklist_deleted_organization(self):
        patch('rest_api.rest_api_server.controllers.employee.'
              'EmployeeController.delete').start()
        code, res = self.client.checklist_list()
        self.assertEqual(code, 200)
        base_checklist = res['checklists'][0]
        self.assertEqual(base_checklist['organization_id'], self.org_id)
        self.client.organization_delete(self.org_id)
        code, res = self.client.checklist_list()
        self.assertEqual(code, 200)
        self.assertEqual(len(res['checklists']), 0)

    def test_create_delete_checklist_on_list(self):
        _, org = self.client.organization_create({'name': "org1"})
        code, res = self.client.checklist_list()
        self.assertEqual(code, 200)
        self.assertEqual(len(res['checklists']), 1)
        self.assertEqual(res['checklists'][0]['organization_id'], self.org_id)

        auth_user = self.gen_id()
        _, self.employee = self.client.employee_create(
            org['id'], {'name': 'employee', 'auth_user_id': auth_user})
        code, cloud_acc = self.create_cloud_account(
            org['id'], self.valid_aws_creds, auth_user_id=auth_user)
        self.assertEqual(code, 201)

        code, res = self.client.checklist_list()
        self.assertEqual(code, 200)
        self.assertEqual(len(res['checklists']), 2)

        code, _ = self.client.cloud_account_delete(cloud_acc['id'])
        self.assertEqual(code, 204)

        code, res = self.client.checklist_list()
        self.assertEqual(code, 200)
        self.assertEqual(len(res['checklists']), 1)
        self.assertEqual(res['checklists'][0]['organization_id'], self.org_id)
