import uuid

from unittest.mock import patch

from rest_api.rest_api_server.tests.unittests.test_infrastructure_base import (
    TestInfrastructureBase)


class TestRunsetsApi(TestInfrastructureBase):
    def setUp(self, version='v2'):
        super().setUp(version)
        _, template = self.client.template_create(
            self.organization_id, self.valid_template)
        self.template_id = template['id']
        self.param_to_obj_map = {
            'application_id': 'application',
            'cloud_account_id': 'cloud_account',
            'region_id': 'region',
            'instance_type': 'instance_size',
            'owner_id': 'owner',
            'template_id': 'template'
        }
        self.another_auth_user = str(uuid.uuid4())
        _, another_employee = self.client.employee_create(
            self.organization_id,
            {'name': 'name1',
             'auth_user_id': self.another_auth_user})
        self.another_employee_id = another_employee['id']

    @staticmethod
    def change_user(user_id):
        patch('rest_api.rest_api_server.controllers.base.BaseController.'
              'get_user_id', return_value=user_id).start()
        user = {
            'id': user_id,
            'display_name': 'default',
            'email': 'email@email.com',
        }
        patch('rest_api.rest_api_server.handlers.v1.base.BaseAuthHandler._get_user_info',
              return_value=user).start()

    def test_create(self):
        code, runset = self.client.runset_create(
            self.organization_id, self.template_id, self.valid_runset)
        self.assertEqual(code, 201)
        valid_runset = self.valid_runset.copy()
        valid_runset['template_id'] = self.template_id
        for k, v in valid_runset.items():
            if k in self.param_to_obj_map:
                new_param = self.param_to_obj_map[k]
                self.assertTrue(isinstance(runset[new_param], dict))
            else:
                self.assertEqual(runset[k], v)
        self.assertEqual(runset['duration'], 0)
        self.assertEqual(runset['runs_count'], 0)
        self.assertEqual(runset['succeeded_runs'], 0)
        self.assertEqual(runset['cost'], 0)

    def test_create_next(self):
        code, runset = self.client.runset_create(
            self.organization_id, self.template_id, self.valid_runset)
        self.assertEqual(code, 201)
        code, _ = self.client.runset_get(self.organization_id, runset['id'])
        self.assertEqual(code, 200)
        code, next_runset = self.client.runset_create(
            self.organization_id, self.template_id, self.valid_runset)
        self.assertEqual(code, 201)
        code, res = self.client.runset_get(
            self.organization_id, next_runset['id'])
        self.assertEqual(code, 200)
        self.assertEqual(res.get('number'), 2)
        self.assertEqual(res.get('duration'), 100)
        # Hardcoded based on duration and flavor cost (hourly cost is 0.175)
        self.assertEqual(res.get('cost'), 0.0049)

    def test_create_nonexisting(self):
        code, _ = self.client.runset_create(
            self.organization_id, str(uuid.uuid4()), self.valid_runset)
        self.assertEqual(code, 404)

    def test_create_incorrect(self):
        incorrect_updates = {
            'tags': 2,
            'hyperparameters': 3,
            'application_id': [4],
            'cloud_account_id': True,
            'region_id': '6',
            'instance_type': {7: 7},
            'budget': 'eight',
            'name_prefix': -1,
            'commands': False,
            'destroy_conditions': 0,
            'open_ingress': 11,
            'spot_settings': [12]
        }
        for k, v in incorrect_updates.items():
            valid_runset = self.valid_runset.copy()
            valid_runset[k] = v
            code, _ = self.client.runset_create(
                self.organization_id, self.template_id, valid_runset)
            self.assertEqual(code, 400, k)

    def test_create_unexpected(self):
        valid_runset = self.valid_runset.copy()
        valid_runset['extra'] = 'value'
        code, res = self.client.runset_create(
            self.organization_id, self.template_id, valid_runset)
        self.assertEqual(code, 400)
        self.assertEqual(res.get('error', {}).get('error_code'), 'OE0212')
        valid_runset = self.valid_runset.copy()
        valid_runset['destroy_conditions']['extra'] = 'value'
        code, res = self.client.runset_create(
            self.organization_id, self.template_id, valid_runset)
        self.assertEqual(code, 400)
        self.assertEqual(res.get('error', {}).get('error_code'), 'OE0212')
        valid_runset = self.valid_runset.copy()
        valid_runset['spot_settings']['extra'] = 'value'
        code, res = self.client.runset_create(
            self.organization_id, self.template_id, valid_runset)
        self.assertEqual(code, 400)
        self.assertEqual(res.get('error', {}).get('error_code'), 'OE0212')

    def test_create_spot_settings(self):
        valid_runset = self.valid_runset.copy()
        valid_runset['spot_settings'] = {}
        code, res = self.client.runset_create(
            self.organization_id, self.template_id, valid_runset)
        self.assertEqual(code, 400)
        self.assertEqual(res.get('error', {}).get('error_code'), 'OE0216')
        valid_runset = self.valid_runset.copy()
        valid_runset['spot_settings']['tries'] = 0
        code, res = self.client.runset_create(
            self.organization_id, self.template_id, valid_runset)
        self.assertEqual(code, 400)
        self.assertEqual(res.get('error', {}).get('error_code'), 'OE0224')
        valid_runset = self.valid_runset.copy()
        valid_runset['spot_settings']['tries'] = 65
        code, res = self.client.runset_create(
            self.organization_id, self.template_id, valid_runset)
        self.assertEqual(code, 400)
        self.assertEqual(res.get('error', {}).get('error_code'), 'OE0224')

    def test_create_redefined_tags(self):
        valid_runset = self.valid_runset.copy()
        valid_runset['tags'] = {'key': 'value'}
        code, res = self.client.runset_create(
            self.organization_id, self.template_id, valid_runset)
        self.assertEqual(code, 400)

    def test_create_missing(self):
        for k, v in self.valid_runset.items():
            valid_runset = self.valid_runset.copy()
            valid_runset.pop(k)
            code, res = self.client.runset_create(
                self.organization_id, self.template_id, valid_runset)
            if k in ['destroy_conditions']:
                # destroy_conditions is optional param
                self.assertEqual(code, 201)
                self.assertTrue(isinstance(res.get('destroy_conditions'), dict))
                self.assertEqual(
                    res.get('destroy_conditions', {}).get('max_budget'),
                    self.valid_template['budget'])
            elif k in ['spot_settings', 'open_ingress']:
                # params above are optional and set based on bulldozer logic
                self.assertEqual(code, 201)
            else:
                self.assertEqual(code, 400, k)
                self.assertEqual(res.get('error', {}).get('error_code'), 'OE0216')

    def test_create_nonexisting_entities(self):
        nonexisting_updates = [
            'application_id',  'cloud_account_id', 'instance_type', 'region_id'
        ]
        for k in nonexisting_updates:
            valid_runset = self.valid_runset.copy()
            valid_runset[k] = str(uuid.uuid4())
            code, res = self.client.runset_create(
                self.organization_id, self.template_id, valid_runset)
            # is limited by related template params
            self.assertEqual(code, 400)
            self.assertEqual(res.get('error', {}).get('error_code'), 'OE0538')

    def test_create_deleted_ca(self):
        code, _ = self.client.cloud_account_delete(self.cloud_account_id)
        self.assertEqual(code, 204)
        code, _ = self.client.runset_create(
            self.organization_id, self.template_id, self.valid_runset)
        self.assertEqual(code, 404)

    def test_create_deleted_app(self):
        code, _ = self.client.application_delete(
            self.organization_id, self.application_id)
        self.assertEqual(code, 204)
        code, _ = self.client.runset_create(
            self.organization_id, self.template_id, self.valid_runset)
        self.assertEqual(code, 404)

    def test_create_deleted_owner(self):
        with patch(
                'rest_api.rest_api_server.controllers.employee.EmployeeController.'
                'get_org_manager_user', return_value=self.another_auth_user):
            code, _ = self.client.employee_delete(self.employee_id)
            self.assertEqual(code, 204)
            code, runset = self.client.runset_create(
                self.organization_id, self.template_id, self.valid_runset)
            self.assertEqual(code, 403)

    def test_update(self):
        code, runset = self.client.runset_create(
            self.organization_id, self.template_id, self.valid_runset)
        self.assertEqual(code, 201)
        action = 'stop'
        code, res = self.client.runset_update(
            self.organization_id, runset['id'], {'action': action})
        self.assertEqual(code, 200)
        self.assertEqual(res['state'], 6)

    def test_update_incorrect(self):
        code, runset = self.client.runset_create(
            self.organization_id, self.template_id, self.valid_runset)
        self.assertEqual(code, 201)
        code, res = self.client.runset_update(
            self.organization_id, runset['id'], {'action': 'action'})
        self.assertEqual(code, 400)
        self.assertEqual(res.get('error', {}).get('error_code'), 'OE0545')

    def test_update_unexpected(self):
        code, runset = self.client.runset_create(
            self.organization_id, self.template_id, self.valid_runset)
        self.assertEqual(code, 201)
        code, res = self.client.runset_update(
            self.organization_id, runset['id'], {'extra': 'value'})
        self.assertEqual(code, 400)
        self.assertEqual(res.get('error', {}).get('error_code'), 'OE0212')

    def test_update_nonexisting(self):
        code, _ = self.client.runset_update(
            self.organization_id, str(uuid.uuid4()), {'action': 'stop'})
        self.assertEqual(code, 404)

    def test_update_deleted_ca(self):
        code, runset = self.client.runset_create(
            self.organization_id, self.template_id, self.valid_runset)
        self.assertEqual(code, 201)
        code, _ = self.client.cloud_account_delete(self.cloud_account_id)
        self.assertEqual(code, 204)
        action = 'stop'
        code, res = self.client.runset_update(
            self.organization_id, runset['id'], {'action': action})
        self.assertEqual(code, 200)

    def test_update_deleted_app(self):
        code, runset = self.client.runset_create(
            self.organization_id, self.template_id, self.valid_runset)
        self.assertEqual(code, 201)
        code, _ = self.client.application_delete(
            self.organization_id, self.application_id)
        self.assertEqual(code, 204)
        action = 'stop'
        code, res = self.client.runset_update(
            self.organization_id, runset['id'], {'action': action})
        self.assertEqual(code, 200)

    def test_get(self):
        code, runset = self.client.runset_create(
            self.organization_id, self.template_id, self.valid_runset)
        self.assertEqual(code, 201)
        code, res = self.client.runset_get(self.organization_id, runset['id'])
        self.assertEqual(code, 200)
        self.assertEqual(res.get('duration'), 100)
        # Hardcoded based on duration and flavor cost (hourly cost is 0.224)
        self.assertEqual(res.get('cost'), 0.0062)
        runset['cost'] = res['cost']
        runset['duration'] = res['duration']
        self.assertEqual(res, runset)

    def test_get_deleted_ca(self):
        code, runset = self.client.runset_create(
            self.organization_id, self.template_id, self.valid_runset)
        self.assertEqual(code, 201)
        code, _ = self.client.cloud_account_delete(self.cloud_account_id)
        self.assertEqual(code, 204)
        code, res = self.client.runset_get(self.organization_id, runset['id'])
        self.assertEqual(code, 200)
        self.assertEqual(res['cloud_account']['deleted'], True)

    def test_get_deleted_app(self):
        code, runset = self.client.runset_create(
            self.organization_id, self.template_id, self.valid_runset)
        self.assertEqual(code, 201)
        code, _ = self.client.application_delete(
            self.organization_id, self.application_id)
        self.assertEqual(code, 204)
        code, res = self.client.runset_get(self.organization_id, runset['id'])
        self.assertEqual(code, 200)
        self.assertEqual(res['application']['deleted'], True)

    def test_get_deleted_owner(self):
        code, runset = self.client.runset_create(
            self.organization_id, self.template_id, self.valid_runset)
        self.assertEqual(code, 201)
        with patch(
                'rest_api.rest_api_server.controllers.employee.EmployeeController.'
                'get_org_manager_user', return_value=self.another_auth_user):
            code, _ = self.client.employee_delete(self.employee_id)
            self.assertEqual(code, 204)
            self.change_user(self.another_auth_user)
            code, res = self.client.runset_get(self.organization_id, runset['id'])
            self.assertEqual(code, 200)
            self.assertEqual(res['owner']['deleted'], True)

    def test_get_nonexisting(self):
        code, _ = self.client.runset_get(
            self.organization_id, str(uuid.uuid4()))
        self.assertEqual(code, 404)

    def test_list(self):
        code, runset = self.client.runset_create(
            self.organization_id, self.template_id, self.valid_runset)
        self.assertEqual(code, 201)
        code, res = self.client.runset_list(
            self.organization_id, self.template_id)
        self.assertEqual(code, 200)
        self.assertEqual(res.get('total_runs'), 0)
        self.assertEqual(res.get('total_cost'), 0.0062)
        self.assertEqual(res.get('last_runset_cost'), 0.0062)
        runsets = res.get('runsets')
        self.assertTrue(runsets)
        for r in runsets:
            self.assertEqual(r['id'], runset['id'])

    def test_list_nonexisting(self):
        code, res = self.client.runset_list(
            self.organization_id, str(uuid.uuid4()))
        self.assertEqual(code, 404)

    def test_list_deleted_ca(self):
        code, runset = self.client.runset_create(
            self.organization_id, self.template_id, self.valid_runset)
        self.assertEqual(code, 201)
        code, _ = self.client.cloud_account_delete(self.cloud_account_id)
        self.assertEqual(code, 204)
        code, res = self.client.runset_list(
            self.organization_id, self.template_id)
        self.assertEqual(code, 200)
        runsets = res.get('runsets')
        self.assertTrue(runsets)
        for r in runsets:
            self.assertEqual(r['cloud_account']['deleted'], True)

    def test_list_deleted_app(self):
        code, runset = self.client.runset_create(
            self.organization_id, self.template_id, self.valid_runset)
        self.assertEqual(code, 201)
        code, _ = self.client.application_delete(
            self.organization_id, self.application_id)
        self.assertEqual(code, 204)
        code, res = self.client.runset_list(
            self.organization_id, self.template_id)
        self.assertEqual(code, 200)
        runsets = res.get('runsets')
        self.assertTrue(runsets)
        for r in runsets:
            self.assertEqual(r['application']['deleted'], True)

    def test_list_deleted_owner(self):
        code, runset = self.client.runset_create(
            self.organization_id, self.template_id, self.valid_runset)
        self.assertEqual(code, 201)
        with patch(
                'rest_api.rest_api_server.controllers.employee.EmployeeController.'
                'get_org_manager_user', return_value=self.another_auth_user):
            code, _ = self.client.employee_delete(self.employee_id)
            self.assertEqual(code, 204)
            self.change_user(self.another_auth_user)
            code, res = self.client.runset_list(
                self.organization_id, self.template_id)
            self.assertEqual(code, 200)
            runsets = res.get('runsets')
            self.assertTrue(runsets)
            for r in runsets:
                self.assertEqual(r['owner']['deleted'], True)
