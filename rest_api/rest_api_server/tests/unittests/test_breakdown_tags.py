import os
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from unittest.mock import patch
from rest_api.rest_api_server.tests.unittests.test_api_base import TestApiBase
from rest_api.rest_api_server.utils import get_nil_uuid

DAY_IN_SECONDS = 86400


class TestBreakdownTagsApi(TestApiBase):

    def setUp(self, version='v2'):
        super().setUp(version)
        patch('rest_api.rest_api_server.controllers.breakdown_tag.'
              'BreakdownTagController._aggregate_resource_data',
              wraps=self.patched_aggregate_breakdown_tags).start()
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
            'type': 'kubernetes_cnr',
            'config': {
                'url': 'https://test.cnr',
                'port': 4433,
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

    def patched_aggregate_breakdown_tags(self, match_query, **kwargs):
        resources = self.resources_collection.aggregate([
            {'$match': match_query},
        ])
        ids = defaultdict(list)
        for r in resources:
            day = None
            tags = r.get('tags')
            if not tags:
                day = int(r.get('first_seen', 0) / DAY_IN_SECONDS)
                tags = {None: None}
            for tag in tags.keys():
                ids[(tag, r.get('cluster_type_id'), day)].append(r['_id'])
        result = []
        for k, v in ids.items():
            result.append({
                '_id': {
                    'tag': k[0], 'cluster_type_id': k[1], 'day': k[2]
                },
                'resources': v
            })
        return result

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
        code, response = self.client.breakdown_tags_get(
            self.org_id, start_ts, start_ts, filters)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0212')

    def test_breakdown_tags_dates_values(self):
        filters = {
            'cloud_account_id': [self.cloud_acc1['id']],
        }
        min_timestamp = 0
        max_timestamp = int(datetime.max.replace(
            tzinfo=timezone.utc).timestamp()) - 1
        code, response = self.client.breakdown_tags_get(
            self.org_id, min_timestamp - 1, max_timestamp, filters)
        self.assertEqual(code, 400)
        self.verify_error_code(response, 'OE0224')
        code, response = self.client.breakdown_tags_get(
            self.org_id, min_timestamp, max_timestamp + 1, filters)
        self.assertEqual(code, 400)
        self.verify_error_code(response, 'OE0224')

        code, response = self.client.breakdown_tags_get(
            self.org_id, min_timestamp - 1, 0, filters)
        self.assertEqual(code, 400)
        self.verify_error_code(response, 'OE0224')

    def test_breakdown_tags_limit(self):
        time = int(datetime.utcnow().timestamp())
        code, response = self.client.breakdown_tags_get(
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
        code, response = self.client.breakdown_tags_get(
            organization2['id'], time, time + 1, filters)
        self.assertEqual(code, 404)
        self.verify_error_code(response, 'OE0470')

    def test_breakdown_tags(self):
        start = int(datetime(2022, 2, 1).timestamp())
        end = int(datetime(2022, 3, 1).timestamp())

        day_1_ts = int(datetime(2022, 2, 2, tzinfo=timezone.utc).timestamp())
        res1 = self._create_resource(
            self.cloud_acc1['id'], first_seen=day_1_ts, last_seen=day_1_ts,
            tags={'tag1': 'val1', 'tag2': 'val2'})
        res2 = self._create_resource(
            self.cloud_acc1['id'], first_seen=day_1_ts, last_seen=day_1_ts,
            tags={'tag1': 'val1'})
        self.expenses = [
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'resource_id': res1['id'],
                'date': datetime(2022, 2, 1),
                'cost': 10,
                'sign': 1
            },
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'resource_id': res2['id'],
                'date': datetime(2022, 2, 1),
                'cost': 15,
                'sign': 1
            },
        ]
        code, response = self.client.breakdown_tags_get(
            self.org_id, start, end)
        self.assertEqual(code, 200)
        expected_breakdown = [
            {'cost': 25, 'count': 2, 'tag': 'tag1'},
            {'cost': 10, 'count': 1, 'tag': 'tag2'}
        ]
        self.assertEqual(response['breakdown'], expected_breakdown)

    def test_breakdown_tags_incorrect_identity(self):
        start = int(datetime(2022, 2, 1).timestamp())
        end = int(datetime(2022, 3, 1).timestamp())

        day_1_ts = int(datetime(2022, 2, 2, tzinfo=timezone.utc).timestamp())
        res = self._create_resource(
            self.cloud_acc1['id'], first_seen=day_1_ts, last_seen=day_1_ts,
            r_type='Instance',  tags={'tag1': 'val1', 'tag2': 'val2'})
        self.expenses = [
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'resource_id': res['id'],
                'date': datetime(2022, 2, 1),
                'cost': 10,
                'sign': 1
            },
        ]
        code, response = self.client.breakdown_tags_get(
            self.org_id, start, end, {'resource_type': 'Instance:unknown'})
        self.assertEqual(code, 400)
        self.verify_error_code(response, 'OE0499')

    def test_empty_breakdown_tags(self):
        start = int(datetime(2022, 2, 1).timestamp())
        end = int(datetime(2022, 3, 1).timestamp())
        code, response = self.client.breakdown_tags_get(
            self.org_id, start, end)
        self.assertEqual(code, 200)
        self.assertEqual(response['breakdown'], [])

    def test_breakdown_tags_without_expenses(self):
        start = int(datetime(2022, 2, 1).timestamp())
        end = int(datetime(2022, 3, 1).timestamp())

        day_1_ts = int(datetime(2022, 2, 2, tzinfo=timezone.utc).timestamp())
        self._create_resource(
            self.cloud_acc1['id'], first_seen=day_1_ts, last_seen=day_1_ts,
            tags={'tag1': 'val1', 'tag2': 'val2'})
        self._create_resource(
            self.cloud_acc1['id'], first_seen=day_1_ts, last_seen=day_1_ts,
            tags={'tag1': 'val1'})
        code, response = self.client.breakdown_tags_get(
            self.org_id, start, end)
        self.assertEqual(code, 200)
        expected_breakdown = [
            {'cost': 0, 'count': 2, 'tag': 'tag1'},
            {'cost': 0, 'count': 1, 'tag': 'tag2'}
        ]
        self.assertEqual(response['breakdown'], expected_breakdown)

    def test_breakdown_tags_expenses_sum(self):
        start = int(datetime(2022, 2, 1).timestamp())
        end = int(datetime(2022, 3, 1).timestamp())

        day_1_ts = int(datetime(2022, 2, 2, tzinfo=timezone.utc).timestamp())
        res1 = self._create_resource(
            self.cloud_acc1['id'], first_seen=day_1_ts, last_seen=day_1_ts,
            tags={'tag1': 'val1', 'tag2': 'val2'})
        cost_map = {
            datetime(2022, 1, 31): 5,
            datetime(2022, 2, 1): 10,
            datetime(2022, 2, 2): 20,
            datetime(2022, 3, 2): 30

        }
        for dt, cost in cost_map.items():
            self.expenses.append({
                'cloud_account_id': self.cloud_acc1['id'],
                'resource_id': res1['id'],
                'date': dt,
                'cost': cost,
                'sign': 1
            })
        code, response = self.client.breakdown_tags_get(
            self.org_id, start, end)
        self.assertEqual(code, 200)
        expected_breakdown = [
            {'tag': 'tag1', 'cost': 30, 'count': 1},
            {'tag': 'tag2', 'cost': 30, 'count': 1}
        ]
        self.assertEqual(response['breakdown'], expected_breakdown)

    def test_breakdown_tags_clusters(self):
        code, cluster_type = self.client.cluster_type_create(
            self.org_id, {'name': 'awesome', 'tag_key': 'tag1'})
        self.assertEqual(code, 201)
        dt = datetime(2021, 2, 1, tzinfo=timezone.utc)
        first_seen = int((dt - timedelta(days=1)).timestamp())
        last_seen = int(dt.timestamp())
        self._create_resource(
            self.cloud_acc1['id'], tags={'tag1': 'val1'}, region='us-east',
            first_seen=first_seen, last_seen=last_seen)
        self._create_resource(
            self.cloud_acc1['id'], tags={'tag2': 'val2'},
            first_seen=first_seen, last_seen=last_seen)
        self._create_resource(
            self.cloud_acc1['id'], tags={'tag1': 'val1', 'tag3': 'val3'},
            region='us-west', first_seen=first_seen, last_seen=last_seen)
        self._create_resource(
            self.cloud_acc1['id'], tags={'tag3': 'val3'}, region='us-test',
            first_seen=first_seen, last_seen=last_seen)

        expected_breakdown = [
            {'tag': 'tag1', 'cost': 0, 'count': 2},
            {'tag': 'tag2', 'cost': 0, 'count': 1},
            {'tag': 'tag3', 'cost': 0, 'count': 2}
        ]

        code, response = self.client.breakdown_tags_get(
            self.org_id, first_seen, last_seen)
        self.assertEqual(code, 200)
        self.assertEqual(expected_breakdown, response['breakdown'])

        code, response = self.client.breakdown_tags_get(
            self.org_id, first_seen, last_seen,
            {'cloud_account_id': self.cloud_acc1['id']})
        self.assertEqual(code, 200)
        self.assertEqual(expected_breakdown, response['breakdown'])

        code, response = self.client.breakdown_tags_get(
            self.org_id, first_seen, last_seen, {'region': get_nil_uuid()})
        self.assertEqual(code, 200)
        expected_breakdown = [
            {'tag': 'tag2', 'cost': 0, 'count': 1},
        ]
        self.assertEqual(expected_breakdown, response['breakdown'])

        code, response = self.client.breakdown_tags_get(
            self.org_id, first_seen, last_seen,
            {'resource_type': '%s:cluster' % cluster_type['name']})
        self.assertEqual(code, 200)
        expected_breakdown = [
            {'tag': 'tag1', 'cost': 0, 'count': 2},
            {'tag': 'tag3', 'cost': 0, 'count': 1}
        ]
        self.assertEqual(expected_breakdown, response['breakdown'])

    def test_breakdown_tags_traffic_filters(self):
        start = int(datetime(2022, 2, 1).timestamp())
        end = int(datetime(2022, 3, 1).timestamp())

        day_1_ts = int(datetime(2022, 2, 2, tzinfo=timezone.utc).timestamp())
        res1 = self._create_resource(
            self.cloud_acc1['id'], first_seen=day_1_ts, last_seen=day_1_ts,
            tags={'tag1': 'val1', 'tag2': 'val2'})
        res2 = self._create_resource(
            self.cloud_acc1['id'], first_seen=day_1_ts, last_seen=day_1_ts,
            tags={'tag1': 'val1'})
        res3 = self._create_resource(
            self.cloud_acc1['id'], first_seen=day_1_ts, last_seen=day_1_ts,
            tags={'tag3': 'val3'})
        self.expenses = [
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'resource_id': res1['id'],
                'date': datetime(2022, 2, 1),
                'cost': 10,
                'sign': 1
            },
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'resource_id': res2['id'],
                'date': datetime(2022, 2, 1),
                'cost': 15,
                'sign': 1
            },
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'resource_id': res3['id'],
                'date': datetime(2022, 2, 1),
                'cost': 30,
                'sign': 1
            },
        ]
        self.traffic_expenses = [
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'resource_id': res1['cloud_resource_id'],
                'date': int(datetime(2022, 2, 1).timestamp()),
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
                'date': int(datetime(2022, 2, 1).timestamp()),
                'type': 1,
                'from': 'from_2',
                'to': 'to_2',
                'usage': 2,
                'cost': 2,
                'sign': 1
            }
        ]
        for body in [
            {
                'traffic_from': 'from_2:aws_cnr'
            },
            {
                'traffic_to': 'to_2:aws_cnr'
            }
        ]:
            code, response = self.client.breakdown_tags_get(
                self.org_id, start, end, body)
            self.assertEqual(code, 200)
            self.assertEqual(len(response['breakdown']), 1)
            self.assertEqual(response['breakdown'][0],
                             {'tag': 'tag1', 'cost': 15, 'count': 1})

        for body in [
            {
                'traffic_from': ['from_2:aws_cnr', 'from_1:aws_cnr']
            },
            {
                'traffic_to': ['to_1:aws_cnr', 'to_2:aws_cnr', 'to_3:azure']
            },
            {
                'traffic_from': 'ANY'
            },
            {
                'traffic_to': 'ANY'
            },
        ]:
            code, response = self.client.breakdown_tags_get(
                self.org_id, start, end, body)
            self.assertEqual(code, 200)
            self.assertEqual(len(response['breakdown']), 2)
            self.assertEqual(response['breakdown'], [
                {'tag': 'tag1', 'cost': 25, 'count': 2},
                {'tag': 'tag2', 'cost': 10, 'count': 1}
            ])

        code, response = self.client.breakdown_tags_get(
            self.org_id, start, end)
        self.assertEqual(code, 200)
        self.assertEqual(len(response['breakdown']), 3)
