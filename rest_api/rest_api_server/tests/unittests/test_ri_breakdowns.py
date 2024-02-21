from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from rest_api.rest_api_server.tests.unittests.test_api_base import TestApiBase


class TestRiBreakdownApi(TestApiBase):
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
        self.insert_mongo_raw_expenses()

    def insert_mongo_raw_expenses(self, date=None):
        if not date:
            date = self.start
        self.raw_expenses.insert_many([
            {
                # LineItemType = Usage
                'box_usage': True,
                'cloud_account_id': self.cloud_acc1['id'],
                'start_date': date,
                'lineItem/LineItemType': 'Usage',
                'product/instanceType': 't2.large',
            },
            {
                # LineItemType = DiscountedUsage
                'box_usage': True,
                'cloud_account_id': self.cloud_acc1['id'],
                'start_date': date,
                'lineItem/LineItemType': 'DiscountedUsage',
                'product/instanceType': 't2.large',
            },
            {
                # not box_usage
                'box_usage': False,
                'cloud_account_id': self.cloud_acc1['id'],
                'start_date': date,
                'lineItem/LineItemType': 'DiscountedUsage',
            },
            {
                # second account
                'box_usage': True,
                'cloud_account_id': self.cloud_acc2['id'],
                'start_date': date,
                'lineItem/LineItemType': 'DiscountedUsage',
                'product/instanceType': 't2.large',
            }
        ])

    @staticmethod
    def _empty_stats(cloud_account_id, cloud_account_name):
        return {
            'cloud_account_id': cloud_account_id,
            'cloud_account_type': 'aws_cnr',
            'cloud_account_name': cloud_account_name,
            'total_usage_hrs': 0,
            'cost_with_offer': 0,
            'cost_without_offer': 0,
            'ri_usage_hrs': 0,
            'ri_overprovision_hrs': {
                't2.large': 0
            },
            'ri_overprovision': 0,
            'ri_cost_with_offer': 0,
            'ri_cost_without_offer': 0
        }

    def test_without_cloud_account_id(self):
        self.ri_sp_usage = [
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'date': self.start,
                'resource_id': self.gen_id(),
                'offer_id': self.gen_id(),
                'offer_type': 'ri',
                'offer_cost': 10,
                'on_demand_cost': 11,
                'usage': 0.3,
                'ri_norm_factor': 2,
                'expected_cost': 10,
                'sign': 1
            }
        ]
        params = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1
        }
        code, response = self.client.ri_breakdown_get(
            self.org_id, **params)
        self.assertEqual(code, 200)
        result = {
            str(self.start_ts): [{
                'cloud_account_id': self.cloud_acc1['id'],
                'total_usage_hrs': 0.3,
                'cost_without_offer': 11,
                'cost_with_offer': 10,
                'ri_usage_hrs': 0.3,
                'ri_overprovision_hrs': {
                    't2.large': 0
                },
                'ri_overprovision': 0,
                'cloud_account_type': self.cloud_acc1['type'],
                'cloud_account_name': self.cloud_acc1['name'],
                'ri_cost_with_offer': 10,
                'ri_cost_without_offer': 11
            }, self._empty_stats(
                self.cloud_acc2['id'], self.cloud_acc2['name'])],
        }
        self.assertDictEqual(response['breakdown'], result)

    def test_with_cloud_account_id(self):
        self.ri_sp_usage = [
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'date': self.start,
                'resource_id': self.gen_id(),
                'offer_id': self.gen_id(),
                'offer_type': 'ri',
                'offer_cost': 10,
                'on_demand_cost': 11,
                'usage': 0.3,
                'ri_norm_factor': 2,
                'expected_cost': 10,
                'sign': 1
            }
        ]
        params = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1,
            'cloud_account_id': self.cloud_acc1['id']
        }
        code, response = self.client.ri_breakdown_get(self.org_id, **params)
        self.assertEqual(code, 200)
        result = {
            str(self.start_ts): [{
                'cloud_account_id': self.cloud_acc1['id'],
                'cloud_account_type': self.cloud_acc1['type'],
                'cloud_account_name': self.cloud_acc1['name'],
                'total_usage_hrs': 0.3,
                'cost_without_offer': 11,
                'cost_with_offer': 10,
                'ri_usage_hrs': 0.3,
                'ri_overprovision': 0,
                'ri_overprovision_hrs': {
                    't2.large': 0
                },
                'ri_cost_without_offer': 11,
                'ri_cost_with_offer': 10
            }],
        }
        self.assertDictEqual(response['breakdown'], result)

    def test_with_several_cloud_account_id(self):
        self.ri_sp_usage = [
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'date': self.start,
                'resource_id': self.gen_id(),
                'offer_id': self.gen_id(),
                'offer_type': 'ri',
                'offer_cost': 10,
                'on_demand_cost': 11,
                'usage': 0.2,
                'ri_norm_factor': 2,
                'expected_cost': 11,
                'sign': 1
            }
        ]
        params = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1,
            'cloud_account_id': [self.cloud_acc1['id'], self.cloud_acc2['id']]
        }
        code, response = self.client.ri_breakdown_get(self.org_id, **params)
        self.assertEqual(code, 200)
        result = {
            str(self.start_ts): [{
                'cloud_account_id': self.cloud_acc1['id'],
                'total_usage_hrs': 0.2,
                'cost_without_offer': 11,
                'cost_with_offer': 10,
                'ri_usage_hrs': 0.2,
                'ri_overprovision_hrs': {
                    't2.large': 0.01  # (11 - 10) / (10 / (0.2 * 2)) / 4
                },
                'ri_overprovision': 1,  # 11 - 10
                'cloud_account_type': self.cloud_acc1['type'],
                'cloud_account_name': self.cloud_acc1['name'],
                'ri_cost_without_offer': 11,
                'ri_cost_with_offer': 10
            }, self._empty_stats(
                self.cloud_acc2['id'], self.cloud_acc2['name'])],
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
        self.raw_expenses.insert_one({
                'box_usage': True,
                'cloud_account_id': cloud_acc['id'],
                'resource_id': self.gen_id(),
                'start_date': self.start,
                'lineItem/LineItemType': 'DiscountedUsage'
            })

        # not aws account is not returned
        params = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1,
            'cloud_account_id': cloud_acc['id']
        }
        code, response = self.client.ri_breakdown_get(self.org_id, **params)
        self.assertEqual(code, 200)
        self.assertEqual(response['breakdown'], {})

        # aws accounts are returned, not aws accounts are not returned
        params = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1
        }
        code, response = self.client.ri_breakdown_get(self.org_id, **params)
        self.assertEqual(code, 200)
        cloud_accounts_ids = [x['cloud_account_id']
                              for x in response['breakdown'][
                                  str(self.start_ts)]]
        self.assertNotIn(cloud_acc['id'], cloud_accounts_ids)
        self.assertIn(self.cloud_acc1['id'], cloud_accounts_ids)
        self.assertIn(self.cloud_acc2['id'], cloud_accounts_ids)

    def test_aws_without_box_usage_expenses(self):
        cloud_acc_new = {
            'name': 'cloud_acc_new',
            'type': 'aws_cnr',
            'config': {
                'access_key_id': 'key',
                'secret_access_key': 'secret',
                'config_scheme': 'create_report'
            }
        }
        _, cloud_acc = self.create_cloud_account(
            self.org_id, cloud_acc_new, auth_user_id=self.auth_user_id_1)
        self.raw_expenses.insert_one({
                'box_usage': False,
                'cloud_account_id': self.cloud_acc1['id'],
                'resource_id': self.gen_id(),
                'start_date': self.start,
                'lineItem/UnblendedCost': 9.5
            })

        params = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1,
            'cloud_account_id': [cloud_acc['id']]
        }
        code, response = self.client.ri_breakdown_get(self.org_id, **params)
        self.assertEqual(code, 200)
        stats = self._empty_stats(
                cloud_acc['id'], cloud_acc['name'])
        stats['ri_overprovision_hrs'] = {}
        result = {
            str(self.start_ts): [stats]
        }
        self.assertEqual(response['breakdown'], result)

        params = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1
        }
        code, response = self.client.ri_breakdown_get(self.org_id, **params)
        self.assertEqual(code, 200)
        self.assertEqual(len(response['breakdown']), 1)
        self.assertIn(self._empty_stats(cloud_acc['id'], cloud_acc['name']),
                      response['breakdown'][str(self.start_ts)])

    def test_required_filters(self):
        params = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1
        }
        for param in ['start_date', 'end_date']:
            params_copy = params.copy()
            params_copy.pop(param)
            code, response = self.client.ri_breakdown_get(
                self.org_id, **params_copy)
            self.assertEqual(code, 400)
            self.verify_error_code(response, 'OE0216')

    def test_unexpected_filters(self):
        params = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1,
            'region': 'us-east-1',
        }
        code, response = self.client.ri_breakdown_get(self.org_id, **params)
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
                code, response = self.client.ri_breakdown_get(
                    self.org_id, **params_copy)
                self.assertEqual(code, 400)
                self.verify_error_code(response, 'OE0217')

            params_copy[param] = -1
            code, response = self.client.ri_breakdown_get(
                self.org_id, **params_copy)
            self.assertEqual(code, 400)
            self.verify_error_code(response, 'OE0224')

        params = {
            'start_date': self.start_ts,
            'end_date': self.start_ts - 15
        }
        code, response = self.client.ri_breakdown_get(self.org_id, **params)
        self.assertEqual(code, 400)
        self.verify_error_code(response, 'OE0446')

    def test_not_found_cloud_acc(self):
        filters = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1,
            'cloud_account_id': 'impostor'
        }
        code, response = self.client.ri_breakdown_get(self.org_id, **filters)
        self.assertEqual(code, 404)
        self.verify_error_code(response, 'OE0470')

    def test_org_without_cloud_accs(self):
        _, organization2 = self.client.organization_create(
            {'name': "organization2"})
        filters = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1
        }
        code, response = self.client.ri_breakdown_get(
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
            code, response = self.client.ri_breakdown_get(org_id, **filters)
            self.assertEqual(code, 404)
            self.verify_error_code(response, 'OE0002')

    def test_ch_cancelled_expenses(self):
        self.ri_sp_usage = [
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'date': self.start,
                'resource_id': self.gen_id(),
                'offer_id': self.gen_id(),
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
                'offer_id': self.gen_id(),
                'offer_type': 'ri',
                'offer_cost': 10,
                'on_demand_cost': 11,
                'usage': 2,
                'ri_norm_factor': 1,
                'expected_cost': 12,
                'sign': -1
            }
        ]
        self.uncovered_usage = [
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'date': self.start,
                'resource_id': self.gen_id(),
                'usage': 1000,
                'cost': 1000,
                'sign': 1
            }
        ]
        params = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1,
            'cloud_account_id': self.cloud_acc1['id']
        }
        code, response = self.client.ri_breakdown_get(self.org_id, **params)
        self.assertEqual(code, 200)
        result = {
            str(self.start_ts): [{
                'cloud_account_id': self.cloud_acc1['id'],
                'cloud_account_type': self.cloud_acc1['type'],
                'cloud_account_name': self.cloud_acc1['name'],
                'total_usage_hrs': 1000,
                'cost_without_offer': 1000,
                'cost_with_offer': 1000,
                'ri_usage_hrs': 0,
                'ri_overprovision': 0,
                'ri_overprovision_hrs': {
                    't2.large': 0
                },
                'ri_cost_with_offer': 0,
                'ri_cost_without_offer': 0
            }],
        }
        self.assertDictEqual(response['breakdown'], result)

    def test_date_ranges(self):
        day1 = self.start + timedelta(days=1)
        day2 = self.start + timedelta(days=2)
        end = self.start + timedelta(days=3)
        day1_ts = int(day1.timestamp())
        day2_ts = int(day2.timestamp())
        end_ts = int(end.timestamp())
        self.uncovered_usage = [
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'date': self.start,
                'resource_id': self.gen_id(),
                'usage': 1000,
                'cost': 1000,
                'sign': 1
            }
        ]
        self.ri_sp_usage = [
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'date': self.start,
                'resource_id': self.gen_id(),
                'offer_id': self.gen_id(),
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
                'offer_id': self.gen_id(),
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
                'offer_id': self.gen_id(),
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
                'offer_id': self.gen_id(),
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
        code, response = self.client.ri_breakdown_get(self.org_id, **params)
        self.assertEqual(code, 200)
        result = {
            str(self.start_ts): [{
                'cloud_account_id': self.cloud_acc1['id'],
                'cloud_account_type': self.cloud_acc1['type'],
                'cloud_account_name': self.cloud_acc1['name'],
                'ri_cost_without_offer': 2.0,
                'ri_cost_with_offer': 1.0,
                'ri_overprovision': 1,  # 2 - 1
                'ri_overprovision_hrs': {
                    't2.large': 0.025  # (2 - 1) / (1 / 0.1) / 4
                },
                'ri_usage_hrs': 0.1,
                'cost_without_offer': 1002,  # 1000 + 2
                'cost_with_offer': 1001,  # 1000 + 1
                'total_usage_hrs': 1000.1  # 1000 + 0.1
            }],
        }
        self.assertDictEqual(response['breakdown'], result)

        params = {
            'start_date': self.start_ts,
            'end_date': end_ts,
            'cloud_account_id': self.cloud_acc1['id']
        }
        code, response = self.client.ri_breakdown_get(self.org_id, **params)
        self.assertEqual(code, 200)
        result = {
            str(self.start_ts): [{
                    'cloud_account_id': self.cloud_acc1['id'],
                    'cloud_account_type': self.cloud_acc1['type'],
                    'cloud_account_name': self.cloud_acc1['name'],
                    'ri_cost_without_offer': 2.0,
                    'ri_cost_with_offer': 1.0,
                    'ri_overprovision': 1,  # 2 - 1
                    'ri_overprovision_hrs': {
                        't2.large': 0.025  # (2 - 1) / (1 / 0.1) / 4
                    },
                    'ri_usage_hrs': 0.1,
                    'cost_without_offer': 1002,  # 1000 + 2
                    'cost_with_offer': 1001,  # 1000 + 1
                    'total_usage_hrs': 1000.1  # 1000 + 0.1
            }],
            str(day1_ts): [
                {
                    'cloud_account_id': self.cloud_acc1['id'],
                    'cloud_account_type': self.cloud_acc1['type'],
                    'cloud_account_name': self.cloud_acc1['name'],
                    'ri_cost_without_offer': 4,
                    'ri_cost_with_offer': 2,
                    'ri_overprovision': 2,  # 4 - 3
                    'ri_overprovision_hrs': {
                        't2.large': 0.05  # (4 - 2) / (2 / 0.2) / 4
                    },
                    'ri_usage_hrs': 0.2,
                    'total_usage_hrs': 0.5,  # 0.3 + 0.2
                    'cost_without_offer': 12,  # 8 + 4
                    'cost_with_offer': 9,  # 7 + 2
                }],
            str(day2_ts): [
                {
                    'cloud_account_id': self.cloud_acc1['id'],
                    'cloud_account_type': self.cloud_acc1['type'],
                    'cloud_account_name': self.cloud_acc1['name'],
                    'ri_cost_without_offer': 0,
                    'ri_cost_with_offer': 0,
                    'ri_overprovision': 0,
                    'ri_overprovision_hrs': {
                        't2.large': 0
                    },
                    'ri_usage_hrs': 0,
                    'total_usage_hrs': 0.5,
                    'cost_without_offer': 10,
                    'cost_with_offer': 9,
                }],
        }
        self.assertDictEqual(response['breakdown'], result)

    def test_date_expected(self):
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
                'resource_id': self.gen_id(),
                'offer_id': self.gen_id(),
                'offer_type': 'ri',
                'offer_cost': 10,
                'on_demand_cost': 11,
                'usage': 2,
                'ri_norm_factor': 2,
                'expected_cost': 11,
                'sign': 1
            }
        ]
        params = {
            'start_date': self.start_ts,
            'end_date': end_ts,
            'cloud_account_id': self.cloud_acc1['id']
        }
        code, response = self.client.ri_breakdown_get(self.org_id, **params)
        self.assertEqual(code, 200)
        result = {
            str(self.start_ts): [{
                'cloud_account_id': self.cloud_acc1['id'],
                'total_usage_hrs': 2,
                'cost_without_offer': 11,
                'cost_with_offer': 10,
                'ri_usage_hrs': 2,
                'ri_overprovision_hrs': {
                    't2.large': 0.1  # (11 - 10) / (10 / 2 * 2) / 4
                },
                'ri_overprovision': 1,  # 11 - 10
                'cloud_account_type': self.cloud_acc1['type'],
                'cloud_account_name': self.cloud_acc1['name'],
                'ri_cost_without_offer': 11,
                'ri_cost_with_offer': 10
            }],
            str(day1_ts): [self._empty_stats(
                self.cloud_acc1['id'], self.cloud_acc1['name'])],
            str(day2_ts): [self._empty_stats(
                self.cloud_acc1['id'], self.cloud_acc1['name'])],
        }
        self.assertDictEqual(response['breakdown'], result)

    def test_total_costs(self):
        self.ri_sp_usage = [
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'date': self.start,
                'resource_id': self.gen_id(),
                'offer_id': 'offer',
                'offer_type': 'ri',
                'offer_cost': 21,
                'on_demand_cost': 22,
                'usage': 1,
                'ri_norm_factor': 1,
                'expected_cost': 56,
                'sign': 1
            },
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'date': self.start,
                'resource_id': self.gen_id(),
                'offer_id': 'offer',
                'offer_type': 'ri',
                'offer_cost': 21,
                'on_demand_cost': 22,
                'usage': 1,
                'ri_norm_factor': 2,
                'expected_cost': 56,
                'sign': 1
            }
        ]
        self.uncovered_usage = [
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'date': self.start,
                'resource_id': self.gen_id(),
                'cost': 1000,
                'usage': 999,
                'sign': 1
            },
            {
                'cloud_account_id': self.cloud_acc2['id'],
                'date': self.start,
                'resource_id': self.gen_id(),
                'cost': 2000,
                'usage': 1999,
                'sign': 1
            },
            {
                'cloud_account_id': self.cloud_acc2['id'],
                'date': self.start,
                'resource_id': self.gen_id(),
                'cost': 2000,
                'usage': 1999,
                'sign': -1
            }
        ]
        params = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1
        }
        code, response = self.client.ri_breakdown_get(self.org_id, **params)
        self.assertEqual(code, 200)
        result = {
            str(self.start_ts): [
                {
                    'cloud_account_id': self.cloud_acc1['id'],
                    'cloud_account_type': self.cloud_acc1['type'],
                    'cloud_account_name': self.cloud_acc1['name'],
                    'ri_cost_without_offer': 44,  # 22 + 22
                    'ri_cost_with_offer': 42,  # 21 + 21
                    'ri_overprovision_hrs': {
                        # (56 - 21 - 21) / ( 42 / (1 + 1 * 2)) / 4
                        't2.large': 0.25
                    },
                    'ri_usage_hrs': 2,  # 1 + 1
                    'ri_overprovision': 14,  # 56 - 21 - 21
                    'total_usage_hrs': 1001,  # 999 + 2
                    'cost_without_offer': 1044,  # 1000 + 44
                    'cost_with_offer': 1042  # 1000 + 42
                },
                self._empty_stats(self.cloud_acc2['id'],
                                  self.cloud_acc2['name'])
            ],
        }
        self.assertDictEqual(response['breakdown'], result)

    def test_post(self):
        code, response = self.client.post(
            self.client.ri_breakdown_url(self.org_id), body={})
        self.assertEqual(code, 405)

    def test_patch(self):
        code, response = self.client.patch(
            self.client.ri_breakdown_url(self.org_id), body={})
        self.assertEqual(code, 405)

    def test_delete(self):
        code, response = self.client.delete(
            self.client.ri_breakdown_url(self.org_id))
        self.assertEqual(code, 405)
