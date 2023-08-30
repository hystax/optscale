from datetime import datetime, timedelta
from unittest.mock import patch

from freezegun import freeze_time

from rest_api.rest_api_server.tests.unittests.test_api_base import TestApiBase


class TestOrganizationsOverviewApi(TestApiBase):

    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.org = self.client.organization_create({'name': "organization"})
        self.org_id = self.org['id']
        _, self.org2 = self.client.organization_create({'name': "organization2"})
        self.org_id2 = self.org2['id']
        self.auth_user = self.gen_id()
        _, self.employee = self.client.employee_create(
            self.org_id, {'name': 'employee',
                          'auth_user_id': self.auth_user})

        patch('rest_api.rest_api_server.controllers.cloud_account.'
              'CloudAccountController._configure_report').start()
        self.valid_cloud_acc_dict = {
            'name': 'my cloud_acc',
            'type': 'aws_cnr',
            'config': {
                'access_key_id': 'key',
                'secret_access_key': 'secret',
                'bucket_name': 'name',
                'config_scheme': 'create_report'
            }
        }

    @staticmethod
    def _mock_user_assignments(resources_ids):
        patch('rest_api.rest_api_server.controllers.organization.OrganizationController.'
              '_get_assignments_by_token',
              return_value=[{
                  'assignment_resource': r_id,
              } for r_id in resources_ids]).start()

    def test_organizations_overview_empty(self):
        self._mock_user_assignments([])
        code, res = self.client.organizations_overview_list()
        self.assertEqual(code, 200)
        self.assertEqual(len(res['organizations']), 0)

    def test_organizations_overview(self):
        for orgs_list in [[self.org], [self.org, self.org2]]:
            mock_params = [org['id'] for org in orgs_list]
            self._mock_user_assignments(mock_params)
            code, res = self.client.organizations_overview_list(details=True)
            self.assertEqual(code, 200)
            self.assertEqual(len(res['organizations']), len(orgs_list))
            orgs_pools = [org['pool_id'] for org in orgs_list]
            res_pools = [org['pools'][0] for org in res['organizations']]
            for detail in res_pools:
                self.assertTrue(detail['id'] in orgs_pools)

    def test_organizations_overview_no_policies(self):
        self._mock_user_assignments([self.org['id']])
        self.client.pool_policy_create(
            self.org['pool_id'], {
                'limit': 150,
                'type': 'ttl'
            }
        )
        code, res = self.client.organizations_overview_list()
        self.assertEqual(code, 200)
        self.assertEqual(len(res['organizations']), 1)
        pools = res['organizations'][0]['pools']
        self.assertIsNone(pools[0].get('policies'))

    def test_organizations_overview_no_children(self):
        self._mock_user_assignments([self.org['id']])
        _, sub_pool = self.client.pool_create(self.org_id, {
            'name': "sub", "parent_id": self.org['pool_id']})
        code, res = self.client.organizations_overview_list()
        self.assertEqual(code, 200)
        self.assertEqual(len(res['organizations']), 1)
        pools = res['organizations'][0]['pools']
        self.assertIsNone(pools[0].get('children'))

    def test_organizations_overview_details(self):
        def check_pool_policies(pool, policy):
            for k, v in policy.items():
                for bp in pool['policies']:
                    self.assertEqual(bp[k], policy[k])

        self._mock_user_assignments([self.org['id']])
        code, res = self.client.organizations_overview_list(
            details=True)
        self.assertEqual(code, 200)
        self.assertEqual(len(res['organizations']), 1)
        for pool in res['organizations'][0]['pools']:
            self.assertIsNotNone(pool['policies'])
            self.assertEqual(len(pool['policies']), 0)
            self.assertIsNotNone(pool['children'])
            self.assertEqual(len(pool['children']), 0)

        policy = {
            'limit': 150,
            'type': 'ttl'
        }
        self.client.pool_policy_create(
            self.org['pool_id'], policy)
        code, res = self.client.organizations_overview_list(
            details=True)
        self.assertEqual(code, 200)
        for pool in res['organizations'][0]['pools']:
            self.assertIsNotNone(pool['policies'])
            self.assertEqual(len(pool['policies']), 1)
            check_pool_policies(pool, policy)

        code, sub_pool = self.client.pool_create(self.org_id, {
            'name': "sub", "parent_id": self.org['pool_id']})
        self.client.pool_policy_create(sub_pool['id'], policy)

        code, sub_pool2 = self.client.pool_create(self.org_id, {
            'parent_id': sub_pool['id'], 'name': 'sub2'})
        self.client.pool_policy_create(sub_pool2['id'], policy)

        code, res = self.client.organizations_overview_list(details=True)
        self.assertEqual(code, 200)
        self.assertEqual(len(res['organizations']), 1)
        for pool in res['organizations'][0]['pools']:
            self.assertIsNotNone(pool['policies'])
            self.assertEqual(len(pool['policies']), 1)
            check_pool_policies(pool, policy)

            pool_children = pool['children']
            self.assertEqual(len(pool_children), 2)
            for pool in pool_children:
                self.assertIsNotNone(pool['policies'])
                self.assertEqual(len(pool['policies']), 1)
                check_pool_policies(pool, policy)

    def test_organizations_overview_unallocated(self):
        root_limit = 1000
        sub_limit = 200
        code, _ = self.client.pool_update(self.org['pool_id'], {
            'limit': root_limit,
        })
        self.assertEqual(code, 200)

        code, child1 = self.client.pool_create(self.org_id, {
            'name': "sub", "parent_id": self.org['pool_id'],
            'limit': sub_limit})
        self.assertEqual(code, 201)

        self._mock_user_assignments([self.org['id']])
        code, res = self.client.organizations_overview_list(details=True)
        self.assertEqual(code, 200)
        self.assertEqual(res['organizations'][0]['pools'][0][
                             'unallocated_limit'], root_limit - sub_limit)

    def test_organizations_overview_org_costs(self):
        _, cloud_account = self.create_cloud_account(
            self.org_id, self.valid_cloud_acc_dict,
            auth_user_id=self.auth_user)

        day_in_month = datetime(2020, 1, 21)
        prev_cost = 10
        _, resource = self.cloud_resource_create(
            cloud_account['id'], {
                'cloud_resource_id': 'res_id_1',
                'resource_type': 'test1',
            })
        self.expenses.append({
            'resource_id': resource['id'],
            'cost': prev_cost,
            'date': day_in_month,
            'cloud_account_id': cloud_account['id'],
            'sign': 1
        })

        c_day_in_month = datetime(2020, 2, 20)
        cost = 20
        forecast = 30
        _, resource2 = self.cloud_resource_create(
            cloud_account['id'], {
                'cloud_resource_id': 'res_id_2',
                'resource_type': 'test2',
            })
        self.expenses.append({
            'resource_id': resource2['id'],
            'cost': cost,
            'date': c_day_in_month,
            'cloud_account_id': cloud_account['id'],
            'sign': 1
        })

        self._mock_user_assignments([self.org['id']])
        with freeze_time(c_day_in_month + timedelta(seconds=1)):
            code, res = self.client.organizations_overview_list(
                details=True)
            self.assertEqual(code, 200)
            self.assertEqual(res['organizations'][0]['last_month_cost'],
                             prev_cost)
            self.assertEqual(res['organizations'][0]['cost'], cost)
            self.assertEqual(res['organizations'][0]['forecast'], forecast)

    def test_organizations_overview_recommendations(self):
        _, cloud_account = self.create_cloud_account(
            self.org_id, self.valid_cloud_acc_dict,
            auth_user_id=self.auth_user)

        completed_at = datetime.utcnow()
        completed_at_ts = int(completed_at.timestamp())
        _, res = self.client.optimizations_get(self.org_id)
        checklist_id = res['id']
        self.client.checklist_update(
            checklist_id, {'last_completed': completed_at_ts,
                           'last_run': completed_at_ts})

        optimization_data = {
            'created_at': completed_at_ts,
            'module': 'module',
            'organization_id': self.org_id,
            'data': []
        }

        for i in range(3):
            rss = {
                'cloud_resource_id': 'res_id_%s' % i,
                'resource_type': 'testb_%s' % i,
            }
            code, resource = self.cloud_resource_create(
                cloud_account['id'], rss)
            self.assertEqual(code, 201)
            rss.update({
                'is_dismissed': i == 0,
                'saving': 100 if i > 1 else 0
            })
            optimization_data['data'].append(rss)
        self.checklists_collection.insert_one(optimization_data)

        self._mock_user_assignments([self.org['id']])
        with freeze_time(completed_at):
            code, res = self.client.organizations_overview_list(details=True)
            self.assertEqual(code, 200)
            org_pool = res['organizations'][0]
            self.assertEqual(org_pool.get('saving'), 100)
