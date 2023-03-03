import os

from datetime import datetime, timezone, timedelta
from unittest.mock import patch
from rest_api_server.tests.unittests.test_api_base import TestApiBase
from rest_api_server.utils import get_nil_uuid

DAY_IN_SECONDS = 86400


class TestBreakdownExpensesApi(TestApiBase):

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
        cloud_acc1 = {
            'name': 'cloud_acc1',
            'type': 'aws_cnr',
            'config': {
                'access_key_id': 'key',
                'secret_access_key': 'secret',
                'config_scheme': 'create_report'
            }
        }
        cloud_acc2 = {
            'name': 'cloud_acc2',
            'type': 'kubernetes_cnr',
            'config': {
                'password': 'secret',
                'user': 'user',
                'cost_model': {}
            }
        }
        self.auth_user_id_1 = self.gen_id()
        self.auth_user_id_2 = self.gen_id()
        _, self.employee1 = self.client.employee_create(
            self.org_id,
            {'name': 'name1', 'auth_user_id': self.auth_user_id_1})
        _, self.employee2 = self.client.employee_create(
            self.org_id,
            {'name': 'name2', 'auth_user_id': self.auth_user_id_2})
        _, self.cloud_acc1 = self.create_cloud_account(
            self.org_id, cloud_acc1, auth_user_id=self.auth_user_id_1)
        _, self.cloud_acc2 = self.create_cloud_account(
            self.org_id, cloud_acc2, auth_user_id=self.auth_user_id_2)

        _, self.sub_pool1 = self.client.pool_create(self.org_id, {
            'name': 'sub1',
            'parent_id': self.org['pool_id'],
        })
        _, self.sub_pool2 = self.client.pool_create(self.org_id, {
            'name': 'sub2',
            'parent_id': self.sub_pool1['id'],
        })
        self.update_default_owner_for_pool(self.org['pool_id'],
                                           self.employee1['id'])

    def _create_resource(self, cloud_account_id, name='default_name',
                         r_type='default_type', **kwargs):
        code, resource = self.cloud_resource_create(
            cloud_account_id, {
                'cloud_resource_id': self.gen_id(), 'name': name,
                'resource_type': r_type, **kwargs
            })
        self.assertEqual(code, 201)
        return resource

    def test_available_filters_unexpected_filters(self):
        start_ts = int(datetime(2022, 2, 1).timestamp())
        filters = {
            'not_a_region': 'us-east',
        }
        code, response = self.client.breakdown_expenses_get(
            self.org_id, start_ts, start_ts, 'pool_id', filters)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0212')

    def test_breakdown_expenses_dates_values(self):
        filters = {
            'cloud_account_id': [self.cloud_acc1['id']],
        }
        min_timestamp = 0
        max_timestamp = int(datetime.max.replace(
            tzinfo=timezone.utc).timestamp()) - 1
        code, response = self.client.breakdown_expenses_get(
            self.org_id, min_timestamp, max_timestamp, 'pool_id', filters)
        self.assertEqual(code, 400)
        self.verify_error_code(response, 'OE0515')
        code, response = self.client.breakdown_expenses_get(
            self.org_id, min_timestamp - 1, max_timestamp, 'pool_id', filters)
        self.assertEqual(code, 400)
        self.verify_error_code(response, 'OE0224')
        code, response = self.client.breakdown_expenses_get(
            self.org_id, min_timestamp, max_timestamp + 1, 'pool_id', filters)
        self.assertEqual(code, 400)
        self.verify_error_code(response, 'OE0224')

        code, response = self.client.breakdown_expenses_get(
            self.org_id, min_timestamp - 1, 0, 'pool_id', filters)
        self.assertEqual(code, 400)
        self.verify_error_code(response, 'OE0224')

    def test_breakdown_expenses_limit(self):
        time = int(datetime.utcnow().timestamp())
        code, response = self.client.breakdown_expenses_get(
            self.org_id, time, time + 1, 'pool_id', {'limit': 1})
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0212')

    def test_invalid_organization(self):
        day_in_month = datetime(2020, 1, 14)

        time = int(day_in_month.timestamp())
        valid_aws_cloud_acc = {
            'name': 'my cloud_acc',
            'type': 'aws_cnr',
            'config': {
                'access_key_id': 'key',
                'secret_access_key': 'secret',
                'config_scheme': 'create_report'
            }
        }
        code, cloud_acc1 = self.create_cloud_account(
            self.org_id, valid_aws_cloud_acc)
        self.assertEqual(code, 201)
        _, organization2 = self.client.organization_create(
            {'name': "organization2"})
        filters = {
            'cloud_account_id': [cloud_acc1['id']]
        }
        code, response = self.client.breakdown_expenses_get(
            organization2['id'], time, time + 1, 'pool_id', filters)
        self.assertEqual(code, 404)
        self.verify_error_code(response, 'OE0470')

    def test_breakdown_expenses_invalid_breakdown_by(self):
        for breakdown_by in [1, 'invalid']:
            time = int(datetime.utcnow().timestamp())
            code, response = self.client.breakdown_expenses_get(
                self.org_id, time, time + 1, breakdown_by)
            self.assertEqual(code, 400)
            self.verify_error_code(response, 'OE0217')

    def test_breakdown_expenses_without_breakdown_by(self):
        day_1_ts = int(datetime(2022, 2, 1, tzinfo=timezone.utc).timestamp())
        day_2_ts = int(datetime(2022, 2, 2, tzinfo=timezone.utc).timestamp())
        res1 = self._create_resource(self.cloud_acc1['id'], r_type='type1',
                                     first_seen=day_1_ts, last_seen=day_2_ts)
        res2 = self._create_resource(self.cloud_acc2['id'], r_type='type2',
                                     first_seen=day_1_ts, last_seen=day_2_ts)
        self.expenses = [
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'resource_id': res1['id'],
                'date': datetime.utcfromtimestamp(day_1_ts),
                'cost': 10,
                'sign': 1
            },
            {
                'cloud_account_id': self.cloud_acc2['id'],
                'resource_id': res2['id'],
                'date': datetime.utcfromtimestamp(day_2_ts),
                'cost': 20,
                'sign': 1
            },
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'resource_id': res1['id'],
                'date': datetime.utcfromtimestamp(day_1_ts) - timedelta(days=1),
                'cost': 1,
                'sign': 1
            },
        ]
        code, response = self.client.breakdown_expenses_get(
            self.org_id, day_1_ts, day_2_ts)
        self.assertEqual(code, 200)
        breakdown = response['breakdown']
        self.assertEqual(len(breakdown), 2)
        for ts in [day_1_ts, day_2_ts]:
            self.assertTrue(str(ts) in breakdown)
            self.assertEqual(len(breakdown[str(ts)]), 1)
        self.assertEqual(breakdown[str(day_1_ts)]['null']['cost'], 10)
        self.assertEqual(breakdown[str(day_2_ts)]['null']['cost'], 20)
        self.assertEqual(len(response['counts']), 1)
        self.assertEqual(response['counts']['null']['total'], 30)
        self.assertEqual(response['counts']['null']['previous_total'], 1)
        self.assertEqual(response['total'], 30)
        self.assertEqual(response['previous_total'], 1)

    def test_breakdown_by_values(self):
        breakdown_by_values = [
            'employee_id', 'k8s_namespace', 'cloud_account_id', 'service_name',
            'region', 'resource_type', 'k8s_node', 'pool_id', 'k8s_service']
        day_1_ts = int(datetime(2022, 2, 1, tzinfo=timezone.utc).timestamp())
        res1 = self._create_resource(self.cloud_acc1['id'], r_type='type1',
                                     first_seen=day_1_ts, last_seen=day_1_ts)
        res2 = self._create_resource(self.cloud_acc2['id'], r_type='type2',
                                     first_seen=day_1_ts, last_seen=day_1_ts)
        for res in [res1, res2]:
            self.expenses.append({
                'cloud_account_id': res['cloud_account_id'],
                'resource_id': res['id'],
                'date': datetime.utcfromtimestamp(day_1_ts),
                'cost': 10,
                'sign': 1
            })
        for breakdown_by in breakdown_by_values:
            code, response = self.client.breakdown_expenses_get(
                self.org_id, day_1_ts, day_1_ts, breakdown_by)
            self.assertEqual(code, 200)
            self.assertEqual(response['total'], 20)
        code, resp = self.client.breakdown_expenses_get(
            self.org_id, day_1_ts, day_1_ts, 'something_strange')
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0217')

    def test_previous_period(self):
        day_1 = datetime(2022, 2, 1, tzinfo=timezone.utc)
        day_1_ts = int(day_1.timestamp())
        res1 = self._create_resource(self.cloud_acc1['id'], r_type='type1',
                                     first_seen=day_1_ts, last_seen=day_1_ts)
        for date in [
            day_1, day_1 - timedelta(days=1), day_1 - timedelta(days=2),
            day_1 - timedelta(days=3)
        ]:
            self.expenses.append({
                'cloud_account_id': res1['cloud_account_id'],
                'resource_id': res1['id'],
                'date': int(date.timestamp()),
                'cost': 1,
                'sign': 1
            })
        code, resp = self.client.breakdown_expenses_get(
            self.org_id, day_1_ts, day_1_ts + DAY_IN_SECONDS)
        self.assertEqual(code, 200)
        self.assertEqual(
            resp['previous_range_start'], day_1_ts - 2 * DAY_IN_SECONDS)
        self.assertEqual(resp['total'], 1)
        self.assertEqual(resp['previous_total'], 2)

        code, resp = self.client.breakdown_expenses_get(
            self.org_id, day_1_ts + DAY_IN_SECONDS,
            day_1_ts + 4 * DAY_IN_SECONDS)
        self.assertEqual(code, 200)
        self.assertEqual(
            resp['previous_range_start'], day_1_ts - 3 * DAY_IN_SECONDS)
        self.assertEqual(resp['total'], 0)
        self.assertEqual(resp['previous_total'], 4)

        min_timestamp = 0
        code, resp = self.client.breakdown_expenses_get(
            self.org_id, min_timestamp, min_timestamp + DAY_IN_SECONDS)
        self.assertEqual(code, 200)
        self.assertEqual(resp['previous_range_start'], 0)
        self.assertEqual(resp['previous_total'], 0)

    def test_breakdown_expenses(self):
        day_1_ts = int(datetime(2022, 2, 1, tzinfo=timezone.utc).timestamp())
        res1 = self._create_resource(
            self.cloud_acc1['id'], r_type='type1', first_seen=day_1_ts,
            last_seen=day_1_ts, region='us-none', service_name='service1',
            pool_id=self.sub_pool1['id'], employee_id=self.employee1['id']
        )
        day_1 = datetime.utcfromtimestamp(day_1_ts)
        self.expenses.extend([
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'resource_id': res1['id'],
                'date': day_1,
                'cost': 10,
                'sign': 1
            }
        ])
        dt2 = day_1_ts - 2 * DAY_IN_SECONDS
        res2 = self._create_resource(
            self.cloud_acc2['id'], r_type='type2', last_seen=day_1_ts,
            first_seen=dt2, k8s_namespace='namespace1',
            k8s_service='k8s_service1', pool_id=self.sub_pool2['id'],
            employee_id=self.employee2['id'])
        self.expenses.extend([
            {
                'cloud_account_id': self.cloud_acc2['id'],
                'resource_id': res2['id'],
                'date': day_1,
                'cost': 20,
                'sign': 1
            },
            {
                'cloud_account_id': self.cloud_acc2['id'],
                'resource_id': res2['id'],
                'date': day_1 - timedelta(days=1),
                'cost': 25,
                'sign': 1
            },
            {
                'cloud_account_id': self.cloud_acc2['id'],
                'resource_id': res2['id'],
                'date': day_1 - timedelta(days=2),
                'cost': 35,
                'sign': 1
            }
        ])

        code, resp = self.client.breakdown_expenses_get(
            self.org_id, day_1_ts, day_1_ts, 'cloud_account_id')
        self.assertEqual(code, 200)
        self.assertEqual(resp['total'], 30)
        self.assertEqual(resp['previous_total'], 25)
        self.assertEqual(resp['previous_range_start'],
                         day_1_ts - DAY_IN_SECONDS)
        expected_breakdown = {
            str(day_1_ts): {
                self.cloud_acc2['id']: {
                    'cost': 20,
                    'id': self.cloud_acc2['id'],
                    'name': self.cloud_acc2['name'],
                    'type': self.cloud_acc2['type']
                },
                self.cloud_acc1['id']: {
                    'cost': 10,
                    'id': self.cloud_acc1['id'],
                    'name': self.cloud_acc1['name'],
                    'type': self.cloud_acc1['type']
                }
            }
        }
        self.assertEqual(resp['breakdown'], expected_breakdown)
        expected_counts = {
            self.cloud_acc1['id']: {
                'total': 10, 'previous_total': 0, 'id': self.cloud_acc1['id'],
                'name': self.cloud_acc1['name'],
                'type': self.cloud_acc1['type']
            },
            self.cloud_acc2['id']: {
                'total': 20, 'previous_total': 25, 'id': self.cloud_acc2['id'],
                'name': self.cloud_acc2['name'],
                'type': self.cloud_acc2['type']
            }
        }
        self.assertEqual(resp['counts'], expected_counts)

        code, resp = self.client.breakdown_expenses_get(
            self.org_id, day_1_ts - DAY_IN_SECONDS, day_1_ts, 'employee_id')
        self.assertEqual(code, 200)
        self.assertEqual(resp['total'], 55)
        self.assertEqual(resp['previous_total'], 35)
        expected_breakdown = {
            str(day_1_ts - DAY_IN_SECONDS): {
                self.employee2['id']: {
                    'cost': 25,
                    'id': self.employee2['id'],
                    'name': self.employee2['name']
                }
            },
            str(day_1_ts): {
                self.employee1['id']: {
                    'cost': 10,
                    'id': self.employee1['id'],
                    'name': self.employee1['name']
                },
                self.employee2['id']: {
                    'cost': 20,
                    'id': self.employee2['id'],
                    'name': self.employee2['name']
                }
            }
        }
        self.assertEqual(resp['breakdown'], expected_breakdown)
        expected_counts = {
            self.employee2['id']: {
                'total': 45, 'previous_total': 35, 'id': self.employee2['id'],
                'name': self.employee2['name']
            },
            self.employee1['id']: {
                'total': 10, 'previous_total': 0, 'id': self.employee1['id'],
                'name': self.employee1['name']
            }
        }
        self.assertEqual(resp['counts'], expected_counts)

        code, resp = self.client.breakdown_expenses_get(
            self.org_id, day_1_ts - DAY_IN_SECONDS,
            day_1_ts + DAY_IN_SECONDS, 'pool_id')
        self.assertEqual(code, 200)
        self.assertEqual(resp['total'], 55)
        self.assertEqual(resp['previous_total'], 35)
        expected_breakdown = {
            str(day_1_ts): {
                self.sub_pool1['id']: {
                    'cost': 10,
                    'id': self.sub_pool1['id'],
                    'name': self.sub_pool1['name'],
                    'purpose': self.sub_pool1['purpose']
                },
                self.sub_pool2['id']: {
                    'cost': 20,
                    'id': self.sub_pool2['id'],
                    'name': self.sub_pool2['name'],
                    'purpose': self.sub_pool2['purpose']
                }
            },
            str(day_1_ts - DAY_IN_SECONDS): {
                self.sub_pool2['id']: {
                    'cost': 25,
                    'id': self.sub_pool2['id'],
                    'name': self.sub_pool2['name'],
                    'purpose': self.sub_pool2['purpose']
                }
            },
            str(day_1_ts + DAY_IN_SECONDS): {}
        }
        self.assertEqual(resp['breakdown'], expected_breakdown)
        expected_counts = {
            self.sub_pool1['id']: {
                'total': 10, 'previous_total': 0, 'id': self.sub_pool1['id'],
                'name': self.sub_pool1['name'],
                'purpose': self.sub_pool1['purpose']
            },
            self.sub_pool2['id']: {
                'total': 45, 'previous_total': 35, 'id': self.sub_pool2['id'],
                'name': self.sub_pool2['name'],
                'purpose': self.sub_pool2['purpose']
            }
        }
        self.assertEqual(resp['counts'], expected_counts)

        code, resp = self.client.breakdown_expenses_get(
            self.org_id, day_1_ts - DAY_IN_SECONDS, day_1_ts, 'k8s_namespace')
        self.assertEqual(code, 200)
        self.assertEqual(resp['total'], 55)
        self.assertEqual(resp['previous_total'], 35)
        self.assertEqual(resp['breakdown'], {
            str(day_1_ts - DAY_IN_SECONDS): {
                'namespace1': {'cost': 25}
            },
            str(day_1_ts): {
                'namespace1': {'cost': 20},
                'null': {'cost': 10}
            }
        })
        self.assertEqual(resp['counts'], {
            'namespace1': {'total': 45, 'previous_total': 35},
            'null': {'total': 10, 'previous_total': 0}
        })

        code, resp = self.client.breakdown_expenses_get(
            self.org_id, day_1_ts - DAY_IN_SECONDS, day_1_ts, 'k8s_namespace',
            {'k8s_service': get_nil_uuid()})
        self.assertEqual(resp['breakdown'], {
            str(day_1_ts): {'null': {'cost': 10}},
            str(day_1_ts - DAY_IN_SECONDS): {}
        })
        self.assertEqual(resp['counts'], {
            'null': {'total': 10, 'previous_total': 0}
        })

    def test_no_expenses(self):
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        code, resp = self.client.breakdown_expenses_get(
            self.org_id, int(start_date.timestamp()), int(end_date.timestamp()))
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['breakdown']), 8)
        for b in resp['breakdown'].values():
            self.assertEqual(b, {})
        self.assertEqual(resp['counts'], {})
        self.assertEqual(resp['previous_total'], 0)
        self.assertEqual(resp['total'], 0)

    def test_breakdown_expenses_clusters(self):
        code, cluster_type = self.client.cluster_type_create(
            self.org_id, {'name': 'awesome', 'tag_key': 'tag'})
        dt = datetime(2021, 2, 1, tzinfo=timezone.utc)
        first_seen = int((dt - timedelta(days=1)).timestamp())
        last_seen = int(dt.timestamp())
        self.assertEqual(code, 201)
        resource1 = self._create_resource(
            self.cloud_acc1['id'], tags={'tag': 'val'}, region='us-east',
            first_seen=first_seen, last_seen=last_seen)
        resource2 = self._create_resource(
            self.cloud_acc1['id'], tags={'tag': 'val2'}, region='us-west',
            first_seen=first_seen, last_seen=last_seen)
        resource3 = self._create_resource(
            self.cloud_acc1['id'], tags={'tag': 'val'}, region='us-west',
            first_seen=first_seen, last_seen=last_seen)
        resource4 = self._create_resource(
            self.cloud_acc1['id'], tags={'another_tag': 'another_value'},
            region='us-test', first_seen=first_seen, last_seen=last_seen)
        self.assertEqual(code, 201)

        expenses = [
            {
                'cost': 150, 'date': dt,
                'cloud_acc': self.cloud_acc1['id'],
                'resource_id': resource1['id'],
            },
            {
                'cost': 125, 'date': dt - timedelta(days=1),
                'cloud_acc': self.cloud_acc1['id'],
                'resource_id': resource1['id'],
            },
            {
                'cost': 300, 'date': dt,
                'cloud_acc': self.cloud_acc2['id'],
                'resource_id': resource2['id'],
            },
            {
                'cost': 100, 'date': dt,
                'cloud_acc': self.cloud_acc1['id'],
                'resource_id': resource3['id'],
            },
            {
                'cost': 250, 'date': dt,
                'cloud_acc': self.cloud_acc1['id'],
                'resource_id': resource4['id'],
            },
            {
                'cost': 250, 'date': dt - timedelta(days=1),
                'cloud_acc': self.cloud_acc1['id'],
                'resource_id': resource4['id'],
            }
        ]

        for e in expenses:
            self.expenses.append({
                'resource_id': e['resource_id'],
                'cost': e['cost'],
                'date': e['date'],
                'cloud_account_id': e['cloud_acc'],
                'sign': 1
            })

        time = int(dt.timestamp())

        code, response = self.client.breakdown_expenses_get(
            self.org_id, time, time + DAY_IN_SECONDS)
        self.assertEqual(code, 200)
        self.assertEqual(response['counts'], {
            'null': {'total': 800, 'previous_total': 375}
        })
        self.assertEqual(response['breakdown'], {
            str(time): {'null': {'cost': 800}},
            str(time + DAY_IN_SECONDS): {}
        })

        code, response = self.client.breakdown_expenses_get(
            self.org_id, time, time + int(DAY_IN_SECONDS / 2))
        self.assertEqual(code, 200)
        self.assertEqual(response['previous_range_start'],
                         time - DAY_IN_SECONDS)
        self.assertEqual(response['counts'], {
            'null': {'total': 800, 'previous_total': 375}
        })
        self.assertEqual(response['breakdown'], {
            str(time): {'null': {'cost': 800}}
        })

        code, response = self.client.breakdown_expenses_get(
            self.org_id, time + 1, time + int(DAY_IN_SECONDS / 2))
        self.assertEqual(code, 200)
        self.assertEqual(response['counts'], {
            'null': {'total': 800, 'previous_total': 375}
        })
        self.assertEqual(response['breakdown'], {
            str(time): {'null': {'cost': 800}}
        })

        body = {'resource_type': '%s:cluster' % cluster_type['name']}
        code, response = self.client.breakdown_expenses_get(
            self.org_id, time, time + DAY_IN_SECONDS, 'resource_type',
            params=body)
        self.assertEqual(
            response['counts'],
            {'awesome:cluster': {'total': 550, 'previous_total': 125}}
        )
        self.assertEqual(response['breakdown'], {
            str(time): {'awesome:cluster': {'cost': 550}},
            str(time + DAY_IN_SECONDS): {}
        })

    def test_resource_type_same_cluster(self):
        code, cluster_type = self.client.cluster_type_create(
            self.org_id, {'name': 'Instance', 'tag_key': 'tag'})
        dt = datetime(2021, 2, 1, tzinfo=timezone.utc)
        first_seen = int((dt - timedelta(days=1)).timestamp())
        last_seen = int(dt.timestamp())
        self.assertEqual(code, 201)
        resource1 = self._create_resource(
            self.cloud_acc1['id'], tags={'tag': 'val'}, region='us-east',
            first_seen=first_seen, last_seen=last_seen)
        resource2 = self._create_resource(
            self.cloud_acc1['id'], region='us-west',
            first_seen=first_seen, last_seen=last_seen,
            resource_type='Instance', active=True)
        _, env_resource = self.environment_resource_create(
            self.org_id, {
                'name': 'resource3',
                'resource_type': 'Instance',
                'tags': {},
                'first_seen': first_seen,
                'last_seen': last_seen
            })
        expenses = [
            {
                'cost': 150, 'date': dt,
                'cloud_acc': self.cloud_acc1['id'],
                'resource_id': resource1['id'],
            },
            {
                'cost': 125, 'date': dt - timedelta(days=1),
                'cloud_acc': self.cloud_acc1['id'],
                'resource_id': resource1['id'],
            },
            {
                'cost': 300, 'date': dt,
                'cloud_acc': self.cloud_acc2['id'],
                'resource_id': resource2['id'],
            },
            {
                'cost': 1, 'date': dt,
                'cloud_acc': env_resource['cloud_account_id'],
                'resource_id': env_resource['id'],
            },
        ]
        for e in expenses:
            self.expenses.append({
                'resource_id': e['resource_id'],
                'cost': e['cost'],
                'date': e['date'],
                'cloud_account_id': e['cloud_acc'],
                'sign': 1
            })

        time = int(dt.timestamp())
        code, response = self.client.breakdown_expenses_get(
            self.org_id, time, time, 'resource_type')
        self.assertEqual(response['counts'], {
            'Instance:cluster': {'total': 150, 'previous_total': 125},
            'Instance': {'total': 300, 'previous_total': 0},
            'Instance:environment': {'total': 1, 'previous_total': 0}
        })
        self.assertEqual(response['breakdown'], {
            str(time): {
                'Instance:cluster': {'cost': 150},
                'Instance': {'cost': 300},
                'Instance:environment': {'cost': 1}}
        })

        code, response = self.client.breakdown_expenses_get(
            self.org_id, time, time, 'resource_type',
            {'active': False})
        self.assertEqual(response['counts'], {
            'Instance:cluster': {'total': 150, 'previous_total': 125}
        })
        self.assertEqual(response['breakdown'], {
            str(time): {'Instance:cluster': {'cost': 150}}})

    def test_date_interval_length(self):
        start_dt = datetime(2022, 1, 1, tzinfo=timezone.utc)
        end_dt = datetime(2023, 1, 1, tzinfo=timezone.utc)
        params = {
            'organization_id': self.org_id,
            'start_date': int(start_dt.timestamp()),
            'end_date': int(end_dt.timestamp())
        }
        code, response = self.client.breakdown_expenses_get(**params)
        self.assertEqual(code, 400)
        self.verify_error_code(response, 'OE0515')

        end_dt -= timedelta(seconds=1)
        params['end_date'] = int(end_dt.timestamp())
        code, response = self.client.breakdown_expenses_get(**params)
        self.assertEqual(code, 200)
        self.assertEqual(
            response['previous_range_start'],
            int(datetime(2021, 1, 1, tzinfo=timezone.utc).timestamp()))
        self.assertEqual(len(response['breakdown']), 365)

        params['end_date'] = params['start_date']
        code, response = self.client.breakdown_expenses_get(**params)
        self.assertEqual(code, 200)
        self.assertEqual(len(response['breakdown']), 1)
        self.assertEqual(
            response['previous_range_start'],
            int(datetime(2021, 12, 31, tzinfo=timezone.utc).timestamp()))

    def test_breakdown_expenses_traffic_filters(self):
        day_1_ts = int(datetime(2022, 2, 1, tzinfo=timezone.utc).timestamp())
        res1 = self._create_resource(
            self.cloud_acc1['id'], r_type='type1', first_seen=day_1_ts,
            last_seen=day_1_ts, region='us-none', service_name='service1',
            pool_id=self.sub_pool1['id'], employee_id=self.employee1['id']
        )
        day_1 = datetime.utcfromtimestamp(day_1_ts)
        self.expenses.extend([
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'resource_id': res1['id'],
                'date': day_1,
                'cost': 10,
                'sign': 1
            }
        ])
        dt2 = day_1_ts - 2 * DAY_IN_SECONDS
        res2 = self._create_resource(
            self.cloud_acc2['id'], r_type='type2', last_seen=day_1_ts,
            first_seen=dt2, k8s_namespace='namespace1',
            k8s_service='k8s_service1', pool_id=self.sub_pool2['id'],
            employee_id=self.employee2['id'])
        self.expenses.extend([
            {
                'cloud_account_id': self.cloud_acc2['id'],
                'resource_id': res2['id'],
                'date': day_1,
                'cost': 20,
                'sign': 1
            },
            {
                'cloud_account_id': self.cloud_acc2['id'],
                'resource_id': res2['id'],
                'date': day_1 - timedelta(days=1),
                'cost': 25,
                'sign': 1
            },
            {
                'cloud_account_id': self.cloud_acc2['id'],
                'resource_id': res2['id'],
                'date': day_1 - timedelta(days=2),
                'cost': 35,
                'sign': 1
            }
        ])
        self.traffic_expenses = [
            {
                'cloud_account_id': self.cloud_acc2['id'],
                'resource_id': res2['cloud_resource_id'],
                'date': day_1,
                'type': 1,
                'from': 'from_1',
                'to': 'to_1',
                'usage': 1,
                'cost': 1,
                'sign': 1
            }
        ]
        body = {
            'traffic_from': 'not_exist:aws_cnr'
        }
        code, resp = self.client.breakdown_expenses_get(
            self.org_id, day_1_ts - DAY_IN_SECONDS, day_1_ts,
            'cloud_account_id', body)
        self.assertEqual(code, 200)
        self.assertEqual(resp['total'], 0)
        self.assertEqual(resp['breakdown'][str(day_1_ts)], {})

        for body in [
            {
                'traffic_from': 'from_1:kubernetes_cnr'
            },
            {
                'traffic_to': 'to_1:kubernetes_cnr'
            },
            {
                'traffic_from': 'ANY',
                'traffic_to': 'ANY'
            }
        ]:
            code, resp = self.client.breakdown_expenses_get(
                self.org_id, day_1_ts - DAY_IN_SECONDS, day_1_ts,
                'cloud_account_id', body)
            self.assertEqual(code, 200)
            self.assertEqual(resp['total'], 45)
            self.assertEqual(len(resp['counts']), 1)
            self.assertTrue(res2['cloud_account_id'] in resp['counts'])
