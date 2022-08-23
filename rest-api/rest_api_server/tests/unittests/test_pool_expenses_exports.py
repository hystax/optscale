import os
from datetime import datetime
from unittest.mock import patch
from rest_api_server.tests.unittests.test_api_base import TestApiBase


class TestExpensesApi(TestApiBase):

    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.org = self.client.organization_create(
            {'name': "organization"})
        self.org_id = self.org['id']
        patch('rest_api_server.controllers.cloud_account.'
              'CloudAccountController._configure_report').start()
        self.p_create_rule = patch(
            'rest_api_server.controllers.rule.RuleController.'
            'create_rule').start()
        cloud_acc = {
            'name': 'cloud_acc',
            'type': 'aws_cnr',
            'config': {
                'access_key_id': 'key',
                'secret_access_key': 'secret',
                'config_scheme': 'create_report'
            }
        }
        self.auth_user_id = self.gen_id()
        _, self.employee = self.client.employee_create(
            self.org_id, {'name': 'name1', 'auth_user_id': self.auth_user_id})
        _, self.cloud_acc1 = self.create_cloud_account(
            self.org_id, cloud_acc, auth_user_id=self.auth_user_id)

        _, self.sub_pool1 = self.client.pool_create(self.org_id, {
            'name': 'sub-pool',
            'parent_id': self.org['pool_id'],
        })
        _, self.sub_pool_deleted = self.client.pool_create(self.org_id, {
            'name': 'sub-pool2',
            'parent_id': self.sub_pool1['id'],
        })
        self.client.pool_delete(self.sub_pool_deleted['id'])

        self.start_date = '20210101'
        self.end_date = '20210202'
        self.start_ts = int(datetime(2021, 1, 1, 0, 0, 0).timestamp())
        self.end_ts = int(datetime(2021, 2, 2, 0, 0, 0).timestamp())
        self.mid_date_ts = int(datetime(2021, 1, 15, 0, 0, 0).timestamp())
        self.exp_start = 123
        exp_end_value = float(456.670000000000015916157281)
        self.exp_end = round(exp_end_value, 6)
        self.dec_exp_end = round(exp_end_value, 6)
        self.exp_total = 12345

    def test_export_create(self):
        public_ip = '172.22.22.22'
        patch('config_client.client.Client.public_ip',
              return_value=public_ip).start()
        code, resp = self.client.pool_expenses_export_create(
            self.sub_pool1['id'])
        self.assertEqual(code, 201)
        self.assertIn(public_ip, resp['expenses_export_link'])

    def test_export_create_not_existing_pool(self):
        code, resp = self.client.pool_expenses_export_create('not-pool')
        self.assertEqual(code, 404)
        self.assertEqual(resp['error']['error_code'], 'OE0002')

        code, resp = self.client.pool_expenses_export_create(
            self.sub_pool_deleted['id'])
        self.assertEqual(code, 404)
        self.assertEqual(resp['error']['error_code'], 'OE0002')

    def test_second_export_create(self):
        code, resp = self.client.pool_expenses_export_create(
            self.sub_pool1['id'])
        self.assertEqual(code, 201)
        code, resp = self.client.pool_expenses_export_create(
            self.sub_pool1['id'])
        self.assertEqual(code, 409)
        self.assertEqual(resp['error']['error_code'], 'OE0469')

    def test_pool_expense_get_all(self):
        patch('rest_api_server.controllers.expense.'
              'PoolFormattedExpenseController.get_formatted_expenses',
              return_value={'expenses': {'breakdown': {
                  str(self.start_ts): [{'expense': self.exp_start}],
                  str(self.end_ts): [{'expense': self.exp_end}]},
                  'total': self.exp_total}}
              ).start()
        code, resp = self.client.pool_expenses_export_create(
            self.sub_pool1['id'])
        self.assertEqual(code, 201)
        code, resp = self.client.pool_expenses_export_data_get(
            self.export_id_from_link(resp['expenses_export_link']))
        self.assertEqual(code, 200)
        self.assertEqual(resp, str(self.exp_total))

    def test_pool_expense_get_by_dates(self):
        _, resource = self.cloud_resource_create(self.cloud_acc1['id'], {
            'cloud_resource_id': 'cl_res_1',
            'resource_type': 'res',
            'pool_id': self.sub_pool1['id'],
            'employee_id': self.employee['id']
        })
        expenses = [
            {
                'cost': self.exp_start,
                'date': datetime.fromtimestamp(self.start_ts),
                'cloud_account_id': self.cloud_acc1['id'],
                'resource_id': resource['id'],
                'sign': 1
            },
            {
                'cost': self.exp_end,
                'date': datetime.fromtimestamp(self.end_ts),
                'cloud_account_id': self.cloud_acc1['id'],
                'resource_id': resource['id'],
                'sign': 1
            }
        ]
        self.expenses.extend(expenses)
        code, resp = self.client.pool_expenses_export_create(
            self.sub_pool1['id'])
        self.assertEqual(code, 201)
        export_link = resp['expenses_export_link']

        code, resp = self.client.pool_expenses_export_data_get(
            self.export_id_from_link(export_link),
            start_date=self.start_date, end_date=self.end_date)
        self.assertEqual(code, 200)
        self.assertEqual(resp, str(self.exp_start) + os.linesep + 31 *
                         (str(0.0) + os.linesep) + str(self.exp_end))

        code, resp = self.client.pool_expenses_export_data_get(
            self.export_id_from_link(export_link),
            start_date=self.start_date)
        self.assertEqual(code, 200)
        self.assertEqual(resp, str(self.exp_start))

    def test_pool_expense_none_start_date(self):
        code, resp = self.client.pool_expenses_export_create(
            self.sub_pool1['id'])
        self.assertEqual(code, 201)
        code, resp = self.client.pool_expenses_export_data_get(
            self.export_id_from_link(resp['expenses_export_link']),
            start_date=None, end_date=self.end_ts)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0216')

    def test_pool_expense_start_date_greater_end_date(self):
        code, resp = self.client.pool_expenses_export_create(
            self.sub_pool1['id'])
        self.assertEqual(code, 201)
        code, resp = self.client.pool_expenses_export_data_get(
            self.export_id_from_link(resp['expenses_export_link']),
            start_date=self.end_date, end_date=self.start_date)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0446')

    def test_get_export_not_exists(self):
        code, resp = self.client.pool_expenses_export_data_get('123')
        self.assertEqual(code, 404)
        self.assertEqual(resp['error']['error_code'], 'OE0002')

        code, resp = self.client.pool_expenses_export_create(
            self.sub_pool1['id'])
        export_id = self.export_id_from_link(resp['expenses_export_link'])
        code, _ = self.client.pool_expenses_export_delete(
            self.sub_pool1['id'])
        self.assertEqual(code, 204)
        code, resp = self.client.pool_expenses_export_data_get(export_id)
        self.assertEqual(code, 404)
        self.assertEqual(resp['error']['error_code'], 'OE0002')

    def test_expense_export_delete(self):
        code, resp = self.client.pool_expenses_export_create(
            self.sub_pool1['id'])
        self.assertEqual(code, 201)
        code, resp = self.client.pool_expenses_export_delete(
            self.sub_pool1['id'])
        self.assertEqual(code, 204)
        self.assertEqual(resp, None)

    def test_expense_export_delete_not_existing(self):
        code, resp = self.client.pool_expenses_export_delete('not-export')
        self.assertEqual(code, 404)
        self.assertEqual(resp['error']['error_code'], 'OE0002')

        code, resp = self.client.pool_expenses_export_delete(
            self.sub_pool_deleted['id'])
        self.assertEqual(code, 404)
        self.assertEqual(resp['error']['error_code'], 'OE0002')

        code, resp = self.client.pool_expenses_export_create(
            self.sub_pool1['id'])
        self.assertEqual(code, 201)
        code, resp = self.client.pool_expenses_export_delete(
            self.sub_pool1['id'])
        self.assertEqual(code, 204)
        code, resp = self.client.pool_expenses_export_delete(
            self.sub_pool1['id'])
        self.assertEqual(code, 404)
        self.assertEqual(resp['error']['error_code'], 'OE0002')

    def test_expense_export_with_subpools(self):
        _, sub_resource = self.cloud_resource_create(self.cloud_acc1['id'], {
            'cloud_resource_id': 'cl_res_1',
            'resource_type': 'res',
            'pool_id': self.sub_pool1['id'],
            'employee_id': self.employee['id']
        })
        _, org_resource = self.cloud_resource_create(self.cloud_acc1['id'], {
            'cloud_resource_id': 'cl_res_2',
            'resource_type': 'res',
            'pool_id': self.org['pool_id'],
            'employee_id': self.employee['id']
        })
        expenses = [
            {
                'cost': 1000,
                'date': datetime.fromtimestamp(self.start_ts),
                'cloud_account_id': self.cloud_acc1['id'],
                'resource_id': org_resource['id'],
                'sign': 1
            },
            {
                'cost': 10,
                'date': datetime.fromtimestamp(self.start_ts),
                'cloud_account_id': self.cloud_acc1['id'],
                'resource_id': sub_resource['id'],
                'sign': 1
            },
            {
                'cost': 500,
                'date': datetime.fromtimestamp(self.end_ts),
                'cloud_account_id': self.cloud_acc1['id'],
                'resource_id': org_resource['id'],
                'sign': 1
            },
            {
                'cost': 5,
                'date': datetime.fromtimestamp(self.end_ts),
                'cloud_account_id': self.cloud_acc1['id'],
                'resource_id': sub_resource['id'],
                'sign': 1
            },
        ]
        self.expenses.extend(expenses)
        code, resp = self.client.pool_expenses_export_create(
            self.org['pool_id'])
        self.assertEqual(code, 201)
        export_link = resp['expenses_export_link']

        code, resp = self.client.pool_expenses_export_data_get(
            self.export_id_from_link(export_link),
            start_date=self.start_date, end_date=self.end_date)
        self.assertEqual(code, 200)
        expected_response = (str(1000 + 10) + os.linesep + 31 *
                             (str(0.0) + os.linesep) + str(500 + 5))
        self.assertEqual(resp, expected_response)

    def test_get_expense_export_for_zero_cost_period(self):
        _, resource = self.cloud_resource_create(self.cloud_acc1['id'], {
            'cloud_resource_id': 'cl_res_1',
            'resource_type': 'res',
            'pool_id': self.org['pool_id'],
            'employee_id': self.employee['id']
        })
        expenses = [
            {
                'cost': 1000,
                'date': datetime.fromtimestamp(self.start_ts),
                'cloud_account_id': self.cloud_acc1['id'],
                'resource_id': resource['id'],
                'sign': 1
            },
            {
                'cost': 500,
                'date': datetime.fromtimestamp(self.end_ts),
                'cloud_account_id': self.cloud_acc1['id'],
                'resource_id': resource['id'],
                'sign': 1
            }
        ]
        self.expenses.extend(expenses)
        code, resp = self.client.pool_expenses_export_create(
            self.org['pool_id'])
        self.assertEqual(code, 201)
        export_link = resp['expenses_export_link']

        old_start_date, old_end_date = ('20200101', '20200101')
        code, resp = self.client.pool_expenses_export_data_get(
            self.export_id_from_link(export_link),
            start_date=old_start_date, end_date=old_end_date)
        self.assertEqual(code, 200)
        self.assertEqual(resp, '0.0')
