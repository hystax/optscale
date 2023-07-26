import uuid
from datetime import datetime
from unittest.mock import patch, call

from rest_api_server.models.models import Checklist
from rest_api_server.tests.unittests.test_api_base import TestApiBase
from rest_api_server.models.db_factory import DBFactory, DBType
from rest_api_server.models.db_base import BaseDB


GET_OPTIMIZATIONS_DATA = ('rest_api_server.controllers.optimization.'
                          'OptimizationController._get_optimizations_data')


class TestOptimizationsApi(TestApiBase):

    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.org = self.client.organization_create(
            {'name': "partner"})
        self.org_id = self.org['id']
        patch('rest_api_server.controllers.cloud_account.'
              'CloudAccountController._configure_report').start()

        creds = {
            'name': 'creds',
            'type': 'aws_cnr',
            'config': {
                'access_key_id': 'key',
                'secret_access_key': 'secret',
                'config_scheme': 'create_report'
            }
        }
        self.user_id = self.gen_id()
        _, self.employee = self.client.employee_create(
            self.org_id, {'name': 'name', 'auth_user_id': self.user_id})
        _, self.cloud_acc = self.create_cloud_account(
            self.org_id, creds, auth_user_id=self.user_id)

        creds2 = creds.copy()
        creds2['name'] = 'creds2'
        _, self.cloud_acc2 = self.create_cloud_account(
            self.org_id, creds2, auth_user_id=self.user_id)

        self.instance = {
            'cloud_resource_id': 'i-9323123124',
            'resource_name': 'my test instance',
            'resource_id': '58bef498-9f06-4c0f-aac0-312b22fcb9ee',
            'cloud_account_id': self.cloud_acc['id'],
            'cloud_type': self.cloud_acc['type'],
            'total_cost': 20,
            'first_seen': 1600077735,
            'last_seen': 1600078565,
            'saving': 150
        }
        self.instance2 = {
            'cloud_resource_id': 'i-8212012013',
            'resource_name': 'my another test instance',
            'resource_id': 'a4f2adbb-aae2-4355-b933-cc6730a2edca',
            'cloud_account_id': self.cloud_acc['id'],
            'cloud_type': self.cloud_acc['type'],
            'total_cost': 10,
            'first_seen': 1600077735,
            'last_seen': 1600078565,
            'saving': 140
        }

    @patch(GET_OPTIMIZATIONS_DATA)
    def test_optimization_nonexistent_organization(
            self, p_get_optimizations_data):
        p_get_optimizations_data.return_value = []
        code, res = self.client.optimizations_get(str(uuid.uuid4()))
        self.assertEqual(code, 404)

    @patch(GET_OPTIMIZATIONS_DATA)
    def test_optimization_initial(self, p_get_optimizations_data):
        p_get_optimizations_data.return_value = []
        code, res = self.client.optimizations_get(self.org_id)
        self.assertEqual(code, 200)
        self.assertEqual(res['optimizations'], {})
        self.assertEqual(res['dismissed_optimizations'], {})
        self.assertEqual(res['organization_id'], self.org_id)

    @patch(GET_OPTIMIZATIONS_DATA)
    def test_optimization(self, p_get_optimizations_data):
        _, res = self.client.optimizations_get(self.org_id)
        checklist_id = res['id']

        completed_at = int(datetime.utcnow().timestamp())
        module = 'module'
        p_get_optimizations_data.return_value = [
            {
                'created_at': completed_at,
                'module': module,
                'organization_id': self.org_id,
                'data': [
                    self.instance
                ],
                'options': {
                    'key': 'value'
                }
            }
        ]
        self.client.checklist_update(
            checklist_id, {'last_completed': completed_at,
                           'last_run': completed_at})
        code, res = self.client.optimizations_get(self.org_id)
        self.assertEqual(code, 200)
        self.assertEqual(res['dismissed_optimizations'], {})
        self.assertEqual(len(res['optimizations']), 1)
        self.assertEqual(res['id'], checklist_id)
        self.assertEqual(res['optimizations'][module]['count'], 1)
        self.assertEqual(res['optimizations'][module]['saving'],
                         self.instance['saving'])
        self.assertEqual(res['total_saving'], self.instance['saving'])
        self.assertIsNone(res['optimizations'][module].get('items'))
        self.assertIsNone(res['optimizations'][module].get('options'))

    def test_optimization_wrong_cloud_acc(self):
        code, res = self.client.optimizations_get(
            self.org_id, cloud_account_ids=[str(uuid.uuid4())])
        self.assertEqual(code, 404)
        self.assertEqual(res['error']['error_code'], 'OE0002')

    @patch(GET_OPTIMIZATIONS_DATA)
    def test_optimization_cloud_acc(self, p_get_optimizations_data):
        _, res = self.client.optimizations_get(self.org_id)
        checklist_id = res['id']

        completed_at = int(datetime.utcnow().timestamp())
        module = 'module'
        p_get_optimizations_data.return_value = [
            {
                'created_at': completed_at,
                'module': module,
                'organization_id': self.org_id,
                'data': [
                    self.instance,
                    self.instance2
                ]
            }
        ]
        self.client.checklist_update(
            checklist_id, {'last_completed': completed_at,
                           'last_run': completed_at})
        code, res = self.client.optimizations_get(
            self.org_id, cloud_account_ids=[self.cloud_acc['id']])
        self.assertEqual(code, 200)
        self.assertEqual(res['dismissed_optimizations'], {})
        self.assertEqual(len(res['optimizations']), 1)
        self.assertEqual(res['id'], checklist_id)
        self.assertEqual(res['optimizations'][module]['count'], 2)

        code, res = self.client.optimizations_get(
            self.org_id, cloud_account_ids=[self.cloud_acc2['id']])
        self.assertEqual(code, 200)
        self.assertEqual(res['dismissed_optimizations'], {})
        self.assertEqual(len(res['optimizations']), 1)
        self.assertEqual(res['id'], checklist_id)
        self.assertEqual(res['optimizations'][module]['count'], 0)

    @patch(GET_OPTIMIZATIONS_DATA)
    def test_optimization_cloud_acc_detailed(self, p_get_optimizations_data):
        _, res = self.client.optimizations_get(self.org_id)
        checklist_id = res['id']

        completed_at = int(datetime.utcnow().timestamp())
        module = 'module'
        p_get_optimizations_data.return_value = [
            {
                'created_at': completed_at,
                'module': module,
                'organization_id': self.org_id,
                'data': [
                    self.instance
                ]
            }
        ]
        self.client.checklist_update(
            checklist_id, {'last_completed': completed_at,
                           'last_run': completed_at})
        code, res = self.client.optimizations_get(
            self.org_id, cloud_account_ids=[self.cloud_acc['id']], types=[module])
        self.assertEqual(code, 200)
        self.assertEqual(res['dismissed_optimizations'], {})
        self.assertEqual(len(res['optimizations']), 1)
        self.assertEqual(res['id'], checklist_id)
        self.assertEqual(res['optimizations'][module]['count'], 1)
        self.assertEqual(res['optimizations'][module]['items'], [self.instance])

        code, res = self.client.optimizations_get(
            self.org_id, cloud_account_ids=[self.cloud_acc2['id']], types=[module])
        self.assertEqual(code, 200)
        self.assertEqual(res['dismissed_optimizations'], {})
        self.assertEqual(len(res['optimizations']), 1)
        self.assertEqual(res['id'], checklist_id)
        self.assertEqual(res['optimizations'][module]['count'], 0)

    @patch(GET_OPTIMIZATIONS_DATA)
    def test_suppressed_optimization(self, p_get_optimizations_data):
        _, res = self.client.optimizations_get(self.org_id)
        checklist_id = res['id']

        completed_at = int(datetime.utcnow().timestamp())
        module = 'module'
        self.instance['is_dismissed'] = True
        p_get_optimizations_data.return_value = [
            {
                'created_at': completed_at,
                'module': module,
                'organization_id': self.org_id,
                'data': [
                    self.instance
                ]
            }
        ]
        self.client.checklist_update(
            checklist_id, {'last_completed': completed_at,
                           'last_run': completed_at})
        code, res = self.client.optimizations_get(self.org_id)
        self.assertEqual(code, 200)
        self.assertEqual(len(res['optimizations']), 1)
        self.assertEqual(res['optimizations'][module]['count'], 0)
        self.assertIsNone(res['optimizations'][module].get('items'))
        self.assertIsNone(res['optimizations'][module].get('options'))
        self.assertEqual(len(res['dismissed_optimizations']), 1)
        self.assertEqual(res['dismissed_optimizations'][module]['count'], 1)
        self.assertEqual(res['dismissed_optimizations'][module]['saving'],
                         self.instance['saving'])
        self.assertEqual(res['id'], checklist_id)
        self.assertEqual(res['total_saving'], 0)

    @patch(GET_OPTIMIZATIONS_DATA)
    def test_optimization_detailed(self, p_get_optimizations_data):
        _, res = self.client.optimizations_get(self.org_id)
        checklist_id = res['id']

        completed_at = int(datetime.utcnow().timestamp())
        module = 'module'
        options = {'key': 'value'}
        p_get_optimizations_data.return_value = [
            {
                'created_at': completed_at,
                'module': module,
                'organization_id': self.org_id,
                'data': [
                    self.instance
                ],
                'options': options
            }
        ]
        self.client.checklist_update(
            checklist_id, {'last_completed': completed_at,
                           'last_run': completed_at})
        code, res = self.client.optimizations_get(self.org_id, types=[module])
        self.assertEqual(code, 200)
        self.assertEqual(res['dismissed_optimizations'], {})
        self.assertEqual(len(res['optimizations']), 1)
        self.assertEqual(res['id'], checklist_id)
        self.assertEqual(res['optimizations'][module]['count'], 1)
        self.assertEqual(res['optimizations'][module]['saving'], self.instance['saving'])
        self.assertEqual(res['optimizations'][module]['items'], [self.instance])
        self.assertEqual(res['optimizations'][module]['options'], options)
        self.assertEqual(res['total_saving'], self.instance['saving'])

    @patch(GET_OPTIMIZATIONS_DATA)
    def test_suppressed_optimization_detailed(self, p_get_optimizations_data):
        _, res = self.client.optimizations_get(self.org_id)
        checklist_id = res['id']

        completed_at = int(datetime.utcnow().timestamp())
        module = 'module'
        self.instance['is_dismissed'] = True
        p_get_optimizations_data.return_value = [
            {
                'created_at': completed_at,
                'module': module,
                'organization_id': self.org_id,
                'data': [
                    self.instance
                ]
            }
        ]
        self.client.checklist_update(
            checklist_id, {'last_completed': completed_at,
                           'last_run': completed_at})
        code, res = self.client.optimizations_get(
            self.org_id, types=[module], status='dismissed')
        self.assertEqual(code, 200)
        self.assertEqual(len(res['optimizations']), 1)
        self.assertEqual(res['optimizations'][module]['count'], 0)
        self.assertIsNone(res['optimizations'][module].get('items'))
        self.assertIsNone(res['optimizations'][module].get('options'))
        self.assertEqual(len(res['dismissed_optimizations']), 1)
        self.assertEqual(res['dismissed_optimizations'][module]['count'], 1)
        self.assertEqual(res['dismissed_optimizations'][module]['saving'],
                         self.instance['saving'])
        self.assertEqual(res['dismissed_optimizations'][module]['items'],
                         [self.instance])
        self.assertEqual(
            res['dismissed_optimizations'][module].get('options'), {})
        self.assertEqual(res['id'], checklist_id)
        self.assertEqual(res['total_saving'], 0)

    @patch(GET_OPTIMIZATIONS_DATA)
    def test_optimization_no_saving(self, p_get_optimizations_data):
        _, res = self.client.optimizations_get(self.org_id)
        checklist_id = res['id']

        completed_at = int(datetime.utcnow().timestamp())
        module = 'module'
        self.instance.pop('saving')
        p_get_optimizations_data.return_value = [
            {
                'created_at': completed_at,
                'module': module,
                'organization_id': self.org_id,
                'data': [
                    self.instance
                ]
            }
        ]
        self.client.checklist_update(
            checklist_id, {'last_completed': completed_at,
                           'last_run': completed_at})
        code, res = self.client.optimizations_get(self.org_id)
        self.assertEqual(code, 200)
        self.assertEqual(res['dismissed_optimizations'], {})
        self.assertEqual(len(res['optimizations']), 1)
        self.assertEqual(res['id'], checklist_id)
        self.assertEqual(res['optimizations'][module]['count'], 1)
        self.assertEqual(res['optimizations'][module].get('saving'), None)
        self.assertEqual(res['total_saving'], 0)

    @patch(GET_OPTIMIZATIONS_DATA)
    def test_optimization_error(self, p_get_optimizations_data):
        _, res = self.client.optimizations_get(self.org_id)
        checklist_id = res['id']

        completed_at = int(datetime.utcnow().timestamp())
        module = 'module'
        error_message = 'Failed to collect optimization data'
        options = {'key': 'value'}
        p_get_optimizations_data.return_value = [
            {
                'created_at': completed_at,
                'module': module,
                'organization_id': self.org_id,
                'data': [self.instance],
                'error': error_message,
                'options': options
            }
        ]
        self.client.checklist_update(
            checklist_id, {'last_completed': completed_at,
                           'last_run': completed_at})
        code, res = self.client.optimizations_get(self.org_id)
        self.assertEqual(code, 200)
        for key in ['optimizations']:
            self.assertEqual(len(res[key]), 1)
            self.assertEqual(res[key][module]['count'], 1)
            self.assertEqual(res[key][module]['saving'], 150)
            self.assertEqual(res[key][module]['error'], error_message)
            self.assertIsNone(res[key][module].get('items'))
            self.assertIsNone(res[key][module].get('options'))
        self.assertEqual(res['id'], checklist_id)
        self.assertEqual(res['total_saving'], 150)

        code, res = self.client.optimizations_get(self.org_id, types=[module])
        self.assertEqual(code, 200)
        for key in ['optimizations']:
            self.assertEqual(len(res[key]), 1)
            self.assertEqual(res[key][module]['count'], 1)
            self.assertEqual(res[key][module]['saving'], 150)
            self.assertEqual(res[key][module]['error'], error_message)
            self.assertEqual(res[key][module].get('items'), [self.instance])
            self.assertEqual(res[key][module].get('options'), options)
        self.assertEqual(res['id'], checklist_id)
        self.assertEqual(res['total_saving'], 150)

    @patch(GET_OPTIMIZATIONS_DATA)
    def test_optimization_unhandled_error(self, p_get_optimizations_data):
        _, res = self.client.optimizations_get(self.org_id)
        checklist_id = res['id']

        completed_at = int(datetime.utcnow().timestamp())
        module = 'module'
        error_message = 'Failed to collect optimization data'
        p_get_optimizations_data.return_value = [
            {
                'created_at': completed_at,
                'module': module,
                'organization_id': self.org_id,
                'data': None,
                'error': error_message,
                'options': None
            }
        ]
        self.client.checklist_update(
            checklist_id, {'last_completed': completed_at,
                           'last_run': completed_at})
        code, res = self.client.optimizations_get(self.org_id)
        self.assertEqual(code, 200)
        for key in ['optimizations']:
            self.assertEqual(len(res[key]), 1)
            self.assertEqual(res[key][module]['count'], 0)
            self.assertEqual(res[key][module]['saving'], 0)
            self.assertEqual(res[key][module]['error'], error_message)
            self.assertIsNone(res[key][module].get('items'))
            self.assertIsNone(res[key][module].get('options'))
        self.assertEqual(res['id'], checklist_id)
        self.assertEqual(res['total_saving'], 0)

        code, res = self.client.optimizations_get(self.org_id, types=[module])
        self.assertEqual(code, 200)
        for key in ['optimizations']:
            self.assertEqual(len(res[key]), 1)
            self.assertEqual(res[key][module]['count'], 0)
            self.assertEqual(res[key][module]['saving'], 0)
            self.assertEqual(res[key][module]['error'], error_message)
            self.assertEqual(res[key][module].get('items'), [])
            self.assertEqual(res[key][module].get('options'), {})
        self.assertEqual(res['id'], checklist_id)
        self.assertEqual(res['total_saving'], 0)

    @patch(GET_OPTIMIZATIONS_DATA)
    def test_optimization_timeout_error(self, p_get_optimizations_data):
        _, res = self.client.optimizations_get(self.org_id)
        checklist_id = res['id']

        completed_at = int(datetime.utcnow().timestamp())
        module = 'module'
        error_message = 'Failed to collect optimization data'
        p_get_optimizations_data.return_value = [
            {
                'created_at': completed_at,
                'module': module,
                'organization_id': self.org_id,
                'timeout_error': error_message,
            }
        ]
        self.client.checklist_update(
            checklist_id, {'last_completed': completed_at,
                           'last_run': completed_at})
        code, res = self.client.optimizations_get(self.org_id)
        self.assertEqual(code, 200)
        for key in ['optimizations']:
            self.assertEqual(len(res[key]), 1)
            self.assertEqual(res[key][module]['count'], 0)
            self.assertEqual(res[key][module]['saving'], 0)
            self.assertEqual(res[key][module]['error'], error_message)
            self.assertIsNone(res[key][module].get('items'))
            self.assertIsNone(res[key][module].get('options'))
        self.assertEqual(res['id'], checklist_id)
        self.assertEqual(res['total_saving'], 0)

    @patch(GET_OPTIMIZATIONS_DATA)
    def test_optimization_several_modules(self, p_get_optimizations_data):
        _, res = self.client.optimizations_get(self.org_id)
        checklist_id = res['id']

        completed_at = int(datetime.utcnow().timestamp())
        module1 = 'module1'
        module2 = 'module2'
        p_get_optimizations_data.return_value = [
            {
                'created_at': completed_at,
                'module': module1,
                'organization_id': self.org_id,
                'data': [
                    self.instance
                ]
            },
            {
                'created_at': completed_at,
                'module': module2,
                'organization_id': self.org_id,
                'data': [
                    self.instance
                ]
            }
        ]
        self.client.checklist_update(
            checklist_id, {'last_completed': completed_at,
                           'last_run': completed_at})
        code, res = self.client.optimizations_get(
            self.org_id, types=[module1, module2])
        self.assertEqual(code, 200)
        self.assertEqual(res['dismissed_optimizations'], {})
        self.assertEqual(len(res['optimizations']), 2)
        self.assertEqual(res['id'], checklist_id)
        self.assertEqual(res['optimizations'][module1]['count'], 1)
        self.assertEqual(res['optimizations'][module1]['saving'],
                         self.instance['saving'])
        self.assertEqual(res['optimizations'][module1]['items'],
                         [self.instance])
        self.assertEqual(res['optimizations'][module2]['count'], 1)
        self.assertEqual(res['optimizations'][module2]['saving'],
                         self.instance['saving'])
        self.assertEqual(res['optimizations'][module2]['items'],
                         [self.instance])
        self.assertEqual(res['total_saving'], self.instance['saving'] * 2)

        code, res = self.client.optimizations_get(self.org_id, types=[module1])
        self.assertEqual(code, 200)
        self.assertEqual(res['dismissed_optimizations'], {})
        self.assertEqual(len(res['optimizations']), 2)
        self.assertEqual(res['id'], checklist_id)
        self.assertEqual(res['optimizations'][module1]['count'], 1)
        self.assertEqual(res['optimizations'][module1]['saving'],
                         self.instance['saving'])
        self.assertEqual(res['optimizations'][module1]['items'],
                         [self.instance])
        self.assertEqual(res['optimizations'][module2]['count'], 1)
        self.assertEqual(res['optimizations'][module2]['saving'],
                         self.instance['saving'])
        self.assertEqual(res['optimizations'][module2].get('items'), None)
        self.assertEqual(res['total_saving'], self.instance['saving'] * 2)

        code, res = self.client.optimizations_get(self.org_id)
        self.assertEqual(code, 200)
        self.assertEqual(res['dismissed_optimizations'], {})
        self.assertEqual(len(res['optimizations']), 2)
        self.assertEqual(res['id'], checklist_id)
        self.assertEqual(res['optimizations'][module1]['count'], 1)
        self.assertEqual(res['optimizations'][module1]['saving'],
                         self.instance['saving'])
        self.assertEqual(res['optimizations'][module1].get('items'), None)
        self.assertEqual(res['optimizations'][module2]['count'], 1)
        self.assertEqual(res['optimizations'][module2]['saving'],
                         self.instance['saving'])
        self.assertEqual(res['optimizations'][module2].get('items'), None)
        self.assertEqual(res['total_saving'], self.instance['saving'] * 2)

    @patch(GET_OPTIMIZATIONS_DATA)
    def test_combi_optimization(self, p_get_optimizations_data):
        _, res = self.client.optimizations_get(self.org_id)
        checklist_id = res['id']

        completed_at = int(datetime.utcnow().timestamp())
        module = 'module'
        self.instance['is_dismissed'] = True
        p_get_optimizations_data.return_value = [
            {
                'created_at': completed_at,
                'module': module,
                'organization_id': self.org_id,
                'data': [
                    self.instance, self.instance2
                ]
            }
        ]
        self.client.checklist_update(
            checklist_id, {'last_completed': completed_at,
                           'last_run': completed_at})
        code, res = self.client.optimizations_get(self.org_id, types=[module])
        self.assertEqual(code, 200)
        self.assertEqual(len(res['dismissed_optimizations']), 1)
        self.assertEqual(len(res['optimizations']), 1)
        self.assertEqual(res['id'], checklist_id)
        self.assertEqual(res['optimizations'][module]['count'], 1)
        self.assertEqual(res['optimizations'][module]['saving'],
                         self.instance2['saving'])
        self.assertEqual(res['optimizations'][module]['items'],
                         [self.instance2])
        self.assertIsNone(res['dismissed_optimizations'][module].get('items'))

        code, res = self.client.optimizations_get(
            self.org_id, types=[module], status='dismissed')
        self.assertEqual(code, 200)
        self.assertEqual(len(res['dismissed_optimizations']), 1)
        self.assertEqual(len(res['optimizations']), 1)
        self.assertEqual(res['id'], checklist_id)
        self.assertEqual(res['dismissed_optimizations'][module]['count'], 1)
        self.assertEqual(res['dismissed_optimizations'][module]['saving'],
                         self.instance['saving'])
        self.assertEqual(res['dismissed_optimizations'][module]['items'],
                         [self.instance])
        self.assertEqual(res['total_saving'], self.instance2['saving'])
        self.assertIsNone(res['optimizations'][module].get('items'))

    @patch(GET_OPTIMIZATIONS_DATA)
    def test_optimization_typeless_limit(self, p_get_optimizations_data):
        p_get_optimizations_data.return_value = []
        code, res = self.client.optimizations_get(self.org_id, limit=1)
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0212')

    @patch(GET_OPTIMIZATIONS_DATA)
    def test_optimization_typeless_is_suppress(self, p_get_optimizations_data):
        p_get_optimizations_data.return_value = []
        code, res = self.client.optimizations_get(self.org_id, status='active')
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0212')

    @patch(GET_OPTIMIZATIONS_DATA)
    def test_optimization_wrong_limit(self, p_get_optimizations_data):
        p_get_optimizations_data.return_value = []
        code, res = self.client.optimizations_get(
            self.org_id, types=['module'], limit=0)
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0224')

    @patch(GET_OPTIMIZATIONS_DATA)
    def test_optimization_wrong_is_suppress(self, p_get_optimizations_data):
        p_get_optimizations_data.return_value = []
        code, res = self.client.optimizations_get(
            self.org_id, types=['module'], status='dva')
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0460')

    @patch(GET_OPTIMIZATIONS_DATA)
    def test_optimization_limit_detailed(self, p_get_optimizations_data):
        _, res = self.client.optimizations_get(self.org_id)
        checklist_id = res['id']

        completed_at = int(datetime.utcnow().timestamp())
        module = 'module'
        opt_data = [self.instance, self.instance2]
        module_saving = self.instance['saving'] + self.instance2['saving']
        p_get_optimizations_data.return_value = [
            {
                'created_at': completed_at,
                'module': module,
                'organization_id': self.org_id,
                'data': opt_data
            }
        ]
        self.client.checklist_update(
            checklist_id, {'last_completed': completed_at,
                           'last_run': completed_at})
        code, res = self.client.optimizations_get(
            self.org_id, types=[module], limit=1)
        self.assertEqual(code, 200)
        self.assertEqual(res['dismissed_optimizations'], {})
        self.assertEqual(len(res['optimizations']), 1)
        self.assertEqual(res['id'], checklist_id)
        self.assertEqual(res['optimizations'][module]['count'], len(opt_data))
        self.assertEqual(res['optimizations'][module]['limit'], 1)
        self.assertEqual(res['optimizations'][module]['saving'], module_saving)
        self.assertEqual(res['optimizations'][module]['items'], [self.instance])
        self.assertEqual(res['total_saving'], module_saving)

    @patch(GET_OPTIMIZATIONS_DATA)
    def test_optimization_detailed_no_data(self, p_get_optimizations_data):
        _, res = self.client.optimizations_get(self.org_id)
        checklist_id = res['id']

        completed_at = int(datetime.utcnow().timestamp())
        module = 'module'
        opt_data = []
        options = {'key': 'value'}
        p_get_optimizations_data.return_value = [
            {
                'created_at': completed_at,
                'module': module,
                'organization_id': self.org_id,
                'data': opt_data,
                'options': options
            }
        ]
        self.client.checklist_update(
            checklist_id, {'last_completed': completed_at,
                           'last_run': completed_at})
        code, res = self.client.optimizations_get(self.org_id, types=[module])
        self.assertEqual(code, 200)
        self.assertEqual(res['dismissed_optimizations'], {})
        self.assertEqual(len(res['optimizations']), 1)
        self.assertEqual(res['id'], checklist_id)
        self.assertEqual(res['optimizations'][module]['count'], len(opt_data))
        self.assertEqual(res['optimizations'][module]['items'], [])
        self.assertEqual(res['optimizations'][module]['options'], options)

    @patch(GET_OPTIMIZATIONS_DATA)
    def test_optimization_limit_detailed_no_saving(self, p_get_optimizations_data):
        _, res = self.client.optimizations_get(self.org_id)
        checklist_id = res['id']

        completed_at = int(datetime.utcnow().timestamp())
        module = 'module'
        self.instance.pop('saving')
        self.instance2.pop('saving')
        opt_data = [self.instance, self.instance2]
        p_get_optimizations_data.return_value = [
            {
                'created_at': completed_at,
                'module': module,
                'organization_id': self.org_id,
                'data': opt_data
            }
        ]
        self.client.checklist_update(
            checklist_id, {'last_completed': completed_at,
                           'last_run': completed_at})
        code, res = self.client.optimizations_get(
            self.org_id, types=[module], limit=1)
        self.assertEqual(code, 200)
        self.assertEqual(res['dismissed_optimizations'], {})
        self.assertEqual(len(res['optimizations']), 1)
        self.assertEqual(res['id'], checklist_id)
        self.assertEqual(res['optimizations'][module]['count'], 2)
        self.assertEqual(len(res['optimizations'][module]['items']), 1)
        self.assertEqual(res['total_saving'], 0)
        self.assertEqual(res['optimizations'][module]['limit'], 1)

    @patch(GET_OPTIMIZATIONS_DATA)
    def test_optimization_limit_several_modules(self, p_get_optimizations_data):
        _, res = self.client.optimizations_get(self.org_id)
        checklist_id = res['id']

        completed_at = int(datetime.utcnow().timestamp())
        module1 = 'module1'
        module2 = 'module2'
        options1 = {'key1': 'value1'}
        options2 = {'key2': 'value2'}
        opt_data = [self.instance, self.instance2]
        module_saving = self.instance['saving'] + self.instance2['saving']
        p_get_optimizations_data.return_value = [
            {
                'created_at': completed_at,
                'module': module1,
                'organization_id': self.org_id,
                'data': opt_data,
                'options': options1
            },
            {
                'created_at': completed_at,
                'module': module2,
                'organization_id': self.org_id,
                'data': opt_data,
                'options': options2
            }
        ]
        self.client.checklist_update(
            checklist_id, {'last_completed': completed_at,
                           'last_run': completed_at})
        code, res = self.client.optimizations_get(
            self.org_id, types=[module1, module2], limit=1)
        self.assertEqual(code, 200)
        self.assertEqual(res['dismissed_optimizations'], {})
        self.assertEqual(len(res['optimizations']), 2)
        self.assertEqual(res['id'], checklist_id)
        self.assertEqual(res['optimizations'][module1]['count'], len(opt_data))
        self.assertEqual(res['optimizations'][module1]['limit'], 1)
        self.assertEqual(res['optimizations'][module1]['saving'], module_saving)
        self.assertEqual(res['optimizations'][module1]['items'], [self.instance])
        self.assertEqual(res['optimizations'][module1]['options'], options1)
        self.assertEqual(res['optimizations'][module2]['count'], len(opt_data))
        self.assertEqual(res['optimizations'][module2]['limit'], 1)
        self.assertEqual(res['optimizations'][module2]['saving'], module_saving)
        self.assertEqual(res['optimizations'][module2]['items'], [self.instance])
        self.assertEqual(res['optimizations'][module2]['options'], options2)
        self.assertEqual(res['total_saving'], module_saving * 2)

    @patch(GET_OPTIMIZATIONS_DATA)
    def test_optimization_limit_error(self, p_get_optimizations_data):
        _, res = self.client.optimizations_get(self.org_id)
        checklist_id = res['id']

        completed_at = int(datetime.utcnow().timestamp())
        module = 'module'
        self.instance.pop('saving')
        error_message = 'Hey, gde kurab\'e?!!1'
        p_get_optimizations_data.return_value = [
            {
                'created_at': completed_at,
                'module': module,
                'organization_id': self.org_id,
                'data': [],
                'error': error_message
            }
        ]
        self.client.checklist_update(
            checklist_id, {'last_completed': completed_at,
                           'last_run': completed_at})
        code, res = self.client.optimizations_get(
            self.org_id, types=[module], limit=1)
        self.assertEqual(code, 200)
        for key in ['optimizations']:
            self.assertEqual(len(res[key]), 1)
            self.assertEqual(res[key][module]['count'], 0)
            self.assertEqual(res[key][module]['saving'], 0)
            self.assertEqual(res[key][module]['error'], error_message)
            self.assertIsNone(res[key][module].get('limit'))
        self.assertEqual(res['total_saving'], 0)
        self.assertEqual(res['id'], checklist_id)

    @patch(GET_OPTIMIZATIONS_DATA)
    def test_optimization_overview(self, p_get_optimizations_data):
        _, res = self.client.optimizations_get(self.org_id)
        checklist_id = res['id']

        completed_at = int(datetime.utcnow().timestamp())
        module1 = 'module1'
        module2 = 'module2'
        options1 = {'key1': 'value1'}
        options2 = {'key2': 'value2'}
        opt_data = [self.instance, self.instance2]
        module_saving = self.instance['saving'] + self.instance2['saving']
        p_get_optimizations_data.return_value = [
            {
                'created_at': completed_at,
                'module': module1,
                'organization_id': self.org_id,
                'data': opt_data,
                'options': options1
            },
            {
                'created_at': completed_at,
                'module': module2,
                'organization_id': self.org_id,
                'data': opt_data,
                'options': options2
            }
        ]
        self.client.checklist_update(
            checklist_id, {'last_completed': completed_at,
                           'last_run': completed_at})
        code, res = self.client.optimizations_get(
            self.org_id, overview=True)
        self.assertEqual(code, 200)
        self.assertEqual(res['dismissed_optimizations'], {})
        self.assertEqual(len(res['optimizations']), 2)
        self.assertEqual(res['id'], checklist_id)
        self.assertEqual(res['optimizations'][module1]['count'], len(opt_data))
        self.assertEqual(res['optimizations'][module1]['saving'], module_saving)
        self.assertEqual(res['optimizations'][module1]['items'],
                         [self.instance, self.instance2])
        self.assertEqual(res['optimizations'][module1]['options'], options1)
        self.assertEqual(res['optimizations'][module2]['count'], len(opt_data))
        self.assertEqual(res['optimizations'][module2]['saving'], module_saving)
        self.assertEqual(res['optimizations'][module2]['items'],
                         [self.instance, self.instance2])
        self.assertEqual(res['optimizations'][module2]['options'], options2)
        self.assertEqual(res['total_saving'], module_saving * 2)

    @patch(GET_OPTIMIZATIONS_DATA)
    def test_optimization_overview_limit(self, p_get_optimizations_data):
        _, res = self.client.optimizations_get(self.org_id)
        checklist_id = res['id']

        completed_at = int(datetime.utcnow().timestamp())
        module1 = 'module1'
        module2 = 'module2'
        options1 = {'key1': 'value1'}
        options2 = {'key2': 'value2'}
        opt_data = [self.instance, self.instance2]
        module_saving = self.instance['saving'] + self.instance2['saving']
        p_get_optimizations_data.return_value = [
            {
                'created_at': completed_at,
                'module': module1,
                'organization_id': self.org_id,
                'data': opt_data,
                'options': options1
            },
            {
                'created_at': completed_at,
                'module': module2,
                'organization_id': self.org_id,
                'data': opt_data,
                'options': options2
            }
        ]
        self.client.checklist_update(
            checklist_id, {'last_completed': completed_at,
                           'last_run': completed_at})
        code, res = self.client.optimizations_get(
            self.org_id, overview=True, limit=1)
        self.assertEqual(code, 200)
        self.assertEqual(res['dismissed_optimizations'], {})
        self.assertEqual(len(res['optimizations']), 2)
        self.assertEqual(res['id'], checklist_id)
        self.assertEqual(res['optimizations'][module1]['count'], len(opt_data))
        self.assertEqual(res['optimizations'][module1]['saving'], module_saving)
        self.assertEqual(res['optimizations'][module1]['limit'], 1)
        self.assertEqual(res['optimizations'][module1]['items'],
                         [self.instance])
        self.assertEqual(res['optimizations'][module1]['options'], options1)
        self.assertEqual(res['optimizations'][module2]['count'], len(opt_data))
        self.assertEqual(res['optimizations'][module2]['saving'], module_saving)
        self.assertEqual(res['optimizations'][module2]['limit'], 1)
        self.assertEqual(res['optimizations'][module2]['items'],
                         [self.instance])
        self.assertEqual(res['optimizations'][module2]['options'], options2)
        self.assertEqual(res['total_saving'], module_saving * 2)

    @patch(GET_OPTIMIZATIONS_DATA)
    def test_optimization_overview_unexpected(self, p_get_optimizations_data):
        p_get_optimizations_data.return_value = []
        for extras in [{'types': ['module']}, {'status': 'smth'}]:
            code, res = self.client.optimizations_get(
                self.org_id, overview=True, **extras)
            self.assertEqual(code, 400)
            self.assertEqual(res['error']['error_code'], 'OE0212')


