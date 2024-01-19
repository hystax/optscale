from datetime import datetime
from freezegun import freeze_time
from unittest.mock import patch
from rest_api.rest_api_server.utils import timestamp_to_day_start
from rest_api.rest_api_server.tests.unittests.test_api_base import TestApiBase
from rest_api.rest_api_server.utils import gen_id


class TestPoolExpensesApi(TestApiBase):
    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.org = self.client.organization_create({'name': 'org'})
        self.auth_user_1 = self.gen_id()
        _, self.employee_1 = self.client.employee_create(
            self.org['id'], {'name': 'employee_1',
                             'auth_user_id': self.auth_user_1})
        _, pool = self.client.pool_update(self.org['pool_id'],
                                          {'limit': 100})
        self.org_id = self.org['id']
        _, self.child1 = self.client.pool_create(self.org_id, {
            'name': 'child1', 'parent_id': self.org['pool_id'],
            'limit': 70})
        _, self.child1_1 = self.client.pool_create(self.org_id, {
            'name': 'child1_1', 'parent_id': self.child1['id'], 'limit': 30})
        _, self.child1_2 = self.client.pool_create(self.org_id, {
            'name': 'child1_2', 'parent_id': self.child1['id'], 'limit': 10})
        _, self.child2 = self.client.pool_create(self.org_id, {
            'name': 'child2', 'parent_id': self.org['pool_id'],
            'limit': 20})
        _, self.child2_1 = self.client.pool_create(self.org_id, {
            'name': 'child2_1', 'parent_id': self.child2['id'], 'limit': 10})
        patch('rest_api.rest_api_server.controllers.cloud_account.'
              'CloudAccountController._configure_report').start()
        _, self.cloud_acc1 = self.create_cloud_account(
            self.org_id, {
                'name': 'my cloud_acc',
                'type': 'aws_cnr',
                'config': {'access_key_id': 'key',
                           'secret_access_key': 'secret',
                           'config_scheme': 'create_report'}
            }, auth_user_id=self.auth_user_1)
        _, self.cloud_acc2 = self.create_cloud_account(
            self.org_id, {
                'name': 'azure cloud_acc',
                'type': 'azure_cnr',
                'config': {'subscription_id': 'id',
                           'secret': 'secret',
                           'client_id': 'id', 'tenant': 't'}
            })

        # org 2 with limit over 9000
        _, self.org2 = self.client.organization_create({'name': 'org2'})
        _, pool = self.client.pool_update(self.org2['pool_id'],
                                          {'limit': 9001})
        self.auth_user_2 = self.gen_id()
        _, self.employee_2 = self.client.employee_create(
            self.org2['id'], {'name': 'employee_2',
                              'auth_user_id': self.auth_user_2})
        _, self.cloud_acc_org2 = self.create_cloud_account(
            self.org2['id'], {
                'name': 'cloud_acc for org 2',
                'type': 'aws_cnr',
                'config': {'access_key_id': 'key',
                           'secret_access_key': 'secret',
                           'config_scheme': 'create_report'}
            }, auth_user_id=self.auth_user_2)

        day_in_last = datetime(2019, 12, 14)
        day_in_last2 = datetime(2019, 12, 15)

        day_in_current = datetime(2020, 1, 3)
        day_in_current2 = datetime(2020, 1, 18)

        # org pool
        self.add_expense(day_in_last, 3, self.cloud_acc1['id'], self.org['pool_id'])
        self.add_expense(day_in_current, 1, self.cloud_acc1['id'], self.org['pool_id'])

        # child1
        self.add_expense(day_in_last, 7, self.cloud_acc1['id'], self.child1['id'])
        self.add_expense(day_in_current, 10, self.cloud_acc1['id'], self.child1['id'])

        # child1_1
        self.add_expense(day_in_current, 3, self.cloud_acc1['id'], self.child1_1['id'])

        # child1_2
        self.add_expense(day_in_last, 4, self.cloud_acc1['id'], self.child1_2['id'])

        # child2_1 in cloud 2
        self.add_expense(day_in_current, 5, self.cloud_acc2['id'], self.child2_1['id'])

        # org2
        self.add_expense(day_in_last, 3000, self.cloud_acc_org2['id'], self.org2['pool_id'])
        self.add_expense(day_in_last2, 4000, self.cloud_acc_org2['id'], self.org2['pool_id'])
        self.add_expense(day_in_current, 4999, self.cloud_acc_org2['id'], self.org2['pool_id'])
        self.add_expense(day_in_current2, 4111, self.cloud_acc_org2['id'], self.org2['pool_id'])

        self.today_ts = int(datetime(2020, 1, 20, 17, 34, 00).timestamp())
        self.last_month_ts = int(datetime(2019, 12, 31, 23, 59, 59).timestamp())
        self.this_month_ts = int(datetime(2020, 1, 31, 23, 59, 59).timestamp())
        self.p_assign = patch(
            'rest_api.rest_api_server.controllers.pool.PoolController.'
            '_get_assignments_actions_by_token').start()

    def add_expense(self, day, cost, cloud, pool, resource_id=None):
        if not resource_id:
            timestamp = int(day.timestamp())
            resource = {
                '_id': self.gen_id(),
                'cloud_account_id': cloud,
                'cloud_resource_id': self.gen_id(),
                'pool_id': pool,
                'employee_id': self.employee_1['id'],
                'name': 'name',
                'resource_type': 'Instance',
                'first_seen': timestamp,
                '_first_seen_date': timestamp_to_day_start(timestamp),
                'last_seen': timestamp,
                '_last_seen_date': timestamp_to_day_start(timestamp),
            }
            self.resources_collection.insert_one(resource)
            resource_id = resource['_id']
        self.expenses.append({
            'cost': cost,
            'date': day,
            'cloud_account_id': cloud,
            'resource_id': resource_id,
            'sign': 1
        })

    @freeze_time("2020-01-20 17:34:00")
    def test_org_manager(self):
        self.p_assign.return_value = {
            'MANAGE_RESOURCES': [('organization', self.org_id),
                                 ('organization', self.org2['id'])],
            'MANAGE_OWN_RESOURCES': []
        }
        code, res = self.client.pool_expenses_get(self.org_id)
        expected = {
            'expenses': {
                'last_month': {
                    'total': 14,  # 3+7+4
                    'date': self.last_month_ts,
                },
                'this_month': {
                    'total': 19,  # 1+10+3+5
                    'date': self.today_ts,
                },
                'this_month_forecast': {
                    'total': 29.7,
                    'date': self.this_month_ts,
                }
            },
            'total': 100,
            'pools': [
                {
                    'id': self.org['pool_id'],
                    'purpose': 'business_unit',
                    'name': 'org',
                    'limit': 100,
                    'this_month_expenses': 19,  # 40 - (10+8+3)
                    'this_month_forecast': 29.7,
                },
            ]
        }
        self.assertEqual(code, 200)
        self.assertEqual(res, expected)

    @freeze_time("2020-01-20 17:34:00")
    def test_manage_own_for_org(self):
        self.p_assign.return_value = {
            'MANAGE_RESOURCES': [],
            'MANAGE_OWN_RESOURCES': [('organization', self.org_id)]
        }
        code, res = self.client.pool_expenses_get(self.org_id)
        self.assertEqual(code, 200)
        self.assertEqual(res, {
            'expenses': {
                'last_month': {
                    'total': 14,  # 3+7+4
                    'date': self.last_month_ts,
                },
                'this_month': {
                    'total': 19,  # 1+10+3+5
                    'date': self.today_ts,
                },
                'this_month_forecast': {
                    'total': 29.7,
                    'date': self.this_month_ts,
                }
            },
            'total': 100,
            'pools': [
                {
                    'id': self.org['pool_id'],
                    'purpose': 'business_unit',
                    'name': 'org',
                    'limit': 100,
                    'this_month_expenses': 19,
                    'this_month_forecast': 29.7,
                }
            ]
        })

    @freeze_time("2020-01-20 17:34:00")
    def test_manage_own_in_subpool_and_all_in_subpool(self):
        self.p_assign.return_value = {
            'MANAGE_RESOURCES': [('pool', self.child1['id'])],
            'MANAGE_OWN_RESOURCES': [('pool', self.child2['id'])]
        }
        code, res = self.client.pool_expenses_get(self.org_id)
        self.assertEqual(code, 200)
        self.assertEqual(res, {
            'expenses': {
                'last_month': {
                    'total': 11,  # 7+4
                    'date': self.last_month_ts,
                },
                'this_month': {
                    'total': 18,  # 10+3+5
                    'date': self.today_ts,
                },
                'this_month_forecast': {
                    'total': 29.310000000000002,
                    'date': self.this_month_ts,
                }
            },
            'total': 90,
            'pools': [
                {
                    'id': self.child1['id'],
                    'purpose': 'budget',
                    'name': 'child1',
                    'limit': 70,
                    'this_month_expenses': 13,  # 10+3
                    'this_month_forecast': 20.78,
                },
                {
                    'id': self.child2['id'],
                    'purpose': 'budget',
                    'name': 'child2',
                    'limit': 20,
                    'this_month_expenses': 5,  # 5
                    'this_month_forecast': 8.53,
                }
            ]
        })

    @freeze_time("2020-01-20 17:34:00")
    def test_without_permissions_in_org1(self):
        self.p_assign.return_value = {
            'MANAGE_RESOURCES': [],
            'MANAGE_OWN_RESOURCES': [('parent', self.org2['id'])],
        }
        code, res = self.client.pool_expenses_get(self.org_id)
        expected = {
            'expenses': {
                'last_month': {
                    'total': 14,  # 3+7+4
                    'date': self.last_month_ts,
                },
                'this_month': {
                    'total': 19,  # 1+10+3+5
                    'date': self.today_ts,
                },
                'this_month_forecast': {
                    'total': 29.7,
                    'date': self.this_month_ts,
                }
            },
            'total': 100,
            'pools': [
                {
                    'id': self.org['pool_id'],
                    'purpose': 'business_unit',
                    'name': 'org',
                    'limit': 100,
                    'this_month_expenses': 19,  # 40 - (10+8+3)
                    'this_month_forecast': 29.7,
                }
            ]
        }
        self.assertEqual(code, 200)
        self.assertEqual(res, expected)

    @freeze_time("2020-01-20 17:34:00")
    def test_manage_own_in_parent_and_all_in_child(self):
        self.p_assign.return_value = {
            'MANAGE_RESOURCES': [('pool', self.child1_1['id'])],
            'MANAGE_OWN_RESOURCES': [('pool', self.child1['id']),
                                     ('organization', self.org2['id'])]
        }
        code, res = self.client.pool_expenses_get(self.org_id)
        self.assertEqual(code, 200)
        self.assertEqual(res, {
            'expenses': {
                'last_month': {
                    'total': 11,  # 7+4
                    'date': self.last_month_ts,
                },
                'this_month': {
                    'total': 13,  # 10+3
                    'date': self.today_ts,
                },
                'this_month_forecast': {
                    'total': 20.78,
                    'date': self.this_month_ts,
                }
            },
            'total': 70,
            'pools': [
                {
                    'id': self.child1['id'],
                    'purpose': 'budget',
                    'name': 'child1',
                    'limit': 70,
                    'this_month_expenses': 13,
                    'this_month_forecast': 20.78,
                },
            ]
        })

    def test_does_not_exist(self):
        code, res = self.client.pool_expenses_get(gen_id())
        self.assertEqual(code, 404)
        self.assertEqual(res['error']['error_code'], 'OE0002')
