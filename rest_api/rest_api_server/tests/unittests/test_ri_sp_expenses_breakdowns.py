from datetime import datetime, timedelta
from unittest.mock import patch
from rest_api.rest_api_server.tests.unittests.test_api_base import TestApiBase


class TestRiSpExpensesBreakdownApi(TestApiBase):
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
                # box_usage in seconds
                'box_usage': True,
                'cloud_account_id': self.cloud_acc1['id'],
                'resource_id': self.gen_id(),
                'start_date': date,
                'lineItem/UnblendedCost': 12,
                'pricing/publicOnDemandCost': 12
            },
            {
                # box_usage in hours
                'box_usage': True,
                'cloud_account_id': self.cloud_acc1['id'],
                'resource_id': self.gen_id(),
                'start_date': date,
                'lineItem/UnblendedCost': 13,
                'pricing/publicOnDemandCost': 13
            },
            {
                # not box_usage
                'box_usage': False,
                'cloud_account_id': self.cloud_acc1['id'],
                'resource_id': self.gen_id(),
                'start_date': date,
                'lineItem/UnblendedCost': 14,
                'pricing/publicOnDemandCost': 14
            },
            {
                # box_usage for second account
                'box_usage': True,
                'cloud_account_id': self.cloud_acc2['id'],
                'resource_id': self.gen_id(),
                'start_date': date,
                'lineItem/UnblendedCost': 15,
                'pricing/publicOnDemandCost': 15
            }
        ])

    @staticmethod
    def _empty_stats(cloud_account_id, cloud_account_name):
        return {
            'cloud_account_id': cloud_account_id,
            'cloud_account_type': 'aws_cnr',
            'cloud_account_name': cloud_account_name,
            'total': {
                'cost_without_offer': 0,
                'cost_with_offer': 0,
            },
            'ri': {
                'cost_without_offer': 0,
                'cost_with_offer': 0,
            },
            'sp': {
                'cost_without_offer': 0,
                'cost_with_offer': 0,
            }
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
                'usage': 2,
                'sign': 1
            }
        ]
        params = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1
        }
        code, response = self.client.ri_sp_expenses_breakdown_get(
            self.org_id, **params)
        self.assertEqual(code, 200)
        result = {
            str(self.start_ts): [{
                'cloud_account_id': self.cloud_acc1['id'],
                'cloud_account_type': self.cloud_acc1['type'],
                'cloud_account_name': self.cloud_acc1['name'],
                'total': {
                    'cost_without_offer': 25,
                    'cost_with_offer': 25,
                },
                'ri': {
                    'cost_without_offer': 11,
                    'cost_with_offer': 10
                },
                'sp': {
                    'cost_without_offer': 0,
                    'cost_with_offer': 0
                }
            }, {
                'cloud_account_id': self.cloud_acc2['id'],
                'cloud_account_type': self.cloud_acc2['type'],
                'cloud_account_name': self.cloud_acc2['name'],
                'total': {
                    'cost_without_offer': 15,
                    'cost_with_offer': 15,
                },
                'ri': {
                    'cost_without_offer': 0,
                    'cost_with_offer': 0
                },
                'sp': {
                    'cost_without_offer': 0,
                    'cost_with_offer': 0
                }
            }],
        }
        self.assertDictEqual(response['breakdown'], result)

    def test_with_cloud_account_id(self):
        self.ri_sp_usage = [
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'date': datetime.fromtimestamp(self.start_ts),
                'resource_id': self.gen_id(),
                'offer_id': self.gen_id(),
                'offer_type': 'ri',
                'offer_cost': 10,
                'on_demand_cost': 11,
                'usage': 2,
                'sign': 1
            }
        ]
        params = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1,
            'cloud_account_id': self.cloud_acc1['id']
        }
        code, response = self.client.ri_sp_expenses_breakdown_get(
            self.org_id, **params)
        self.assertEqual(code, 200)
        result = {
            str(self.start_ts): [{
                'cloud_account_id': self.cloud_acc1['id'],
                'cloud_account_type': self.cloud_acc1['type'],
                'cloud_account_name': self.cloud_acc1['name'],
                'total': {
                        'cost_without_offer': 25,
                        'cost_with_offer': 25,
                    },
                'ri': {
                    'cost_without_offer': 11,
                    'cost_with_offer': 10
                },
                'sp': {
                    'cost_without_offer': 0,
                    'cost_with_offer': 0
                }
            }],
        }
        self.assertDictEqual(response['breakdown'], result)

    def test_with_several_cloud_account_id(self):
        self.ri_sp_usage = [
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'date': datetime.fromtimestamp(self.start_ts),
                'resource_id': self.gen_id(),
                'offer_id': self.gen_id(),
                'offer_type': 'ri',
                'offer_cost': 10,
                'on_demand_cost': 11,
                'usage': 2,
                'sign': 1
            }
        ]
        params = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1,
            'cloud_account_id': [self.cloud_acc1['id'], self.cloud_acc2['id']]
        }
        code, response = self.client.ri_sp_expenses_breakdown_get(
            self.org_id, **params)
        self.assertEqual(code, 200)
        result = {
            str(self.start_ts): [{
                'cloud_account_id': self.cloud_acc1['id'],
                'cloud_account_type': self.cloud_acc1['type'],
                'cloud_account_name': self.cloud_acc1['name'],
                'total': {
                        'cost_without_offer': 25,
                        'cost_with_offer': 25,
                    },
                'ri': {
                    'cost_without_offer': 11,
                    'cost_with_offer': 10
                },
                'sp': {
                    'cost_without_offer': 0,
                    'cost_with_offer': 0
                }
            }, {
                'cloud_account_id': self.cloud_acc2['id'],
                'cloud_account_type': self.cloud_acc2['type'],
                'cloud_account_name': self.cloud_acc2['name'],
                'total': {
                    'cost_without_offer': 15,
                    'cost_with_offer': 15,
                },
                'ri': {
                    'cost_without_offer': 0,
                    'cost_with_offer': 0
                },
                'sp': {
                    'cost_without_offer': 0,
                    'cost_with_offer': 0
                }
            }],
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
                'start_date': self.start
            })

        # not aws account is not returned
        params = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1,
            'cloud_account_id': cloud_acc['id']
        }
        code, response = self.client.ri_sp_usage_breakdown_get(
            self.org_id, **params)
        self.assertEqual(code, 200)
        self.assertEqual(response['breakdown'], {})

        # aws accounts are returned, not aws accounts are not returned
        params = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1
        }
        code, response = self.client.ri_sp_usage_breakdown_get(
            self.org_id, **params)
        self.assertEqual(code, 200)
        cloud_accounts_ids = [x['cloud_account_id']
                              for x in response['breakdown'][str(self.start_ts)]]
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
        code, response = self.client.ri_sp_expenses_breakdown_get(
            self.org_id, **params)
        self.assertEqual(code, 200)
        result = {
            str(self.start_ts): [self._empty_stats(
                cloud_acc['id'], cloud_acc['name'])]
        }
        self.assertEqual(response['breakdown'], result)

        params = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1
        }
        code, response = self.client.ri_sp_expenses_breakdown_get(
            self.org_id, **params)
        self.assertEqual(code, 200)
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
            code, response = self.client.ri_sp_expenses_breakdown_get(
                self.org_id, **params_copy)
            self.assertEqual(code, 400)
            self.verify_error_code(response, 'OE0216')

    def test_unexpected_filters(self):
        params = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1,
            'region': 'us-east-1',
        }
        code, response = self.client.ri_sp_expenses_breakdown_get(
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
                code, response = self.client.ri_sp_expenses_breakdown_get(
                    self.org_id, **params_copy)
                self.assertEqual(code, 400)
                self.verify_error_code(response, 'OE0217')

            params_copy[param] = -1
            code, response = self.client.ri_sp_expenses_breakdown_get(
                self.org_id, **params_copy)
            self.assertEqual(code, 400)
            self.verify_error_code(response, 'OE0224')

        params = {
            'start_date': self.start_ts,
            'end_date': self.start_ts - 15
        }
        code, response = self.client.ri_sp_expenses_breakdown_get(
            self.org_id, **params)
        self.assertEqual(code, 400)
        self.verify_error_code(response, 'OE0446')

    def test_not_found_cloud_acc(self):
        filters = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1,
            'cloud_account_id': 'impostor'
        }
        code, response = self.client.ri_sp_expenses_breakdown_get(
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
        code, response = self.client.ri_sp_expenses_breakdown_get(
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
            code, response = self.client.ri_sp_expenses_breakdown_get(
                org_id, **filters)
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
                'sign': -1
            }
        ]
        params = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1,
            'cloud_account_id': self.cloud_acc1['id']
        }
        code, response = self.client.ri_sp_expenses_breakdown_get(
            self.org_id, **params)
        self.assertEqual(code, 200)
        result = {
            str(self.start_ts): [{
                'cloud_account_id': self.cloud_acc1['id'],
                'cloud_account_type': self.cloud_acc1['type'],
                'cloud_account_name': self.cloud_acc1['name'],
                'total': {
                        'cost_without_offer': 25,
                        'cost_with_offer': 25,
                    },
                'ri': {
                    'cost_without_offer': 0,
                    'cost_with_offer': 0
                },
                'sp': {
                    'cost_without_offer': 0,
                    'cost_with_offer': 0
                }
            }],
        }
        self.assertDictEqual(response['breakdown'], result)

    def test_ri_sp_usage(self):
        self.ri_sp_usage = [
            # ri
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'date': self.start,
                'resource_id': self.gen_id(),
                'offer_id': self.gen_id(),
                'offer_type': 'ri',
                'offer_cost': 1,
                'on_demand_cost': 2,
                'usage': 1,
                'sign': 1
            },
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'date': self.start,
                'resource_id': self.gen_id(),
                'offer_id': self.gen_id(),
                'offer_type': 'ri',
                'offer_cost': 4,
                'on_demand_cost': 5,
                'usage': 5,
                'sign': 1
            },
            # sp
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'date': self.start,
                'resource_id': self.gen_id(),
                'offer_id': self.gen_id(),
                'offer_type': 'sp',
                'offer_cost': 10,
                'on_demand_cost': 11,
                'usage': 1.5,
                'sign': 1
            },
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'date': self.start,
                'resource_id': self.gen_id(),
                'offer_id': self.gen_id(),
                'offer_type': 'sp',
                'offer_cost': 6,
                'on_demand_cost': 7,
                'usage': 0.5,
                'sign': 1
            }
        ]
        params = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1,
            'cloud_account_id': self.cloud_acc1['id']
        }
        code, response = self.client.ri_sp_expenses_breakdown_get(
            self.org_id, **params)
        self.assertEqual(code, 200)
        result = {
            str(self.start_ts): [{
                'cloud_account_id': self.cloud_acc1['id'],
                'cloud_account_type': self.cloud_acc1['type'],
                'cloud_account_name': self.cloud_acc1['name'],
                'total': {
                    'cost_without_offer': 25,
                    'cost_with_offer': 25,
                },
                'ri': {
                    'cost_without_offer': 7,  # 2 + 5
                    'cost_with_offer': 5  # 1 + 4
                },
                'sp': {
                    'cost_without_offer': 18,  # 7 + 11
                    'cost_with_offer': 16  # 6 + 10
                }
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
        self.ri_sp_usage = [
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'date': self.start,
                'resource_id': self.gen_id(),
                'offer_id': self.gen_id(),
                'offer_type': 'ri',
                'offer_cost': 1,
                'on_demand_cost': 2,
                'usage': 1,
                'sign': 1
            },
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'date': day1,
                'resource_id': self.gen_id(),
                'offer_id': self.gen_id(),
                'offer_type': 'ri',
                'offer_cost': 3,
                'on_demand_cost': 4,
                'usage': 5,
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
                'usage': 1.5,
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
                'sign': 1
            }
        ]
        self.insert_mongo_raw_expenses(day1)
        self.insert_mongo_raw_expenses(day2)
        params = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1,
            'cloud_account_id': self.cloud_acc1['id']
        }
        code, response = self.client.ri_sp_expenses_breakdown_get(
            self.org_id, **params)
        self.assertEqual(code, 200)
        result = {
            str(self.start_ts): [{
                'cloud_account_id': self.cloud_acc1['id'],
                'cloud_account_type': self.cloud_acc1['type'],
                'cloud_account_name': self.cloud_acc1['name'],
                'total': {
                    'cost_without_offer': 25,
                    'cost_with_offer': 25,
                },
                'ri': {
                    'cost_without_offer': 2,
                    'cost_with_offer': 1
                },
                'sp': {
                    'cost_without_offer': 0,
                    'cost_with_offer': 0
                }
            }],
        }
        self.assertDictEqual(response['breakdown'], result)

        params = {
            'start_date': self.start_ts,
            'end_date': end_ts,
            'cloud_account_id': self.cloud_acc1['id']
        }
        code, response = self.client.ri_sp_expenses_breakdown_get(
            self.org_id, **params)
        self.assertEqual(code, 200)
        result = {
            str(self.start_ts): [
                {
                    'cloud_account_id': self.cloud_acc1['id'],
                    'cloud_account_type': self.cloud_acc1['type'],
                    'cloud_account_name': self.cloud_acc1['name'],
                    'total': {
                        'cost_without_offer': 25,
                        'cost_with_offer': 25,
                    },
                    'ri': {
                        'cost_without_offer': 2,
                        'cost_with_offer': 1
                    },
                    'sp': {
                        'cost_without_offer': 0,
                        'cost_with_offer': 0
                    }
                }],
            str(day1_ts): [
                {
                    'cloud_account_id': self.cloud_acc1['id'],
                    'cloud_account_type': self.cloud_acc1['type'],
                    'cloud_account_name': self.cloud_acc1['name'],
                    'total': {
                        'cost_without_offer': 25,
                        'cost_with_offer': 25,
                    },
                    'ri': {
                        'cost_without_offer': 4,
                        'cost_with_offer': 3
                    },
                    'sp': {
                        'cost_without_offer': 8,
                        'cost_with_offer': 7
                    }
                }],
            str(day2_ts): [
                {
                    'cloud_account_id': self.cloud_acc1['id'],
                    'cloud_account_type': self.cloud_acc1['type'],
                    'cloud_account_name': self.cloud_acc1['name'],
                    'total': {
                        'cost_without_offer': 25,
                        'cost_with_offer': 25,
                    },
                    'ri': {
                        'cost_without_offer': 0,
                        'cost_with_offer': 0
                    },
                    'sp': {
                        'cost_without_offer': 10,
                        'cost_with_offer': 9
                    }
                }],
        }
        self.assertDictEqual(response['breakdown'], result)

    def test_date_without_box_usage(self):
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
                'offer_cost': 21,
                'on_demand_cost': 22,
                'usage': 1,
                'sign': 1
            }
        ]
        params = {
            'start_date': self.start_ts,
            'end_date': end_ts,
            'cloud_account_id': self.cloud_acc1['id']
        }
        code, response = self.client.ri_sp_expenses_breakdown_get(
            self.org_id, **params)
        self.assertEqual(code, 200)
        result = {
            str(self.start_ts): [
                {
                    'cloud_account_id': self.cloud_acc1['id'],
                    'cloud_account_type': self.cloud_acc1['type'],
                    'cloud_account_name': self.cloud_acc1['name'],
                    'total': {
                        'cost_without_offer': 25,
                        'cost_with_offer': 25,
                    },
                    'ri': {
                        'cost_without_offer': 22,
                        'cost_with_offer': 21,
                    },
                    'sp': {
                        'cost_without_offer': 0,
                        'cost_with_offer': 0,
                    }
                }
            ],
            str(day1_ts): [self._empty_stats(
                self.cloud_acc1['id'], self.cloud_acc1['name'])],
            str(day2_ts): [self._empty_stats(
                self.cloud_acc1['id'], self.cloud_acc1['name'])],
        }
        self.assertDictEqual(response['breakdown'], result)

    def test_total_cost_with_offer(self):
        self.ri_sp_usage = [
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'date': self.start,
                'resource_id': self.gen_id(),
                'offer_id': self.gen_id(),
                'offer_type': 'ri',
                'offer_cost': 21,
                'on_demand_cost': 22,
                'usage': 1,
                'sign': 1
            }
        ]
        self.raw_expenses.insert_many([{
            'box_usage': True,
            'cloud_account_id': self.cloud_acc1['id'],
            'resource_id': self.gen_id(),
            'start_date': self.start,
            'lineItem/UnblendedCost': 1.5,
            'pricing/publicOnDemandCost': 3
        }, {
            'box_usage': True,
            'cloud_account_id': self.cloud_acc1['id'],
            'resource_id': self.gen_id(),
            'start_date': self.start,
            'lineItem/LineItemType': 'SavingsPlanCoveredUsage',
            'lineItem/UnblendedCost': 111,
            'savingsPlan/SavingsPlanEffectiveCost': 2,
            'pricing/publicOnDemandCost': 5
        }, {
                'box_usage': True,
                'cloud_account_id': self.cloud_acc1['id'],
                'resource_id': self.gen_id(),
                'start_date': self.start,
                'lineItem/LineItemType': 'SavingsPlanNegation',
                'lineItem/UnblendedCost': -111,
                'savingsPlan/SavingsPlanEffectiveCost': 0,
                'pricing/publicOnDemandCost': 0
        }, {
            'box_usage': True,
            'cloud_account_id': self.cloud_acc1['id'],
            'resource_id': self.gen_id(),
            'start_date': self.start,
            'lineItem/UnblendedCost': 0,
            'reservation/EffectiveCost': 5,
            'pricing/publicOnDemandCost': 7
        }])
        params = {
            'start_date': self.start_ts,
            'end_date': self.start_ts + 1,
            'cloud_account_id': self.cloud_acc1['id']
        }
        code, response = self.client.ri_sp_expenses_breakdown_get(
            self.org_id, **params)
        self.assertEqual(code, 200)
        result = {
            str(self.start_ts): [
                {
                    'cloud_account_id': self.cloud_acc1['id'],
                    'cloud_account_type': self.cloud_acc1['type'],
                    'cloud_account_name': self.cloud_acc1['name'],
                    'total': {
                        'cost_without_offer': 40,  # 25 + 3 + 5 + 7
                        'cost_with_offer': 33.5,  # 25 + 1.5 + 2 + 5
                    },
                    'ri': {
                        'cost_without_offer': 22,
                        'cost_with_offer': 21,
                    },
                    'sp': {
                        'cost_without_offer': 0,
                        'cost_with_offer': 0,
                    }
                }
            ],
        }
        self.assertDictEqual(response['breakdown'], result)

    def test_post(self):
        code, response = self.client.post(
            self.client.ri_sp_expenses_breakdown_url(self.org_id), body={})
        self.assertEqual(code, 405)

    def test_patch(self):
        code, response = self.client.patch(
            self.client.ri_sp_expenses_breakdown_url(self.org_id), body={})
        self.assertEqual(code, 405)

    def test_delete(self):
        code, response = self.client.delete(
            self.client.ri_sp_expenses_breakdown_url(self.org_id))
        self.assertEqual(code, 405)
