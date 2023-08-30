import uuid
from datetime import datetime
from unittest.mock import patch, ANY

from freezegun import freeze_time

from rest_api.rest_api_server.models.enums import ThresholdBasedTypes, ThresholdTypes
from rest_api.rest_api_server.tests.unittests.test_api_base import TestApiBase


class TestPoolAlertsApi(TestApiBase):
    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.organization_1 = self.client.organization_create({
            'name': 'test organization 1_1'})
        self.auth_user_1 = self.gen_id()
        _, self.employee_1_1 = self.client.employee_create(
            self.organization_1['id'], {'name': 'employee 1_1',
                                        'auth_user_id': self.auth_user_1})
        _, self.employee_1_2 = self.client.employee_create(
            self.organization_1['id'], {'name': 'employee 1_2',
                                        'auth_user_id': self.gen_id()})
        _, self.pool1_1 = self.client.pool_create(self.organization_1['id'], {
            'name': 'test pool 1_2',
            'parent_id': self.organization_1['pool_id']
        })
        _, self.organization_2 = self.client.organization_create({
            'name': 'test organization 2'})
        self.auth_user_2 = self.gen_id()
        _, self.employee_2 = self.client.employee_create(
            self.organization_2['id'], {'name': 'employee 2',
                                        'auth_user_id': self.auth_user_2})
        patch('rest_api.rest_api_server.controllers.cloud_account.'
              'CloudAccountController._configure_report').start()
        self.p_send_message = patch(
            'rest_api.rest_api_server.controllers.base.'
            'BaseController.publish_activities_task').start()
        self.cloud_acc_dict = {
            'name': 'my cloud_acc',
            'type': 'aws_cnr',
            'config': {
                'access_key_id': 'key',
                'secret_access_key': 'secret',
                'bucket_name': 'name',
                'config_scheme': 'create_report'
            }
        }

    def test_create(self):
        body = {
            'pool_id': self.organization_1['pool_id'],
            'contacts': [
                {'employee_id': self.employee_1_1['id']},
                {'employee_id': self.employee_1_2['id']},
            ],
            'threshold': 80
        }
        code, response = self.client.alert_create(
            self.organization_1['id'], body)
        self.assertEqual(code, 201)
        self.assertEqual(response['threshold'], 80)
        self.assertEqual(
            response['threshold_type'], ThresholdTypes.ABSOLUTE.value)
        self.assertEqual(response['based'], ThresholdBasedTypes.COST.value)

    def test_create_invalid_contacts(self):
        body = {
            'pool_id': self.organization_1['pool_id'],
            'threshold': 80
        }
        code, response = self.client.alert_create(
            self.organization_1['id'], body)
        self.assertEqual(code, 400)
        self.assertEqual(
            response['error']['reason'], 'contacts is not provided')
        body.update({'contacts': 1})
        code, response = self.client.alert_create(
            self.organization_1['id'], body)
        self.assertEqual(code, 400)
        self.assertEqual(
            response['error']['reason'], 'contacts should be a list')
        body = {
            'pool_id': self.organization_1['pool_id'],
            'threshold': 80,
            'contacts': []
        }
        code, response = self.client.alert_create(
            self.organization_1['id'], body)
        self.assertEqual(code, 400)
        self.assertEqual(
            response['error']['reason'], 'contacts is not provided')

        body = {
            'pool_id': self.organization_1['pool_id'],
            'threshold': 80,
            'contacts': [{'employee_id': 'id', 'slack_channel_id': 'id'}]
        }
        code, response = self.client.alert_create(
            self.organization_1['id'], body)
        self.assertEqual(code, 400)
        self.verify_error_code(response, 'OE0462')

        body = {
            'pool_id': self.organization_1['pool_id'],
            'threshold': 80,
            'contacts': [{'test': 'test'}]
        }
        code, response = self.client.alert_create(
            self.organization_1['id'], body)
        self.assertEqual(code, 400)
        self.verify_error_code(response, 'OE0462')

    def test_create_invalid_threshold(self):
        body = {
            'pool_id': self.organization_1['pool_id'],
            'contacts': [{'employee_id': str(uuid.uuid4())}],
            'threshold': None
        }
        code, response = self.client.alert_create(
            self.organization_1['id'], body)
        self.assertEqual(code, 400)
        self.assertEqual(
            response['error']['reason'], 'threshold is not provided')
        body.update({'threshold': '123'})
        code, response = self.client.alert_create(
            self.organization_1['id'], body)
        self.assertEqual(code, 400)
        self.assertEqual(
            response['error']['reason'], 'threshold should be integer')
        body.update({'threshold': -1})
        code, response = self.client.alert_create(
            self.organization_1['id'], body)
        self.assertEqual(code, 400)
        self.assertEqual(
            response['error']['reason'],
            'Value of "threshold" should be between 0 and 2147483647')

    def test_create_invalid_threshold_type(self):
        body = {
            'pool_id': self.organization_1['pool_id'],
            'threshold': 80,
            'contacts': [{'employee_id': self.employee_1_1['id']}],
            'threshold_type': 'asd'
        }
        code, response = self.client.alert_create(
            self.organization_1['id'], body)
        self.assertEqual(code, 400)
        self.assertEqual(
            response['error']['reason'],
            "Bad request: 'asd' is not a valid ThresholdTypes")

    def test_create_valid_threshold_type(self):
        body = {
            'pool_id': self.organization_1['pool_id'],
            'threshold': 80,
            'contacts': [{'employee_id': self.employee_1_1['id']}],
            'threshold_type': 'percentage'
        }
        code, response = self.client.alert_create(
            self.organization_1['id'], body)
        self.assertEqual(code, 201)
        self.assertEqual(
            response['threshold_type'], ThresholdTypes.PERCENTAGE.value)

    def test_create_invalid_based(self):
        body = {
            'pool_id': self.organization_1['pool_id'],
            'threshold': 80,
            'contacts': [{'employee_id': self.employee_1_1['id']}],
            'based': 'asd'
        }
        code, response = self.client.alert_create(
            self.organization_1['id'], body)
        self.assertEqual(code, 400)
        self.assertEqual(
            response['error']['reason'],
            "Bad request: 'asd' is not a valid ThresholdBasedTypes")

    def test_create_valid_based(self):
        based = [ThresholdBasedTypes.FORECAST.value,
                 ThresholdBasedTypes.COST.value,
                 ThresholdBasedTypes.CONSTRAINT.value,
                 ThresholdBasedTypes.ENV_CHANGE.value]
        for b in based:
            body = {
                'pool_id': self.organization_1['pool_id'],
                'threshold': 80,
                'contacts': [{'employee_id': self.employee_1_1['id']}],
                'based': b
            }
            code, response = self.client.alert_create(
                self.organization_1['id'], body)
            self.assertEqual(code, 201)
            self.assertEqual(response['based'], b)

    def test_create_immutable_params(self):
        body = {
            'pool_id': self.organization_1['pool_id'],
            'threshold': 80,
            'contacts': [{'employee_id': self.employee_1_1['id']}],
            'deleted_at': 1
        }
        code, response = self.client.alert_create(
            self.organization_1['id'], body)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['reason'],
                         'Parameter "deleted_at" is immutable')

    def test_create_unexpected_params(self):
        body = {
            'pool_id': self.organization_1['pool_id'],
            'threshold': 80,
            'contacts': [{'employee_id': self.employee_1_1['id']}],
            'some': 'value'
        }
        code, response = self.client.alert_create(
            self.organization_1['id'], body)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['reason'],
                         "Unexpected parameters: ['some']")

    def test_invalid_contact_uuid(self):
        uuid_1 = str(uuid.uuid4())
        uuid_2 = self.employee_2['id']
        body = {
            'pool_id': self.organization_1['pool_id'],
            'contacts': [
                {'employee_id': uuid_1},
                {'employee_id': uuid_2},
            ],
            'threshold': 80
        }
        code, response = self.client.alert_create(
            self.organization_1['id'], body)
        self.assertEqual(code, 400)
        self.verify_error_code(response, 'OE0386')

    def test_invalid_contact_uuid_format(self):
        uuid_1 = {'invalid': 'format'}
        uuid_2 = self.employee_2['id']
        body = {
            'pool_id': self.organization_1['pool_id'],
            'contacts': [
                {'employee_id': uuid_1},
                {'employee_id': uuid_2},
            ],
            'threshold': 80
        }
        code, response = self.client.alert_create(
            self.organization_1['id'], body)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['reason'],
                         'employee_id should be a string')

    def test_invalid_pool_id(self):
        pool_id = str(uuid.uuid4())
        body = {
            'pool_id': pool_id,
            'contacts': [
                {'employee_id': str(uuid.uuid4())}
            ],
            'threshold': 80
        }
        code, response = self.client.alert_create(self.organization_1['id'], body)
        self.assertEqual(code, 404)
        self.assertEqual(response['error']['reason'],
                         'Pool %s not found' % pool_id)

    def test_patch(self):
        body = {
            'pool_id': self.pool1_1['id'],
            'contacts': [
                {'employee_id': self.employee_1_1['id']}
            ],
            'threshold': 80
        }
        _, alert = self.client.alert_create(
            self.organization_1['id'], body)
        code, response = self.client.alert_update(
            alert['id'], {
                'threshold': 70,
                'threshold_type': ThresholdTypes.PERCENTAGE.value
            })
        self.assertEqual(code, 200)
        self.assertEqual(response['threshold'], 70)
        self.assertEqual(
            response['threshold_type'], ThresholdTypes.PERCENTAGE.value)

    def test_patch_contacts(self):
        body = {
            'pool_id': self.pool1_1['id'],
            'contacts': [
                {'employee_id': self.employee_1_1['id']},
            ],
            'threshold': 80
        }
        _, alert = self.client.alert_create(
            self.organization_1['id'], body)
        contacts = alert['contacts']
        self.assertEqual(len(contacts), 1)
        self.assertEqual(contacts[0]['employee_id'], self.employee_1_1['id'])
        code, response = self.client.alert_update(
            alert['id'], {
                'contacts': [{'employee_id': self.employee_1_2['id']}]
            })
        contacts = response['contacts']
        self.assertEqual(code, 200)
        self.assertEqual(len(contacts), 1)
        self.assertEqual(contacts[0]['employee_id'], self.employee_1_2['id'])

        code, response = self.client.alert_update(
            alert['id'], {
                'contacts': [
                    {'employee_id': self.employee_1_2['id']},
                    {'employee_id': self.employee_1_1['id']}
                ]
            })
        contacts = response['contacts']
        self.assertEqual(code, 200)
        self.assertEqual(len(contacts), 2)

        code, response = self.client.alert_update(
            alert['id'], {
                'threshold': 70,
                'contacts': [
                    {'employee_id': self.employee_1_2['id']}
                ]
            })
        contacts = response['contacts']
        self.assertEqual(code, 200)
        self.assertEqual(len(contacts), 1)
        self.assertEqual(contacts[0]['employee_id'], self.employee_1_2['id'])
        self.assertEqual(response['threshold'], 70)

    def test_patch_invalid_contacts(self):
        body = {
            'pool_id': self.pool1_1['id'],
            'contacts': [
                {'employee_id': self.employee_1_1['id']},
            ],
            'threshold': 80
        }
        _, alert = self.client.alert_create(
            self.organization_1['id'], body)
        code, response = self.client.alert_update(
            alert['id'], {
                'contacts': [{'employee_id': self.employee_2['id']}]
            })
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['reason'],
                         'Invalid contacts: %s' % self.employee_2['id'])

    def test_patch_immutable(self):
        body = {
            'pool_id': self.pool1_1['id'],
            'contacts': [{'employee_id': self.employee_1_1['id']}],
            'threshold': 80
        }
        _, alert = self.client.alert_create(
            self.organization_1['id'], body)
        code, response = self.client.alert_update(
            alert['id'], {'deleted_at': '123'})
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['reason'],
                         'Parameter "deleted_at" is immutable')

    def test_patch_unexpected(self):
        body = {
            'pool_id': self.pool1_1['id'],
            'contacts': [{'employee_id': self.employee_1_1['id']}],
            'threshold': 80
        }
        _, alert = self.client.alert_create(
            self.organization_1['id'], body)
        code, response = self.client.alert_update(
            alert['id'], {'unexpected': '123'})
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['reason'],
                         "Unexpected parameters: ['unexpected']")

    def test_patch_invalid_contact_format(self):
        body = {
            'pool_id': self.pool1_1['id'],
            'contacts': [{'employee_id': self.employee_1_1['id']}],
            'threshold': 80
        }
        _, alert = self.client.alert_create(
            self.organization_1['id'], body)
        code, response = self.client.alert_update(
            alert['id'], {'contacts': '123'})
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['reason'],
                         'contacts should be a list')

    def test_get_alert(self):
        body = {
            'pool_id': self.pool1_1['id'],
            'contacts': [{'employee_id': self.employee_1_1['id']}],
            'threshold': 80
        }
        _, alert = self.client.alert_create(
            self.organization_1['id'], body)
        code, response = self.client.alert_get(alert['id'])
        self.assertEqual(code, 200)
        self.assertEqual(response['id'], alert['id'])
        self.assertEqual(response['threshold'], 80)
        self.assertEqual(len(response['contacts']), 1)
        self.assertEqual(response['contacts'][0]['employee_id'],
                         self.employee_1_1['id'])

    def test_get_alert_not_exist(self):
        random_uuid = str(uuid.uuid4())
        code, response = self.client.alert_get(random_uuid)
        self.assertEqual(code, 404)
        self.assertEqual(response['error']['reason'],
                         'PoolAlert %s not found' % random_uuid)

    def test_list_alerts_not_exist(self):
        random_uuid = str(uuid.uuid4())
        code, response = self.client.alert_list(random_uuid)
        self.assertEqual(code, 200)
        self.assertEqual(len(response['alerts']), 0)

    def test_list_alerts(self):
        body = {
            'pool_id': self.pool1_1['id'],
            'contacts': [{'employee_id': self.employee_1_1['id']}],
            'threshold': 80
        }
        _, alert = self.client.alert_create(self.organization_1['id'], body)
        body['threshold'] = 70
        _, alert = self.client.alert_create(self.organization_1['id'], body)
        code, response = self.client.alert_list(self.organization_1['id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(response['alerts']), 2)

    def test_delete_alert_not_exist(self):
        item_id = str(uuid.uuid4())
        code, response = self.client.alert_delete(item_id)
        self.assertEqual(code, 404)
        self.assertEqual(response['error']['reason'],
                         'PoolAlert %s not found' % item_id)

    def test_delete_alert(self):
        body = {
            'pool_id': self.pool1_1['id'],
            'contacts': [{'employee_id': self.employee_1_1['id']}],
            'threshold': 80
        }
        _, alert = self.client.alert_create(self.organization_1['id'], body)
        code, response = self.client.alert_delete(alert['id'])
        self.assertEqual(code, 204)

    def test_delete_deleted_alert(self):
        body = {
            'pool_id': self.pool1_1['id'],
            'contacts': [{'employee_id': self.employee_1_1['id']}],
            'threshold': 80
        }
        _, alert = self.client.alert_create(self.organization_1['id'], body)
        code, response = self.client.alert_delete(alert['id'])
        self.assertEqual(code, 204)
        code, response = self.client.alert_delete(alert['id'])
        self.assertEqual(code, 404)

    def test_process_alerts_not_exist_org(self):
        org_id = str(uuid.uuid4())
        code, resp = self.client.alert_process(org_id)
        self.assertEqual(code, 404)
        self.verify_error_code(resp, 'OE0002')

    @freeze_time('2020-04-15')
    def test_process_alerts(self):
        code, cloud_acc = self.create_cloud_account(
            self.organization_1['id'], self.cloud_acc_dict,
            auth_user_id=self.auth_user_1)
        self.assertEqual(code, 201)
        resource = {
            'cloud_resource_id': 'res_id',
            'name': 'resource',
            'resource_type': 'test',
            'pool_id': self.organization_1['pool_id'],
            'employee_id': self.employee_1_1['id']
        }
        code, _ = self.cloud_resource_create(cloud_acc['id'], resource)
        self.assertEqual(code, 201)
        resource['cloud_resource_id'] = 'res_2'
        code, _ = self.cloud_resource_create(cloud_acc['id'], resource)
        self.assertEqual(code, 201)
        resource['cloud_resource_id'] = 'res_3'
        code, _ = self.cloud_resource_create(cloud_acc['id'], resource)
        self.assertEqual(code, 201)
        self.client.pool_update(self.organization_1['pool_id'],
                                {'limit': 5000})
        code, child_pool = self.client.pool_create(
            self.organization_1['id'], {
                'name': 'b1', 'parent_id': self.organization_1['pool_id'],
                'limit': 2000})
        self.assertEqual(code, 201)
        resource2 = {
            'cloud_resource_id': 'res_id_2',
            'name': 'resource',
            'resource_type': 'test2',
            'pool_id': child_pool['id'],
            'employee_id': self.employee_1_1['id']
        }
        code, _ = self.cloud_resource_create(cloud_acc['id'], resource2)
        self.assertEqual(code, 201)
        body = {
            'pool_id': self.organization_1['pool_id'],
            'contacts': [{'employee_id': self.employee_1_1['id']}],
            'threshold': 1600
        }

        _, alert = self.client.alert_create(
            self.organization_1['id'], body)

        _, alert = self.client.alert_create(
            self.organization_1['id'], {
                'pool_id': self.organization_1['pool_id'],
                'contacts': [{'employee_id': self.employee_1_2['id']}],
                'threshold': 80,
                'threshold_type': 'percentage',
                'based': 'forecast'
            })
        body['pool_id'] = child_pool['id']
        _, alert = self.client.alert_create(
            self.organization_1['id'], body)
        body = {
            'pool_id': self.organization_2['pool_id'],
            'contacts': [{'employee_id': self.employee_2['id']}],
            'threshold': 80
        }
        code, cloud_acc2 = self.create_cloud_account(
            self.organization_2['id'], self.cloud_acc_dict,
            auth_user_id=self.auth_user_2)
        resource3 = {
            'cloud_resource_id': 'res_id_2',
            'name': 'resource',
            'resource_type': 'test2',
            'pool_id': self.organization_2['pool_id'],
            'employee_id': self.employee_2['id']
        }
        self.cloud_resource_create(cloud_acc2['id'], resource3)
        _, alert = self.client.alert_create(
            self.organization_2['id'], body)
        today = datetime.today()
        file_path = 'rest_api.rest_api_server.controllers.expense'
        patch('%s.ExpenseController.get_expenses_for_pools' %
              file_path,
              return_value=[
                  {
                      'cost': 1500,
                      '_id': {
                          'date': today,
                          'pool_id': child_pool['id'],
                      },
                  },
                  {
                      'cost': 3000,
                      '_id': {
                          'date': today,
                          'pool_id': self.organization_1['pool_id'],
                      },
                  }
              ]).start()
        code, response = self.client.alert_process(self.organization_1['id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(response['alerts']), 2)
        for alert in response['alerts']:
            self.assertTrue(
                alert['pool_id'] == self.organization_1['pool_id'])
        code, response = self.client.alert_process(self.organization_2['id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(response['alerts']), 0)
        patch('%s.ExpenseController.get_expenses_for_pools' %
              file_path,
              return_value=[
                  {
                      'cost': 2000,
                      '_id': {
                          'date': today,
                          'pool_id': child_pool['id'],
                      },
                  },
                  {
                      'cost': 3000,
                      '_id': {
                          'date': today,
                          'pool_id': self.organization_1['pool_id'],
                      },
                  }
              ]).start()
        code, response = self.client.alert_process(self.organization_1['id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(response['alerts']), 1)
        self.assertTrue(
            response['alerts'][0]['pool_id'] == child_pool['id'])

        # 'constraint' alerts are not processed
        alert_params = {
            'pool_id': self.organization_1['pool_id'],
            'threshold': 0,
            'contacts': [{'slack_channel_id': 'channel',
                          'slack_team_id': 'team'}],
            'based': ThresholdBasedTypes.CONSTRAINT.value
        }
        code, alert = self.client.alert_create(self.organization_1['id'],
                                               alert_params)
        self.assertEqual(code, 201)
        code, response = self.client.alert_process(self.organization_1['id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(response['alerts']), 0)

        # 'env_change' alerts are not processed
        alert_params = {
            'pool_id': self.organization_1['pool_id'],
            'contacts': [{'slack_channel_id': 'channel',
                          'slack_team_id': 'team'}],
            'threshold': 0,
            'based': ThresholdBasedTypes.ENV_CHANGE.value
        }
        code, alert = self.client.alert_create(self.organization_1['id'],
                                               alert_params)
        self.assertEqual(code, 201)
        code, response = self.client.alert_process(self.organization_1['id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(response['alerts']), 0)

    def test_create_invalid_slack_channel_id(self):
        body = {
            'pool_id': self.organization_1['pool_id'],
            'threshold': 80,
            'contacts': [{'slack_channel_id': 1}]
        }
        code, response = self.client.alert_create(
            self.organization_1['id'], body)
        self.assertEqual(code, 400)
        self.verify_error_code(response, 'OE0214')

    def test_slack_contacts(self):
        body = {
            'pool_id': self.organization_1['pool_id'],
            'threshold': 80,
            'contacts': [{'slack_channel_id': 1}]
        }
        code, response = self.client.alert_create(
            self.organization_1['id'], body)
        self.assertEqual(code, 400)
        self.verify_error_code(response, 'OE0214')

    @freeze_time('2020-04-15')
    def test_process_slack_contact(self):
        code, cloud_acc = self.create_cloud_account(
            self.organization_1['id'], self.cloud_acc_dict,
            auth_user_id=self.auth_user_1)
        self.assertEqual(code, 201)
        resource = {
            'cloud_resource_id': 'res_id',
            'name': 'resource',
            'resource_type': 'test',
            'pool_id': self.organization_1['pool_id'],
            'employee_id': self.employee_1_1['id']
        }
        code, res = self.cloud_resource_create(cloud_acc['id'], resource)
        self.assertEqual(code, 201)

        self.expenses.append({
            'cost': 5000,
            'cloud_account_id': cloud_acc['id'],
            'resource_id': res['id'],
            'date': datetime(2020, 4, 14),
            'sign': 1
        })

        self.client.pool_update(self.organization_1['pool_id'],
                                {'limit': 5000})
        _, alert = self.client.alert_create(
            self.organization_1['id'], {
                'pool_id': self.organization_1['pool_id'],
                'contacts': [{
                    'slack_channel_id': 'channel',
                    'slack_team_id': 'team'
                }],
                'threshold': 1600
            })

        _, alert = self.client.alert_create(
            self.organization_1['id'], {
                'pool_id': self.organization_1['pool_id'],
                'contacts': [{
                    'slack_channel_id': 'channel',
                    'slack_team_id': 'team'
                }],
                'threshold': 80,
                'threshold_type': 'percentage',
                'based': 'forecast'
            })

        code, response = self.client.alert_process(self.organization_1['id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(response['alerts']), 2)
        for alert in response['alerts']:
            self.assertTrue(
                alert['pool_id'] == self.organization_1['pool_id'])
        self.assertTrue(self.p_send_message.called)

    def test_create_invalid_include_children(self):
        body = {
            'pool_id': self.organization_1['pool_id'],
            'threshold': 80,
            'contacts': [{
                'slack_channel_id': 'channel',
                'slack_team_id': 'team'
            }],
            'include_children': 5,
        }
        code, response = self.client.alert_create(
            self.organization_1['id'], body)
        self.assertEqual(code, 400)
        self.verify_error_code(response, 'OE0226')

    def _add_resource_with_expenses(self, ca_id, pool_id, expenses):
        resource = {
            'cloud_resource_id': self.gen_id(),
            'name': self.gen_id(),
            'resource_type': self.gen_id(),
            'pool_id': pool_id,
            'employee_id': self.employee_1_1['id'],
        }
        code, res = self.cloud_resource_create(ca_id, resource)
        self.assertEqual(code, 201)
        self.expenses.append({
            'cost': expenses,
            'cloud_account_id': ca_id,
            'resource_id': res['id'],
            'date': datetime(2020, 4, 14),
            'sign': 1
        })

    @freeze_time('2020-04-15')
    def test_process_include_children(self):
        code, cloud_acc = self.create_cloud_account(
            self.organization_1['id'], self.cloud_acc_dict,
            auth_user_id=self.auth_user_1)
        self.assertEqual(code, 201)

        self.client.pool_update(self.organization_1['pool_id'],
                                {'limit': 5000})
        code, child_pool1 = self.client.pool_create(
            self.organization_1['id'], {'name': 'ch1', 'limit': 2000})
        self.assertEqual(code, 201)
        code, child_pool2 = self.client.pool_create(
            self.organization_1['id'], {'name': 'ch2', 'limit': 2000})
        self.assertEqual(code, 201)
        code, ch_ch_pool = self.client.pool_create(
            self.organization_1['id'], {'name': 'ch2', 'limit': 500,
                                        'parent_id': child_pool1['id']})
        self.assertEqual(code, 201)

        self._add_resource_with_expenses(
            cloud_acc['id'], self.organization_1['pool_id'], 800)
        self._add_resource_with_expenses(
            cloud_acc['id'], child_pool1['id'], 1900)
        self._add_resource_with_expenses(
            cloud_acc['id'], child_pool2['id'], 1800)
        self._add_resource_with_expenses(
            cloud_acc['id'], ch_ch_pool['id'], 600)

        _, alert = self.client.alert_create(
            self.organization_1['id'], {
                'pool_id': self.organization_1['pool_id'],
                'contacts': [{
                    'slack_channel_id': 'channel',
                    'slack_team_id': 'team'
                }],
                'threshold': 100,
                'threshold_type': 'percentage',
                'based': 'cost',
                'include_children': True,
            })

        code, response = self.client.alert_process(self.organization_1['id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(response['alerts']), 1)
        for alert in response['alerts']:
            self.assertTrue(
                alert['pool_id'] == self.organization_1['pool_id'])
        self.assertEqual(self.p_send_message.call_count, 11)

        # test last_shoot_at checking
        code, response = self.client.alert_process(self.organization_1['id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(response['alerts']), 0)

    @freeze_time('2020-04-15')
    def test_process_zero_limit_with_children(self):
        code, cloud_acc = self.create_cloud_account(
            self.organization_1['id'], self.cloud_acc_dict,
            auth_user_id=self.auth_user_1)
        self.assertEqual(code, 201)

        code, child_pool = self.client.pool_create(
            self.organization_1['id'], {'name': 'ch1', 'limit': 0})
        self.assertEqual(code, 201)

        self._add_resource_with_expenses(
            cloud_acc['id'], child_pool['id'], 1900)

        _, alert = self.client.alert_create(
            self.organization_1['id'], {
                'pool_id': self.organization_1['pool_id'],
                'contacts': [{
                    'slack_channel_id': 'channel',
                    'slack_team_id': 'team'
                }],
                'threshold': 10,
                'threshold_type': 'percentage',
                'based': 'cost',
                'include_children': True,
            })

        code, response = self.client.alert_process(self.organization_1['id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(response['alerts']), 1)
        for alert in response['alerts']:
            self.assertTrue(
                alert['pool_id'] == self.organization_1['pool_id'])
        self.assertEqual(self.p_send_message.call_count, 8)

        # test last_shoot_at checking
        code, response = self.client.alert_process(self.organization_1['id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(response['alerts']), 0)

    @freeze_time('2020-04-15')
    def test_process_zero_limit_no_children(self):
        code, cloud_acc = self.create_cloud_account(
            self.organization_1['id'], self.cloud_acc_dict,
            auth_user_id=self.auth_user_1)
        self.assertEqual(code, 201)

        code, child_pool = self.client.pool_create(
            self.organization_1['id'], {'name': 'ch1', 'limit': 0})
        self.assertEqual(code, 201)

        self._add_resource_with_expenses(
            cloud_acc['id'], self.organization_1['pool_id'], 800)

        _, alert = self.client.alert_create(
            self.organization_1['id'], {
                'pool_id': self.organization_1['pool_id'],
                'contacts': [{
                    'slack_channel_id': 'channel',
                    'slack_team_id': 'team'
                }],
                'threshold': 10,
                'threshold_type': 'percentage',
                'based': 'cost',
                'include_children': False,
            })

        code, response = self.client.alert_process(self.organization_1['id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(response['alerts']), 1)
        for alert in response['alerts']:
            self.assertTrue(
                alert['pool_id'] == self.organization_1['pool_id'])
        self.assertEqual(self.p_send_message.call_count, 6)

        # test last_shoot_at checking
        code, response = self.client.alert_process(self.organization_1['id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(response['alerts']), 0)

    def test_create_without_slack_team_id(self):
        body = {
            'pool_id': self.organization_1['pool_id'],
            'threshold': 80,
            'contacts': [{
                'slack_channel_id': 'channel'
            }],
            'include_children': 5,
        }
        code, response = self.client.alert_create(
            self.organization_1['id'], body)
        self.assertEqual(code, 400)
        self.verify_error_code(response, 'OE0216')

    @freeze_time('2020-04-15')
    def test_slack_alert_cost(self):
        code, cloud_acc = self.create_cloud_account(
            self.organization_1['id'], self.cloud_acc_dict,
            auth_user_id=self.auth_user_1)
        self.assertEqual(code, 201)

        self.client.pool_update(self.organization_1['pool_id'],
                                {'limit': 1000})
        self.assertEqual(code, 201)

        self._add_resource_with_expenses(
            cloud_acc['id'], self.organization_1['pool_id'], 1000)

        _, alert = self.client.alert_create(
            self.organization_1['id'], {
                'pool_id': self.organization_1['pool_id'],
                'contacts': [{
                    'slack_channel_id': 'channel',
                    'slack_team_id': 'team'
                }],
                'threshold': 50,
                'threshold_type': 'percentage',
                'based': 'cost',
                'include_children': False,
            })

        code, response = self.client.alert_process(self.organization_1['id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(response['alerts']), 1)
        self.assertEqual(
            self.p_send_message.call_args[0][4]['cost'], 1000)

    @freeze_time('2020-04-15')
    def test_slack_alert_forecast(self):
        code, cloud_acc = self.create_cloud_account(
            self.organization_1['id'], self.cloud_acc_dict,
            auth_user_id=self.auth_user_1)
        self.assertEqual(code, 201)

        self.client.pool_update(self.organization_1['pool_id'],
                                {'limit': 1000})
        self.assertEqual(code, 201)

        self._add_resource_with_expenses(
            cloud_acc['id'], self.organization_1['pool_id'], 1000)

        _, alert = self.client.alert_create(
            self.organization_1['id'], {
                'pool_id': self.organization_1['pool_id'],
                'contacts': [{
                    'slack_channel_id': 'channel',
                    'slack_team_id': 'team'
                }],
                'threshold': 50,
                'threshold_type': 'percentage',
                'based': 'forecast',
                'include_children': False,
            })

        code, response = self.client.alert_process(self.organization_1['id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(response['alerts']), 1)
        # 1000 + 1000 * (30 - 14)
        self.assertEqual(
            self.p_send_message.call_args[0][4]['cost'], 17000)

    def test_create_activities_task(self):
        body = {
            'pool_id': self.organization_1['pool_id'],
            'contacts': [
                {'employee_id': self.employee_1_1['id']},
                {'employee_id': self.employee_1_2['id']},
            ],
            'threshold': 80
        }
        code, response = self.client.alert_create(
            self.organization_1['id'], body)
        self.assertEqual(code, 201)
        meta = {
            'initiator_name': ANY,
            'initiator_email': ANY,
            'alert': ANY,
            'pool_name': ANY,
            'with_subpools': ANY,
            'warn_type': ANY,
            'object_name': 'alert(%s)' % response['id']
        }
        self.p_send_message.assert_called_once_with(
            self.organization_1['id'], response['id'], 'pool_alert',
            'alert_added', meta, 'alert.action.added', add_token=True)

    def test_delete_activities_task(self):
        body = {
            'pool_id': self.organization_1['pool_id'],
            'contacts': [
                {'employee_id': self.employee_1_1['id']},
                {'employee_id': self.employee_1_2['id']},
            ],
            'threshold': 80
        }
        code, alert = self.client.alert_create(
            self.organization_1['id'], body)
        self.assertEqual(code, 201)
        self.p_send_message.reset_mock()

        code, resp = self.client.alert_delete(alert['id'])
        self.assertEqual(code, 204)
        meta = {
            'initiator_name': ANY,
            'initiator_email': ANY,
            'alert': ANY,
            'pool_name': ANY,
            'with_subpools': ANY,
            'warn_type': ANY,
            'object_name': ANY
        }
        self.p_send_message.assert_called_once_with(
            self.organization_1['id'], alert['id'], 'pool_alert',
            'alert_removed', meta, 'alert.action.removed', add_token=True)
