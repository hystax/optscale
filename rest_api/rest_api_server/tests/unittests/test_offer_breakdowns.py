from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from rest_api.rest_api_server.tests.unittests.test_api_base import TestApiBase


class TestOfferBreakdownApi(TestApiBase):
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
        self.ri_id = 'ri_id'
        self.sp_id = 'sp_id'
        self.ri = {
            'cloud_account_id': self.cloud_acc1['id'],
            '_id': self.gen_id(),
            'cloud_resource_id': self.ri_id,
            'resource_type': 'Reserved Instances',
            'meta': {
                'payment_option': 'Partial Upfront',
                'offering_type': 'standard',
                'purchase_term': '1yr'
            }
        }
        self.sp = {
            'cloud_account_id': self.cloud_acc1['id'],
            '_id': self.gen_id(),
            'cloud_resource_id': self.sp_id,
            'resource_type': 'Savings Plan',
            'meta': {
                'payment_option': 'No Upfront',
                'offering_type': 'standard',
                'purchase_term': '1yr',
                'applied_region': 'Any'
            }
        }
        self.sp_acc2 = {
                'cloud_account_id': self.cloud_acc2['id'],
                '_id': self.gen_id(),
                'cloud_resource_id': self.gen_id(),
                'resource_type': 'Savings Plan',
                'meta': {
                    'payment_option': 'No Upfront',
                    'offering_type': 'standard',
                    'purchase_term': '1yr',
                    'applied_region': 'Any'
                }
            }
        self.resources_collection.insert_many([
            self.ri,
            self.sp,
            self.sp_acc2
        ])

    def test_without_cloud_account_id(self):
        self.ri_sp_usage = [
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'date': self.start,
                'resource_id': self.gen_id(),
                'offer_id': self.ri_id,
                'offer_type': 'ri',
                'offer_cost': 10,
                'on_demand_cost': 11,
                'usage': 0.2,
                'ri_norm_factor': 2,
                'expected_cost': 11,
                'sign': 1
            },
            {
                'cloud_account_id': self.cloud_acc2['id'],
                'date': self.start,
                'resource_id': self.gen_id(),
                'offer_id': self.sp_acc2['cloud_resource_id'],
                'offer_type': 'sp',
                'offer_cost': 1,
                'on_demand_cost': 11,
                'usage': 0.2,
                'ri_norm_factor': 2,
                'expected_cost': 1.1,
                'sign': 1
            }
        ]
        params = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1
        }
        code, response = self.client.offer_breakdown_get(
            self.org_id, **params)
        self.assertEqual(code, 200)
        result = {
            str(self.start_ts): [{
                'offer_type': 'ri',
                'cloud_resource_id': self.ri_id,
                'cost': 10,
                'expected_cost': 11,
                'id': self.ri['_id'],
                'payment_option': self.ri['meta']['payment_option'],
                'offering_type': self.ri['meta']['offering_type'],
                'purchase_term': self.ri['meta']['purchase_term'],
                'cloud_account_type': 'aws_cnr',
                'cloud_account_name': self.cloud_acc1['name'],
                'cloud_account_id': self.cloud_acc1['id']
            }, {
                'offer_type': 'sp',
                'cloud_resource_id': self.sp_acc2['cloud_resource_id'],
                'cost': 1,
                'expected_cost': 1.1,
                'id': self.sp_acc2['_id'],
                'payment_option': self.sp_acc2['meta']['payment_option'],
                'offering_type': self.sp_acc2['meta']['offering_type'],
                'purchase_term': self.sp_acc2['meta']['purchase_term'],
                'applied_region': self.sp_acc2['meta']['applied_region'],
                'cloud_account_type': 'aws_cnr',
                'cloud_account_name': self.cloud_acc2['name'],
                'cloud_account_id': self.cloud_acc2['id']
            }]
        }
        self.assertIn(result[str(self.start_ts)][0],
                      response['breakdown'][str(self.start_ts)])
        self.assertIn(result[str(self.start_ts)][1],
                      response['breakdown'][str(self.start_ts)])

    def test_with_cloud_account_id(self):
        self.ri_sp_usage = [
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'date': self.start,
                'resource_id': self.gen_id(),
                'offer_id': self.ri_id,
                'offer_type': 'ri',
                'offer_cost': 10,
                'on_demand_cost': 11,
                'usage': 0.3,
                'ri_norm_factor': 2,
                'expected_cost': 12,
                'sign': 1
            }
        ]
        params = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1,
            'cloud_account_id': self.cloud_acc1['id']
        }
        code, response = self.client.offer_breakdown_get(self.org_id, **params)
        self.assertEqual(code, 200)
        result = {
            str(self.start_ts): [{
                'offer_type': 'ri',
                'cloud_resource_id': self.ri_id,
                'cost': 10,
                'expected_cost': 12,
                'id': self.ri['_id'],
                'payment_option': self.ri['meta']['payment_option'],
                'offering_type': self.ri['meta']['offering_type'],
                'purchase_term': self.ri['meta']['purchase_term'],
                'cloud_account_type': 'aws_cnr',
                'cloud_account_name': self.cloud_acc1['name'],
                'cloud_account_id': self.cloud_acc1['id']
            }],
        }
        self.assertDictEqual(response['breakdown'], result)

    def test_with_several_cloud_account_id(self):
        self.ri_sp_usage = [
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'date': self.start,
                'resource_id': self.gen_id(),
                'offer_id': self.ri_id,
                'offer_type': 'ri',
                'offer_cost': 10,
                'on_demand_cost': 11,
                'usage': 0.2,
                'ri_norm_factor': 2,
                'expected_cost': 11,
                'sign': 1
            },
            {
                'cloud_account_id': self.cloud_acc2['id'],
                'date': self.start,
                'resource_id': self.gen_id(),
                'offer_id': self.sp_acc2['cloud_resource_id'],
                'offer_type': 'sp',
                'offer_cost': 1,
                'on_demand_cost': 11,
                'usage': 0.2,
                'ri_norm_factor': 2,
                'expected_cost': 1.1,
                'sign': 1
            }
        ]
        params = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1,
            'cloud_account_id': [self.cloud_acc1['id'], self.cloud_acc2['id']]
        }
        code, response = self.client.offer_breakdown_get(self.org_id, **params)
        self.assertEqual(code, 200)
        result = {
            str(self.start_ts): [{
                'offer_type': 'ri',
                'cloud_resource_id': self.ri_id,
                'cost': 10,
                'expected_cost': 11,
                'id': self.ri['_id'],
                'payment_option': self.ri['meta']['payment_option'],
                'offering_type': self.ri['meta']['offering_type'],
                'purchase_term': self.ri['meta']['purchase_term'],
                'cloud_account_type': 'aws_cnr',
                'cloud_account_name': self.cloud_acc1['name'],
                'cloud_account_id': self.cloud_acc1['id']
            }, {
                'offer_type': 'sp',
                'cloud_resource_id': self.sp_acc2['cloud_resource_id'],
                'cost': 1,
                'expected_cost': 1.1,
                'id': self.sp_acc2['_id'],
                'payment_option': self.sp_acc2['meta']['payment_option'],
                'offering_type': self.sp_acc2['meta']['offering_type'],
                'purchase_term': self.sp_acc2['meta']['purchase_term'],
                'applied_region': self.sp_acc2['meta']['applied_region'],
                'cloud_account_type': 'aws_cnr',
                'cloud_account_name': self.cloud_acc2['name'],
                'cloud_account_id': self.cloud_acc2['id']
            }]
        }
        self.assertIn(result[str(self.start_ts)][0],
                      response['breakdown'][str(self.start_ts)])
        self.assertIn(result[str(self.start_ts)][1],
                      response['breakdown'][str(self.start_ts)])

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

        self.ri_sp_usage = [
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'date': self.start,
                'resource_id': self.gen_id(),
                'offer_id': self.ri_id,
                'offer_type': 'ri',
                'offer_cost': 10,
                'on_demand_cost': 11,
                'usage': 0.3,
                'ri_norm_factor': 2,
                'expected_cost': 12,
                'sign': 1
            }
        ]

        # not aws account is not returned
        params = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1,
            'cloud_account_id': cloud_acc['id']
        }
        code, response = self.client.offer_breakdown_get(self.org_id, **params)
        self.assertEqual(code, 200)
        self.assertEqual(response['breakdown'], {})

        # aws accounts are returned, not aws accounts are not returned
        params = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1
        }
        code, response = self.client.offer_breakdown_get(self.org_id, **params)
        self.assertEqual(code, 200)
        result = {
            str(self.start_ts): [{
                'offer_type': 'ri',
                'cloud_resource_id': self.ri_id,
                'cost': 10,
                'expected_cost': 12,
                'id': self.ri['_id'],
                'payment_option': self.ri['meta']['payment_option'],
                'offering_type': self.ri['meta']['offering_type'],
                'purchase_term': self.ri['meta']['purchase_term'],
                'cloud_account_type': 'aws_cnr',
                'cloud_account_name': self.cloud_acc1['name'],
                'cloud_account_id': self.cloud_acc1['id']
            }],
        }
        self.assertDictEqual(response['breakdown'], result)

    def test_required_filters(self):
        params = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1
        }
        for param in ['start_date', 'end_date']:
            params_copy = params.copy()
            params_copy.pop(param)
            code, response = self.client.offer_breakdown_get(
                self.org_id, **params_copy)
            self.assertEqual(code, 400)
            self.verify_error_code(response, 'OE0216')

    def test_unexpected_filters(self):
        params = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1,
            'region': 'us-east-1',
        }
        code, response = self.client.offer_breakdown_get(self.org_id, **params)
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
                code, response = self.client.offer_breakdown_get(
                    self.org_id, **params_copy)
                self.assertEqual(code, 400)
                self.verify_error_code(response, 'OE0217')

            params_copy[param] = -1
            code, response = self.client.offer_breakdown_get(
                self.org_id, **params_copy)
            self.assertEqual(code, 400)
            self.verify_error_code(response, 'OE0224')

        params = {
            'start_date': self.start_ts,
            'end_date': self.start_ts - 15
        }
        code, response = self.client.offer_breakdown_get(self.org_id, **params)
        self.assertEqual(code, 400)
        self.verify_error_code(response, 'OE0446')

    def test_not_found_cloud_acc(self):
        filters = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1,
            'cloud_account_id': 'impostor'
        }
        code, response = self.client.offer_breakdown_get(
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
        code, response = self.client.offer_breakdown_get(
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
            code, response = self.client.offer_breakdown_get(org_id, **filters)
            self.assertEqual(code, 404)
            self.verify_error_code(response, 'OE0002')

    def test_ch_cancelled_expenses(self):
        self.ri_sp_usage = [
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'date': self.start,
                'resource_id': self.gen_id(),
                'offer_id': self.ri_id,
                'offer_type': 'ri',
                'offer_cost': 10,
                'on_demand_cost': 11,
                'usage': 2,
                'ri_norm_factor': 1,
                'expected_cost': 12,
                'sign': 1
            },
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'date': self.start,
                'resource_id': self.gen_id(),
                'offer_id': self.ri_id,
                'offer_type': 'ri',
                'offer_cost': 10,
                'on_demand_cost': 11,
                'usage': 2,
                'ri_norm_factor': 1,
                'expected_cost': 12,
                'sign': -1
            }
        ]
        params = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1,
            'cloud_account_id': self.cloud_acc1['id']
        }
        code, response = self.client.offer_breakdown_get(self.org_id, **params)
        self.assertEqual(code, 200)
        result = {
            str(self.start_ts): [],
        }
        self.assertDictEqual(response['breakdown'], result)

    def test_date_ranges(self):
        day1 = self.start + timedelta(days=1)
        day2 = self.start + timedelta(days=2)
        end = self.start + timedelta(days=3)
        day1_ts = int(day1.timestamp())
        day2_ts = int(day2.timestamp())
        end_ts = int(end.timestamp())
        self.ri_sp_usage = [
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'date': self.start,
                'offer_id': self.ri_id,
                'resource_id': self.gen_id(),
                'offer_type': 'ri',
                'offer_cost': 1,
                'on_demand_cost': 2,
                'usage': 0.1,
                'ri_norm_factor': 1,
                'expected_cost': 2,
                'sign': 1
            },
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'date': day1,
                'resource_id': self.gen_id(),
                'offer_id': self.ri_id,
                'offer_type': 'ri',
                'offer_cost': 2,
                'on_demand_cost': 4,
                'usage': 0.2,
                'ri_norm_factor': 1,
                'expected_cost': 4,
                'sign': 1
            },
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'date': day1,
                'resource_id': self.gen_id(),
                'offer_id': self.sp_id,
                'offer_type': 'sp',
                'offer_cost': 7,
                'on_demand_cost': 8,
                'usage': 0.3,
                'ri_norm_factor': 1,
                'expected_cost': 7,
                'sign': 1
            },
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'date': day2,
                'resource_id': self.gen_id(),
                'offer_id': self.sp_id,
                'offer_type': 'sp',
                'offer_cost': 9,
                'on_demand_cost': 10,
                'usage': 0.5,
                'ri_norm_factor': 1,
                'expected_cost': 9,
                'sign': 1
            }
        ]
        params = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1,
            'cloud_account_id': self.cloud_acc1['id']
        }
        code, response = self.client.offer_breakdown_get(self.org_id, **params)
        self.assertEqual(code, 200)
        result = {
            str(self.start_ts): [{
                'offer_type': 'ri',
                'cloud_resource_id': self.ri_id,
                'cost': 1,
                'expected_cost': 2,
                'id': self.ri['_id'],
                'payment_option': self.ri['meta']['payment_option'],
                'offering_type': self.ri['meta']['offering_type'],
                'purchase_term': self.ri['meta']['purchase_term'],
                'cloud_account_type': 'aws_cnr',
                'cloud_account_name': self.cloud_acc1['name'],
                'cloud_account_id': self.cloud_acc1['id']
            }],
        }
        self.assertDictEqual(response['breakdown'], result)

        params = {
            'start_date': self.start_ts,
            'end_date': end_ts,
            'cloud_account_id': self.cloud_acc1['id']
        }
        code, response = self.client.offer_breakdown_get(self.org_id, **params)
        self.assertEqual(code, 200)
        result = {
            str(self.start_ts): [{
                'offer_type': 'ri',
                'cloud_resource_id': self.ri_id,
                'cost': 1,
                'expected_cost': 2,
                'id': self.ri['_id'],
                'payment_option': self.ri['meta']['payment_option'],
                'offering_type': self.ri['meta']['offering_type'],
                'purchase_term': self.ri['meta']['purchase_term'],
                'cloud_account_type': 'aws_cnr',
                'cloud_account_name': self.cloud_acc1['name'],
                'cloud_account_id': self.cloud_acc1['id']
            }],
            str(day1_ts): [
                {
                    'offer_type': 'ri',
                    'cloud_resource_id': self.ri_id,
                    'cost': 2,
                    'expected_cost': 4,
                    'id': self.ri['_id'],
                    'payment_option': self.ri['meta']['payment_option'],
                    'offering_type': self.ri['meta']['offering_type'],
                    'purchase_term': self.ri['meta']['purchase_term'],
                    'cloud_account_type': 'aws_cnr',
                    'cloud_account_name': self.cloud_acc1['name'],
                    'cloud_account_id': self.cloud_acc1['id']
                },
                {
                    'offer_type': 'sp',
                    'cloud_resource_id': self.sp_id,
                    'cost': 7,
                    'expected_cost': 7,
                    'id': self.sp['_id'],
                    'payment_option': self.sp['meta']['payment_option'],
                    'offering_type': self.sp['meta']['offering_type'],
                    'purchase_term': self.sp['meta']['purchase_term'],
                    'applied_region': self.sp['meta']['applied_region'],
                    'cloud_account_type': 'aws_cnr',
                    'cloud_account_name': self.cloud_acc1['name'],
                    'cloud_account_id': self.cloud_acc1['id']
                }
            ],
            str(day2_ts): [
                {
                    'offer_type': 'sp',
                    'cloud_resource_id': self.sp_id,
                    'cost': 9,
                    'expected_cost': 9,
                    'id': self.sp['_id'],
                    'payment_option': self.sp['meta']['payment_option'],
                    'offering_type': self.sp['meta']['offering_type'],
                    'purchase_term': self.sp['meta']['purchase_term'],
                    'applied_region': self.sp['meta']['applied_region'],
                    'cloud_account_type': 'aws_cnr',
                    'cloud_account_name': self.cloud_acc1['name'],
                    'cloud_account_id': self.cloud_acc1['id']
                }],
        }
        self.assertListEqual(response['breakdown'][str(self.start_ts)],
                             result[str(self.start_ts)])
        self.assertListEqual(response['breakdown'][str(day2_ts)],
                             result[str(day2_ts)])
        self.assertIn(result[str(day1_ts)][0],
                      response['breakdown'][str(day1_ts)])
        self.assertIn(result[str(day1_ts)][1],
                      response['breakdown'][str(day1_ts)])

    def test_post(self):
        code, response = self.client.post(
            self.client.offer_breakdown_url(self.org_id), body={})
        self.assertEqual(code, 405)

    def test_patch(self):
        code, response = self.client.patch(
            self.client.offer_breakdown_url(self.org_id), body={})
        self.assertEqual(code, 405)

    def test_delete(self):
        code, response = self.client.delete(
            self.client.offer_breakdown_url(self.org_id))
        self.assertEqual(code, 405)
