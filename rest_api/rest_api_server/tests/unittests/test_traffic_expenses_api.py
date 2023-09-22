from datetime import datetime, timezone, timedelta
from unittest.mock import patch, ANY
from rest_api.rest_api_server.tests.unittests.test_api_base import TestApiBase
from rest_api.rest_api_server.utils import get_nil_uuid


class TestTrafficExpensesApi(TestApiBase):

    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.org = self.client.organization_create(
            {'name': "organization"})
        self.org_id = self.org['id']
        patch('rest_api.rest_api_server.controllers.cloud_account.'
              'CloudAccountController._configure_report').start()
        self.p_create_rule = patch(
            'rest_api.rest_api_server.controllers.rule.RuleController.'
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
            'type': 'azure_cnr',
            'config': {
                'subscription_id': 'id',
                'secret': 'secret',
                'client_id': 'id',
                'tenant': 't'
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
        patch('rest_api.rest_api_server.controllers.traffic_expense.'
              'TrafficExpenseController._aggregate_resource_data',
              wraps=self.patched_aggregate_resource_data).start()

    def patched_aggregate_resource_data(self, match_query, **kwargs):
        group_stage = {
            '_id': {
                'cloud_account_id': {'$ifNull': ['$cloud_account_id', None]},
                'day': {'$trunc': {
                    '$divide': ['$first_seen', 86400]}},
            },
            'resources': {'$addToSet': '$cloud_resource_id'},
            'cluster_ids': {'$addToSet': {'$cond': {
                'if': {'$ifNull': ['$cluster_type_id', False]},
                'then': '$_id',
                'else': None
            }}}
        }
        return self.resources_collection.aggregate([
            {'$match': match_query},
            {'$group': group_stage}
        ], allowDiskUse=True)

    def _create_resource(self, cloud_account_id, name='default_name',
                         r_type='default_type', **kwargs):
        code, resource = self.cloud_resource_create(
            cloud_account_id, {
                'cloud_resource_id': self.gen_id(), 'name': name,
                'resource_type': r_type, **kwargs
            })
        self.assertEqual(code, 201)
        return resource

    def test_unexpected_filters(self):
        start_ts = int(datetime(2022, 2, 1).timestamp())
        filters = {
            'not_a_region': 'us-east',
        }
        code, response = self.client.traffic_expenses_get(
            self.org_id, start_ts, start_ts, filters)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0212')

    def test_dates_values(self):
        filters = {
            'cloud_account_id': [self.cloud_acc1['id']],
        }
        min_timestamp = 0
        max_timestamp = int(datetime.max.replace(
            tzinfo=timezone.utc).timestamp()) - 1
        code, response = self.client.traffic_expenses_get(
            self.org_id, min_timestamp - 1, max_timestamp, filters)
        self.assertEqual(code, 400)
        self.verify_error_code(response, 'OE0224')
        code, response = self.client.traffic_expenses_get(
            self.org_id, min_timestamp, max_timestamp + 1, filters)
        self.assertEqual(code, 400)
        self.verify_error_code(response, 'OE0224')

        code, response = self.client.traffic_expenses_get(
            self.org_id, min_timestamp - 1, 0, filters)
        self.assertEqual(code, 400)
        self.verify_error_code(response, 'OE0224')

    def test_limit(self):
        time = int(datetime.utcnow().timestamp())
        code, response = self.client.traffic_expenses_get(
            self.org_id, time, time + 1, {'limit': 1})
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
        code, response = self.client.traffic_expenses_get(
            organization2['id'], time, time + 1, filters)
        self.assertEqual(code, 404)
        self.verify_error_code(response, 'OE0470')

    def test_traffic_expenses(self):
        start = int(datetime(2022, 2, 1).timestamp())
        end = int(datetime(2022, 3, 1).timestamp())

        day_1_ts = int(datetime(2022, 2, 2, tzinfo=timezone.utc).timestamp())
        res1 = self._create_resource(
            self.cloud_acc1['id'], first_seen=day_1_ts, last_seen=day_1_ts)
        res2 = self._create_resource(
            self.cloud_acc2['id'], first_seen=day_1_ts, last_seen=day_1_ts)
        self.traffic_expenses = [
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'resource_id': res1['cloud_resource_id'],
                'date': datetime(2022, 2, 1),
                'type': 1,
                'from': 'eu-central-1',
                'to': 'External',
                'usage': 10,
                'cost': 5,
                'sign': 1
            },
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'resource_id': res1['cloud_resource_id'],
                'date': datetime(2022, 2, 2),
                'type': 1,
                'from': 'eu-central-1',
                'to': 'External',
                'usage': 10,
                'cost': 5,
                'sign': 1
            },
            {
                'cloud_account_id': self.cloud_acc2['id'],
                'resource_id': res2['cloud_resource_id'],
                'date': datetime(2022, 2, 2),
                'type': 1,
                'from': 'usgovarizona',
                'to': 'usgovarizona',
                'usage': 20,
                'cost': 10,
                'sign': 1
            }
        ]
        code, response = self.client.traffic_expenses_get(
            self.org_id, start, end)
        self.assertEqual(code, 200)
        self.assertEqual(response['start_date'], start)
        self.assertEqual(response['end_date'], end)
        self.assertEqual(response['total_cost'], 20)
        self.assertEqual(response['total_usage'], 40)
        traffic_expenses = response['traffic_expenses']
        self.assertEqual(len(traffic_expenses), 2)
        expected_expense_1 = {
            'cloud_type': self.cloud_acc1['type'],
            'from': {
                'name': 'eu-central-1', 'latitude': ANY, 'longitude': ANY
            },
            'to': {
                'name': 'External'
            },
            'usage': 20,
            'cost': 10
        }
        expected_expense_2 = {
            'cloud_type': self.cloud_acc2['type'],
            'from': {
                'name': 'usgovarizona', 'latitude': ANY, 'longitude': ANY},
            'to': {
                'name': 'usgovarizona', 'latitude': ANY, 'longitude': ANY
            },
            'usage': 20,
            'cost': 10
        }
        for e in traffic_expenses:
            if e['cloud_type'] == self.cloud_acc1['type']:
                self.assertEqual(e, expected_expense_1)
            else:
                self.assertEqual(e, expected_expense_2)
                self.assertEqual(e['from']['latitude'], e['to']['latitude'])
                self.assertEqual(e['from']['longitude'], e['to']['longitude'])

    def test_incorrect_identity(self):
        start = int(datetime(2022, 2, 1).timestamp())
        end = int(datetime(2022, 3, 1).timestamp())
        code, response = self.client.traffic_expenses_get(
            self.org_id, start, end, {'resource_type': 'Instance:unknown'})
        self.assertEqual(code, 400)
        self.verify_error_code(response, 'OE0499')

    def test_empty_expenses(self):
        start = int(datetime(2022, 2, 1).timestamp())
        end = int(datetime(2022, 3, 1).timestamp())
        code, response = self.client.traffic_expenses_get(
            self.org_id, start, end)
        self.assertEqual(code, 200)
        self.assertEqual(response, {
            'traffic_expenses': [],
            'start_date': start,
            'end_date': end,
            'total_cost': 0,
            'total_usage': 0
        })

    def test_different_regions(self):
        start = int(datetime(2022, 2, 1).timestamp())
        end = int(datetime(2022, 3, 1).timestamp())

        day_1_ts = int(datetime(2022, 2, 2, tzinfo=timezone.utc).timestamp())
        res1 = self._create_resource(
            self.cloud_acc1['id'], first_seen=day_1_ts, last_seen=day_1_ts)
        res2 = self._create_resource(
            self.cloud_acc1['id'], first_seen=day_1_ts, last_seen=day_1_ts)
        self.traffic_expenses = [
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'resource_id': res1['cloud_resource_id'],
                'date': datetime(2022, 2, 1),
                'type': 1,
                'from': 'eu-central-1',
                'to': 'External',
                'usage': 5,
                'cost': 5,
                'sign': 1
            },
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'resource_id': res2['cloud_resource_id'],
                'date': datetime(2022, 2, 2),
                'type': 1,
                'from': 'eu-central-1',
                'to': 'External',
                'usage': 5,
                'cost': 5,
                'sign': 1
            },
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'resource_id': res1['cloud_resource_id'],
                'date': datetime(2022, 2, 3),
                'type': 1,
                'from': 'Unknown',
                'to': 'External',
                'usage': 20,
                'cost': 10,
                'sign': 1
            }
        ]
        code, response = self.client.traffic_expenses_get(
            self.org_id, start, end)
        expenses = response['traffic_expenses']
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 20)
        self.assertEqual(response['total_usage'], 30)
        self.assertEqual(len(expenses), 2)

    def test_collapsed_records(self):
        start = int(datetime(2022, 2, 1).timestamp())
        end = int(datetime(2022, 3, 1).timestamp())

        day_1_ts = int(datetime(2022, 2, 2, tzinfo=timezone.utc).timestamp())
        res1 = self._create_resource(
            self.cloud_acc1['id'], first_seen=day_1_ts, last_seen=day_1_ts)
        self.traffic_expenses = [
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'resource_id': res1['cloud_resource_id'],
                'date': datetime(2022, 2, 1),
                'type': 1,
                'from': 'eu-central-1',
                'to': 'External',
                'usage': 5,
                'cost': 5,
                'sign': 1
            },
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'resource_id': res1['cloud_resource_id'],
                'date': datetime(2022, 2, 1),
                'type': 1,
                'from': 'eu-central-1',
                'to': 'External',
                'usage': 5,
                'cost': 5,
                'sign': -1
            },
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'resource_id': res1['cloud_resource_id'],
                'date': datetime(2022, 2, 1),
                'type': 1,
                'from': 'eu-central-1',
                'to': 'External',
                'usage': 20,
                'cost': 10,
                'sign': 1
            }
        ]
        code, response = self.client.traffic_expenses_get(
            self.org_id, start, end)
        self.assertEqual(code, 200)
        traffic_expenses = response['traffic_expenses']
        self.assertEqual(len(traffic_expenses), 1)
        self.assertEqual(response['total_cost'], 10)
        self.assertEqual(response['total_usage'], 20)

    def test_traffic_expenses_date_ranges(self):
        start = int(datetime(2022, 2, 1).timestamp())
        end = int(datetime(2022, 2, 2).timestamp())

        day_1_ts = int(datetime(2022, 2, 1, tzinfo=timezone.utc).timestamp())
        res1 = self._create_resource(
            self.cloud_acc1['id'], first_seen=day_1_ts, last_seen=day_1_ts)
        self.traffic_expenses = [
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'resource_id': res1['cloud_resource_id'],
                'date': datetime(2022, 2, 1),
                'type': 1,
                'from': 'Unknown',
                'to': 'External',
                'usage': 1,
                'cost': 2,
                'sign': 1
            },
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'resource_id': res1['cloud_resource_id'],
                'date': datetime(2022, 2, 2),
                'type': 1,
                'from': 'Unknown',
                'to': 'External',
                'usage': 1,
                'cost': 3,
                'sign': 1
            },
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'resource_id': res1['cloud_resource_id'],
                'date': datetime(2022, 2, 3),
                'type': 1,
                'from': 'eu-central-1',
                'to': 'External',
                'usage': 20,
                'cost': 10,
                'sign': 1
            }
        ]
        code, response = self.client.traffic_expenses_get(
            self.org_id, start, end)
        traffic_expenses = response['traffic_expenses']
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 5)
        self.assertEqual(response['total_usage'], 2)
        self.assertEqual(traffic_expenses, [
            {
                'cloud_type': self.cloud_acc1['type'],
                'from': {'name': 'Unknown'},
                'to': {'name': 'External'},
                'usage': 2, 'cost': 5
            }
        ])

    def test_traffic_expenses_filters(self):
        start = int(datetime(2022, 2, 1).timestamp())
        end = int(datetime(2022, 3, 1).timestamp())
        day_1_ts = int(datetime(2022, 2, 2, tzinfo=timezone.utc).timestamp())
        res1 = self._create_resource(
            self.cloud_acc1['id'], first_seen=day_1_ts, last_seen=day_1_ts,
            service_name='srv1')
        res2 = self._create_resource(
            self.cloud_acc2['id'], first_seen=day_1_ts, last_seen=day_1_ts,
            region='reg2'
        )
        self.traffic_expenses = [
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'resource_id': res1['cloud_resource_id'],
                'date': datetime(2022, 2, 1),
                'type': 1,
                'from': 'Unknown',
                'to': 'External',
                'usage': 1,
                'cost': 1,
                'sign': 1
            },
            {
                'cloud_account_id': self.cloud_acc2['id'],
                'resource_id': res2['cloud_resource_id'],
                'date': datetime(2022, 2, 1),
                'type': 1,
                'from': 'Unknown',
                'to': 'External',
                'usage': 2,
                'cost': 2,
                'sign': 1
            }
        ]
        expected_expense = {
            'cloud_type': self.cloud_acc1['type'],
            'from': {'name': 'Unknown'},
            'to': {'name': 'External'},
            'usage': 1,
            'cost': 1
        }
        for body in [
            {'service_name': 'srv1'},
            {'cloud_account_id': self.cloud_acc1['id']},
            {'region': get_nil_uuid()}
        ]:
            code, response = self.client.traffic_expenses_get(
                self.org_id, start, end, body)
            self.assertEqual(code, 200)
            traffic_expenses = response['traffic_expenses']
            self.assertEqual(len(traffic_expenses), 1)
            self.assertEqual(traffic_expenses[0], expected_expense)

        expected_expense = {
            'cloud_type': self.cloud_acc2['type'],
            'from': {'name': 'Unknown'},
            'to': {'name': 'External'},
            'usage': 2,
            'cost': 2
        }
        for body in [
            {'service_name': get_nil_uuid()},
            {'cloud_account_id': self.cloud_acc2['id']},
            {'region': 'reg2'}
        ]:
            code, response = self.client.traffic_expenses_get(
                self.org_id, start, end, body)
            self.assertEqual(code, 200)
            traffic_expenses = response['traffic_expenses']
            self.assertEqual(len(traffic_expenses), 1)
            self.assertEqual(traffic_expenses[0], expected_expense)
        for body in [
            {'traffic_from': ['Unknown:aws_cnr', 'Unknown:azure_cnr']},
            {'traffic_to': ['External:aws_cnr', 'External:azure_cnr']},
            {'traffic_from': 'ANY'}
        ]:
            code, response = self.client.traffic_expenses_get(
                self.org_id, start, end, body)
            self.assertEqual(code, 200)
            traffic_expenses = response['traffic_expenses']
            self.assertEqual(len(traffic_expenses), 2)
            self.assertEqual(
                sorted(traffic_expenses, key=lambda x: x['cost']),
                [{
                    'cloud_type': self.cloud_acc1['type'],
                    'from': {'name': 'Unknown'},
                    'to': {'name': 'External'},
                    'usage': 1,
                    'cost': 1
                }, {
                    'cloud_type': self.cloud_acc2['type'],
                    'from': {'name': 'Unknown'},
                    'to': {'name': 'External'},
                    'usage': 2,
                    'cost': 2
                }]
            )

        code, response = self.client.traffic_expenses_get(
            self.org_id, start, end, {'traffic_from': 'not_ex:aws_cnr'})
        self.assertEqual(code, 200)
        traffic_expenses = response['traffic_expenses']
        self.assertEqual(len(traffic_expenses), 0)

    def test_traffic_expenses_clusters(self):
        code, cluster_type = self.client.cluster_type_create(
            self.org_id, {'name': 'awesome', 'tag_key': 'tag1'})
        self.assertEqual(code, 201)
        dt = datetime(2021, 2, 1, tzinfo=timezone.utc)
        first_seen = int((dt - timedelta(days=1)).timestamp())
        last_seen = int(dt.timestamp())
        res1 = self._create_resource(
            self.cloud_acc1['id'], tags={'tag1': 'val1'}, region='us-east',
            first_seen=first_seen, last_seen=last_seen)
        res2 = self._create_resource(
            self.cloud_acc1['id'], tags={'tag1': 'val2'}, region='us-west',
            first_seen=first_seen, last_seen=last_seen)
        res3 = self._create_resource(
            self.cloud_acc1['id'], region='us-test',
            first_seen=first_seen, last_seen=last_seen)
        self.traffic_expenses = [
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'resource_id': res1['cloud_resource_id'],
                'date': datetime.fromtimestamp(first_seen),
                'type': 1,
                'from': 'from_1',
                'to': 'to_1',
                'usage': 1,
                'cost': 1,
                'sign': 1
            },
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'resource_id': res2['cloud_resource_id'],
                'date': datetime.fromtimestamp(first_seen),
                'type': 1,
                'from': 'from_2',
                'to': 'to_2',
                'usage': 2,
                'cost': 2,
                'sign': 1
            },
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'resource_id': res3['cloud_resource_id'],
                'date': datetime.fromtimestamp(first_seen),
                'type': 1,
                'from': 'from_3',
                'to': 'to_3',
                'usage': 3,
                'cost': 3,
                'sign': 1
            }
        ]
        code, response = self.client.traffic_expenses_get(
            self.org_id, first_seen, last_seen)
        self.assertEqual(code, 200)
        traffic_expenses = response['traffic_expenses']
        self.assertEqual(len(traffic_expenses), 3)
        self.assertEqual(response['total_cost'], 6)
        self.assertEqual(response['total_usage'], 6)

        code, response = self.client.traffic_expenses_get(
            self.org_id, first_seen, last_seen, {'region': 'us-west'})
        self.assertEqual(code, 200)
        traffic_expenses = response['traffic_expenses']
        self.assertEqual(len(traffic_expenses), 1)
        self.assertEqual(response['total_cost'], 2)
        self.assertEqual(response['total_usage'], 2)

        code, response = self.client.traffic_expenses_get(
            self.org_id, first_seen, last_seen,
            {'resource_type': '%s:cluster' % cluster_type['name']}
        )
        traffic_expenses = response['traffic_expenses']
        self.assertEqual(len(traffic_expenses), 2)
        self.assertEqual(response['total_cost'], 3)
        self.assertEqual(response['total_usage'], 3)

    def test_traffic_expenses_grouping(self):
        start = int(datetime(2022, 2, 1).timestamp())
        end = int(datetime(2022, 3, 1).timestamp())
        day_1_ts = int(datetime(2022, 2, 2, tzinfo=timezone.utc).timestamp())

        valid_azure_cloud_acc = {
            'name': 'my another acc',
            'type': 'azure_cnr',
            'config': {
                'subscription_id': 'id',
                'secret': 'secret',
                'client_id': 'id',
                'tenant': 't'
            }
        }
        code, cloud_acc3 = self.create_cloud_account(
            self.org_id, valid_azure_cloud_acc)
        self.assertEqual(code, 201)

        res_aws = self._create_resource(
            self.cloud_acc1['id'], first_seen=day_1_ts, last_seen=day_1_ts)
        res_azure_1 = self._create_resource(
            self.cloud_acc2['id'], first_seen=day_1_ts, last_seen=day_1_ts)
        res_azure_2 = self._create_resource(
            cloud_acc3['id'], first_seen=day_1_ts, last_seen=day_1_ts)

        self.traffic_expenses = [
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'resource_id': res_aws['cloud_resource_id'],
                'date': datetime(2022, 2, 1),
                'type': 1,
                'from': 'westus2',
                'to': 'External',
                'usage': 5,
                'cost': 5,
                'sign': 1
            },
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'resource_id': res_aws['cloud_resource_id'],
                'date': datetime(2022, 2, 1),
                'type': 1,
                'from': 'westus2',
                'to': 'Another',
                'usage': 5,
                'cost': 5,
                'sign': 1
            },
            {
                'cloud_account_id': self.cloud_acc2['id'],
                'resource_id': res_azure_1['cloud_resource_id'],
                'date': datetime(2022, 2, 1),
                'type': 1,
                'from': 'westus2',
                'to': 'External',
                'usage': 6,
                'cost': 6,
                'sign': 1
            },
            {
                'cloud_account_id': cloud_acc3['id'],
                'resource_id': res_azure_2['cloud_resource_id'],
                'date': datetime(2022, 2, 1),
                'type': 1,
                'from': 'westus2',
                'to': 'External',
                'usage': 7,
                'cost': 7,
                'sign': 1
            },
            {
                'cloud_account_id': self.cloud_acc2['id'],
                'resource_id': res_azure_1['cloud_resource_id'],
                'date': datetime(2022, 2, 2),
                'type': 1,
                'from': 'westus2',
                'to': 'External',
                'usage': 8,
                'cost': 8,
                'sign': 1
            },
            {
                'cloud_account_id': cloud_acc3['id'],
                'resource_id': res_azure_2['cloud_resource_id'],
                'date': datetime(2022, 2, 2),
                'type': 1,
                'from': 'westus',
                'to': 'External',
                'usage': 9,
                'cost': 9,
                'sign': 1
            },
        ]
        code, response = self.client.traffic_expenses_get(
            self.org_id, start, end)
        self.assertEqual(code, 200)
        traffic_expenses = response['traffic_expenses']
        self.assertEqual(len(traffic_expenses), 4)
        expected_expense_map = {
            ('azure_cnr', 'westus', 'External'): {
                'cloud_type': 'azure_cnr',
                'from': {'name': 'westus', 'latitude': ANY, 'longitude': ANY},
                'to': {'name': 'External'},
                'usage': 9,
                'cost': 9
            },
            ('azure_cnr', 'westus2', 'External'): {
                'cloud_type': 'azure_cnr',
                'from': {'name': 'westus2', 'latitude': ANY, 'longitude': ANY},
                'to': {'name': 'External'},
                'usage': 21,
                'cost': 21
            },
            ('aws_cnr', 'westus2', 'External'): {
                'cloud_type': 'aws_cnr',
                'from': {'name': 'westus2'},
                'to': {'name': 'External'},
                'usage': 5,
                'cost': 5
            },
            ('aws_cnr', 'westus2', 'Another'): {
                'cloud_type': 'aws_cnr',
                'from': {'name': 'westus2'},
                'to': {'name': 'Another'},
                'usage': 5,
                'cost': 5
            }
        }
        for t in traffic_expenses:
            key = t['cloud_type'], t['from']['name'], t['to']['name']
            expected_expense = expected_expense_map.pop(key)
            self.assertEqual(expected_expense, t)