class TestOptimizationDataApi(TestApiBase):
    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.org = self.client.organization_create({'name': "partner"})
        self.org_id = self.org['id']
        patch('rest_api_server.controllers.cloud_account.'
              'CloudAccountController._configure_report').start()
        self.user_id = self.gen_id()
        self._mock_auth_user(self.user_id)
        _, self.employee = self.client.employee_create(
            self.org_id, {'name': 'name', 'auth_user_id': self.user_id})
        config = {
            'name': 'creds',
            'type': 'aws_cnr',
            'config': {
                'access_key_id': 'key',
                'secret_access_key': 'secret',
                'config_scheme': 'create_report'
            }
        }
        _, self.cloud_acc = self.create_cloud_account(
            self.org_id, config, auth_user_id=self.user_id)
        config2 = config.copy()
        config2['name'] = 'creds2'
        _, self.cloud_acc2 = self.create_cloud_account(
            self.org_id, config2, auth_user_id=self.user_id)
        self.instance = self._generate_instance('test instance', 20, 150)
        self.instance2 = self._generate_instance('another instance', 10, 140)
        self.checklist = self._add_checklist(self.org_id)
        self._add_checklist_result(self.checklist, 'test_module',
                                   [self.instance, self.instance2])

        self.valid_resource = {
            'cloud_resource_id': self.gen_id(),
            'name': 'test_resource',
            'resource_type': 'Instance',
            'employee_id': self.employee['id'],
            'pool_id': self.org['pool_id']
        }

    def _create_cloud_resource(self, cloud_acc_id, params):
        code, resource = self.cloud_resource_create(
            cloud_acc_id, params)
        self.resources_collection.update_one(
            filter={
                '_id': resource['id']
            },
            update={'$set': {
                'last_seen': int(datetime.utcnow().timestamp() - 1),
                'active': True
            }}
        )
        return code, resource

    @staticmethod
    def _add_checklist(organization_id, timestamp=None):
        if not timestamp:
            timestamp = int(datetime.utcnow().timestamp())
        db = DBFactory(DBType.Test, None).db
        engine = db.engine
        session = BaseDB.session(engine)()
        record = Checklist(
            organization_id=organization_id,
            last_run=timestamp,
            last_completed=timestamp
        )
        session.add(record)
        session.commit()
        return record.to_dict()

    def _add_checklist_result(self, checklist, module, data, created_at=None,
                              tie_to_resource=False):
        if not created_at:
            created_at = checklist['last_completed']
        checklist_rec = {
            'module': module,
            'organization_id': checklist['organization_id'],
            'created_at': created_at,
            'data': data
        }
        self.checklists_collection.insert_one(checklist_rec)
        return checklist_rec

    def _generate_instance(self, name, cost, saving):
        return {
            'cloud_resource_id': str(uuid.uuid4()),
            'resource_name': name,
            'resource_id': str(uuid.uuid4()),
            'cloud_account_id': self.cloud_acc['id'],
            'cloud_type': self.cloud_acc['type'],
            'total_cost': cost,
            'first_seen': 1600077735,
            'last_seen': 1600078565,
            'saving': saving
        }

    def test_optimization_data_nonexistent_organization(self):
        code, response = self.client.optimization_data_get(
            str(uuid.uuid4()), 'test_module')
        self.assertEqual(code, 404)
        self.verify_error_code(response, 'OE0002')

    def test_optimization_data_without_type(self):
        code, response = self.client.optimization_data_get(self.org_id, None)
        self.assertEqual(code, 400)
        self.verify_error_code(response, 'OE0216')

    def test_optimization_data_invalid_type(self):
        invalid_types = ['', ''.join('x' for i in range(0, 256))]
        for t in invalid_types:
            code, response = self.client.optimization_data_get(
                self.org_id, t)
            self.assertEqual(code, 400)
            self.verify_error_code(response, 'OE0215')

    def test_not_existing_optimization(self):
        code, response = self.client.optimization_data_get(
            self.org_id, 'some')
        self.assertEqual(code, 200)
        self.assertEqual(response, [])

    def test_optimization_wrong_cloud_acc(self):
        code, response = self.client.optimization_data_get(
            self.org_id, 'some', cloud_account_ids=[str(uuid.uuid4())])
        self.assertEqual(code, 404)
        self.assertEqual(response['error']['error_code'], 'OE0002')

    def test_optimization_data_limit(self):
        instance_3 = self._generate_instance('3 instance', 10, 10)
        instance_4 = self._generate_instance('4 instance', 10, 1)
        self._add_checklist_result(self.checklist, 'module2', [instance_3,
                                                               instance_4])

        code, response = self.client.optimization_data_get(
            self.org_id, 'module2', limit=5)
        self.assertEqual(code, 200)
        self.assertEqual(len(response), 2)

        code, response = self.client.optimization_data_get(
            self.org_id, 'module2', limit=1)
        self.assertEqual(code, 200)
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]['saving'], 10)

        code, response = self.client.optimization_data_get(
            self.org_id, 'module2', limit=0)
        self.assertEqual(code, 200)
        self.assertEqual(len(response), 2)

    def test_optimization_data_invalid_limit(self):
        code, response = self.client.optimization_data_get(
            self.org_id, 'module2', limit='limit')
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0217')

    def test_optimization_data(self):
        instance_3 = self._generate_instance('3 instance', 10, 10)
        self._add_checklist_result(self.checklist, 'module2', [instance_3])

        code, response = self.client.optimization_data_get(
            self.org_id, 'test_module')
        self.assertEqual(code, 200)
        self.assertEqual(len(response), 2)
        self.assertEqual(sum(r['saving'] for r in response),
                         self.instance['saving'] + self.instance2['saving'])
        resp_resource_ids = list(map(lambda x: x['resource_id'], response))
        self.assertEqual(resp_resource_ids, [self.instance['resource_id'],
                                             self.instance2['resource_id']])

        code, response = self.client.optimization_data_get(
            self.org_id, 'module2')
        self.assertEqual(code, 200)
        self.assertEqual(len(response), 1)
        self.assertEqual(sum(r['saving'] for r in response),
                         instance_3['saving'])
        resp_resource_ids = list(map(lambda x: x['resource_id'], response))
        self.assertEqual(resp_resource_ids, [instance_3['resource_id']])

    def _add_optimization(self, resource, module, checklist_data):
        checklist_result = self._add_checklist_result(
            self.checklist, module, checklist_data)
        optimization = {
            'run_timestamp': checklist_result['created_at']
        }
        data = checklist_result['data']
        for entry in data:
            entry['name'] = checklist_result['module']
        optimization['modules'] = data
        self.resources_collection.update_one(
            filter={
                '_id': resource['id']
            },
            update={'$set': {
                'recommendations': optimization
            }}
        )

    def _get_optimization(self, module, checklist=None):
        if not checklist:
            checklist = self.checklist
        res = self.checklists_collection.find({
            'organization_id': checklist['organization_id'],
            'created_at': checklist['last_completed'],
            'module': module
        })
        if res:
            return res[0]

    @staticmethod
    def _build_optimization_data(resource):
        return {
            'resource_id': resource['id'],
            'cloud_resource_id': resource['cloud_resource_id'],
        }

    def test_suppress_resource_optimization(self):
        module = 'module'
        _, resource = self._create_cloud_resource(
            self.cloud_acc['id'], self.valid_resource)
        self._add_optimization(
            resource, module, [self._build_optimization_data(resource)])
        code, response = self.client.resource_optimization_dismiss(
            resource['id'], module)
        self.assertEqual(code, 200)
        self.assertTrue(module in response.get('dismissed', []))
        self.assertEqual(len(response.get('recommendations', {})), 0)
        self.assertEqual(len(response.get(
            'dismissed_recommendations', {}).get('modules', [])), 1)
        self.assertTrue(any(filter(
            lambda x: x['name'] == module, response.get(
                'dismissed_recommendations', {}).get('modules', []))))
        optimization = self._get_optimization(module)
        for data_obj in optimization.get('data', []):
            self.assertEqual(data_obj['is_dismissed'], True)

    def test_resuppress_resource_optimization(self):
        module = 'module'
        _, resource = self._create_cloud_resource(
            self.cloud_acc['id'], self.valid_resource)
        self._add_optimization(
            resource, module, [self._build_optimization_data(resource)])
        for i in range(3):
            code, response = self.client.resource_optimization_dismiss(
                resource['id'], module)
            self.assertEqual(code, 200)
            self.assertTrue(module in response.get('dismissed', []))
            self.assertEqual(len(response.get('recommendations', {})), 0)
            self.assertEqual(len(response.get(
                'dismissed_recommendations', {}).get('modules', [])), 1)
            self.assertTrue(any(filter(
                lambda x: x['name'] == module, response.get(
                    'dismissed_recommendations', {}).get('modules', []))))

    def test_unsuppress_resource_optimization(self):
        module = 'module'
        _, resource = self._create_cloud_resource(
            self.cloud_acc['id'], self.valid_resource)
        self._add_optimization(
            resource, module, [self._build_optimization_data(resource)])
        code, response = self.client.resource_optimization_dismiss(
            resource['id'], module)
        self.assertEqual(code, 200)
        code, response = self.client.resource_optimization_activate(
            resource['id'], module)
        self.assertEqual(code, 200)
        self.assertEqual(len(response.get('dismissed', [])), 0)
        self.assertEqual(len(response.get('dismissed_recommendations', {})), 0)
        self.assertEqual(len(response.get(
            'recommendations', {}).get('modules', [])), 1)
        self.assertTrue(any(filter(
            lambda x: x['name'] == module, response.get(
                'recommendations', {}).get('modules', []))))
        optimization = self._get_optimization(module)
        for data_obj in optimization.get('data', []):
            self.assertEqual(data_obj.get('is_dismissed', False), False)

    def test_unsuppress_resource_optimization_independant(self):
        module = 'module'
        module2 = 'module2'
        _, resource = self._create_cloud_resource(
            self.cloud_acc['id'], self.valid_resource)
        self._add_optimization(
            resource, module, [self._build_optimization_data(resource)])
        code, response = self.client.resource_optimization_dismiss(
            resource['id'], module2)
        self.assertEqual(code, 200)
        code, response = self.client.resource_optimization_activate(
            resource['id'], module2)
        self.assertEqual(code, 200)
        self.assertEqual(len(response.get('dismissed', [])), 0)
        self.assertEqual(len(response.get('dismissed_recommendations', {})), 0)
        self.assertEqual(len(response.get(
            'recommendations', {}).get('modules', [])), 1)
        self.assertTrue(any(filter(
            lambda x: x['name'] == module, response.get(
                'recommendations', {}).get('modules', []))))
        optimization = self._get_optimization(module)
        for data_obj in optimization.get('data', []):
            self.assertEqual(data_obj.get('is_dismissed', False), False)

    def test_reunsuppress_resource_optimization(self):
        module = 'module'
        _, resource = self._create_cloud_resource(
            self.cloud_acc['id'], self.valid_resource)
        self._add_optimization(
            resource, module, [self._build_optimization_data(resource)])
        code, response = self.client.resource_optimization_dismiss(
            resource['id'], module)
        self.assertEqual(code, 200)
        for _ in range(3):
            code, response = self.client.resource_optimization_activate(
                resource['id'], module)
            self.assertEqual(code, 200)
        self.assertEqual(len(response.get('dismissed', [])), 0)
        self.assertEqual(len(response.get('dismissed_recommendations', {})), 0)
        self.assertEqual(len(response.get(
            'recommendations', {}).get('modules', [])), 1)
        self.assertTrue(any(filter(
            lambda x: x['name'] == module, response.get(
                'recommendations', {}).get('modules', []))))

    def test_suppress_resource_optimization_restricted(self):
        module = 'obsolete_images'
        _, resource = self._create_cloud_resource(
            self.cloud_acc['id'], self.valid_resource)
        self._add_optimization(
            resource, module, [self._build_optimization_data(resource)])
        code, response = self.client.resource_optimization_dismiss(
            resource['id'], module)
        self.assertEqual(code, 400)
        self.assertEqual(response.get('error', {}).get('error_code'), 'OE0217')

    def test_suppress_resource_optimization_action(self):
        module = 'obsolete_images'
        _, resource = self._create_cloud_resource(
            self.cloud_acc['id'], self.valid_resource)
        self._add_optimization(
            resource, module, [self._build_optimization_data(resource)])
        code, response = self.client.resource_optimization_update(
            resource['id'], module, 'SuPpReSs')
        self.assertEqual(code, 400)
        self.assertEqual(response.get('error', {}).get('error_code'), 'OE0217')

    def test_suppress_resource_optimization_cluster(self):
        module = 'obsolete_images'

        code, _ = self.client.cluster_type_create(
            self.org_id, {'name': 'c_type', 'tag_key': 'tn'})
        self.assertEqual(code, 201)

        valid_resource = self.valid_resource.copy()
        valid_resource['tags'] = {'tn': 'tv'}
        _, resource = self._create_cloud_resource(
            self.cloud_acc['id'], valid_resource)
        code, response = self.client.resource_optimization_update(
            resource['cluster_id'], module, 'suppress')
        self.assertEqual(code, 424)
        self.assertEqual(response.get('error', {}).get('error_code'), 'OE0465')

    def test_suppress_resource_optimization_nonexisting(self):
        code, response = self.client.resource_optimization_dismiss(
            str(uuid.uuid4()), 'obsolete_images')
        self.assertEqual(code, 404)
        self.assertEqual(response.get('error', {}).get('error_code'), 'OE0002')

    def test_suppress_resource_optimization_no_checklist(self):
        module = 'module'
        _, resource = self._create_cloud_resource(
            self.cloud_acc['id'], self.valid_resource)
        code, response = self.client.resource_optimization_dismiss(
            resource['id'], module)
        self.assertEqual(code, 200)
        self.assertTrue(module in response.get('dismissed', []))
        self.assertEqual(len(response.get('recommendations', {})), 0)
        self.assertEqual(len(response.get('dismissed_recommendations', {})), 0)

    def test_unsuppress_resource_optimization_no_checklist(self):
        module = 'module'
        _, resource = self._create_cloud_resource(
            self.cloud_acc['id'], self.valid_resource)
        code, response = self.client.resource_optimization_activate(
            resource['id'], module)
        self.assertEqual(code, 200)
        self.assertTrue(module not in response.get('dismissed', []))
        self.assertEqual(len(response.get('recommendations', {})), 0)
        self.assertEqual(len(response.get('dismissed_recommendations', {})), 0)

    def test_optimization_data_status(self):
        instance_3 = self._generate_instance('3 instance', 10, 10)
        instance_3['is_dismissed'] = True
        self._add_checklist_result(self.checklist, 'module2', [instance_3])

        code, response = self.client.optimization_data_get(
            self.org_id, 'module2')
        self.assertEqual(code, 200)
        self.assertEqual(len(response), 0)

        code, response = self.client.optimization_data_get(
            self.org_id, 'module2', status='dismissed')
        self.assertEqual(len(response), 1)
        self.assertEqual(sum(r['saving'] for r in response),
                         instance_3['saving'])
        resp_resource_ids = list(map(lambda x: x['resource_id'], response))
        self.assertEqual(resp_resource_ids, [instance_3['resource_id']])

    def test_optimization_data_invalid_status(self):
        code, response = self.client.optimization_data_get(
            self.org_id, 'module', status='module')
        self.assertEqual(code, 400)
        self.verify_error_code(response, 'OE0460')

    def test_optimization_data_cloud_account(self):
        instance_3 = self._generate_instance('3 instance', 10, 10)
        self._add_checklist_result(self.checklist, 'module2', [instance_3])

        code, response = self.client.optimization_data_get(
            self.org_id, 'module2', cloud_account_ids=[self.cloud_acc['id']])
        self.assertEqual(code, 200)
        self.assertEqual(len(response), 1)

        code, response = self.client.optimization_data_get(
            self.org_id, 'module2', cloud_account_ids=[self.cloud_acc2['id']])
        self.assertEqual(code, 200)
        self.assertEqual(len(response), 0)

    def test_optimization_data_environment_cloud_account(self):
        code, resource = self.environment_resource_create(
            self.org_id, {'name': 'name', 'resource_type': 'type'})

        code, response = self.client.optimization_data_get(
            self.org_id, 'module2',
            cloud_account_ids=[resource['cloud_account_id']])
        self.assertEqual(code, 200)
        self.assertEqual(len(response), 0)

    def test_suppress_optimization_events(self):
        module = 'module'
        _, resource = self._create_cloud_resource(
            self.cloud_acc['id'], self.valid_resource)
        self._add_optimization(
            resource, module, [self._build_optimization_data(resource)])

        p_publish_activities = patch(
            'rest_api_server.controllers.base.BaseController.'
            'publish_activities_task'
        ).start()
        fmt_args = {
            'initiator_name': 'user',
            'initiator_email': 'user@ema.il',
        }
        self.p_get_user_info.return_value = {
            'display_name': fmt_args['initiator_name'], 'id': self._user_id,
            'email': fmt_args['initiator_email']}

        code, response = self.client.resource_optimization_dismiss(
            resource['id'], module)
        self.assertEqual(code, 200)
        activity_param_tuples = self.get_publish_activity_tuple(
            self.org_id, resource['id'], 'resource',
            'recommendations_dismissed', {
                'object_name': resource['name'],
                'recommendation': module
            })
        p_publish_activities.assert_called_once_with(
            *activity_param_tuples, add_token=True
        )

        code, response = self.client.resource_optimization_activate(
            resource['id'], module)
        self.assertEqual(code, 200)
        activity_param_tuples_1 = self.get_publish_activity_tuple(
            self.org_id, resource['id'], 'resource',
            'recommendations_reactivated', {
                'object_name': resource['name'],
                'recommendation': module
            })
        p_publish_activities.assert_has_calls([
            call(*activity_param_tuples_1, add_token=True)
        ])
