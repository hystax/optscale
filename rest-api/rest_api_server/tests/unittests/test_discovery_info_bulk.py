import uuid
from unittest.mock import patch
from rest_api_server.tests.unittests.test_api_base import TestApiBase


class TestDiscoveryInfoBulk(TestApiBase):
    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.org = self.client.organization_create(
            {'name': "partner_test"})
        self.valid_aws_creds = {
            'name': 'my creds',
            'type': 'aws_cnr',
            'config': {
                'access_key_id': 'key',
                'secret_access_key': 'secret',
                'config_scheme': 'create_report'
            }
        }
        self.org_id = self.org['id']
        self.user_id = self.gen_id()
        self.valid_employee = {
            'name': 'Eliot Alterson', 'auth_user_id': self.user_id
        }
        _, self.employee = self.client.employee_create(
            self.org_id, self.valid_employee)
        patch('rest_api_server.controllers.cloud_account.'
              'CloudAccountController._configure_report').start()
        _, cloud_account = self.create_cloud_account(
            self.org_id, self.valid_aws_creds, update_discovery_info=False,
            auth_user_id=self.user_id)
        self.cloud_acc_id = cloud_account['id']
        self.valid_discovery_params = [{
            "enabled": True,
            "resource_type": "k8s_pod"
        }]

    def test_create_discovery_info(self):
        valid_aws_creds = self.valid_aws_creds.copy()
        valid_aws_creds['name'] = 'new_creds'
        _, cloud_account = self.create_cloud_account(
            self.org_id, valid_aws_creds, update_discovery_info=False)
        code, res = self.client.discovery_info_create_bulk(
            cloud_account['id'], {'discovery_info': self.valid_discovery_params})
        self.assertEqual(code, 200)

    def test_create_existing_discovery_info(self):
        valid_aws_creds = self.valid_aws_creds.copy()
        valid_aws_creds['name'] = 'new_creds'
        _, cloud_account = self.create_cloud_account(
            self.org_id, valid_aws_creds, update_discovery_info=False)
        params = [{
            "enabled": True,
            "resource_type": "instance"
        }]
        code, res = self.client.discovery_info_create_bulk(
            cloud_account['id'], {'discovery_info': params})
        self.assertEqual(code, 409)
        self.assertEqual(res['error']['error_code'], 'OE0518')

    def test_create_invalid_cloud_account(self):
        code, res = self.client.discovery_info_create_bulk(
            'str', {'discovery_info': self.valid_discovery_params})
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0217')

    def test_create_discovery_info_not_provided(self):
        code, res = self.client.discovery_info_create_bulk(
            self.cloud_acc_id, {})
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0216')

    def test_create_invalid_discovery_info(self):
        code, res = self.client.discovery_info_create_bulk(
            self.cloud_acc_id, {'discovery_info': 123})
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0385')

    def test_create_disabled(self):
        params = self.valid_discovery_params.copy()
        params[0]['enabled'] = False
        code, res = self.client.discovery_info_create_bulk(
            self.cloud_acc_id, {'discovery_info': params})
        self.assertEqual(code, 200)
        self.assertEqual(res['discovery_info'][0]['enabled'], False)

    def test_create_enabled_is_not_provided(self):
        params = self.valid_discovery_params.copy()
        params[0].pop('enabled', None)
        code, res = self.client.discovery_info_create_bulk(
            self.cloud_acc_id, {'discovery_info': params})
        self.assertEqual(code, 200)
        self.assertEqual(res['discovery_info'][0]['enabled'], True)

    def test_create_invalid_enabled(self):
        params = self.valid_discovery_params.copy()
        params[0]['enabled'] = 'str'
        code, res = self.client.discovery_info_create_bulk(
            self.cloud_acc_id, {'discovery_info': params})
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0226')

    def test_create_resource_type_is_not_provided(self):
        params = self.valid_discovery_params.copy()
        params[0].pop('resource_type', None)
        code, res = self.client.discovery_info_create_bulk(
            self.cloud_acc_id, {'discovery_info': params})
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0216')

    def test_create_invalid_resource_type(self):
        params = self.valid_discovery_params.copy()
        params[0]['resource_type'] = 'str'
        code, res = self.client.discovery_info_create_bulk(
            self.cloud_acc_id, {'discovery_info': params})
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0384')

    def test_create_invalid_body(self):
        code, res = self.client.discovery_info_create_bulk(
            self.cloud_acc_id, self.valid_discovery_params)
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0233')

    def test_create_immutable(self):
        for f in ['created_at', 'deleted_at', 'last_error_at', 'last_error',
                  'last_discovery_at', 'id']:
            params = self.valid_discovery_params.copy()
            params[0][f] = '123'
            code, res = self.client.discovery_info_create_bulk(
                self.cloud_acc_id, {'discovery_info': params})
            self.assertEqual(code, 400)
            self.assertEqual(res['error']['error_code'], 'OE0211')

    def test_create_unexpected(self):
        params = self.valid_discovery_params.copy()
        params[0]['123'] = '123'
        code, res = self.client.discovery_info_create_bulk(
            self.cloud_acc_id, {'discovery_info': params})
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0212')

    def test_delete_discovery_info(self):
        valid_aws_creds = self.valid_aws_creds.copy()
        valid_aws_creds['name'] = 'new_creds'
        _, cloud_account = self.create_cloud_account(
            self.org_id, valid_aws_creds, update_discovery_info=False)
        _, res = self.client.discovery_info_list(self.cloud_acc_id)
        di_info_id = res['discovery_info'][0]['id']

        code, res = self.client.discovery_info_delete_bulk(
            self.cloud_acc_id, [di_info_id])
        self.assertEqual(code, 204)

    def test_delete_not_existing_cloud_acc(self):
        valid_aws_creds = self.valid_aws_creds.copy()
        valid_aws_creds['name'] = 'new_creds'
        _, cloud_account = self.create_cloud_account(
            self.org_id, valid_aws_creds, update_discovery_info=False)
        _, res = self.client.discovery_info_list(self.cloud_acc_id)
        di_info_id = res['discovery_info'][0]['id']

        code, res = self.client.discovery_info_delete_bulk(
            str(uuid.uuid4()), [di_info_id])
        self.assertEqual(code, 404)
        self.assertEqual(res['error']['error_code'], 'OE0002')

    def test_delete_empty_list(self):
        code, res = self.client.discovery_info_delete_bulk(
            self.cloud_acc_id, [])
        self.assertEqual(code, 204)

    def test_delete_invalid_body(self):
        url = self.client.discovery_info_bulk_url(self.cloud_acc_id)
        code, res = self.client.delete(url, self.valid_discovery_params)
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0233')

    def test_delete_without_discovery_info(self):
        url = self.client.discovery_info_bulk_url(self.cloud_acc_id)
        code, res = self.client.delete(url, {})
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0216')

    def test_delete_invalid_discovery_info_id_type(self):
        for x in [123, {}, []]:
            code, res = self.client.discovery_info_delete_bulk(
                self.cloud_acc_id, [x])
            self.assertEqual(code, 400)
            self.assertEqual(res['error']['error_code'], 'OE0218')

    def test_not_allowed(self):
        url = self.client.discovery_info_bulk_url(str(uuid.uuid4()))
        code, _ = self.client.patch(url, {})
        self.assertEqual(code, 405)

        code, _ = self.client.get(url, {})
        self.assertEqual(code, 405)
