import uuid

from unittest.mock import patch, ANY, call

from rest_api_server.tests.unittests.test_api_base import TestApiBase


class TestCostModelsApi(TestApiBase):
    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.org = self.client.organization_create({'name': 'organization'})
        self.org_id = self.org['id']

        auth_user = self.gen_id()
        self.client.employee_create(
            self.org['id'], {'name': 'employee_1',
                             'auth_user_id': auth_user})
        patch('rest_api_server.controllers.base.BaseController.'
              'get_user_id', return_value=auth_user).start()

        self.p_configure = patch(
            'cloud_adapter.clouds.aws.Aws.configure_report').start()
        valid_aws_config = {
            'name': 'my cloud_acc',
            'type': 'aws_cnr',
            'config': {
                'access_key_id': 'key',
                'secret_access_key': 'secret',
                'config_scheme': 'create_report'
            }
        }
        code, self.aws_cloud_acc = self.create_cloud_account(
            self.org_id, valid_aws_config)
        self.assertEqual(code, 201)

        self.k8s_cost_model = {
            'cpu_hourly_cost': 0.002,
            'memory_hourly_cost': 0.001
        }
        valid_k8s_config = {
            'name': 'k8s cloud_acc',
            'type': 'kubernetes_cnr',
            'config': {
                'user': 'user',
                'password': 'password',
                'cost_model': self.k8s_cost_model
            }
        }
        code, self.k8s_cloud_acc = self.create_cloud_account(
            self.org_id, valid_k8s_config)
        self.assertEqual(code, 201)

        self.env_cost_model = {
            'hourly_cost': 0.05
        }
        self.valid_resource1 = {
            'name': 'resource_1',
            'resource_type': 'test',
        }
        self.valid_resource2 = {
            'name': 'resource_2',
            'resource_type': 'test',
        }

    def test_list(self):
        code, res = self.client.cost_model_list(self.org_id)
        self.assertEqual(code, 200)
        self.assertTrue(isinstance(res, dict))
        self.assertTrue(len(res.get('cost_models', [])), 1)

    def test_list_empty(self):
        code, _ = self.client.cloud_account_delete(self.k8s_cloud_acc['id'])
        self.assertEqual(code, 204)
        code, res = self.client.cost_model_list(self.org_id)
        self.assertEqual(code, 200)
        self.assertTrue(isinstance(res, dict))
        self.assertEqual(len(res.get('cost_models', [])), 0)

    def test_list_wrong_org(self):
        code, res = self.client.cost_model_list(str(uuid.uuid4()))
        self.assertEqual(code, 404)
        self.assertEqual(res['error']['error_code'], 'OE0002')

    def test_list_deleted_org(self):
        patch('rest_api_server.controllers.employee.'
              'EmployeeController.delete').start()
        code, _ = self.client.organization_delete(self.org_id)
        self.assertEqual(code, 204)
        code, res = self.client.cost_model_list(self.org_id)
        self.assertEqual(code, 404)
        self.assertEqual(res['error']['error_code'], 'OE0002')

    def test_get_unsupported_cloud(self):
        cost_model_id = self.aws_cloud_acc['id']
        code, res = self.client.cloud_account_cost_model_get(cost_model_id)
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0436')

    def test_get_wrong_cloud(self):
        code, res = self.client.cloud_account_cost_model_get(
            str(uuid.uuid4()))
        self.assertEqual(code, 404)
        self.assertEqual(res['error']['error_code'], 'OE0002')

    def test_get_deleted_cloud(self):
        code, _ = self.client.cloud_account_delete(self.k8s_cloud_acc['id'])
        self.assertEqual(code, 204)
        code, res = self.client.cloud_account_cost_model_get(
            self.k8s_cloud_acc['id'])
        self.assertEqual(code, 404)
        self.assertEqual(res['error']['error_code'], 'OE0002')

    def test_get_deleted_wrong_cloud(self):
        code, _ = self.client.cloud_account_delete(self.aws_cloud_acc['id'])
        self.assertEqual(code, 204)
        code, res = self.client.cloud_account_cost_model_get(
            self.aws_cloud_acc['id'])
        self.assertEqual(code, 404)
        self.assertEqual(res['error']['error_code'], 'OE0002')

    def test_get_correct_cloud(self):
        cost_model_id = self.k8s_cloud_acc['id']
        code, res = self.client.cloud_account_cost_model_get(cost_model_id)
        self.assertEqual(code, 200)
        for cost_param, cost_value in self.k8s_cloud_acc.get(
                'config', {}).get('cost_model').items():
            self.assertEqual(res.get('value', {}).get(cost_param), cost_value)

    def test_patch_unsupported_cloud(self):
        cost_model_id = self.aws_cloud_acc['id']
        code, res = self.client.cloud_account_cost_model_update(
            cost_model_id, {'value': {'some': 'value'}}
        )
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0436')

    def test_patch_wrong_cloud(self):
        code, res = self.client.cloud_account_cost_model_update(
            str(uuid.uuid4()), {'value': {'some': 'value'}}
        )
        self.assertEqual(code, 404)
        self.assertEqual(res['error']['error_code'], 'OE0002')

    def test_patch_deleted_cloud(self):
        code, _ = self.client.cloud_account_delete(self.k8s_cloud_acc['id'])
        self.assertEqual(code, 204)
        code, res = self.client.cloud_account_cost_model_update(
            self.k8s_cloud_acc['id'], {'value': {'some': 'value'}}
        )
        self.assertEqual(code, 404)
        self.assertEqual(res['error']['error_code'], 'OE0002')

    def test_patch_deleted_wrong_cloud(self):
        code, _ = self.client.cloud_account_delete(self.aws_cloud_acc['id'])
        self.assertEqual(code, 204)
        code, res = self.client.cloud_account_cost_model_update(
            self.aws_cloud_acc['id'], {'value': {'some': 'value'}}
        )
        self.assertEqual(code, 404)
        self.assertEqual(res['error']['error_code'], 'OE0002')

    def test_patch_cloud_wrong_cost_model(self):
        code, res = self.client.cloud_account_cost_model_update(
            self.k8s_cloud_acc['id'], {'value': {'cost': 'model'}}
        )
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0212')

        code, res = self.client.cloud_account_cost_model_update(
            self.k8s_cloud_acc['id'], {'value': [123]}
        )
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0344')

        code, res = self.client.cloud_account_cost_model_update(
            self.k8s_cloud_acc['id'], {'hello': 'world'}
        )
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0216')

        code, res = self.client.cloud_account_cost_model_update(
            self.k8s_cloud_acc['id'],
            {'hello': 'world', 'value': self.k8s_cost_model}
        )
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0212')

        k8s_cost_model = self.k8s_cost_model.copy()
        k8s_cost_model['cpu_hourly_cost'] = 'value'
        code, res = self.client.cloud_account_cost_model_update(
            self.k8s_cloud_acc['id'],
            {'value': k8s_cost_model}
        )
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0466')

    def test_patch_cloud_cost_model(self):
        patch('rest_api_server.controllers.report_import.'
              'ReportImportBaseController.publish_task').start()
        k8s_cost_model = self.k8s_cost_model.copy()
        k8s_cost_model['cpu_hourly_cost'] = 123
        code, res = self.client.cloud_account_cost_model_update(
            self.k8s_cloud_acc['id'],
            {'value': k8s_cost_model}
        )
        self.assertEqual(code, 200)
        for param, value in k8s_cost_model.items():
            self.assertEqual(res['value'][param], value)

        k8s_cost_model['cpu_hourly_cost'] = 0.123
        code, res = self.client.cloud_account_cost_model_update(
            self.k8s_cloud_acc['id'],
            {'value': k8s_cost_model}
        )
        self.assertEqual(code, 200)
        for param, value in k8s_cost_model.items():
            self.assertEqual(res['value'][param], value)

    def test_get_wrong_acc_resource(self):
        self.valid_resource2['cloud_resource_id'] = 'res2_id'
        code, res = self.client.cloud_resource_create_bulk(
            self.aws_cloud_acc['id'],
            {'resources': [self.valid_resource2]},
            return_resources=True, behavior='skip_existing', is_report_import=True)
        self.assertEqual(code, 200)
        resource_id = res['resources'][0]['id']
        code, res = self.client.resource_cost_model_get(resource_id)
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0436')

    def test_get_nonexisting_resource(self):
        code, res = self.client.resource_cost_model_get(str(uuid.uuid4()))
        self.assertEqual(code, 404)
        self.assertEqual(res['error']['error_code'], 'OE0002')

    def test_get_correct_resource(self):
        code, resource = self.environment_resource_create(
            self.org_id, self.valid_resource1)
        self.assertEqual(code, 201)
        code, res = self.client.resource_cost_model_get(resource['id'])
        self.assertEqual(code, 200)
        self.assertIsNotNone(res)
        for cost_param, cost_value in self.env_cost_model.items():
            self.assertEqual(res.get('value', {}).get(cost_param), cost_value)

    def test_patch_wrong_acc_resource(self):
        self.valid_resource2['cloud_resource_id'] = 'res2_id'
        code, res = self.client.cloud_resource_create_bulk(
            self.aws_cloud_acc['id'],
            {'resources': [self.valid_resource2]},
            return_resources=True, behavior='skip_existing', is_report_import=True)
        self.assertEqual(code, 200)
        resource_id = res['resources'][0]['id']
        code, res = self.client.resource_cost_model_update(
            resource_id, {'value': {'cost': 'model'}})
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0436')

    def test_patch_nonexisting_resource(self):
        code, res = self.client.resource_cost_model_update(
            str(uuid.uuid4()), {'value': {'cost': 'model'}})
        self.assertEqual(code, 404)
        self.assertEqual(res['error']['error_code'], 'OE0002')

    def test_recalculation_on_model_change(self):
        patch('rest_api_server.controllers.report_import.'
              'ReportImportBaseController.publish_task').start()
        p_publish_activities = patch(
            'rest_api_server.controllers.base.BaseController.'
            'publish_activities_task'
        ).start()
        valid_resource = {
            'name': 'resource',
            'resource_type': 'some_env_type',
            'tags': {}
        }
        code, resource = self.client.environment_resource_create(
            self.org_id, valid_resource)
        self.assertEqual(code, 201)
        code, res = self.client.resource_cost_model_update(
            resource['id'], {'value': {'hourly_cost': 12.0}})
        self.assertEqual(code, 200)
        activity_param_tuples = self.get_publish_activity_tuple(
            self.org_id, ANY, 'report_import',
            'recalculation_started', {
                'object_name': 'Environment',
                'cloud_account_id': ANY,
                'level': 'INFO'
            })
        p_publish_activities.assert_has_calls([
            call(*activity_param_tuples, add_token=True)
        ])

    def test_patch_correct_resource(self):
        patch('rest_api_server.controllers.report_import.'
              'ReportImportBaseController.publish_task').start()
        code, resource = self.environment_resource_create(
            self.org_id, self.valid_resource1)
        self.assertEqual(code, 201)
        model_value = {'hourly_cost': 1}
        code, res = self.client.resource_cost_model_update(
            resource['id'], {'value': {'hourly_cost': 1}})
        self.assertEqual(code, 200)
        self.assertIsNotNone(res)
        self.assertDictEqual(res.get('value'), model_value)
