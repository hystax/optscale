from datetime import datetime, timedelta

from freezegun import freeze_time
from unittest.mock import patch

from rest_api.rest_api_server.tests.unittests.test_api_base import TestApiBase


class TestTtlAnalysis(TestApiBase):
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
        user_id = self.gen_id()
        self.valid_employee = {
            'name': 'Eliot Alderson', 'auth_user_id': user_id
        }
        _, self.employee = self.client.employee_create(
            self.org_id, self.valid_employee)
        self.employee_id = self.employee['id']
        patch('rest_api.rest_api_server.controllers.cloud_account.'
              'CloudAccountController._configure_report').start()
        _, self.cloud_account = self.create_cloud_account(
            self.org_id, self.valid_aws_creds, auth_user_id=user_id)
        self.cloud_acc_id = self.cloud_account['id']
        self.pool_id = self.org['pool_id']
        self.update_default_owner_for_pool(self.pool_id, self.employee_id)

    def add_resource(self, owner_id=None, pool_id=None, active=False,
                     noname=False, last_seen=None):
        resource_dict = {'resources': [{
            'name': 'r1',
            'cloud_resource_id': self.gen_id(),
            'resource_type': 'Instance',
            'pool_id': pool_id,
            'employee_id': owner_id,
        }]}
        if noname:
            del resource_dict['resources'][0]['name']
        if active:
            resource_dict['resources'][0]['active'] = True
            resource_dict['resources'][0]['last_seen'] = int(
                datetime.utcnow().timestamp())
        if last_seen:
            resource_dict['resources'][0]['last_seen'] = int(last_seen)
        code, resources = self.cloud_resource_create_bulk(
            self.cloud_acc_id, resource_dict, behavior='update_existing',
            return_resources=True)
        self.assertEqual(code, 200)
        return resources['resources'][0]

    def add_expenses(self, resource, starting_date):
        now = int(datetime.utcnow().timestamp())
        last_seen = resource.get('last_seen')
        if not last_seen:
            last_seen = now
        last_date = datetime.fromtimestamp(last_seen)
        last_date = last_date.replace(hour=0, minute=0, second=0, microsecond=0)
        while last_date >= starting_date:
            self.expenses.append({
                'resource_id': resource['id'],
                'cost': 1,
                'date': last_date,
                'cloud_account_id': resource['cloud_account_id'],
                'sign': 1
            })
            last_date -= timedelta(days=1)
        self.update_resource_info_by_expenses([resource['id']])

    def test_no_default_ttl_value(self):
        now = int(datetime.utcnow().timestamp())
        code, resp = self.client.ttl_analysis_get(self.pool_id, 0, now)
        self.assertEqual(code, 424)
        self.verify_error_code(resp, 'OE0457')

    def test_invalid_pool(self):
        now = int(datetime.utcnow().timestamp())
        code, resp = self.client.ttl_analysis_get(self.gen_id(), 0, now, 10)
        self.assertEqual(code, 404)
        self.verify_error_code(resp, 'OE0002')

    def test_invalid_dates(self):
        for invalid_date, err_code in [(None, 'OE0216'), ('aa', 'OE0217'),
                                       (-1, 'OE0224')]:
            code, resp = self.client.ttl_analysis_get(
                self.pool_id, invalid_date, ttl=10)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, err_code)

        for invalid_date, err_code in [('aa', 'OE0217'), (-1, 'OE0224')]:
            code, resp = self.client.ttl_analysis_get(
                self.pool_id, 0, invalid_date, ttl=10)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, err_code)

        code, resp = self.client.ttl_analysis_get(self.pool_id, 1, 0, ttl=10)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0446')

    def test_invalid_ttl(self):
        for invalid_ttl, err_code in [('aa', 'OE0217'), (-1, 'OE0224'),
                                      (0, 'OE0224'), (9001, 'OE0224')]:
            code, resp = self.client.ttl_analysis_get(
                self.pool_id, 0, 1, ttl=invalid_ttl)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, err_code)

    def test_ttl_analysis_no_data(self):
        code, resp = self.client.ttl_analysis_get(self.pool_id, 0, ttl=10)
        self.assertEqual(code, 200)
        self.assertEqual(resp, {
            "resources_tracked": 0,
            "resources_outside_of_ttl": 0,
            "total_expenses": 0,
            "expenses_outside_of_ttl": 0,
            "resources": [],
        })

    @freeze_time("2021-01-12 16:14:00")
    def test_ttl_analysis(self):
        ttl = 30
        now = datetime.utcnow()
        expense_start_date = now - timedelta(days=3)
        code, sub_pool = self.client.pool_create(
            self.org_id, {"name": "sub", "parent_id": self.pool_id})
        self.assertEqual(code, 201)
        resource1 = self.add_resource(active=True)
        self.add_expenses(resource1, expense_start_date)
        resource2 = self.add_resource()
        self.add_expenses(resource2, expense_start_date)
        resource3 = self.add_resource(owner_id=self.employee_id,
                                      pool_id=sub_pool['id'], active=True)
        self.add_expenses(resource3, expense_start_date)
        resource4 = self.add_resource(owner_id=self.employee_id,
                                      pool_id=sub_pool['id'])
        self.add_expenses(resource4, expense_start_date)

        analysis_start = int((now - timedelta(days=2)).timestamp())
        code, resp = self.client.ttl_analysis_get(self.pool_id,
                                                  analysis_start, ttl=ttl)
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['resources']), 1)
        ret_resource = resp['resources'][0]
        self.assertEqual(ret_resource['id'], resource1['id'])
        self.assertEqual(resp['resources_tracked'], 2)
        self.assertEqual(resp['resources_outside_of_ttl'], 1)
        self.assertEqual(resp['total_expenses'], 4)
        hours_in_range = 48
        hours_outside_of_ttl = 64 - ttl
        self.assertEqual(ret_resource['hours_outside_of_ttl'],
                         hours_outside_of_ttl)
        self.assertEqual(resp['expenses_outside_of_ttl'],
                         2 / hours_in_range * hours_outside_of_ttl)
        self.assertEqual(ret_resource['owner_name'], self.employee['name'])
        self.assertEqual(ret_resource['cloud_account_name'],
                         self.cloud_account['name'])
        self.assertEqual(ret_resource['cloud_type'], self.cloud_account['type'])

    @freeze_time("2021-01-12 16:14:00")
    def test_resources_created_deleted_in_range(self):
        ttl = 5
        now = datetime.utcnow()
        expense_start_date = now - timedelta(days=1)
        code, sub_pool = self.client.pool_create(
            self.org_id, {"name": "sub", "parent_id": self.pool_id})
        self.assertEqual(code, 201)
        resource1 = self.add_resource(
            owner_id=self.employee_id, pool_id=sub_pool['id'], active=True)
        self.add_expenses(resource1, expense_start_date)
        resource2 = self.add_resource(
            owner_id=self.employee_id, pool_id=sub_pool['id'])
        self.add_expenses(resource2, expense_start_date)
        with freeze_time(expense_start_date):
            resource3 = self.add_resource(owner_id=self.employee_id,
                                          pool_id=self.pool_id, active=True,
                                          last_seen=now.timestamp())
        self.add_expenses(resource3, expense_start_date)
        resource4 = self.add_resource(owner_id=self.employee_id,
                                      pool_id=self.pool_id)
        self.add_expenses(resource4, expense_start_date)

        analysis_start = int((now - timedelta(days=2)).timestamp())
        analysis_end = int((now + timedelta(days=1)).timestamp())
        code, resp = self.client.ttl_analysis_get(
            self.pool_id, analysis_start, analysis_end, ttl=ttl)
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['resources']), 1)
        ret_resource = resp['resources'][0]
        self.assertEqual(ret_resource['id'], resource3['id'])
        self.assertEqual(resp['resources_tracked'], 2)
        self.assertEqual(resp['resources_outside_of_ttl'], 1)
        self.assertEqual(resp['total_expenses'], 2)
        hours_in_range = 24
        hours_outside_of_ttl = hours_in_range - ttl
        self.assertEqual(ret_resource['hours_outside_of_ttl'],
                         hours_outside_of_ttl)
        self.assertEqual(resp['expenses_outside_of_ttl'],
                         1 / hours_in_range * hours_outside_of_ttl)
        self.assertEqual(ret_resource['owner_name'], self.employee['name'])
        self.assertEqual(ret_resource['cloud_account_name'],
                         self.cloud_account['name'])
        self.assertEqual(ret_resource['cloud_type'], self.cloud_account['type'])

    @freeze_time("2021-01-12 16:14:00")
    def test_ttl_reached_before_date_range(self):
        ttl = 30
        now = datetime.utcnow()
        expense_start_date = now - timedelta(days=4)
        code, sub_pool = self.client.pool_create(
            self.org_id, {"name": "sub", "parent_id": self.pool_id})
        self.assertEqual(code, 201)
        resource1 = self.add_resource(active=True)
        self.add_expenses(resource1, expense_start_date)
        resource2 = self.add_resource()
        self.add_expenses(resource2, expense_start_date)
        resource3 = self.add_resource(owner_id=self.employee_id,
                                      pool_id=sub_pool['id'], active=True)
        self.add_expenses(resource3, expense_start_date)
        resource4 = self.add_resource(owner_id=self.employee_id,
                                      pool_id=sub_pool['id'])
        self.add_expenses(resource4, expense_start_date)

        analysis_start = int((now - timedelta(days=2)).timestamp())
        analysis_end = int((now - timedelta(days=1)).timestamp())
        code, resp = self.client.ttl_analysis_get(
            self.pool_id, analysis_start, analysis_end, ttl=ttl)
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['resources']), 1)
        ret_resource = resp['resources'][0]
        self.assertEqual(ret_resource['id'], resource1['id'])
        self.assertEqual(resp['resources_tracked'], 2)
        self.assertEqual(resp['resources_outside_of_ttl'], 1)
        self.assertEqual(resp['total_expenses'], 2)
        hours_outside_of_ttl = 24
        self.assertEqual(ret_resource['hours_outside_of_ttl'],
                         hours_outside_of_ttl)
        self.assertEqual(resp['expenses_outside_of_ttl'],
                         1 / 24 * hours_outside_of_ttl)
        self.assertEqual(ret_resource['owner_name'], self.employee['name'])
        self.assertEqual(ret_resource['cloud_account_name'],
                         self.cloud_account['name'])
        self.assertEqual(ret_resource['cloud_type'], self.cloud_account['type'])

    @freeze_time("2021-01-12 16:14:00")
    def test_ttl_from_policy(self):
        ttl = 30
        code, policy = self.client.pool_policy_create(
            self.pool_id, {'limit': ttl, 'type': 'ttl'})
        self.assertEqual(code, 201)

        now = datetime.utcnow()
        expense_start_date = now - timedelta(days=3)
        resource = self.add_resource(owner_id=self.employee_id,
                                     pool_id=self.pool_id, active=True)
        self.add_expenses(resource, expense_start_date)

        analysis_start = int((now - timedelta(days=2)).timestamp())
        code, resp = self.client.ttl_analysis_get(
            self.pool_id, analysis_start)
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['resources']), 1)
        ret_resource = resp['resources'][0]
        self.assertEqual(ret_resource['id'], resource['id'])
        self.assertEqual(resp['resources_tracked'], 1)
        self.assertEqual(resp['resources_outside_of_ttl'], 1)
        self.assertEqual(resp['total_expenses'], 2)
        hours_outside_of_ttl = 64 - ttl
        self.assertEqual(ret_resource['hours_outside_of_ttl'],
                         hours_outside_of_ttl)
        self.assertEqual(resp['expenses_outside_of_ttl'],
                         1 / 24 * hours_outside_of_ttl)
        self.assertEqual(ret_resource['owner_name'], self.employee['name'])
        self.assertEqual(ret_resource['cloud_account_name'],
                         self.cloud_account['name'])
        self.assertEqual(ret_resource['cloud_type'], self.cloud_account['type'])

    @freeze_time("2021-01-12 16:14:00")
    def test_resource_without_name(self):
        now = datetime.utcnow()
        expense_start_date = now - timedelta(days=3)
        resource = self.add_resource(owner_id=self.employee_id,
                                     pool_id=self.pool_id, active=True,
                                     noname=True)
        self.add_expenses(resource, expense_start_date)

        analysis_start = int((now - timedelta(days=2)).timestamp())
        code, resp = self.client.ttl_analysis_get(
            self.pool_id, analysis_start, ttl=30)
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['resources']), 1)
