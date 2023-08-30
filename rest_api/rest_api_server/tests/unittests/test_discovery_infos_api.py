import uuid
from datetime import datetime
from unittest.mock import patch

from tools.cloud_adapter.model import ResourceTypes
from rest_api.rest_api_server.tests.unittests.test_api_base import TestApiBase


class TestDiscoveryInfo(TestApiBase):
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
        patch('rest_api.rest_api_server.controllers.cloud_account.'
              'CloudAccountController._configure_report').start()
        _, cloud_account = self.create_cloud_account(
            self.org_id, self.valid_aws_creds, update_discovery_info=False,
            auth_user_id=self.user_id)
        self.cloud_acc_id = cloud_account['id']
        self.valid_discovery_params = {
            "enabled": True,
            "resource_type": "k8s_pod"
        }

    def test_list_discovery_info(self):
        valid_aws_creds = self.valid_aws_creds.copy()
        valid_aws_creds['name'] = 'new_creds'
        _, cloud_account = self.create_cloud_account(
            self.org_id, valid_aws_creds, update_discovery_info=False)
        code, res = self.client.discovery_info_list(cloud_account['id'])
        self.assertEqual(code, 200)
        # aws discovers 5 types of resources (images not included)
        self.assertEqual(5, len(res.get('discovery_info')))
        for di_info in res['discovery_info']:
            self.assertEqual(di_info['last_discovery_at'], 0)
            self.assertEqual(di_info['last_error_at'], 0)
            self.assertEqual(di_info['observe_time'], 0)
            self.assertEqual(di_info['last_error'], None)

    def test_list_discovery_info_filtered(self):
        for res_type in [ResourceTypes.instance, ResourceTypes.volume,
                         ResourceTypes.snapshot, ResourceTypes.bucket,
                         ResourceTypes.ip_address]:
            code, res = self.client.discovery_info_list(
                self.cloud_acc_id, resource_type=res_type.name)
            self.assertEqual(code, 200)
            self.assertEqual(1, len(res.get('discovery_info')))
            self.assertEqual(
                res_type.name, res['discovery_info'][0]['resource_type'])

    def test_list_discovery_info_nonexistent_cloud_acc(self):
        code, res = self.client.discovery_info_list(str(uuid.uuid4()))
        self.assertEqual(code, 404)
        self.assertEqual(res['error']['error_code'], 'OE0002')

    def test_list_discovery_info_resource_type_not_exists_for_cloud(self):
        code, res = self.client.discovery_info_list(
            self.cloud_acc_id, resource_type=ResourceTypes.k8s_pod.name)
        self.assertEqual(code, 200)
        self.assertEqual(len(res.get('discovery_info')), 0)

    def test_list_discovery_info_deleted_cloud_acc(self):
        valid_aws_creds = self.valid_aws_creds.copy()
        valid_aws_creds['name'] = 'new_creds'
        _, cloud_account = self.create_cloud_account(
            self.org_id, valid_aws_creds, update_discovery_info=False)
        self.client.cloud_account_delete(cloud_account['id'])
        code, res = self.client.discovery_info_list(cloud_account['id'])
        self.assertEqual(code, 404)
        self.assertEqual(res['error']['error_code'], 'OE0002')

    def test_list_discovery_info_wrong_resource_type(self):
        code, res = self.client.discovery_info_list(
            self.cloud_acc_id, resource_type='cookie')
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0384')

    def test_list_discovery_info_environment(self):
        code, resource = self.client.environment_resource_create(
            self.org_id, {'name': 'res', 'resource_type': 'type'})
        self.assertEqual(code, 201)
        code, res = self.client.discovery_info_list(
            resource['cloud_account_id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(res.get('discovery_info')), 0)

    def test_update_discovery_info(self):
        _, res = self.client.discovery_info_list(self.cloud_acc_id)
        some_time = int(datetime.utcnow().timestamp())
        for di_info in res['discovery_info']:
            code, res = self.client.discovery_info_update(
                di_info['id'], {'last_discovery_at': some_time,
                                'last_error_at': 1625086800,
                                'last_error': 'Test Error Text',
                                'observe_time': 1625086700}
            )
            self.assertEqual(code, 200)
            self.assertEqual(res['last_discovery_at'], some_time)
            self.assertEqual(res['last_error_at'], 1625086800)
            self.assertEqual(res['observe_time'], 1625086700)
            self.assertEqual(res['last_error'], 'Test Error Text')

    def test_update_discovery_info_wrong_arg(self):
        _, res = self.client.discovery_info_list(self.cloud_acc_id)
        di_info_id = res['discovery_info'][0]['id']
        for val in ['not_id', str(uuid.uuid4())]:
            code, res = self.client.discovery_info_update(
                di_info_id, {'last_discovery_at': val}
            )
            self.assertEqual(code, 400)
            self.assertEqual(res['error']['error_code'], 'OE0223')

        code, res = self.client.discovery_info_update(
            di_info_id, {'last_discovery_at': -1}
        )
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0224')

    def test_update_discovery_info_cloud_acc(self):
        valid_aws_creds = self.valid_aws_creds.copy()
        valid_aws_creds['name'] = 'new_creds'
        _, cloud_account = self.create_cloud_account(
            self.org_id, valid_aws_creds, update_discovery_info=False)

        _, res = self.client.discovery_info_list(self.cloud_acc_id)
        di_info_id = res['discovery_info'][0]['id']

        code, res = self.client.discovery_info_update(
            di_info_id, {'cloud_account_id': cloud_account['id']}
        )
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0212')

    def test_update_discovery_info_nonexisting(self):
        code, res = self.client.discovery_info_update(
            str(uuid.uuid4()),
            {'last_discovery_at': int(datetime.utcnow().timestamp())}
        )
        self.assertEqual(code, 404)

    def test_disable_discovery_info(self):
        _, res = self.client.discovery_info_list(self.cloud_acc_id)
        di_info = res['discovery_info'][0]
        enabled = di_info['enabled']

        code, res = self.client.discovery_info_switch_enable(
            self.cloud_acc_id, di_info['resource_type'], not enabled
        )
        di_info['enabled'] = not di_info['enabled']
        self.assertEqual(code, 200)
        self.assertDictEqual(res, di_info)

    def test_invalid_switch_discovery_enabled(self):
        _, res = self.client.discovery_info_list(self.cloud_acc_id)
        di_info = res['discovery_info'][0]
        code, res = self.client.discovery_info_switch_enable(
            self.cloud_acc_id, None, True
        )
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0216')

        code, res = self.client.discovery_info_switch_enable(
            self.cloud_acc_id, di_info['resource_type'], None
        )
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0216')

        code, res = self.client.discovery_info_switch_enable(
            self.cloud_acc_id, 'Test', True
        )
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0384')

        code, res = self.client.discovery_info_switch_enable(
            self.cloud_acc_id, di_info['resource_type'], 'Test'
        )
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0226')

    def test_not_allowed(self):
        item_url = self.client.discovery_info_url(
            discovery_info_id=str(uuid.uuid4()))
        code, _ = self.client.post(item_url, {})
        self.assertEqual(code, 405)

        code, _ = self.client.delete(item_url, {})
        self.assertEqual(code, 405)

        code, _ = self.client.get(item_url, {})
        self.assertEqual(code, 405)

        collection_url = self.client.discovery_info_url(
            cloud_account_id=str(uuid.uuid4()))

        code, _ = self.client.post(collection_url, {})
        self.assertEqual(code, 405)

        code, _ = self.client.delete(collection_url, {})
        self.assertEqual(code, 405)

        code, _ = self.client.patch(collection_url, {})
        self.assertEqual(code, 405)
