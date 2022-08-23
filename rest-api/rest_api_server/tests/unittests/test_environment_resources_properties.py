import datetime

from unittest.mock import patch, ANY

from freezegun import freeze_time

from rest_api_server.tests.unittests.test_api_base import TestApiBase


class TestEnvironmentResourceApi(TestApiBase):

    def setUp(self, version='v2'):
        super().setUp(version)
        patch('rest_api_server.controllers.cloud_account.'
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
        _, invalid_resource = self.cloud_resource_create(
            self.cloud_acc_id, {
                'cloud_resource_id': 'res_id',
                'name': 'resource',
                'resource_type': 'some_env_type',
                'tags': {}
            })
        self.invalid_resource_id = invalid_resource['id']
        _, env_resource = self.environment_resource_create(
            self.org_id, {
                'name': 'resource',
                'resource_type': 'some_env_type',
                'tags': {}
            })
        self.env_resource_id = env_resource['id']
        self.history_default_keys = ['_id', 'resource_id', 'time', 'changes']

    @patch('config_client.client.Client.public_ip')
    def test_get_script(self, m_public_ip):
        m_public_ip.return_value = '172.22.22.22'
        code, _ = self.client.env_properties_script_get('1234')
        self.assertEqual(code, 404)
        code, resp = self.client.env_properties_script_get(
            self.invalid_resource_id)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0480')
        code, resp = self.client.env_properties_script_get(self.env_resource_id)
        self.assertEqual(code, 200)
        self.assertIn(self.env_resource_id, resp['script'])

    def test_send_properties(self):
        code, _ = self.client.env_properties_send(self.env_resource_id, {})
        self.assertEqual(code, 204)
        code, resp = self.client.cloud_resource_get(self.env_resource_id)
        self.assertEqual(code, 200)
        self.assertEqual(resp.get('env_properties'), {})
        history = list(self.property_history_collection.find())
        self.assertEqual(len(history), 1)
        self.assertCountEqual(history[0].keys(), self.history_default_keys)

        init_props = {
            'field1': 'value1', 'field2': 'value2', 'field3': 'value3'}
        code, _ = self.client.env_properties_send(
            self.env_resource_id, init_props)
        self.assertEqual(code, 204)
        code, resp = self.client.cloud_resource_get(self.env_resource_id)
        self.assertEqual(code, 200)
        self.assertEqual(resp.get('env_properties'), init_props)
        history = list(self.property_history_collection.find())
        self.assertEqual(len(history), 2)
        self.assertCountEqual(
            history[1]['changes'].keys(), list(init_props.keys()))
        for key, value in history[1]['changes'].items():
            self.assertEqual(init_props.get(key), value.get('new'))
            self.assertIsNone(value.get('old'))

        new_props = {
            'field1': 'key1', 'field3': 'value3', 'field4': 'another_value'}
        code, _ = self.client.env_properties_send(
            self.env_resource_id, new_props)
        self.assertEqual(code, 204)
        code, resp = self.client.cloud_resource_get(self.env_resource_id)
        self.assertEqual(code, 200)
        result_props = resp.get('env_properties', {})
        for key, value in result_props.items():
            if new_props.get(key):
                self.assertEqual(new_props.get(key), result_props.get(key))
            else:
                self.assertEqual(init_props.get(key), result_props.get(key))
        self.assertEqual(set(init_props) - set(result_props), set())
        self.assertEqual(set(new_props) - set(result_props), set())
        history = list(self.property_history_collection.find())
        self.assertEqual(len(history), 3)
        self.assertCountEqual(
            history[2]['changes'].keys(), list(new_props.keys()))
        for key, value in history[2]['changes'].items():
            self.assertEqual(new_props.get(key), value.get('new'))
            self.assertEqual(init_props.get(key), value.get('old'))

        new_props = {'field1': None}
        code, _ = self.client.env_properties_send(
            self.env_resource_id, new_props)
        self.assertEqual(code, 204)
        code, resp = self.client.cloud_resource_get(self.env_resource_id)
        self.assertEqual(code, 200)
        result_props = resp.get('env_properties', {})
        self.assertNotIn('field1', result_props.keys())

    def test_send_properties_slack_message(self):
        p_send_msg = patch('rest_api_server.controllers.base.'
                           'BaseController.publish_activities_task').start()
        env_alert = {
            'based': 'env_change',
            'pool_id': self.org['pool_id'],
            'contacts': [{'slack_channel_id': 'superchannel',
                          'slack_team_id': 'superteam'}],
            'threshold': 0
        }
        code, pool_alert = self.client.alert_create(self.org_id, env_alert)
        self.assertEqual(code, 201)
        p_send_msg.reset_mock()

        props = {'field1': 'value1'}
        code, _ = self.client.env_properties_send(
            self.env_resource_id, props)
        self.assertEqual(code, 204)
        meta = {
                'alert_id': pool_alert['id'],
                'env_properties': ANY
        }
        p_send_msg.assert_called_once_with(
            self.org_id, self.env_resource_id, 'resource',
            'env_property_updated', meta, 'alert.violation.env_change')

    def test_send_invalid_properties(self):
        code, _ = self.client.env_properties_send('1234', {})
        self.assertEqual(code, 404)
        code, resp = self.client.env_properties_send(
            self.invalid_resource_id, {})
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0480')
        history = list(self.property_history_collection.find())
        self.assertEqual(len(history), 0)

    def test_send_properties_without_autorization(self):
        cl_secret = self.client.secret
        cl_token = self.client.token
        self.client.secret = None
        self.client.token = None
        init_props = {'some_field': 'some_value'}
        code, _ = self.client.env_properties_send(
            self.env_resource_id, init_props)
        self.assertEqual(code, 204)
        self.client.secret = cl_secret
        self.client.token = cl_token
        code, resp = self.client.cloud_resource_get(self.env_resource_id)
        self.assertEqual(code, 200)
        self.assertEqual(resp.get('env_properties'), init_props)
        history = list(self.property_history_collection.find())
        self.assertEqual(len(history), 1)

    def test_send_properties_double(self):
        init_props = {'some_field': 'some_value'}
        now = datetime.datetime.utcnow()
        with freeze_time(now):
            code, _ = self.client.env_properties_send(
                self.env_resource_id, init_props)
            self.assertEqual(code, 204)
            code, _ = self.client.env_properties_send(
                self.env_resource_id, init_props)
            self.assertEqual(code, 204)
        history = list(self.property_history_collection.find())
        self.assertEqual(len(history), 2)

    def test_get_history(self):
        code, env_resource = self.environment_resource_create(
            self.org_id, {
                'name': 'resource2',
                'resource_type': 'some_env_type2',
                'tags': {}
            })
        self.assertEqual(code, 201)
        property_history = [
            {
                'resource_id': self.env_resource_id,
                'time': 20,
                'changes': {
                    'field1': {
                        'old': 'value1',
                        'new': 'value2'
                    }
                }
            },
            {
                'resource_id': self.env_resource_id,
                'time': 10,
                'changes': {
                    'field1': {
                        'old': None,
                        'new': 'value1'
                    }
                }
            },
            {
                'resource_id': env_resource['id'],
                'time': 15,
                'changes': {
                    'field1': {
                        'old': None,
                        'new': 'value1'
                    }
                }
            },
            {
                'resource_id': env_resource['id'],
                'time': 25,
                'changes': {
                    'field1': {
                        'old': 'value1',
                        'new': 'value2'
                    }
                }
            }
        ]
        r = self.property_history_collection.insert_many(property_history)
        self.assertEqual(len(r.inserted_ids), len(property_history))
        for prop in property_history:
            prop.pop('_id', None)
        code, resp = self.client.env_properties_history_get(
            self.env_resource_id)
        self.assertEqual(code, 200)
        self.assertEqual(
            resp['history'], [property_history[1], property_history[0]])
        code, resp = self.client.env_properties_history_get(
            self.env_resource_id, start_date=15)
        self.assertEqual(code, 200)
        self.assertEqual(resp['history'], [property_history[0]])
        code, resp = self.client.env_properties_history_get(
            self.env_resource_id, end_date=15)
        self.assertEqual(code, 200)
        self.assertEqual(resp['history'], [property_history[1]])
        code, resp = self.client.env_properties_history_get(
            self.env_resource_id, start_date=15, end_date=30)
        self.assertEqual(code, 200)
        self.assertEqual(resp['history'], [property_history[0]])
        code, resp = self.client.env_properties_history_get(
            env_resource['id'], start_date=15, end_date=30)
        self.assertEqual(code, 200)
        self.assertEqual(
            resp['history'], [property_history[2], property_history[3]])

    def test_get_history_invalid(self):
        code, _ = self.client.env_properties_history_get('1234')
        self.assertEqual(code, 404)
        code, resp = self.client.env_properties_history_get(
            self.invalid_resource_id)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0480')
        code, resp = self.client.env_properties_history_get('1234', 2, 1)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0446')
        code, resp = self.client.env_properties_history_get('1234', -1, 1)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0224')
