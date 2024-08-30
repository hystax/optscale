import datetime
import copy
import uuid
from copy import deepcopy

from freezegun import freeze_time
from sqlalchemy import and_
from unittest.mock import patch, ANY, call
from rest_api.rest_api_server.models.models import (
    CloudAccount, DiscoveryInfo, OrganizationLimitHit, Organization)
from rest_api.rest_api_server.models.db_base import BaseDB
from rest_api.rest_api_server.models.db_factory import DBType, DBFactory
from rest_api.rest_api_server.utils import decode_config
from rest_api.rest_api_server.controllers.cloud_account import CloudAccountController
from tools.cloud_adapter.exceptions import ReportConfigurationException
from rest_api.rest_api_server.tests.unittests.test_api_base import TestApiBase
from rest_api.rest_api_server.models.enums import CloudTypes
from tools.cloud_adapter.cloud import Cloud as CloudAdapter


class TestCloudAccountApi(TestApiBase):

    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.org = self.client.organization_create({'name': "organization"})
        _, self.org2 = self.client.organization_create({'name': "organization2"})
        self.org_id = self.org['id']
        self.org_id2 = self.org2['id']
        self.auth_user_1 = self.gen_id()
        _, self.employee_1 = self.client.employee_create(
            self.org['id'], {'name': 'employee_1',
                             'auth_user_id': self.auth_user_1})
        _, self.employee_2 = self.client.employee_create(
            self.org2['id'], {'name': 'employee_2',
                              'auth_user_id': self.auth_user_1})
        patch('rest_api.rest_api_server.controllers.report_import.ReportImportBaseController.'
              'publish_task').start()
        patch('rest_api.rest_api_server.controllers.base.BaseController.'
              'get_user_id',
              return_value=self.auth_user_1).start()

        self.valid_cloud_config = {
            'access_key_id': 'key',
            'secret_access_key': 'secret',
            'config_scheme': 'create_report'
        }
        self.valid_aws_cloud_acc = {
            'name': 'my cloud_acc',
            'type': 'aws_cnr',
            'config': self.valid_cloud_config
        }
        self.valid_aws_cloud_acc_response = {
            'name': 'my cloud_acc',
            'type': 'aws_cnr',
            'config': {
                'access_key_id': 'key',
                'config_scheme': 'create_report'
            }
        }
        self.valid_databricks_cloud_acc = {
            'name': 'my cloud_acc',
            'type': 'databricks',
            'config': {
                'client_id': 'databricks_client_id',
                'client_secret': 'databricks_client_secret',
                'account_id': 'databricks_account_id'
            }
        }
        self.p_configure_aws = patch(
            'tools.cloud_adapter.clouds.aws.Aws.configure_report').start()
        self.p_configure_azure = patch(
            'tools.cloud_adapter.clouds.azure.Azure.configure_report').start()
        self.p_configure_nebius = patch(
            'tools.cloud_adapter.clouds.nebius.Nebius.configure_report').start()

        self.valid_azure_cloud_acc = {
            'name': 'azure cloud_acc',
            'type': 'azure_cnr',
            'config': {
                'subscription_id': 'id',
                'secret': 'secret',
                'client_id': 'id',
                'tenant': 't'
            }
        }
        self.valid_azure_response = deepcopy(self.valid_azure_cloud_acc)
        del self.valid_azure_response['config']['secret']

        self.valid_kubernetes_cloud_acc = {
            'name': 'k8s cloud_acc',
            'type': 'kubernetes_cnr',
            'config': {
                'user': 'user',
                'password': 'secure_pass'
            }
        }
        self.default_kubernetes_cost_model = {
            'cpu_hourly_cost': 0.002,
            'memory_hourly_cost': 0.001
        }
        self.valid_kubernetes_response = deepcopy(self.valid_kubernetes_cloud_acc)
        self.valid_kubernetes_response['config'].update(
            {'cost_model': self.default_kubernetes_cost_model})
        self.valid_kubernetes_response['config'].pop('password')

        self.valid_gcp_cloud_acc = {
            'name': 'gcp cloud_acc',
            'type': 'gcp_cnr',
            'config': {
                'credentials': {
                    "type": "service_account",
                    "project_id": "hystax",
                    "private_key_id": "redacted",
                    "private_key": "redacted",

                },
                'billing_data': {
                    'dataset_name': 'billing_data',
                    'table_name': 'gcp_billing_export_v1',
                },
            }
        }
        self.valid_nebius_cloud_acc = {
            'name': 'nebius_cloud_acc',
            'type': 'nebius',
            'config': {
                "bucket_name": "bucket",
                "bucket_prefix": "prefix",
                "access_key_id": "access_key_id",
                "secret_access_key": "secret_access_key",
                "key_id": "key_id",
                "service_account_id": "service_account_id",
                "private_key": "private_key",
                "cloud_name": "cloud",
            }
        }

    @staticmethod
    def get_cloud_account_object(ca_id):
        db = DBFactory(DBType.Test, None).db
        engine = db.engine
        session = BaseDB.session(engine)()
        ca_obj = session.query(CloudAccount).filter(
            CloudAccount.id == ca_id).one_or_none()
        return ca_obj

    def test_create_cloud_acc(self):
        code, cloud_acc = self.create_cloud_account(self.org_id,
                                                    self.valid_aws_cloud_acc)
        self.assertEqual(code, 201)
        self.assertEqual(cloud_acc['process_recommendations'], True)
        self.assertDictEqual(self.valid_aws_cloud_acc_response['config'],
                             cloud_acc['config'])
        self.p_configure_aws.assert_called_once_with()
        self.assertEqual(self.p_send_ca_email.call_count, 1)

    def test_pool_and_rule_for_created_cloud_acc(self):
        auth_user_id = self.gen_id()
        _, employee = self.client.employee_create(
            self.org['id'], {'name': 'employee',
                             'auth_user_id': auth_user_id})
        created_at = datetime.datetime.utcnow().timestamp()
        with freeze_time(datetime.datetime.fromtimestamp(created_at)):
            _, cloud_acc = self.create_cloud_account(
                self.org_id, self.valid_aws_cloud_acc,
                auth_user_id=auth_user_id)
        code, response = self.client.rules_list(self.org_id)
        self.assertEqual(code, 200)
        rules = response['rules']
        self.assertEqual(len(rules), 1)
        created_cloud_rule = rules[0]
        self.assertEqual(created_cloud_rule['owner_id'], employee['id'])
        self.assertEqual(created_cloud_rule['creator_id'], employee['id'])
        self.assertEqual(
            created_cloud_rule['name'], 'Rule for %s_%s' % (
                cloud_acc['name'], int(created_at)))
        self.assertEqual(created_cloud_rule['priority'], 1)
        self.assertEqual(created_cloud_rule['pool_purpose'], 'budget')
        self.assertEqual(len(created_cloud_rule['conditions']), 1)
        self.assertEqual(created_cloud_rule['conditions'][0]['type'], 'cloud_is')
        self.assertEqual(created_cloud_rule['conditions'][0]['meta_info'],
                         cloud_acc['id'])
        self.set_allowed_pair(auth_user_id, created_cloud_rule['pool_id'])

        code, created_cloud_pool = self.client.pool_get(created_cloud_rule['pool_id'])
        self.assertEqual(code, 200)
        self.assertEqual(created_cloud_pool['limit'], 0)
        self.assertEqual(created_cloud_pool['purpose'], 'budget')
        self.assertEqual(created_cloud_rule['pool_id'], created_cloud_pool['id'])
        self.assertEqual(created_cloud_pool['name'], cloud_acc['name'])
        self.assertEqual(created_cloud_pool['default_owner_name'], employee['name'])

        self.assertEqual(created_cloud_rule['pool_id'], created_cloud_pool['id'])

    def test_pool_name_for_created_cloud(self):
        auth_user_id = self.gen_id()
        _, employee = self.client.employee_create(
            self.org['id'], {'name': 'employee',
                             'auth_user_id': auth_user_id})
        cloud_name = 'aws cloud name'
        self.valid_aws_cloud_acc['name'] = cloud_name
        created_at = datetime.datetime.utcnow().timestamp()
        with freeze_time(datetime.datetime.fromtimestamp(created_at - 6)):
            _, cloud_acc = self.create_cloud_account(
                self.org_id, self.valid_aws_cloud_acc,
                auth_user_id=auth_user_id)
        code, response = self.client.rules_list(self.org_id)
        self.assertEqual(code, 200)
        created_cloud_rule = response['rules'][0]
        self.assertEqual(created_cloud_rule['priority'], 1)
        code, created_cloud_pool = self.client.pool_get(
            created_cloud_rule['pool_id'])
        self.assertEqual(code, 200)
        self.assertEqual(created_cloud_pool['name'], cloud_acc['name'])

        with freeze_time(datetime.datetime.fromtimestamp(created_at - 5)):
            code, _ = self.client.cloud_account_delete(cloud_acc['id'])
        self.assertEqual(code, 204)
        with freeze_time(datetime.datetime.fromtimestamp(created_at - 4)):
            _, cloud_acc = self.create_cloud_account(
                self.org_id, self.valid_aws_cloud_acc,
                auth_user_id=auth_user_id)
        code, response = self.client.rules_list(self.org_id)
        self.assertEqual(code, 200)
        created_cloud_rule = response['rules'][1]
        self.assertEqual(created_cloud_rule['priority'], 2)
        code, created_cloud_pool = self.client.pool_get(
            created_cloud_rule['pool_id'])
        self.assertEqual(code, 200)
        self.assertEqual('%s %s' % (cloud_acc['name'], '1'),
                         created_cloud_pool['name'])

        with freeze_time(datetime.datetime.fromtimestamp(created_at - 3)):
            code, _ = self.client.cloud_account_delete(cloud_acc['id'])
        self.assertEqual(code, 204)
        with freeze_time(datetime.datetime.fromtimestamp(created_at - 2)):
            _, cloud_acc = self.create_cloud_account(
                self.org_id, self.valid_aws_cloud_acc,
                auth_user_id=auth_user_id)
        code, response = self.client.rules_list(self.org_id)
        self.assertEqual(code, 200)
        created_cloud_rule = response['rules'][2]
        self.assertEqual(created_cloud_rule['priority'], 3)
        code, created_cloud_pool = self.client.pool_get(created_cloud_rule['pool_id'])
        self.assertEqual(code, 200)
        self.assertEqual('%s %s' % (cloud_acc['name'], '2'), created_cloud_pool['name'])

        cloud_name = 'aws cloud name 1'
        self.valid_aws_cloud_acc['name'] = cloud_name

        with freeze_time(datetime.datetime.fromtimestamp(created_at - 1)):
            _, cloud_acc = self.create_cloud_account(
                self.org_id, self.valid_aws_cloud_acc,
                auth_user_id=auth_user_id)
        code, response = self.client.rules_list(self.org_id)
        self.assertEqual(code, 200)
        created_cloud_rule = response['rules'][2]
        self.assertEqual(created_cloud_rule['priority'], 3)
        code, created_cloud_pool = self.client.pool_get(
            created_cloud_rule['pool_id'])
        self.assertEqual(code, 200)
        self.assertEqual('aws cloud name 2', created_cloud_pool['name'])

    def test_create_cloud_accounts_rules(self):
        auth_user_id = self.gen_id()
        _, employee = self.client.employee_create(
            self.org['id'], {'name': 'employee',
                             'auth_user_id': auth_user_id})
        cloud_name = 'aws cloud name'
        self.valid_aws_cloud_acc['name'] = cloud_name
        _, cloud_acc = self.create_cloud_account(
            self.org_id, self.valid_aws_cloud_acc, auth_user_id=auth_user_id)
        code, response = self.client.rules_list(self.org_id)
        self.assertEqual(code, 200)
        created_cloud_rule = response['rules'][0]
        self.assertEqual(created_cloud_rule['priority'], 1)

        cloud_name = 'aws cloud name 1'
        self.valid_aws_cloud_acc['name'] = cloud_name
        _, cloud_acc = self.create_cloud_account(
            self.org_id, self.valid_aws_cloud_acc, auth_user_id=auth_user_id)
        code, response = self.client.rules_list(self.org_id)
        self.assertEqual(code, 200)
        created_cloud_rule = response['rules'][1]
        self.assertEqual(created_cloud_rule['priority'], 2)

        cloud_name = 'aws cloud name 2'
        self.valid_aws_cloud_acc['name'] = cloud_name
        _, cloud_acc = self.create_cloud_account(
            self.org_id, self.valid_aws_cloud_acc, auth_user_id=auth_user_id)
        code, response = self.client.rules_list(self.org_id)
        self.assertEqual(code, 200)
        created_cloud_rule = response['rules'][2]
        self.assertEqual(created_cloud_rule['priority'], 3)

    def test_create_missing_required(self):
        for param in ['name', 'type']:
            params = self.valid_aws_cloud_acc.copy()
            del params[param]
            code, ret = self.create_cloud_account(self.org_id, params)
            self.assertEqual(code, 400)
            self.assertEqual(ret['error']['reason'],
                             '{0} is not provided'.format(param))

        params = self.valid_aws_cloud_acc.copy()
        del params['config']['access_key_id']
        code, ret = self.create_cloud_account(self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(ret['error']['reason'],
                         'access_key_id is not provided')

    def test_create_unexpected(self):
        params = self.valid_aws_cloud_acc.copy()
        params['error'] = '1'
        code, ret = self.create_cloud_account(self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(ret['error']['reason'],
                         "Unexpected parameters: ['error']")

    def test_create_whitespaced_name(self):
        params = self.valid_aws_cloud_acc.copy()
        params['name'] = '       '
        code, ret = self.create_cloud_account(self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(ret['error']['reason'],
                         "name should not contain only whitespaces")

    def test_create_whitespaced_config_params(self):
        params = self.valid_aws_cloud_acc.copy()
        bucket_name_config = self.valid_cloud_config.copy()
        bucket_name_config['bucket_name'] = "       "
        params['config'] = bucket_name_config
        code, ret = self.create_cloud_account(self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(ret['error']['reason'],
                         "bucket_name should not contain only whitespaces")
        report_name_config = self.valid_cloud_config.copy()
        report_name_config['report_name'] = "       "
        params['config'] = report_name_config
        code, ret = self.create_cloud_account(self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(ret['error']['reason'],
                         "report_name should not contain only whitespaces")
        bucket_prefix_config = self.valid_cloud_config.copy()
        bucket_prefix_config['bucket_prefix'] = "       "
        params['config'] = bucket_prefix_config
        code, ret = self.create_cloud_account(self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(ret['error']['reason'],
                         "bucket_prefix should not contain only whitespaces")

    def test_create_with_non_required(self):
        params = self.valid_aws_cloud_acc.copy()
        params['config']['bucket_name'] = 'bucket_name'
        code, ret = self.create_cloud_account(self.org_id, params)
        self.assertEqual(code, 201)

    def test_create_with_empty_bucket_prefix(self):
        params = self.valid_aws_cloud_acc.copy()
        params['config']['bucket_prefix'] = ''
        code, response = self.create_cloud_account(self.org_id, params)
        self.assertEqual(code, 201)

    def test_create_invalid_bucket_prefix(self):
        params = self.valid_aws_cloud_acc.copy()
        params['config']['bucket_prefix'] = 123
        code, response = self.create_cloud_account(self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['reason'],
                         'bucket_prefix should be a string')

    def test_create_unexpected_in_cloud_acc(self):
        params = self.valid_aws_cloud_acc.copy()
        params['config']['key'] = '1'
        code, ret = self.create_cloud_account(self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(ret['error']['reason'],
                         "Unexpected parameters: ['key']")

    def test_create_wrong_format(self):
        params = self.valid_aws_cloud_acc.copy()
        params['config']['access_key_id'] = 1
        code, ret = self.create_cloud_account(self.org_id, params)
        self.assertEqual(code, 400)

    @patch('rest_api.rest_api_server.controllers.cloud_account.'
           'ExpensesRecalculationScheduleController.schedule')
    def test_patch(self, schedule_patch):
        account_id = self.gen_id()
        code, cloud_acc = self.create_cloud_account(
            self.org_id, self.valid_aws_cloud_acc, account_id=account_id)
        self.assertEqual(code, 201)
        self.assertEqual(self.p_configure_aws.call_count, 1)

        params = {'config': {
            'access_key_id': 'new_key',
            'secret_access_key': 'new_secret',
            'config_scheme': 'create_report'
        }}
        patch('tools.cloud_adapter.clouds.aws.Aws.validate_credentials',
              return_value={'account_id': account_id, 'warnings': []}).start()
        code, ret = self.client.cloud_account_update(cloud_acc['id'], params)
        self.assertEqual(code, 200)
        params['config'].pop('secret_access_key')
        cloud_acc.update(params)
        self.assertDictEqual(ret, cloud_acc)
        self.assertEqual(self.p_configure_aws.call_count, 2)
        self.assertEqual(schedule_patch.call_count, 0)

    def test_update_not_changed_params(self):
        code, cloud_acc = self.create_cloud_account(
            self.org_id, self.valid_aws_cloud_acc)
        self.assertEqual(code, 201)

        code, resp = self.client.cloud_account_update(
            cloud_acc['id'], {'last_import_at': 123,
                              'last_import_modified_at': 321})
        self.assertEqual(code, 200)
        self.assertEqual(resp['last_import_at'], 123)
        self.assertEqual(resp['last_import_modified_at'], 321)

        patch('rest_api.rest_api_server.handlers.v1.base.BaseAuthHandler.'
              'check_cluster_secret', return_value=False).start()
        code, resp = self.client.cloud_account_update(
            cloud_acc['id'], {'last_import_at': 456})
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0449')

        code, resp = self.client.cloud_account_update(
            cloud_acc['id'], {'last_import_modified_at': 789})
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0449')

        code, resp = self.client.cloud_account_update(
            cloud_acc['id'], {'last_import_attempt_at': 987})
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0449')

        code, resp = self.client.cloud_account_update(
            cloud_acc['id'], {'last_import_attempt_error': 'error_text'})
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0449')

    def test_delete(self):
        mock_delete_expenses = patch(
            'rest_api.rest_api_server.controllers.expense.ExpenseController.'
            'delete_cloud_expenses').start()
        mock_clean_ch = patch(
            'rest_api.rest_api_server.controllers.cloud_account.'
            'CloudAccountController.clean_clickhouse').start()
        code, cloud_acc = self.create_cloud_account(self.org_id,
                                                    self.valid_aws_cloud_acc)
        self.assertEqual(code, 201)

        self.resources_collection.insert_one({
            'cloud_resource_id': '1',
            'cloud_account_id': cloud_acc['id'],
            'deleted_at': 0,
            'cluster_id': 'some_id'
        })
        self.resources_collection.insert_one({
            'cloud_resource_id': '2',
            'cloud_account_id': cloud_acc['id'],
            'deleted_at': 0
        })

        # need to get cloud_account without cluster secret
        patch('optscale_client.config_client.client.Client.cluster_secret',
              return_value=None).start()
        code, get_cloud_acc = self.client.cloud_account_get(cloud_acc['id'])
        self.assertEqual(code, 200)
        self.assertDictEqual(get_cloud_acc, cloud_acc)

        code, _ = self.client.cloud_account_delete(cloud_acc['id'])
        self.assertEqual(code, 204)
        mock_delete_expenses.assert_called_once_with(cloud_acc['id'])
        mock_clean_ch.assert_called_once_with(
            cloud_acc['id'], CloudTypes.AWS_CNR)
        code, _ = self.client.cloud_account_get(cloud_acc['id'])
        self.assertEqual(code, 404)

        resources = list(self.resources_collection.find({'cloud_account_id': cloud_acc['id']}))
        for resource in resources:
            self.assertNotEqual(resource['deleted_at'], 0)
            self.assertIsNone(resource.get('cluster_id'))

    @patch('rest_api.rest_api_server.handlers.v2.cloud_account.'
           'CloudAccountAsyncCollectionHandler.check_cluster_secret',
           return_value=False)
    def test_list_by_token(self, p):
        code, cloud_acc = self.create_cloud_account(
            self.org_id, self.valid_aws_cloud_acc)
        self.assertEqual(code, 201)

        code, cloud_acc_list = self.client.cloud_account_list(self.org_id)
        self.assertEqual(code, 200)
        self.assertEqual(len(cloud_acc_list['cloud_accounts']), 1)

        cloud_acc_copy = deepcopy(self.valid_aws_cloud_acc)
        cloud_acc_copy['config'].pop('secret_access_key')
        self.assertDictEqual(
            cloud_acc_copy['config'],
            cloud_acc_list['cloud_accounts'][0]['config']
        )
        cloud_acc_params2 = deepcopy(self.valid_aws_cloud_acc)
        cloud_acc_params2['name'] = 'awesome cloud_acc'
        code, cloud_acc2 = self.create_cloud_account(
            self.org_id, cloud_acc_params2)
        self.assertEqual(code, 201)

        code, organization2 = self.client.organization_create({'name': "p2"})
        auth_user_1 = self.gen_id()
        _, employee_1 = self.client.employee_create(
            organization2['id'], {'name': 'employee_1',
                                  'auth_user_id': auth_user_1})
        self.assertEqual(code, 201)
        code, cloud_acc3 = self.create_cloud_account(
            organization2['id'], self.valid_aws_cloud_acc, auth_user_id=auth_user_1)
        self.assertEqual(code, 201)

        code, cloud_acc_list = self.client.cloud_account_list(self.org_id)
        self.assertEqual(code, 200)
        self.assertEqual(len(cloud_acc_list['cloud_accounts']), 2)
        self.assertIsNone(cloud_acc_list['cloud_accounts'][0].get('resources'))

    def test_list_by_secret(self):
        code, cloud_acc = self.create_cloud_account(
            self.org_id,
            self.valid_aws_cloud_acc)
        self.assertEqual(code, 201)

        code, ca_list = self.client.cloud_account_list(self.org_id)
        self.assertEqual(code, 200)
        self.assertEqual(len(ca_list['cloud_accounts']), 1)

        self.assertDictEqual(
            self.valid_aws_cloud_acc['config'],
            ca_list['cloud_accounts'][0]['config']
        )

    def test_verify_credentials(self):
        credentials = self.valid_aws_cloud_acc.copy()
        credentials.pop('type')
        code, response = self.client.cloud_account_verify(credentials)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['reason'],
                         'type is not provided')

        self.valid_aws_cloud_acc['config'].pop('access_key_id')
        code, response = self.client.cloud_account_verify(
            self.valid_aws_cloud_acc)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['reason'],
                         'access_key_id is not provided')

    def test_list_details(self):
        self.valid_aws_cloud_acc['name'] = 'cloud_1'
        code, cloud_acc1 = self.create_cloud_account(
            self.org_id, self.valid_aws_cloud_acc)
        self.assertEqual(code, 201)
        code, discovery_info_1 = self.client.discovery_info_list(
            cloud_acc1['id'])
        self.assertEqual(code, 200)
        res_discovery_info_1 = {
            di['id']: di for di in discovery_info_1['discovery_info']}
        ca_params2 = deepcopy(self.valid_aws_cloud_acc)
        ca_params2['name'] = 'awesome_cloud_acc'
        code, cloud_acc2 = self.create_cloud_account(
            self.org_id, ca_params2, account_id='mock2')
        self.assertEqual(code, 201)
        code, discovery_info_2 = self.client.discovery_info_list(
            cloud_acc2['id'])
        self.assertEqual(code, 200)
        res_discovery_info_2 = {
            di['id']: di for di in discovery_info_2['discovery_info']}

        day_in_month = datetime.datetime(2020, 1, 14)
        day_in_last_month = datetime.datetime(2019, 12, 16)
        expenses = [
            {'cost': 150, 'date': day_in_month, 'cloud_acc': cloud_acc1['id']},
            {'cost': 300, 'date': day_in_month, 'cloud_acc': cloud_acc1['id']},
            {'cost': 90, 'date': day_in_month, 'cloud_acc': cloud_acc2['id']},
            {'cost': 180, 'date': day_in_last_month, 'cloud_acc': cloud_acc1['id']},
            {'cost': 240, 'date': day_in_last_month, 'cloud_acc': cloud_acc2['id']},
        ]

        for i, e in enumerate(expenses):
            _, resource = self.cloud_resource_create(
                e['cloud_acc'], {
                    'cloud_resource_id': 'res_id_%s' % i,
                    'resource_type': 'type_%s' % i,
                    'first_seen': int(e['date'].timestamp()),
                    'last_seen': int(e['date'].timestamp())
                })
            self.expenses.append({
                'resource_id': str(uuid.uuid4()),
                'cost': e['cost'],
                'date': e['date'],
                'cloud_account_id': e['cloud_acc'],
                'sign': 1,
            })
        with freeze_time(datetime.datetime(2020, 1, 15)):
            code, cloud_acc_list = self.client.cloud_account_list(
                self.org_id, details=True)
        self.assertEqual(len(cloud_acc_list['cloud_accounts']), 2)
        for cloud_acc in cloud_acc_list['cloud_accounts']:
            details = cloud_acc['details']
            cloud_discovery_info = {
                di['id']: di for di in details['discovery_infos']
            }
            if cloud_acc['id'] == cloud_acc2['id']:
                self.assertEqual(cloud_acc['details']['cost'], 90)
                self.assertEqual(cloud_acc['details']['tracked'], 1)
                self.assertEqual(cloud_acc['details']['forecast'], 277)
                self.assertEqual(
                    cloud_acc['details']['last_month_cost'], 240)
                self.assertDictEqual(cloud_discovery_info,
                                     res_discovery_info_2)
            else:
                self.assertEqual(cloud_acc['details']['cost'], 450)
                self.assertEqual(cloud_acc['details']['tracked'], 2)
                self.assertEqual(cloud_acc['details']['forecast'], 807)
                self.assertEqual(
                    cloud_acc['details']['last_month_cost'], 180)
                self.assertDictEqual(cloud_discovery_info,
                                     res_discovery_info_1)

    def test_get_details(self):
        self.valid_aws_cloud_acc['name'] = 'cloud_1'
        code, cloud_acc1 = self.create_cloud_account(
            self.org_id, self.valid_aws_cloud_acc)
        self.assertEqual(code, 201)

        day_in_month = datetime.datetime(2020, 1, 14)
        day_in_last_month = datetime.datetime(2019, 12, 16)
        day_in_future = datetime.datetime(2020, 1, 31)

        type_cost_map = {
            'volume': 90,
            'instance': 150,
        }

        for r_type, cost in type_cost_map.items():
            _, resource = self.cloud_resource_create(
                cloud_acc1['id'], {
                    'cloud_resource_id': 'res_id_%s' % r_type,
                    'resource_type': r_type,
                    'first_seen': int(day_in_month.timestamp()),
                    'last_seen': int(day_in_month.timestamp())
                })
            self.expenses.append({
                'resource_id': resource['id'],
                'cost': cost,
                'date': day_in_month,
                'cloud_account_id': cloud_acc1['id'],
                'sign': 1,
            })

        _, resource = self.cloud_resource_create(
            cloud_acc1['id'], {
                'cloud_resource_id': 'res_id_3',
                'resource_type': 'test',
                'first_seen': int(day_in_last_month.timestamp()),
                'last_seen': int(day_in_last_month.timestamp())
            })
        self.expenses.append({
            'resource_id': resource['id'],
            'cost': 360,
            'date': day_in_last_month,
            'cloud_account_id': cloud_acc1['id'],
            'sign': 1,
        })
        _, resource = self.cloud_resource_create(
            cloud_acc1['id'], {
                'cloud_resource_id': 'res_id_4',
                'resource_type': 'test',
                'first_seen': int(day_in_future.timestamp()),
                'last_seen': int(day_in_future.timestamp())
            })
        self.expenses.append({
            'resource_id': resource['id'],
            'cost': 1000,
            'date': day_in_future,
            'cloud_account_id': cloud_acc1['id'],
            'sign': 1,
        })
        code, res = self.client.discovery_info_list(
            cloud_acc1['id'])
        self.assertEqual(code, 200)
        res_discovery_info = {di['id']: di for di in res['discovery_info']}

        with freeze_time(datetime.datetime(2020, 1, 15)):
            code, cloud_acc = self.client.cloud_account_get(
                cloud_acc1['id'], details=True)
            details = cloud_acc['details']
            cloud_discovery_info = {
                di['id']: di for di in details['discovery_infos']
            }
            self.assertEqual(details['cost'], 240)
            self.assertEqual(details['forecast'], 580)
            self.assertEqual(details['last_month_cost'], 360)
            self.assertEqual(details['resources'], 2)
            self.assertDictEqual(cloud_discovery_info, res_discovery_info)

    def test_patch_enable_import(self):
        ca_params = self.valid_aws_cloud_acc
        code, cloud_acc = self.create_cloud_account(
            self.org_id, ca_params)
        self.assertEqual(code, 201)
        self.assertEqual(cloud_acc['auto_import'], True)
        self.p_configure_aws.assert_called_once_with()

        ca_patch = {'auto_import': True}
        code, cloud_acc_patched = self.client.cloud_account_update(
            cloud_acc['id'], ca_patch)
        self.assertEqual(code, 200)

        ca_patch = {'auto_import': False}
        code, cloud_acc_patched = self.client.cloud_account_update(
            cloud_acc['id'], ca_patch)
        self.assertEqual(code, 200)

    def test_create_cloud_acc_report_configure_error(self):
        self.p_configure_aws.side_effect = ReportConfigurationException(
            'reason text')
        code, ret = self.create_cloud_account(
            self.org_id, self.valid_aws_cloud_acc)
        self.assertEqual(code, 400)
        self.assertEqual(
            ret['error']['reason'],
            'Unable to configure billing report: %s' % 'reason text')

    @patch('rest_api.rest_api_server.handlers.v2.cloud_account.'
           'CloudAccountAsyncItemHandler.check_cluster_secret',
           return_value=False)
    def test_get_cloud_acc_secure(self, p):
        code, cloud_acc = self.create_cloud_account(self.org_id,
                                                    self.valid_aws_cloud_acc)
        self.assertEqual(code, 201)
        self.assertDictEqual(self.valid_aws_cloud_acc_response['config'],
                             cloud_acc['config'])

        code, cloud_acc = self.client.cloud_account_get(cloud_acc['id'])
        self.assertEqual(code, 200)
        self.valid_aws_cloud_acc['config'].pop('secret_access_key')
        self.assertDictEqual(self.valid_aws_cloud_acc['config'],
                             cloud_acc['config'])

        p.return_value = True
        code, ca = self.client.cloud_account_get(cloud_acc['id'])
        self.assertEqual(code, 200)
        self.assertEqual(ca['id'], cloud_acc['id'])
        self.assertDictEqual(self.valid_aws_cloud_acc['config'],
                             cloud_acc['config'])

    @patch('rest_api.rest_api_server.handlers.v2.cloud_account.'
           'CloudAccountAsyncItemHandler.check_cluster_secret',
           return_value=True)
    def test_get_k8s_cloud_acc_secure(self, m_secret):
        code, cloud_acc = self.create_cloud_account(
            self.org_id, self.valid_kubernetes_cloud_acc)
        self.assertEqual(code, 201)

        code, ca = self.client.cloud_account_get(cloud_acc['id'])
        self.assertEqual(code, 200)
        self.assertIsNotNone(ca['config'].get('credentials'))

        m_secret.return_value = False
        code, ca = self.client.cloud_account_get(cloud_acc['id'])
        self.assertEqual(code, 200)
        self.assertIsNone(ca['config'].get('credentials'))

    def test_list_deleted_cloud_acc(self):
        code, cloud_acc = self.create_cloud_account(
            self.org_id, self.valid_aws_cloud_acc)
        self.assertEqual(code, 201)
        _, cloud_acc_list = self.client.cloud_account_list(self.org_id)
        self.assertEqual(len(cloud_acc_list['cloud_accounts']), 1)

        self.client.cloud_account_delete(cloud_acc['id'])
        code, cloud_acc_list = self.client.cloud_account_list(self.org_id)
        self.assertEqual(code, 200)
        self.assertEqual(len(cloud_acc_list['cloud_accounts']), 0)
        code, cloud_acc_list = self.client.cloud_account_list(
            self.org_id, details=True)
        self.assertEqual(len(cloud_acc_list['cloud_accounts']), 0)
        self.assertEqual(code, 200)

    def test_create_cloud_acc_duplicate_name(self):
        self.create_cloud_account(
            self.org_id, self.valid_aws_cloud_acc)
        code, _ = self.create_cloud_account(
            self.org_id, self.valid_aws_cloud_acc)
        self.assertEqual(code, 409)

    def test_create_duplicate_name_after_deletion(self):
        created_at = datetime.datetime.utcnow().timestamp()
        with freeze_time(datetime.datetime.fromtimestamp(created_at - 1)):
            _, resp = self.create_cloud_account(
                self.org_id, self.valid_aws_cloud_acc)
        self.client.cloud_account_delete(resp['id'])
        with freeze_time(datetime.datetime.fromtimestamp(created_at)):
            code, _ = self.create_cloud_account(
                self.org_id, self.valid_aws_cloud_acc)
        self.assertEqual(code, 201)

    def test_create_duplicated_cloud_acc(self):
        account_id = self.gen_id()
        code, cloud_acc = self.create_cloud_account(
            self.org_id, self.valid_aws_cloud_acc, account_id=account_id)
        self.assertEqual(code, 201)
        code, cloud_acc = self.create_cloud_account(
            self.org_id, self.valid_aws_cloud_acc, account_id=account_id)
        self.assertEqual(code, 409)
        self.assertEqual(cloud_acc['error']['error_code'], 'OE0402')

    def test_patch_duplicated_cloud_acc(self):
        account_id = self.gen_id()
        account_2_id = self.gen_id()
        code, cloud_acc = self.create_cloud_account(
            self.org_id, self.valid_aws_cloud_acc, account_id=account_id)
        self.assertEqual(code, 201)
        self.valid_aws_cloud_acc['name'] = 'another name'
        code, cloud_acc2 = self.create_cloud_account(
            self.org_id, self.valid_aws_cloud_acc, account_id=account_2_id)

        params = {'config': {
            'access_key_id': 'new_key',
            'secret_access_key': 'new_secret',
            'config_scheme': 'create_report'
        }}
        patch('tools.cloud_adapter.clouds.aws.Aws.validate_credentials',
              return_value={'account_id': account_id, 'warnings': []}).start()
        code, cloud_acc = self.client.cloud_account_update(
            cloud_acc2['id'], params)
        self.assertEqual(code, 409)
        self.assertEqual(cloud_acc['error']['error_code'], 'OE0402')

        patch('tools.cloud_adapter.clouds.aws.Aws.validate_credentials',
              return_value={'account_id': account_2_id, 'warnings': []}).start()
        code, cloud_acc = self.client.cloud_account_update(
            cloud_acc2['id'], params)
        self.assertEqual(code, 200)

    def test_change_account_id_afeter_update_cloud_acc(self):
        account_id = self.gen_id()
        code, cloud_acc = self.create_cloud_account(
            self.org_id, self.valid_aws_cloud_acc, account_id=account_id)
        self.assertEqual(code, 201)
        self.assertEqual(cloud_acc['account_id'], account_id)

        account_2_id = self.gen_id()
        patch('tools.cloud_adapter.clouds.aws.Aws.validate_credentials',
              return_value={'account_id': account_2_id, 'warnings': []}).start()
        params = {'config': {
            'access_key_id': 'new_key',
            'secret_access_key': 'new_secret',
            'config_scheme': 'create_report'
        }}
        code, cloud_acc = self.client.cloud_account_update(
            cloud_acc['id'], params)
        self.assertEqual(code, 200)
        self.assertEqual(cloud_acc['account_id'], account_2_id)

    def test_create_account_id_immutable(self):
        self.valid_aws_cloud_acc['account_id'] = self.gen_id()
        code, cloud_acc = self.create_cloud_account(
            self.org_id, self.valid_aws_cloud_acc)
        self.assertEqual(code, 400)
        self.assertEqual(cloud_acc['error']['error_code'], 'OE0211')

    def test_update_account_id_immutable(self):
        code, cloud_acc = self.create_cloud_account(
            self.org_id, self.valid_aws_cloud_acc)
        self.assertEqual(code, 201)
        code, resp = self.client.cloud_account_update(
            cloud_acc['id'], {'account_id': self.gen_id()})
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0211')

    def test_patch_cloud_acc_when_import_enabled(self):
        account_id = self.gen_id()
        code, cloud_acc = self.create_cloud_account(
            self.org_id, self.valid_aws_cloud_acc, account_id=account_id)
        self.assertEqual(code, 201)

        params = {'config': {
            'access_key_id': 'new_key',
            'secret_access_key': 'new_secret',
            'config_scheme': 'create_report'
        }}
        patch('tools.cloud_adapter.clouds.aws.Aws.validate_credentials',
              return_value={'account_id': account_id, 'warnings': []}).start()
        code, cloud_acc = self.client.cloud_account_update(cloud_acc['id'], params)
        self.assertEqual(code, 200)
        self.assertEqual(self.p_configure_aws.call_count, 2)

    def test_update_cloud_acc_events(self):
        code, cloud_acc = self.create_cloud_account(
            self.org_id, self.valid_aws_cloud_acc)
        self.assertEqual(code, 201)

        patch('tools.cloud_adapter.clouds.aws.Aws.validate_credentials',
              return_value={'account_id': 'another_acc_id', 'warnings': []}).start()
        params = {'config': {
            'access_key_id': 'new_key',
            'secret_access_key': 'new_secret',
            'config_scheme': 'create_report'
        }}

        p_publish_activities = patch(
            'rest_api.rest_api_server.controllers.base.BaseController.'
            'publish_activities_task'
        ).start()
        code, cloud_acc = self.client.cloud_account_update(cloud_acc['id'], params)
        self.assertEqual(code, 200)
        activity_param_tuples = self.get_publish_activity_tuple(
            self.org_id, cloud_acc['id'], 'cloud_account',
            'cloud_account_updated', {
                'object_name': cloud_acc['name'],
                'level': 'INFO'
            })
        p_publish_activities.assert_called_once_with(
            *activity_param_tuples, add_token=True
        )

        p_publish_activities1 = patch(
            'rest_api.rest_api_server.controllers.base.BaseController.'
            'publish_activities_task'
        ).start()
        params = {'config': {
            'access_key_id': 'new_key',
            'secret_access_key': 'new_secret',
            'config_scheme': 'create_report'},
            'last_import_at': 1,
            'last_import_modified_at': 1,
            'last_import_attempt_at': 1,
            'last_import_attempt_error': 'error'
        }
        code, cloud_acc = self.client.cloud_account_update(cloud_acc['id'],
                                                           params)
        self.assertEqual(code, 200)
        activity_param_tuples1 = self.get_publish_activity_tuple(
            self.org_id, cloud_acc['id'], 'cloud_account',
            'cloud_account_updated', {
                'object_name': cloud_acc['name'],
                'level': 'INFO'
            })
        p_publish_activities1.assert_called_once_with(
            *activity_param_tuples1, add_token=True
        )

        p_publish_activities2 = patch(
            'rest_api.rest_api_server.controllers.base.BaseController.'
            'publish_activities_task'
        ).start()
        code, cloud_acc = self.client.cloud_account_update(
            cloud_acc['id'], {'last_import_at': 1})
        self.assertEqual(code, 200)
        p_publish_activities2.assert_not_called()

        code, cloud_acc = self.client.cloud_account_update(
            cloud_acc['id'], {'last_import_modified_at': 1})
        self.assertEqual(code, 200)
        p_publish_activities2.assert_not_called()

        code, cloud_acc = self.client.cloud_account_update(cloud_acc['id'], {
            'last_import_modified_at': 1, 'last_import_at': 1})
        self.assertEqual(code, 200)
        p_publish_activities2.assert_not_called()

        code, cloud_acc = self.client.cloud_account_update(cloud_acc['id'], {
            'last_import_attempt_at': 1})
        self.assertEqual(code, 200)
        p_publish_activities2.assert_not_called()

        code, cloud_acc = self.client.cloud_account_update(cloud_acc['id'], {
            'last_import_attempt_error': 'error'})
        self.assertEqual(code, 200)
        p_publish_activities2.assert_not_called()

        code, cloud_acc = self.client.cloud_account_update(cloud_acc['id'], {
            'last_import_attempt_at': 1, 'last_import_attempt_error': 'error'})
        self.assertEqual(code, 200)
        p_publish_activities2.assert_not_called()

    def test_create_linked_aws_cloud_acc(self):
        self.p_configure_aws.stop()
        self.valid_aws_cloud_acc['config']['linked'] = True

        code, cloud_acc = self.create_cloud_account(self.org_id,
                                                    self.valid_aws_cloud_acc)
        self.assertEqual(code, 201)
        self.valid_aws_cloud_acc_response['config']['linked'] = True
        self.assertDictEqual(self.valid_aws_cloud_acc_response['config'],
                             cloud_acc['config'])

    def test_create_not_linked_aws_cloud(self):
        self.valid_aws_cloud_acc['config']['linked'] = False
        code, cloud_acc = self.create_cloud_account(
            self.org_id, self.valid_aws_cloud_acc)
        self.assertEqual(code, 201)
        self.assertFalse(cloud_acc.get('config', {}).get('linked', True))

    def test_list_by_linked_and_type(self):
        code, cloud_acc = self.create_cloud_account(
            self.org_id, self.valid_aws_cloud_acc)
        self.assertEqual(code, 201)
        _, cloud_acc_list = self.client.cloud_account_list(self.org_id)
        self.assertEqual(len(cloud_acc_list['cloud_accounts']), 1)

        _, cloud_acc_list = self.client.cloud_account_list(
            self.org_id, type='aws_cnr')
        self.assertEqual(len(cloud_acc_list['cloud_accounts']), 1)

        _, cloud_acc_list = self.client.cloud_account_list(
            self.org_id, type='azure_cnr')
        self.assertEqual(len(cloud_acc_list['cloud_accounts']), 0)

        _, cloud_acc_list = self.client.cloud_account_list(
            self.org_id, type='gcp_cnr')
        self.assertEqual(len(cloud_acc_list['cloud_accounts']), 0)

        cloud_acc2_dict = deepcopy(self.valid_aws_cloud_acc)
        cloud_acc2_dict['name'] = 'manual import cloud_acc'
        code, cloud_acc = self.create_cloud_account(self.org_id, cloud_acc2_dict)
        self.assertEqual(code, 201)

        _, cloud_acc_list = self.client.cloud_account_list(
            self.org_id, type='aws_cnr')
        self.assertEqual(len(cloud_acc_list['cloud_accounts']), 2)

        cloud_acc3_dict = deepcopy(self.valid_aws_cloud_acc)
        cloud_acc3_dict['config']['linked'] = True
        cloud_acc3_dict['name'] = 'linked cloud_acc'
        code, cloud_acc = self.create_cloud_account(self.org_id, cloud_acc3_dict)
        self.assertEqual(code, 201)

        _, cloud_acc_list = self.client.cloud_account_list(
            self.org_id, type='aws_cnr', only_linked=True)
        self.assertEqual(len(cloud_acc_list['cloud_accounts']), 1)
        self.assertEqual(cloud_acc_list['cloud_accounts'][0]['id'], cloud_acc['id'])

    def test_list_invalid_filters(self):
        for bad_value in [1, 'str']:
            code, cloud_acc_list = self.client.cloud_account_list(
                self.org_id, details=bad_value)
            self.assertEqual(code, 400)
            self.verify_error_code(cloud_acc_list, 'OE0217')

            code, cloud_acc_list = self.client.cloud_account_list(
                self.org_id, auto_import=bad_value)
            self.assertEqual(code, 400)
            self.verify_error_code(cloud_acc_list, 'OE0217')

    def test_create_azure_cloud_acc(self):
        code, cloud_acc = self.create_cloud_account(
            self.org_id, self.valid_azure_cloud_acc)
        self.assertEqual(code, 201)
        self.assertDictEqual(self.valid_azure_response['config'],
                             cloud_acc['config'])

    def test_create_azure_cloud_acc_subscription_id_is_spaces(self):
        for invalid_subscription_id in [" ", "    "]:
            invalid_azure_cloud_acc = {
                'name': 'azure cloud_acc',
                'type': 'azure_cnr',
                'config': {
                    'subscription_id': invalid_subscription_id,
                    'secret': 'secret',
                    'client_id': 'id',
                    'tenant': 't'
                }
            }
            code, resp = self.client.cloud_account_create(
                self.org_id, invalid_azure_cloud_acc)
            self.assertEqual(code, 400)
            self.assertEqual(resp['error']['reason'],
                             'subscription_id should not contain only whitespaces')

    def test_cloud_acc_for_deleted_org(self):
        patch('rest_api.rest_api_server.controllers.employee.'
              'EmployeeController.delete').start()
        code, cloud_acc = self.create_cloud_account(
            self.org_id, self.valid_aws_cloud_acc)
        self.assertEqual(code, 201)
        code, _ = self.client.organization_delete(self.org_id)
        self.assertEqual(code, 204)
        code, _ = self.client.cloud_account_get(cloud_acc['id'])
        self.assertEqual(code, 404)
        code, _ = self.client.cloud_account_list(self.org_id)
        self.assertEqual(code, 404)

    def test_list_with_recommendation_flag(self):
        cloud_enabled_recommendations = deepcopy(self.valid_aws_cloud_acc)
        cloud_enabled_recommendations['name'] = 'enabled'
        cloud_enabled_recommendations['process_recommendations'] = True
        cloud_disabled_recommendations = deepcopy(self.valid_aws_cloud_acc)
        cloud_disabled_recommendations['name'] = 'disabled'
        cloud_disabled_recommendations['process_recommendations'] = False
        code, enabled = self.create_cloud_account(
            self.org_id, cloud_enabled_recommendations)
        self.assertEqual(code, 201)
        code, disabled = self.create_cloud_account(
            self.org_id, cloud_disabled_recommendations)
        self.assertEqual(code, 201)

        code, ca_list = self.client.cloud_account_list(self.org_id)
        self.assertEqual(code, 200)
        self.assertEqual(len(ca_list['cloud_accounts']), 2)

        code, ca_list = self.client.cloud_account_list(
            self.org_id, process_recommendations=True)
        self.assertEqual(code, 200)
        self.assertEqual(len(ca_list['cloud_accounts']), 1)
        self.assertEqual(ca_list['cloud_accounts'][0]['id'], enabled['id'])

        code, ca_list = self.client.cloud_account_list(
            self.org_id, process_recommendations=False)
        self.assertEqual(code, 200)
        self.assertEqual(len(ca_list['cloud_accounts']), 1)
        self.assertEqual(ca_list['cloud_accounts'][0]['id'], disabled['id'])

    def test_patch_disable_enable_recommendations(self):
        ca_params = self.valid_aws_cloud_acc
        ca_params['process_recommendations'] = False
        code, cloud_acc = self.create_cloud_account(
            self.org_id, ca_params)
        self.assertEqual(code, 201)

        ca_patch = {'process_recommendations': True}
        code, cloud_acc = self.client.cloud_account_update(
            cloud_acc['id'], ca_patch)
        self.assertEqual(code, 200)
        self.assertEqual(cloud_acc['process_recommendations'], True)

        ca_patch = {'process_recommendations': False}
        code, cloud_acc = self.client.cloud_account_update(
            cloud_acc['id'], ca_patch)
        self.assertEqual(code, 200)
        self.assertEqual(cloud_acc['process_recommendations'], False)

    def test_create_with_cleaned_at(self):
        ca_params = self.valid_aws_cloud_acc
        ca_params['cleaned_at'] = 123
        code, resp = self.create_cloud_account(
            self.org_id, ca_params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0211')

    def test_patch_cleaned_at(self):
        ca_params = self.valid_aws_cloud_acc
        code, cloud_acc = self.create_cloud_account(
            self.org_id, ca_params)
        self.assertEqual(code, 201)

        ca_patch = {'cleaned_at': 123}
        code, cloud_acc = self.client.cloud_account_update(
            cloud_acc['id'], ca_patch)
        self.assertEqual(code, 200)
        self.assertEqual(cloud_acc['cleaned_at'], 123)

    def test_validation_warning(self):
        p_publish_activities = patch(
            'rest_api.rest_api_server.controllers.base.BaseController.'
            'publish_activities_task'
        ).start()

        warning = 'the Moon is full'
        code, cloud_acc = self.create_cloud_account(
            self.org_id, self.valid_aws_cloud_acc, warnings=[warning])
        self.assertEqual(code, 201)
        activity_param_tuples = self.get_publish_activity_tuple(
            self.org_id, cloud_acc['id'], 'cloud_account',
            'cloud_account_warning', {
                'object_name': cloud_acc['name'],
                'level': 'WARNING',
                'reason': warning
            })
        p_publish_activities.assert_any_call(
            *activity_param_tuples, add_token=True
        )

        params = {'config': {
            'access_key_id': 'new_key',
            'secret_access_key': 'new_secret',
            'config_scheme': 'create_report'
        }}

        warning = 'the Moon is new'
        patch('tools.cloud_adapter.clouds.aws.Aws.validate_credentials',
              return_value={'account_id': 'another_acc_id',
                            'warnings': [warning]}).start()
        code, cloud_acc = self.client.cloud_account_update(
            cloud_acc['id'], params)
        self.assertEqual(code, 200)
        activity_param_tuples = self.get_publish_activity_tuple(
            self.org_id, cloud_acc['id'], 'cloud_account',
            'cloud_account_warning', {
                'object_name': cloud_acc['name'],
                'level': 'WARNING',
                'reason': warning
            })
        p_publish_activities.assert_any_call(
            *activity_param_tuples, add_token=True
        )

    def test_create_kubernetes_cloud_acc(self):
        code, cloud_acc = self.create_cloud_account(
            self.org_id, self.valid_kubernetes_cloud_acc)
        self.assertEqual(code, 201)
        self.assertDictEqual(self.valid_kubernetes_response['config'],
                             cloud_acc['config'], '%s and %s' % (
                                 self.valid_kubernetes_response['config'],
                                 cloud_acc['config']))

    def test_create_kubernetes_cloud_acc_custom_cost_model(self):
        kubernetes_cost_model = self.default_kubernetes_cost_model.copy()
        kubernetes_cost_model['cpu_hourly_cost'] = 0.123
        valid_kubernetes_cloud_acc = self.valid_kubernetes_cloud_acc.copy()
        valid_kubernetes_cloud_acc['config']['cost_model'] = kubernetes_cost_model
        code, cloud_acc = self.create_cloud_account(
            self.org_id, valid_kubernetes_cloud_acc)
        self.assertEqual(code, 201)
        self.assertDictEqual(
            kubernetes_cost_model, cloud_acc['config']['cost_model'])

    def test_create_kubernetes_cloud_acc_cost_model_unexpected(self):
        kubernetes_cost_model = self.default_kubernetes_cost_model.copy()
        kubernetes_cost_model['gpu_hourly_cost'] = 0.123
        valid_kubernetes_cloud_acc = self.valid_kubernetes_cloud_acc.copy()
        valid_kubernetes_cloud_acc['config']['cost_model'] = kubernetes_cost_model
        code, response = self.create_cloud_account(
            self.org_id, valid_kubernetes_cloud_acc)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0212')

    def test_create_kubernetes_cloud_acc_partial_cost_model(self):
        kubernetes_cost_model = self.default_kubernetes_cost_model.copy()
        kubernetes_cost_model.pop('cpu_hourly_cost')
        valid_kubernetes_cloud_acc = self.valid_kubernetes_cloud_acc.copy()
        valid_kubernetes_cloud_acc['config']['cost_model'] = kubernetes_cost_model
        code, res = self.create_cloud_account(
            self.org_id, valid_kubernetes_cloud_acc)
        self.assertEqual(code, 400)
        self.assertEqual(res.get('error', {}).get('error_code'), 'OE0212')

    @patch('rest_api.rest_api_server.controllers.cloud_account.'
           'ExpensesRecalculationScheduleController.schedule')
    def test_patch_kubernetes(self, schedule_patch):
        code, cloud_acc = self.create_cloud_account(
            self.org_id, self.valid_kubernetes_cloud_acc)
        self.assertEqual(code, 201)
        self.assertDictEqual(self.valid_kubernetes_response['config'],
                             cloud_acc['config'])

        valid_kubernetes_config = self.valid_kubernetes_cloud_acc['config'].copy()
        valid_kubernetes_config['user'] = 'name'
        params = {'config': valid_kubernetes_config}
        code, ret = self.client.cloud_account_update(
            cloud_acc['id'], params)
        self.assertEqual(code, 200)

        kubernetes_cost_model = self.default_kubernetes_cost_model.copy()
        kubernetes_cost_model['cpu_hourly_cost'] = 0.123
        valid_kubernetes_config['cost_model'] = kubernetes_cost_model
        valid_kubernetes_config.pop('user')
        valid_kubernetes_config.pop('password')
        params = {'config': valid_kubernetes_config}
        code, ret = self.client.cloud_account_update(
            cloud_acc['id'], params)
        self.assertEqual(code, 200)

        self.assertDictEqual(ret.get('config', {}).get('cost_model'),
                             valid_kubernetes_config.get('cost_model'))
        self.assertEqual(schedule_patch.call_count, 1)

    def test_recalculation_start_event(self):
        code, cloud_acc = self.create_cloud_account(
            self.org_id, self.valid_kubernetes_cloud_acc)
        self.assertEqual(code, 201)

        kubernetes_cost_model = self.default_kubernetes_cost_model.copy()
        kubernetes_cost_model['cpu_hourly_cost'] = 0.123
        valid_kubernetes_cloud_acc = self.valid_kubernetes_cloud_acc.copy()
        valid_kubernetes_cloud_acc['config']['cost_model'] = kubernetes_cost_model

        params = {'config': valid_kubernetes_cloud_acc['config']}
        patch('tools.cloud_adapter.clouds.kubernetes.Kubernetes.validate_credentials',
              return_value={'account_id': cloud_acc['account_id'],
                            'warnings': []}).start()
        patch('rest_api.rest_api_server.controllers.report_import.'
              'ReportImportBaseController.publish_task').start()
        p_publish_activities = patch(
            'rest_api.rest_api_server.controllers.base.BaseController.'
            'publish_activities_task'
        ).start()
        code, ret = self.client.cloud_account_update(
            cloud_acc['id'], params)
        self.assertEqual(code, 200)
        p_publish_activities.assert_has_calls([
            call(self.org_id, ANY, 'report_import', 'recalculation_started',
                 {'object_name': cloud_acc['name'],
                  'cloud_account_id': cloud_acc['id'],
                  'level': 'INFO'},
                 'report_import.recalculation_started', add_token=True)])

    @patch('rest_api.rest_api_server.controllers.cloud_account.'
           'ExpensesRecalculationScheduleController.schedule')
    def test_patch_kubernetes_cost_model_only(self, schedule_patch):
        code, cloud_acc = self.create_cloud_account(
            self.org_id, self.valid_kubernetes_cloud_acc)
        self.assertEqual(code, 201)
        self.assertDictEqual(self.valid_kubernetes_response['config'],
                             cloud_acc['config'])

        kubernetes_cost_model = self.default_kubernetes_cost_model.copy()
        kubernetes_cost_model['cpu_hourly_cost'] = 0.123

        params = {'config': {'cost_model': kubernetes_cost_model}}
        code, ret = self.client.cloud_account_update(
            cloud_acc['id'], params)
        self.assertEqual(code, 200)
        cloud_acc['config']['cost_model'] = kubernetes_cost_model
        self.assertDictEqual(ret, cloud_acc, '%s and %s' % (ret, cloud_acc))
        self.assertEqual(schedule_patch.call_count, 1)

        kubernetes_cost_model = self.default_kubernetes_cost_model.copy()
        kubernetes_cost_model['cpu_hourly_cost'] = 123

        params = {'config': {'cost_model': kubernetes_cost_model}}
        code, ret = self.client.cloud_account_update(
            cloud_acc['id'], params)
        self.assertEqual(code, 200)
        cloud_acc['config']['cost_model'] = kubernetes_cost_model
        self.assertDictEqual(ret, cloud_acc, '%s and %s' % (ret, cloud_acc))
        self.assertEqual(schedule_patch.call_count, 2)

    def test_patch_nonkubernetes_cost_model_only(self):
        account_id = self.gen_id()
        code, cloud_acc = self.create_cloud_account(
            self.org_id, self.valid_aws_cloud_acc, account_id=account_id)
        self.assertEqual(code, 201)
        self.assertEqual(self.p_configure_aws.call_count, 1)

        params = {'config': {
            'cost_model': self.default_kubernetes_cost_model
        }}
        patch('tools.cloud_adapter.clouds.aws.Aws.validate_credentials',
              return_value={'account_id': account_id, 'warnings': []}).start()
        code, ret = self.client.cloud_account_update(cloud_acc['id'], params)
        self.assertEqual(code, 400)

    def test_patch_kubernetes_import_time(self):
        kubernetes_cost_model = self.default_kubernetes_cost_model.copy()
        kubernetes_cost_model['cpu_hourly_cost'] = 0.123
        valid_kubernetes_cloud_acc = self.valid_kubernetes_cloud_acc.copy()
        valid_kubernetes_cloud_acc['config']['cost_model'] = kubernetes_cost_model
        code, cloud_acc = self.create_cloud_account(
            self.org_id, valid_kubernetes_cloud_acc)
        self.assertEqual(code, 201)

        patch('tools.cloud_adapter.clouds.kubernetes.Kubernetes.validate_credentials',
              return_value={'account_id': cloud_acc['account_id'],
                            'warnings': []}).start()
        ts = int(datetime.datetime.utcnow().timestamp())
        code, res = self.client.cloud_account_update(
            cloud_acc['id'], {'last_import_at': ts})
        self.assertEqual(code, 200)
        self.assertDictEqual(kubernetes_cost_model,
                             res.get('config', {}).get('cost_model', {}))
        self.assertEqual(ts, res.get('last_import_at', 0))

    @patch('rest_api.rest_api_server.controllers.cloud_account.'
           'ExpensesRecalculationScheduleController.schedule')
    def test_patch_kubernetes_cost_model_duplicate(self, schedule_patch):
        code, cloud_acc = self.create_cloud_account(
            self.org_id, self.valid_kubernetes_cloud_acc)
        self.assertEqual(code, 201)
        self.assertDictEqual(self.valid_kubernetes_response['config'],
                             cloud_acc['config'])

        patch('tools.cloud_adapter.clouds.kubernetes.Kubernetes.validate_credentials',
              return_value={'account_id': cloud_acc['account_id'],
                            'warnings': []}).start()

        kubernetes_cost_model = self.default_kubernetes_cost_model.copy()
        params = {'config': {'cost_model': kubernetes_cost_model}}
        code, ret = self.client.cloud_account_update(
            cloud_acc['id'], params)
        self.assertEqual(code, 200)
        self.assertDictEqual(ret, cloud_acc, '%s and %s' % (ret, cloud_acc))
        self.assertEqual(schedule_patch.call_count, 0)

        kubernetes_cost_model['cpu_hourly_cost'] = 0.123
        kubernetes_cost_model['memory_hourly_cost'] = 0.234
        params = {'config': {'cost_model': kubernetes_cost_model}}
        code, ret = self.client.cloud_account_update(
            cloud_acc['id'], params)
        self.assertEqual(code, 200)
        cloud_acc['config']['cost_model'] = kubernetes_cost_model
        self.assertDictEqual(ret, cloud_acc, '%s and %s' % (ret, cloud_acc))
        self.assertEqual(schedule_patch.call_count, 1)

        code, ret = self.client.cloud_account_update(
            cloud_acc['id'], params)
        self.assertEqual(code, 200)
        self.assertDictEqual(ret, cloud_acc, '%s and %s' % (ret, cloud_acc))
        self.assertEqual(schedule_patch.call_count, 1)

    def test_create_environment_cloud_account_api(self):
        account_id = self.gen_id()
        config = {
            'name': 'my cloud_acc',
            'type': 'environment'
        }
        code, resp = self.create_cloud_account(
            self.org_id, config, account_id=account_id)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0436')

    def test_get_or_create_environment_cloud_account(self):
        ca_controller = self._make_controller(CloudAccountController)
        patch(
            'rest_api.rest_api_server.controllers.assignment.AssignmentController.'
            '_authorize_action_for_pool', return_value=True).start()
        db = DBFactory(DBType.Test, None).db
        engine = db.engine
        session = BaseDB.session(engine)()
        cloud_accs = session.query(CloudAccount).all()
        self.assertEqual(len(cloud_accs), 0)

        created_ca = ca_controller.get_or_create_environment_cloud_account(
            self.org_id)
        self.assertEqual(created_ca.organization_id, self.org_id)
        self.assertEqual(created_ca.deleted_at, 0)
        self.assertEqual(created_ca.account_id, self.org_id)
        self.assertEqual(created_ca.type.value, 'environment')
        self.assertEqual(created_ca.name, 'Environment')

        another_ca = ca_controller.get_or_create_environment_cloud_account(
            self.org_id)
        self.assertEqual(another_ca, created_ca)
        cloud_accs = session.query(CloudAccount).all()
        self.assertEqual(len(cloud_accs), 1)

        discovery_infos = session.query(DiscoveryInfo).all()
        self.assertEqual(len(discovery_infos), 0)

    def test_environment_recommendations(self):
        ca_controller = self._make_controller(CloudAccountController)
        patch(
            'rest_api.rest_api_server.controllers.assignment.AssignmentController.'
            '_authorize_action_for_pool', return_value=True).start()
        created_ca = ca_controller.get_or_create_environment_cloud_account(
            self.org_id)
        self.assertFalse(created_ca.process_recommendations)

        ca_patch = {'process_recommendations': True}
        code, cloud_acc = self.client.cloud_account_update(
            created_ca.id, ca_patch)
        self.assertEqual(code, 424)
        self.verify_error_code(cloud_acc, 'OE0476')

    def test_environment_account_discovery_info(self):
        ca_controller = self._make_controller(CloudAccountController)
        patch(
            'rest_api.rest_api_server.controllers.assignment.'
            'AssignmentController._authorize_action_for_pool',
            return_value=True).start()
        created_ca = ca_controller.get_or_create_environment_cloud_account(
            self.org_id)
        code, cloud_acc_list = self.client.cloud_account_get(
            created_ca.id, details=True)
        self.assertEqual(code, 200)
        self.assertEqual(cloud_acc_list['details']['discovery_infos'], [])

    def test_delete_environment_account(self):
        ca_controller = self._make_controller(CloudAccountController)
        patch(
            'rest_api.rest_api_server.controllers.assignment.AssignmentController.'
            '_authorize_action_for_pool', return_value=True).start()
        created_ca = ca_controller.get_or_create_environment_cloud_account(
            self.org_id)

        code, cloud_acc = self.client.cloud_account_delete(created_ca.id)
        self.assertEqual(code, 424)
        self.verify_error_code(cloud_acc, 'OE0477')

    def test_delete_org_constraint_on_cloud_acc_deleting(self):
        code, cloud_acc = self.create_cloud_account(self.org_id,
                                                    self.valid_aws_cloud_acc)
        self.assertEqual(code, 201)
        constr = self.create_org_constraint(
            self.org_id, self.org['pool_id'],
            filters={'cloud_account_id': [cloud_acc['id']]})

        code, cloud_acc = self.client.cloud_account_delete(cloud_acc['id'])
        self.assertEqual(code, 204)
        code, resp = self.client.organization_constraint_get(constr['id'])
        self.assertEqual(code, 404)
        self.assertEqual(resp['error']['error_code'], 'OE0002')

    def test_delete_org_limit_hit_on_cloud_acc_deleting(self):
        code, cloud_acc = self.create_cloud_account(self.org_id,
                                                    self.valid_aws_cloud_acc)
        self.assertEqual(code, 201)
        self.create_org_limit_hit(self.org_id, self.org['pool_id'],
                                  filters={'cloud_account_id': [cloud_acc['id']]})

        code, cloud_acc = self.client.cloud_account_delete(cloud_acc['id'])
        self.assertEqual(code, 204)
        db = DBFactory(DBType.Test, None).db
        engine = db.engine
        session = BaseDB.session(engine)()
        hits = session.query(OrganizationLimitHit).filter(and_(
            OrganizationLimitHit.organization_id == self.org_id,
            OrganizationLimitHit.deleted.is_(False)
        )).one_or_none()
        self.assertEqual(hits, None)

    def test_delete_cloud_acc_email(self):
        code, cloud_acc = self.create_cloud_account(self.org_id,
                                                    self.valid_aws_cloud_acc)
        self.assertEqual(code, 201)
        self.p_send_ca_email.reset_mock()
        code, cloud_acc = self.client.cloud_account_delete(cloud_acc['id'])
        self.assertEqual(code, 204)
        self.assertEqual(self.p_send_ca_email.call_count, 1)

        # the email should not be sent for demo organizations
        db = DBFactory(DBType.Test, None).db
        engine = db.engine
        session = BaseDB.session(engine)()
        session.query(Organization).filter(
            Organization.id == self.org_id).update({'is_demo': True})
        code, cloud_acc2 = self.create_cloud_account(
            self.org_id, self.valid_azure_cloud_acc)
        self.p_send_ca_email.reset_mock()
        code, resp = self.client.cloud_account_delete(cloud_acc2['id'])
        self.assertEqual(code, 204)
        self.p_send_ca_email.assert_not_called()

    def test_cloud_accounts_encryption(self):
        code, cloud_acc = self.create_cloud_account(self.org_id,
                                                    self.valid_aws_cloud_acc)
        self.assertEqual(code, 201)
        ca_obj = self.get_cloud_account_object(cloud_acc['id'])
        self.assertEqual(decode_config(ca_obj.config),
                         self.valid_aws_cloud_acc['config'])

        account_2_id = self.gen_id()
        patch('tools.cloud_adapter.clouds.aws.Aws.validate_credentials',
              return_value={'account_id': account_2_id,
                            'warnings': []}).start()
        params = {'config': {
            'access_key_id': 'new_key_1',
            'secret_access_key': 'new_secret',
            'config_scheme': 'create_report'
        }}
        code, cloud_acc = self.client.cloud_account_update(
            cloud_acc['id'], params)
        ca_obj = self.get_cloud_account_object(cloud_acc['id'])
        self.assertEqual(decode_config(ca_obj.config), params['config'])

    def test_create_gcp_cloud_acc(self):
        code, cloud_acc = self.create_cloud_account(
            self.org_id, self.valid_gcp_cloud_acc)
        self.assertEqual(code, 201)
        config = self.valid_gcp_cloud_acc['config'].copy()
        config.pop('credentials')
        self.assertDictEqual(config, cloud_acc['config'])

    def test_create_gcp_non_standard_billing(self):
        ca_config = copy.deepcopy(self.valid_gcp_cloud_acc)
        ca_config['config']['billing_data']['table_name'] = "bad_table_name"
        code, resp = self.client.cloud_account_create(
            self.org_id, ca_config)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0455')

    def test_create_gcp_incorrect_table_name(self):
        ca_config = copy.deepcopy(self.valid_gcp_cloud_acc)
        ca_config['config']['billing_data']['table_name'] = "gcp_billing_export_v1.something"
        code, response = self.client.cloud_account_verify(ca_config)
        self.assertEqual(code, 400)
        self.assertTrue('Invalid billing table_name' in response['error']['reason'])

    def test_create_gcp_incorrect_dataset_name(self):
        ca_config = copy.deepcopy(self.valid_gcp_cloud_acc)
        ca_config['config']['billing_data']['dataset_name'] = "dataset.table"
        code, response = self.client.cloud_account_verify(ca_config)
        self.assertEqual(code, 400)
        self.assertTrue('Invalid billing dataset_name' in response['error']['reason'])

    @patch('rest_api.rest_api_server.controllers.report_import.ReportImportBaseController.create')
    def test_assign_task(self, p_create):
        self.p_configure_aws.stop()
        _, cloud_acc = self.create_cloud_account(self.org_id,
                                                 self.valid_aws_cloud_acc)
        self.assertEqual(p_create.call_count, 1)
        p_create.assert_called_with(cloud_acc['id'], priority=8)

    @patch('rest_api.rest_api_server.controllers.report_import.ReportImportBaseController.create')
    def test_assign_task_linked_acc(self, p_create):
        self.p_configure_aws.stop()
        _, cloud_acc = self.create_cloud_account(self.org_id2,
                                                 self.valid_aws_cloud_acc)
        self.assertEqual(p_create.call_count, 1)
        p_create.assert_called_with(cloud_acc['id'], priority=8)
        p_create.reset_mock()
        self.valid_aws_cloud_acc['config']['linked'] = True
        self.valid_aws_cloud_acc['name'] = 'linked_acc'

        self.create_cloud_account(self.org_id2, self.valid_aws_cloud_acc)
        self.assertEqual(p_create.call_count, 1)
        p_create.assert_called_with(cloud_acc['id'], priority=8)

    @patch('rest_api.rest_api_server.controllers.cloud_account.CloudAccountController._publish_cloud_acc_activity')
    @patch('rest_api.rest_api_server.controllers.cloud_account.ExpensesRecalculationScheduleController.schedule')
    def test_notify_ca_changed_succeed(self, schedule_patch, publish_patch):
        account_id = self.gen_id()
        code, cloud_acc = self.create_cloud_account(
            self.org_id, self.valid_aws_cloud_acc, account_id=account_id)
        self.assertEqual(code, 201)

        params = {'config': {
            'access_key_id': 'new_key',
            'secret_access_key': 'new_secret',
            'config_scheme': 'create_report'
        }}
        patch('tools.cloud_adapter.clouds.aws.Aws.validate_credentials',
              return_value={'account_id': account_id, 'warnings': []}).start()
        publish_patch.reset_mock()
        code, ret = self.client.cloud_account_update(cloud_acc['id'], params)
        self.assertEqual(code, 200)
        publish_patch.assert_called_once()

    @patch('rest_api.rest_api_server.controllers.cloud_account.CloudAccountController._publish_cloud_acc_activity')
    @patch('rest_api.rest_api_server.controllers.cloud_account.ExpensesRecalculationScheduleController.schedule')
    def test_notify_ca_changed_skip_sending(self, schedule_patch, publish_patch):
        account_id = self.gen_id()
        code, cloud_acc = self.create_cloud_account(
            self.org_id, self.valid_aws_cloud_acc, account_id=account_id)
        self.assertEqual(code, 201)

        params = {'last_import_at': int(datetime.datetime.utcnow().timestamp())}
        patch('tools.cloud_adapter.clouds.aws.Aws.validate_credentials',
              return_value={'account_id': account_id, 'warnings': []}).start()
        publish_patch.reset_mock()
        code, ret = self.client.cloud_account_update(cloud_acc['id'], params)
        self.assertEqual(code, 200)
        publish_patch.assert_not_called()

    def test_auto_import_change(self):
        p_schedule_import = patch(
            'rest_api.rest_api_server.controllers.cloud_account.CloudAccountController.'
            '_schedule_report_import'
        ).start()
        body = {
            'name': 'my cloud_acc 1', 'type': 'aws_cnr',
            'config': self.valid_cloud_config, 'auto_import': False
        }
        code, cloud_acc = self.create_cloud_account(self.org_id, body)
        self.assertEqual(code, 201)
        self.assertEqual(cloud_acc['auto_import'], False)
        p_schedule_import.assert_not_called()

        body = {
            'name': 'my cloud_acc 2', 'type': 'aws_cnr',
            'config': self.valid_cloud_config
        }
        code, cloud_acc = self.create_cloud_account(
            self.org_id, body)
        self.assertEqual(code, 201)
        self.assertEqual(cloud_acc['auto_import'], True)
        p_schedule_import.assert_called_once()

        body.update({
            'name': 'my cloud_acc 3', 'auto_import': True
        })
        code, cloud_acc = self.create_cloud_account(
            self.org_id, body)
        self.assertEqual(code, 201)
        self.assertEqual(cloud_acc['auto_import'], True)
        self.assertEqual(p_schedule_import.call_count, 2)

        code, resp = self.client.cloud_account_update(
            cloud_acc['id'], {'auto_import': False})
        self.assertEqual(code, 200)

    def test_auto_import_negative(self):
        valid_body = {
            'name': 'my cloud_acc 1', 'type': 'aws_cnr',
            'config': self.valid_cloud_config
        }
        for k in [2, '', 'False']:
            body = valid_body.copy()
            body['auto_import'] = k
            code, resp = self.create_cloud_account(
                self.org_id, body)
            self.assertEqual(code, 400)

        code, cloud_acc = self.create_cloud_account(
            self.org_id, valid_body)
        self.assertEqual(code, 201)
        for k in [2, '', 'False']:
            code, resp = self.client.cloud_account_update(
                cloud_acc['id'], {'auto_import': k})
            self.assertEqual(code, 400)

    def test_create_with_parent_id_param(self):
        self.valid_azure_cloud_acc['parent_id'] = str(uuid.uuid4())
        code, resp = self.create_cloud_account(
            self.org_id, self.valid_azure_cloud_acc)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0212')

    def test_create_azure_tenant_with_subscription(self):
        body = self.valid_azure_cloud_acc.copy()
        body['type'] = 'azure_tenant'
        code, resp = self.create_cloud_account(
            self.org_id, body)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0212')

    def test_azure_tenant_workflow(self):
        body = {
            'name': 'azure cloud_acc',
            'type': 'azure_tenant',
            'config': {
                'secret': 'secret',
                'client_id': 'id',
                'tenant': 't'
            }
        }
        patch('tools.cloud_adapter.clouds.azure_tenant.AzureTenant.validate_credentials',
              return_value={'account_id': 't', 'warnings': []}
              ).start()
        code, parent_ca = self.create_cloud_account(self.org_id, body)
        self.assertEqual(code, 201)
        self.assertEqual(parent_ca['type'], body['type'])
        self.assertEqual(parent_ca['config'],
                         {'client_id': 'id', 'tenant': 't'})
        self.p_configure_azure.return_value = {
            'config_updates': {'expense_import_scheme': 'raw_usage'},
            'warnings': []
        }
        patch('tools.cloud_adapter.clouds.azure_tenant.AzureTenant.get_children_configs',
              return_value=[
                  {
                      'name': 'child 1',
                      'config': {'subscription_id': 'subscription_1'},
                      'type': 'azure_cnr'
                  }
              ]).start()
        patch('tools.cloud_adapter.clouds.azure.Azure.validate_credentials',
              return_value={'account_id': 'subscription_1', 'warnings': []}
              ).start()
        code, _ = self.client.observe_resources(self.org_id)
        self.assertEqual(code, 204)
        code, resp = self.client.cloud_account_list(self.org_id)
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['cloud_accounts']), 2)
        child_ca_id = None
        for c in resp['cloud_accounts']:
            if c['id'] != parent_ca['id']:
                child_ca_id = c['id']
                self.assertEqual(c['config'], {
                    'secret': 'secret',
                    'client_id': 'id',
                    'tenant': 't',
                    'subscription_id': 'subscription_1',
                    'expense_import_scheme': 'raw_usage'
                })
                self.assertEqual(c['type'], 'azure_cnr')
                ca_obj = self.get_cloud_account_object(child_ca_id)
                conf = decode_config(ca_obj.config)
                self.assertEqual(conf, {
                    'subscription_id': 'subscription_1',
                    'expense_import_scheme': 'raw_usage'
                })

        for params in [
            {'config': {'subscription_id': 'new_key'}},
            {'parent_id': str(uuid.uuid4())}
        ]:
            code, ret = self.client.cloud_account_update(child_ca_id, params)
            self.assertEqual(code, 400)
            self.verify_error_code(ret, 'OE0211')

        self.client.cloud_account_delete(child_ca_id)
        code, resp = self.client.cloud_account_list(self.org_id)
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['cloud_accounts']), 1)

        code, _ = self.client.observe_resources(self.org_id)
        code, resp = self.client.cloud_account_list(self.org_id)
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['cloud_accounts']), 2)
        with freeze_time(datetime.datetime(2023, 5, 1)):
            code, _ = self.client.cloud_account_delete(parent_ca['id'])
            self.assertEqual(code, 204)
        code, resp = self.client.cloud_account_list(self.org_id)
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['cloud_accounts']), 0)

    def test_create_nebius_cloud_acc(self):
        code, cloud_acc = self.create_cloud_account(
            self.org_id, self.valid_nebius_cloud_acc)
        self.assertEqual(code, 201)
        config = self.valid_nebius_cloud_acc['config'].copy()
        # protected keys are removed
        config.pop('private_key', None)
        config.pop('secret_access_key', None)
        self.assertDictEqual(config, cloud_acc['config'])

    def test_create_nebius_optional_params(self):
        for param in ['endpoint', 'region_name', 's3_endpoint',
                      'console_endpoint']:
            params = deepcopy(self.valid_nebius_cloud_acc)
            params['name'] = str(uuid.uuid4())
            params['config'][param] = param
            code, resp = self.create_cloud_account(
                self.org_id, params)
            self.assertEqual(code, 201)
            self.assertEqual(resp['config'][param], param)

        for param in ['regions_coordinates', 'platforms', 'rds_platforms']:
            params = deepcopy(self.valid_nebius_cloud_acc)
            params['name'] = str(uuid.uuid4())
            params['config'][param] = {'test': 'test'}
            code, resp = self.create_cloud_account(
                self.org_id, params)
            self.assertEqual(code, 201)
            self.assertEqual(resp['config'][param], {'test': 'test'})

    def test_create_nebius_cloud_acc_missing_params(self):
        for param in self.valid_nebius_cloud_acc['config']:
            params = deepcopy(self.valid_nebius_cloud_acc)
            params['config'].pop(param, None)
            code, resp = self.create_cloud_account(
                self.org_id, params)
            self.assertEqual(code, 400)
            self.assertEqual(resp['error']['error_code'], 'OE0216')

    def test_create_nebius_cloud_acc_invalid_params(self):
        for param in self.valid_nebius_cloud_acc['config'].copy():
            for value in [123, {}, []]:
                params = deepcopy(self.valid_nebius_cloud_acc)
                params['config'][param] = value
                code, resp = self.create_cloud_account(
                    self.org_id, params)
                self.assertEqual(code, 400)
                self.assertEqual(resp['error']['error_code'], 'OE0214')

        for param in ['regions_coordinates', 'platforms', 'rds_platforms']:
            for value in [123, 'test']:
                params = deepcopy(self.valid_nebius_cloud_acc)
                params['config'][param] = value
                code, resp = self.create_cloud_account(
                    self.org_id, params)
                self.assertEqual(code, 400)
                self.assertEqual(resp['error']['error_code'], 'OE0344')

    def test_valid_databricks(self):
        patch(
            'tools.cloud_adapter.clouds.databricks.Databricks.validate_credentials',
            return_value={
                'account_id': 'databricks_account_id', 'warnings': []
            }).start()
        code, _ = self.client.cloud_account_verify(
            self.valid_databricks_cloud_acc)
        self.assertEqual(code, 200)
        code, cloud_acc = self.create_cloud_account(
            self.org_id, self.valid_databricks_cloud_acc)
        self.assertEqual(code, 201)
        self.assertEqual(cloud_acc['account_id'], 'databricks_account_id')
        self.assertEqual(cloud_acc['config'], {
            'client_id': 'databricks_client_id',
            'account_id': 'databricks_account_id',
            'cost_model': {}
        })

    def test_databricks_another_currency(self):
        patch(
            'tools.cloud_adapter.clouds.databricks.Databricks.validate_credentials',
            return_value={
                'account_id': 'databricks_account_id', 'warnings': []
            }).start()
        _, org = self.client.organization_create(
            {'name': "organization in BRL", 'currency': 'BRL'})
        code, resp = self.create_cloud_account(
            org['id'], self.valid_databricks_cloud_acc)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0437')

    def test_databricks_verify_config(self):
        credentials = self.valid_databricks_cloud_acc.copy()
        credentials.pop('type')
        code, response = self.client.cloud_account_verify(credentials)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['reason'],
                         'type is not provided')

        self.valid_databricks_cloud_acc['config'].pop('client_secret')
        code, response = self.client.cloud_account_verify(
            self.valid_databricks_cloud_acc)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['reason'],
                         'client_secret is not provided')

    def test_databricks_patch_config(self):
        patch(
            'tools.cloud_adapter.clouds.databricks.Databricks.validate_credentials',
            return_value={
                'account_id': 'databricks_account_id', 'warnings': []
            }).start()
        code, cloud_acc = self.create_cloud_account(
            self.org_id, self.valid_databricks_cloud_acc)
        self.assertEqual(code, 201)
        config = self.valid_databricks_cloud_acc['config'].copy()
        config['cost_model'] = {'new_sku': 2}
        code, ret = self.client.cloud_account_update(cloud_acc['id'],
                                                     {'config': config})
        self.assertEqual(code, 200)
        self.assertEqual(ret['config']['cost_model'], config['cost_model'])
        code, cost_model = self.client.sku_cost_model_get(cloud_acc['id'])
        self.assertEqual(code, 200)
        self.assertEqual(cost_model['value'], config['cost_model'])

    def test_adapter_implemented(self):
        for t in list(CloudTypes):
            CloudAdapter.get_adapter({'type': t.value})
