import uuid

from unittest.mock import call, patch, ANY

from rest_api.rest_api_server.tests.unittests.test_api_base import TestApiBase


class TestEnvironmentResourceApi(TestApiBase):

    def setUp(self, version='v2'):
        super().setUp(version)
        patch('rest_api.rest_api_server.controllers.cloud_account.'
              'CloudAccountController._configure_report').start()
        _, self.org = self.client.organization_create({'name': "organization"})
        self.org_id = self.org['id']
        self.auth_user = self.gen_id()
        _, self.employee = self.client.employee_create(
            self.org['id'], {'name': 'employee_1',
                             'auth_user_id': self.auth_user})
        aws_cloud_acc = {
            'name': 'my cloud_acc',
            'type': 'aws_cnr',
            'config': {
                'access_key_id': 'key',
                'secret_access_key': 'secret',
                'config_scheme': 'create_report'
            }
        }
        _, self.cloud_acc = self.create_cloud_account(
            self.org_id, aws_cloud_acc, auth_user_id=self.auth_user)
        self.cloud_acc_id = self.cloud_acc['id']
        self.valid_resource = {
            'cloud_resource_id': 'res_id',
            'name': 'resource',
            'resource_type': 'some_env_type',
            'tags': {}
        }
        self.valid_resource2 = {
            'cloud_resource_id': 'res_id_2',
            'name': 'resource',
            'resource_type': 'some_env_type',
            'tags': {}
        }

    def check_environment_account_missing(self):
        code, res = self.client.cloud_account_list(self.org_id)
        self.assertEqual(code, 200)
        for cloud_acc in res['cloud_accounts']:
            self.assertTrue(cloud_acc['type'] != 'environment')

    def check_environment_account_exists(self):
        code, res = self.client.cloud_account_list(self.org_id)
        self.assertEqual(code, 200)
        cloud_acc_types = set()
        for cloud_acc in res['cloud_accounts']:
            cloud_acc_types.add(cloud_acc['type'])
        self.assertTrue('environment' in cloud_acc_types)

    def test_list_empty(self):
        code, res = self.client.environment_resource_list(self.org_id)
        self.assertEqual(code, 200)
        self.assertEqual(len(res['resources']), 0)
        self.check_environment_account_missing()

    def test_list(self):
        self.valid_resource.pop('cloud_resource_id')
        code, _ = self.client.environment_resource_create(
            self.org_id, self.valid_resource)
        self.assertEqual(code, 201)
        self.check_environment_account_exists()

        code, _ = self.client.cloud_resource_create(
            self.cloud_acc_id, self.valid_resource2)
        self.assertEqual(code, 201)

        code, res = self.client.environment_resource_list(self.org_id)
        self.assertEqual(code, 200)
        self.assertEqual(len(res['resources']), 1)
        self.assertTrue(res['resources'].pop().get('is_environment', False))

    def test_list_nonexisting_org(self):
        code, res = self.client.environment_resource_list(str(uuid.uuid4()))
        self.assertEqual(code, 404)
        self.assertEqual(res['error']['error_code'], 'OE0002')

    def test_get_nonexisting(self):
        code, res = self.client.environment_resource_get(str(uuid.uuid4()))
        self.assertEqual(code, 404)
        self.assertEqual(res['error']['error_code'], 'OE0002')
        self.check_environment_account_missing()

    def test_get(self):
        self.valid_resource.pop('cloud_resource_id')
        code, res = self.client.environment_resource_create(
            self.org_id, self.valid_resource)
        self.assertEqual(code, 201)
        self.check_environment_account_exists()

        code, res_1 = self.client.environment_resource_get(res['id'])
        self.assertEqual(code, 200)
        self.assertEqual(res['cloud_resource_id'], res_1['cloud_resource_id'])

    def test_get_wrong_ca_type(self):
        code, resource = self.cloud_resource_create(
            self.cloud_acc_id, self.valid_resource)
        self.assertEqual(code, 201)

        code, res = self.client.environment_resource_get(resource['id'])
        self.assertEqual(code, 404)
        self.assertEqual(res['error']['error_code'], 'OE0002')

    def test_delete_nonexisting(self):
        code, res = self.client.environment_resource_delete(str(uuid.uuid4()))
        self.assertEqual(code, 404)
        self.assertEqual(res['error']['error_code'], 'OE0002')

    def test_delete(self):
        self.valid_resource.pop('cloud_resource_id')
        code, res = self.client.environment_resource_create(
            self.org_id, self.valid_resource)
        self.assertEqual(code, 201)

        code, res_1 = self.client.environment_resource_delete(res['id'])
        self.assertEqual(code, 204)
        self.check_environment_account_exists()

    def test_create_nonexisting_org(self):
        code, res = self.environment_resource_create(
            str(uuid.uuid4()), self.valid_resource)
        self.assertEqual(code, 404)
        self.assertEqual(res['error']['error_code'], 'OE0002')

    def test_create_immutable(self):
        valid_resource = self.valid_resource.copy()
        code, res = self.environment_resource_create(
            self.org_id, self.valid_resource)
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0211')

        valid_resource = self.valid_resource.copy()
        valid_resource.pop('cloud_resource_id')
        valid_resource['is_environment'] = True
        valid_resource['shareable'] = True
        code, res = self.environment_resource_create(
            self.org_id, self.valid_resource)
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0211')

        valid_resource = self.valid_resource.copy()
        valid_resource.pop('cloud_resource_id')
        valid_resource['created_at'] = 12345678
        code, res = self.environment_resource_create(
            self.org_id, self.valid_resource)
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0211')

    def test_create_unexpected(self):
        valid_resource = self.valid_resource.copy()
        valid_resource.pop('cloud_resource_id')
        valid_resource['region'] = 'Uganda'
        code, res = self.environment_resource_create(
            self.org_id, valid_resource)
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0212')

    def test_create(self):
        self.valid_resource.pop('cloud_resource_id')
        code, res = self.environment_resource_create(
            self.org_id, self.valid_resource)
        self.assertEqual(code, 201)
        for k, v in self.valid_resource.items():
            self.assertEqual(res[k], v)
        self.assertTrue(res['is_environment'])
        self.assertTrue(res['shareable'])
        self.assertTrue(res.get('active'))
        code, res = self.client.resource_cost_model_get(res['id'])
        self.assertEqual(code, 200)
        self.check_environment_account_exists()
        self.valid_resource['env_properties'] = {'field': 'value'}
        self.valid_resource['name'] = 'resource2'
        code, res = self.environment_resource_create(
            self.org_id, self.valid_resource)
        self.assertEqual(code, 201)
        self.assertEqual(len(list(self.property_history_collection.find())), 1)

    def test_create_tags(self):
        self.valid_resource.pop('cloud_resource_id')
        self.valid_resource['tags'] = {'tk': 'tv'}
        code, res = self.environment_resource_create(
            self.org_id, self.valid_resource)
        self.assertEqual(code, 201)
        self.assertNotEqual(res['tags'], {})

    def test_create_with_employee(self):
        code, employee = self.client.employee_create(
            self.org_id, {'name': 'John Smith'})
        self.assertEqual(code, 201)
        valid_resource = self.valid_resource.copy()
        valid_resource.pop('cloud_resource_id')
        valid_resource.update({
            'employee_id': employee['id'],
            'pool_id': self.org['pool_id']
        })
        code, res = self.environment_resource_create(
            self.org_id, valid_resource, set_allowed=True)
        self.assertEqual(code, 201)
        self.assertEqual(res['employee_id'], employee['id'])
        self.assertEqual(res['pool_id'], self.org['pool_id'])

    def test_create_clustering(self):
        code, ct = self.client.cluster_type_create(
            self.org_id, {'name': 'my_ct', 'tag_key': 'tn'})
        self.assertEqual(code, 201)
        valid_resource = self.valid_resource.copy()
        valid_resource.pop('cloud_resource_id')
        valid_resource['tags'] = {'tn': 'tv'}
        code, res = self.environment_resource_create(
            self.org_id, valid_resource)
        self.assertEqual(code, 201)
        self.assertIsNotNone(res.get('cluster_id'))

    def test_create_activities_task(self):
        patch('rest_api.rest_api_server.controllers.base.'
              'BaseController.publish_activities_task').start()
        alert_params = {
            'pool_id': self.org['pool_id'],
            'threshold': 0,
            'contacts': [{'slack_channel_id': 'channel',
                          'slack_team_id': 'team'}],
            'based': 'env_change'
        }
        code, alert = self.client.alert_create(self.org['pool_id'],
                                               alert_params)
        self.assertEqual(code, 201)
        p_disp_task = patch('rest_api.rest_api_server.controllers.base.'
                            'BaseController.publish_activities_task').start()
        resource = self.valid_resource.copy()
        resource.pop('cloud_resource_id')
        resource['env_properties'] = {"test_will_pass": "yes"}
        code, res = self.environment_resource_create(self.org_id, resource)
        self.assertEqual(code, 201)
        meta = {
            'alert_id': alert['id'],
            'env_properties': ANY
        }
        p_disp_task.assert_has_calls([
            call(self.org_id, res['id'], 'resource', 'env_property_updated',
                 meta, 'alert.violation.env_change')])

    def test_create_activities_task_with_employee_contact(self):
        patch('rest_api.rest_api_server.controllers.base.'
              'BaseController.publish_activities_task').start()
        alert_params = {
            'pool_id': self.org['pool_id'],
            'threshold': 0,
            'contacts': [{'employee_id': self.employee['id']}],
            'based': 'env_change'
        }
        code, alert = self.client.alert_create(self.org['pool_id'],
                                               alert_params)
        self.assertEqual(code, 201)
        p_disp_task = patch('rest_api.rest_api_server.controllers.base.'
                            'BaseController.publish_activities_task').start()
        resource = self.valid_resource.copy()
        resource.pop('cloud_resource_id')
        resource['env_properties'] = {"test_will_pass": "yes"}
        code, res = self.environment_resource_create(self.org_id, resource)
        self.assertEqual(code, 201)
        meta = {
            'alert_id': alert['id'],
            'env_properties': ANY
        }
        p_disp_task.assert_has_calls([
            call(self.org_id, res['id'], 'resource', 'env_property_updated',
                 meta, 'alert.violation.env_change')
        ])

    def test_patch(self):
        patch('rest_api.rest_api_server.controllers.base.'
              'BaseController.publish_activities_task').start()
        self.valid_resource.pop('cloud_resource_id')
        code, res = self.environment_resource_create(
            self.org_id, self.valid_resource)
        self.assertEqual(code, 201)
        code, res = self.client.environment_resource_update(
            res['id'], {'active': False})
        self.assertEqual(code, 200)
        self.assertFalse(res['active'])
        env_props = {'field': 'val'}
        code, res = self.client.environment_resource_update(
            res['id'], {'env_properties': env_props})
        self.assertEqual(code, 200)
        self.assertEqual(res['env_properties'], env_props)
        self.assertEqual(code, 200)
        self.assertEqual(len(list(self.property_history_collection.find())), 1)

        env_props = {'field': 'val2'}
        code, res = self.client.environment_resource_update(
            res['id'], {
                'active': True,
                'env_properties': env_props
            }
        )
        self.assertEqual(code, 200)
        self.assertTrue(res['active'])
        self.assertEqual(res['env_properties'], env_props)
        self.assertEqual(code, 200)
        self.assertEqual(len(list(self.property_history_collection.find())), 2)

    def test_patch_activities_task(self):
        self.valid_resource.pop('cloud_resource_id')
        code, res = self.environment_resource_create(
            self.org_id, self.valid_resource)
        self.assertEqual(code, 201)
        alert_params = {
            'pool_id': self.org['pool_id'],
            'threshold': 0,
            'contacts': [{'slack_channel_id': 'channel',
                          'slack_team_id': 'team'}],
            'based': 'env_change'
        }
        code, alert = self.client.alert_create(self.org['pool_id'],
                                               alert_params)
        self.assertEqual(code, 201)
        p_disp_task = patch('rest_api.rest_api_server.controllers.base.'
                            'BaseController.publish_activities_task').start()

        # resource state changed: active -> not active
        code, res = self.client.environment_resource_update(
            res['id'], {'active': False})
        res['active'] = True
        self.assertEqual(code, 200)
        meta = {
            'alert_id': alert['id'],
            'previous_state': 'Active',
            'new_state': 'Not Active'
        }
        p_disp_task.assert_called_once_with(
            self.org_id, res['id'], 'resource', 'env_active_state_changed',
            meta, 'alert.violation.env_change')
        p_disp_task.reset_mock()

        # env_properties updated
        code, _ = self.client.alert_delete(alert['id'])
        alert_params = {
            'pool_id': self.org['pool_id'],
            'threshold': 0,
            'contacts': [{'employee_id': self.employee['id']}],
            'based': 'env_change'
        }
        code, alert = self.client.alert_create(self.org['pool_id'],
                                               alert_params)
        self.assertEqual(code, 201)
        p_disp_task.reset_mock()

        param = {'env_properties': {'test_will_pass': 'yes'}}
        code, res = self.client.environment_resource_update(
            res['id'], param)
        res.pop('env_properties', None)
        self.assertEqual(code, 200)
        meta = {
            'alert_id': alert['id'],
            'env_properties': ANY
        }
        p_disp_task.assert_called_once_with(
            self.org_id, res['id'], 'resource', 'env_property_updated', meta,
            'alert.violation.env_change')

    def test_patch_activities_task_without_alert(self):
        self.valid_resource.pop('cloud_resource_id')
        code, res = self.environment_resource_create(
            self.org_id, self.valid_resource)
        self.assertEqual(code, 201)
        p_disp_task = patch('rest_api.rest_api_server.controllers.base.'
                            'BaseController.publish_activities_task').start()

        # resource state changed: active -> not active
        code, res = self.client.environment_resource_update(
            res['id'], {'active': False})
        res['active'] = True
        self.assertEqual(code, 200)
        meta = {
            'previous_state': 'Active',
            'new_state': 'Not Active'
        }
        p_disp_task.assert_called_once_with(
            self.org_id, res['id'], 'resource', 'env_active_state_changed',
            meta, 'alert.violation.env_change')
        p_disp_task.reset_mock()

        # env_properties updated
        param = {'env_properties': {'test_will_pass': 'yes'}}
        code, res = self.client.environment_resource_update(
            res['id'], param)
        res.pop('env_properties', None)
        self.assertEqual(code, 200)
        meta = {
            'env_properties': ANY
        }
        p_disp_task.assert_called_once_with(
            self.org_id, res['id'], 'resource', 'env_property_updated', meta,
            'alert.violation.env_change')

    def test_get_first_shareable_email(self):
        send_email_patch = self.mock_email_send_enable()
        self.valid_resource.pop('cloud_resource_id')
        code, res = self.environment_resource_create(
            self.org_id, self.valid_resource)
        self.assertEqual(code, 201)
        send_email_patch.assert_called_once_with(
            [ANY], 'OptScale shareable resources notification',
            template_type='first_shareable_resources',
            template_params={
                'texts': {'organization': {
                    'id': self.org['id'],
                    'name': self.org['name'],
                    'currency_code': '$'},
                    'title': 'First shareable resource',
                    'shareable_resource_count': 1}}
        )
        send_email_patch.stop()
        send_email_patch_2 = self.mock_email_send_enable()
        self.valid_resource['name'] = 'resource_2'
        self.valid_resource['resource_type'] = 'resource_type_2'
        code, res = self.environment_resource_create(
            self.org_id, self.valid_resource)
        self.assertEqual(code, 201)
        self.assertEqual(send_email_patch_2.call_count, 0)

    def test_recreation(self):
        self.valid_resource.pop('cloud_resource_id')
        code, res = self.environment_resource_create(
            self.org_id, self.valid_resource)
        self.assertEqual(code, 201)
        code, _ = self.client.environment_resource_delete(res['id'])
        self.assertEqual(code, 204)
        code, res = self.environment_resource_create(
            self.org_id, self.valid_resource)
        self.assertEqual(code, 201)

    def test_create_ssh_only(self):
        self.valid_resource.pop('cloud_resource_id')
        self.valid_resource['active'] = False
        self.valid_resource['ssh_only'] = True
        code, res = self.client.environment_resource_create(
            self.org_id, self.valid_resource)
        self.assertEqual(code, 201)
        self.assertEqual(res['active'], False)
        self.assertEqual(res['ssh_only'], True)

    def test_update_ssh_only(self):
        self.valid_resource.pop('cloud_resource_id')
        self.valid_resource['active'] = False
        code, res = self.client.environment_resource_create(
            self.org_id, self.valid_resource)
        self.assertEqual(code, 201)
        self.assertEqual(res['ssh_only'], False)

        code, res = self.client.environment_resource_update(
            res['id'], {'ssh_only': True})
        self.assertEqual(code, 200)
        self.assertEqual(res['ssh_only'], True)
