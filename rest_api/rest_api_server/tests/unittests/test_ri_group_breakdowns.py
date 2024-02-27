from datetime import datetime, timedelta
from unittest.mock import patch
from rest_api.rest_api_server.tests.unittests.test_api_base import TestApiBase


class TestRiGroupBreakdownApi(TestApiBase):
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
            'type': 'aws_cnr',
            'config': {
                'access_key_id': 'key',
                'secret_access_key': 'secret',
                'config_scheme': 'create_report'
            }
        }
        self.auth_user_id_1 = self.gen_id()
        _, self.employee1 = self.client.employee_create(
            self.org_id,
            {'name': 'name1', 'auth_user_id': self.auth_user_id_1})
        _, self.cloud_acc1 = self.create_cloud_account(
            self.org_id, cloud_acc1, auth_user_id=self.auth_user_id_1)
        _, self.cloud_acc2 = self.create_cloud_account(
            self.org_id, cloud_acc2, auth_user_id=self.auth_user_id_1)
        self.start = datetime(2023, 1, 1, 0, 0, 0)
        self.start_ts = int(self.start.timestamp())

    def test_without_cloud_account_id(self):
        resource_id = self.gen_id()
        self.uncovered_usage = [
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'date': self.start,
                'resource_id': resource_id,
                'location': 'us-west',
                'instance_type': 't2.large',
                'os': 'Linux',
                'usage': 1000,
                'cost': 1000,
                'sign': 1
            }
        ]
        self.resources_collection.insert_one({
            '_id': resource_id,
            'cloud_resource_id': resource_id,
            'cloud_account_id': self.cloud_acc1['id']
        })
        params = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1
        }
        code, response = self.client.ri_group_breakdown_get(
            self.org_id, **params)
        self.assertEqual(code, 200)
        result = {
            str(self.start_ts): [{
                'group_id': {
                    'instance_type': 't2.large',
                    'os': 'Linux',
                    'location': 'us-west'
                },
                'data': [{
                    'cloud_account_id': self.cloud_acc1['id'],
                    'cloud_resource_id': resource_id,
                    'usage': 1000,
                    'cost': 1000,
                    'cloud_account_type': 'aws_cnr',
                    'cloud_account_name': self.cloud_acc1['name'],
                    'id': resource_id,
                    'name': None}]}]
        }
        self.assertDictEqual(response['breakdown'], result)

    def test_with_cloud_account_id(self):
        resource_id = self.gen_id()
        self.uncovered_usage = [
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'date': self.start,
                'resource_id': resource_id,
                'location': 'us-west',
                'instance_type': 't2.large',
                'os': 'Linux',
                'usage': 1000,
                'cost': 1000,
                'sign': 1
            }
        ]
        self.resources_collection.insert_one({
            '_id': resource_id,
            'cloud_resource_id': resource_id,
            'cloud_account_id': self.cloud_acc1['id']
        })
        params = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1,
            'cloud_account_id': self.cloud_acc1['id']
        }
        code, response = self.client.ri_group_breakdown_get(
            self.org_id, **params)
        self.assertEqual(code, 200)
        result = {
            str(self.start_ts): [{
                'group_id': {
                    'instance_type': 't2.large',
                    'os': 'Linux',
                    'location': 'us-west'
                },
                'data': [{
                    'cloud_account_id': self.cloud_acc1['id'],
                    'cloud_resource_id': resource_id,
                    'usage': 1000,
                    'cost': 1000,
                    'cloud_account_type': 'aws_cnr',
                    'cloud_account_name': self.cloud_acc1['name'],
                    'id': resource_id,
                    'name': None}]}]
        }
        self.assertDictEqual(response['breakdown'], result)

    def test_with_several_cloud_account_id(self):
        resource_id = self.gen_id()
        self.uncovered_usage = [
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'date': self.start,
                'resource_id': resource_id,
                'location': 'us-west',
                'instance_type': 't2.large',
                'os': 'Linux',
                'usage': 1000,
                'cost': 1000,
                'sign': 1
            }
        ]
        self.resources_collection.insert_one({
            '_id': resource_id,
            'cloud_resource_id': resource_id,
            'cloud_account_id': self.cloud_acc1['id']
        })
        params = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1,
            'cloud_account_id': [self.cloud_acc1['id'], self.cloud_acc2['id']]
        }
        code, response = self.client.ri_group_breakdown_get(
            self.org_id, **params)
        self.assertEqual(code, 200)
        result = {
            str(self.start_ts): [{
                'group_id': {
                    'instance_type': 't2.large',
                    'os': 'Linux',
                    'location': 'us-west'
                },
                'data': [{
                    'cloud_account_id': self.cloud_acc1['id'],
                    'cloud_resource_id': resource_id,
                    'usage': 1000,
                    'cost': 1000,
                    'cloud_account_type': 'aws_cnr',
                    'cloud_account_name': self.cloud_acc1['name'],
                    'id': resource_id,
                    'name': None}]}],
        }
        self.assertDictEqual(response['breakdown'], result)

    def test_not_aws_account(self):
        cloud_acc_az = {
            'name': 'cloud_acc_az',
            'type': 'azure_cnr',
            'config': {
                'subscription_id': 'id',
                'secret': 'secret',
                'client_id': 'id',
                'tenant': 't',
            }
        }
        _, cloud_acc = self.create_cloud_account(
            self.org_id, cloud_acc_az, auth_user_id=self.auth_user_id_1)
        resource_id = self.gen_id()
        self.uncovered_usage = [
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'date': self.start,
                'resource_id': resource_id,
                'location': 'us-west',
                'instance_type': 't2.large',
                'os': 'Linux',
                'usage': 1000,
                'cost': 1000,
                'sign': 1
            }
        ]
        self.resources_collection.insert_one({
            '_id': resource_id,
            'cloud_resource_id': resource_id,
            'cloud_account_id': self.cloud_acc1['id']
        })

        # not aws account is not returned
        params = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1,
            'cloud_account_id': cloud_acc['id']
        }
        code, response = self.client.ri_group_breakdown_get(
            self.org_id, **params)
        self.assertEqual(code, 200)
        self.assertEqual(response['breakdown'], {})

    def test_required_filters(self):
        params = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1
        }
        for param in ['start_date', 'end_date']:
            params_copy = params.copy()
            params_copy.pop(param)
            code, response = self.client.ri_group_breakdown_get(
                self.org_id, **params_copy)
            self.assertEqual(code, 400)
            self.verify_error_code(response, 'OE0216')

    def test_unexpected_filters(self):
        params = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1,
            'region': 'us-east-1',
        }
        code, response = self.client.ri_group_breakdown_get(
            self.org_id, **params)
        self.assertEqual(code, 400)
        self.verify_error_code(response, 'OE0212')

    def test_invalid_dates(self):
        params = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1
        }
        for param in ['start_date', 'end_date']:
            params_copy = params.copy()
            for value in ['impostor', 0.5]:
                params_copy[param] = value
                code, response = self.client.ri_group_breakdown_get(
                    self.org_id, **params_copy)
                self.assertEqual(code, 400)
                self.verify_error_code(response, 'OE0217')

            params_copy[param] = -1
            code, response = self.client.ri_group_breakdown_get(
                self.org_id, **params_copy)
            self.assertEqual(code, 400)
            self.verify_error_code(response, 'OE0224')

        params = {
            'start_date': self.start_ts,
            'end_date': self.start_ts - 15
        }
        code, response = self.client.ri_group_breakdown_get(
            self.org_id, **params)
        self.assertEqual(code, 400)
        self.verify_error_code(response, 'OE0446')

    def test_not_found_cloud_acc(self):
        filters = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1,
            'cloud_account_id': 'impostor'
        }
        code, response = self.client.ri_group_breakdown_get(
            self.org_id, **filters)
        self.assertEqual(code, 404)
        self.verify_error_code(response, 'OE0470')

    def test_org_without_cloud_accs(self):
        _, organization2 = self.client.organization_create(
            {'name': "organization2"})
        filters = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1
        }
        code, response = self.client.ri_group_breakdown_get(
            organization2['id'], **filters)
        self.assertEqual(code, 424)
        self.verify_error_code(response, 'OE0445')

    def test_invalid_organization(self):
        _, organization2 = self.client.organization_create(
            {'name': "organization2"})
        self.client.organization_delete(organization2['id'])
        filters = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1,
            'cloud_account_id': self.cloud_acc1['id']
        }
        for org_id in [organization2['id'], 'impostor']:
            code, response = self.client.ri_group_breakdown_get(
                org_id, **filters)
            self.assertEqual(code, 404)
            self.verify_error_code(response, 'OE0002')

    def test_ch_cancelled_expenses(self):
        resource_id = self.gen_id()
        self.uncovered_usage = [
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'date': self.start,
                'resource_id': resource_id,
                'location': 'us-east',
                'os': 'Linux',
                'instance_type': 't2.large',
                'usage': 1000,
                'cost': 1000,
                'sign': 1
            },
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'date': self.start,
                'resource_id': resource_id,
                'location': 'us-east',
                'os': 'Linux',
                'instance_type': 't2.large',
                'usage': 1000,
                'cost': 1000,
                'sign': -1
            }
        ]
        self.resources_collection.insert_one({
            '_id': resource_id,
            'cloud_resource_id': resource_id,
            'cloud_account_id': self.cloud_acc1['id']
        })
        params = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1,
            'cloud_account_id': self.cloud_acc1['id']
        }
        code, response = self.client.ri_group_breakdown_get(
            self.org_id, **params)
        self.assertEqual(code, 200)
        self.assertDictEqual(response['breakdown'], {})

    def test_multiple_usage_in_group(self):
        resource_id = self.gen_id()
        resource_id2 = self.gen_id()
        self.uncovered_usage = [
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'date': self.start,
                'resource_id': resource_id,
                'location': 'us-east',
                'os': 'Linux',
                'instance_type': 't2.large',
                'usage': 1000,
                'cost': 1000,
                'sign': 1
            },
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'date': self.start,
                'resource_id': resource_id2,
                'location': 'us-east',
                'os': 'Linux',
                'instance_type': 't2.large',
                'usage': 1000,
                'cost': 1000,
                'sign': 1
            }]
        self.resources_collection.insert_one({
            '_id': resource_id,
            'cloud_resource_id': resource_id,
            'cloud_account_id': self.cloud_acc1['id']
        })
        self.resources_collection.insert_one({
            '_id': resource_id2,
            'cloud_resource_id': resource_id2,
            'cloud_account_id': self.cloud_acc1['id']
        })
        params = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1,
            'cloud_account_id': self.cloud_acc1['id']
        }
        code, response = self.client.ri_group_breakdown_get(
            self.org_id, **params)
        result = {
            str(self.start_ts): [{
                'group_id': {
                    'instance_type': 't2.large',
                    'os': 'Linux',
                    'location': 'us-east'},
                'data': [
                    {
                        'cloud_account_id': self.cloud_acc1['id'],
                        'cloud_resource_id': resource_id,
                        'usage': 1000,
                        'cost': 1000,
                        'cloud_account_type': 'aws_cnr',
                        'cloud_account_name': 'cloud_acc1',
                        'id': resource_id,
                        'name': None
                    },
                    {
                        'cloud_account_id': self.cloud_acc1['id'],
                        'cloud_resource_id': resource_id2,
                        'usage': 1000,
                        'cost': 1000,
                        'cloud_account_type': 'aws_cnr',
                        'cloud_account_name': 'cloud_acc1',
                        'id': resource_id2,
                        'name': None
                    }
                ]}],
        }
        self.assertDictEqual(
            response['breakdown'][str(self.start_ts)][0]['group_id'],
            result[str(self.start_ts)][0]['group_id']
        )
        for usage in response['breakdown'][str(self.start_ts)][0]['data']:
            self.assertIn(usage, result[str(self.start_ts)][0]['data'])

    def test_date_ranges(self):
        day1 = self.start + timedelta(days=1)
        day2 = self.start + timedelta(days=2)
        end = self.start + timedelta(days=3)
        day1_ts = int(day1.timestamp())
        day2_ts = int(day2.timestamp())
        end_ts = int(end.timestamp())
        resource_id = self.gen_id()
        self.uncovered_usage = [
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'date': self.start,
                'resource_id': resource_id,
                'location': 'us-east',
                'os': 'Linux',
                'instance_type': 't2.large',
                'usage': 1000,
                'cost': 1000,
                'sign': 1
            },
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'date': day1,
                'resource_id': resource_id,
                'location': 'us-east',
                'os': 'Linux',
                'instance_type': 't2.large',
                'usage': 1001,
                'cost': 1001,
                'sign': 1
            },
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'date': day2,
                'resource_id': resource_id,
                'location': 'us-west',
                'os': 'Linux',
                'instance_type': 't3.large',
                'usage': 1002,
                'cost': 1002,
                'sign': 1
            },
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'date': day2,
                'resource_id': resource_id,
                'location': 'us-east',
                'os': 'Linux',
                'instance_type': 't2.large',
                'usage': 1003,
                'cost': 1003,
                'sign': 1
            }
        ]
        self.resources_collection.insert_one({
            '_id': resource_id,
            'cloud_resource_id': resource_id,
            'cloud_account_id': self.cloud_acc1['id']
        })
        params = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1,
            'cloud_account_id': self.cloud_acc1['id']
        }
        code, response = self.client.ri_group_breakdown_get(
            self.org_id, **params)
        self.assertEqual(code, 200)
        result = {
            str(self.start_ts): [{
                'group_id': {
                    'instance_type': 't2.large',
                    'os': 'Linux',
                    'location': 'us-east'},
                'data': [{
                    'cloud_account_id': self.cloud_acc1['id'],
                    'cloud_resource_id': resource_id,
                    'usage': 1000,
                    'cost': 1000,
                    'cloud_account_type': 'aws_cnr',
                    'cloud_account_name': 'cloud_acc1',
                    'id': resource_id,
                    'name': None}]}],
        }
        self.assertDictEqual(response['breakdown'], result)
        params = {
            'start_date': self.start_ts,
            'end_date': end_ts,
            'cloud_account_id': self.cloud_acc1['id']
        }
        code, response = self.client.ri_group_breakdown_get(
            self.org_id, **params)
        self.assertEqual(code, 200)
        result = {
            str(self.start_ts): [{
                'group_id': {
                    'instance_type': 't2.large',
                    'os': 'Linux',
                    'location': 'us-east'},
                'data': [{
                    'cloud_account_id': self.cloud_acc1['id'],
                    'cloud_resource_id': resource_id,
                    'usage': 1000,
                    'cost': 1000,
                    'cloud_account_type': 'aws_cnr',
                    'cloud_account_name': 'cloud_acc1',
                    'id': resource_id,
                    'name': None}]}],
            str(day1_ts): [{
                'group_id': {
                    'instance_type': 't2.large',
                    'os': 'Linux',
                    'location': 'us-east'},
                'data': [{
                    'cloud_account_id': self.cloud_acc1['id'],
                    'cloud_resource_id': resource_id,
                    'usage': 1001,
                    'cost': 1001,
                    'cloud_account_type': 'aws_cnr',
                    'cloud_account_name': 'cloud_acc1',
                    'id': resource_id,
                    'name': None}]}],
            str(day2_ts): [
                {
                    'group_id': {
                        'instance_type': 't2.large',
                        'os': 'Linux',
                        'location': 'us-east'},
                    'data': [{
                        'cloud_account_id': self.cloud_acc1['id'],
                        'cloud_resource_id': resource_id,
                        'usage': 1003,
                        'cost': 1003,
                        'cloud_account_type': 'aws_cnr',
                        'cloud_account_name': 'cloud_acc1',
                        'id': resource_id,
                        'name': None}]
                },
                {
                    'group_id': {
                        'instance_type': 't3.large',
                        'os': 'Linux',
                        'location': 'us-west'},
                    'data': [
                        {
                            'cloud_account_id': self.cloud_acc1['id'],
                            'cloud_resource_id': resource_id,
                            'usage': 1002,
                            'cost': 1002,
                            'cloud_account_type': 'aws_cnr',
                            'cloud_account_name': 'cloud_acc1',
                            'id': resource_id,
                            'name': None
                        }
                    ]
                }
            ]
        }
        for date, values in response['breakdown'].items():
            for val in values:
                self.assertIn(val, result[date])

    def test_total_costs(self):
        resource_id1 = self.gen_id()
        resource_id2 = self.gen_id()
        self.uncovered_usage = [
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'date': self.start,
                'resource_id': resource_id1,
                'location': 'us-east',
                'os': 'Linux',
                'instance_type': 't2.large',
                'cost': 1000,
                'usage': 999,
                'sign': 1
            },
            {
                'cloud_account_id': self.cloud_acc2['id'],
                'date': self.start,
                'resource_id': resource_id2,
                'location': 'us-east',
                'os': 'Linux',
                'instance_type': 't2.large',
                'cost': 2000,
                'usage': 1999,
                'sign': 1
            },
            {
                'cloud_account_id': self.cloud_acc2['id'],
                'date': self.start,
                'resource_id': resource_id2,
                'location': 'us-east',
                'os': 'Linux',
                'instance_type': 't2.large',
                'cost': 2000,
                'usage': 1999,
                'sign': -1
            }
        ]
        self.resources_collection.insert_one({
            '_id': resource_id1,
            'cloud_resource_id': resource_id1,
            'cloud_account_id': self.cloud_acc1['id']
        })
        self.resources_collection.insert_one({
            '_id': resource_id2,
            'cloud_resource_id': resource_id2,
            'cloud_account_id': self.cloud_acc2['id']
        })
        params = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1
        }
        code, response = self.client.ri_group_breakdown_get(
            self.org_id, **params)
        self.assertEqual(code, 200)
        result = {
            str(self.start_ts): [{
                'group_id': {
                    'instance_type': 't2.large',
                    'os': 'Linux',
                    'location': 'us-east'},
                'data': [
                    {
                        'cloud_account_id': self.cloud_acc1['id'],
                        'cloud_resource_id': resource_id1,
                        'id': resource_id1,
                        'name': None,
                        'usage': 999,
                        'cost': 1000,
                        'cloud_account_type': 'aws_cnr',
                        'cloud_account_name': 'cloud_acc1'
                    }
                ]}]
        }
        self.assertDictEqual(response['breakdown'], result)

    def test_post(self):
        code, response = self.client.post(
            self.client.ri_group_breakdown_url(self.org_id), body={})
        self.assertEqual(code, 405)

    def test_patch(self):
        code, response = self.client.patch(
            self.client.ri_group_breakdown_url(self.org_id), body={})
        self.assertEqual(code, 405)

    def test_delete(self):
        code, response = self.client.delete(
            self.client.ri_group_breakdown_url(self.org_id))
        self.assertEqual(code, 405)
