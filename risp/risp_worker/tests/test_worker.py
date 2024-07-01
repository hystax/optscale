import uuid
import unittest
from unittest.mock import patch, MagicMock, PropertyMock
from datetime import datetime, timezone
from risp.risp_worker.worker import RISPWorker


class TestRISPWorker(unittest.TestCase):
    def setUp(self):
        self.conn = MagicMock()
        self.config_cl = MagicMock()
        self.worker = RISPWorker(self.conn, self.config_cl)
        self.task_body = {'cloud_account_id': 'cloud_account_id'}
        self.rabbit_message = MagicMock()
        self._ri_raw_expenses = []
        self._sp_raw_expenses = []
        self._uncovered_raw_expenses = []
        self._ri_exp_cost_raw_expenses = []
        self._sp_exp_cost_raw_expenses = []
        self.mock_common()
        self.mock_ri_sp_ch_expenses()
        self.mock_uncovered_ch_expenses()
        self.mock_mongo_raw()
        self.mock_risp_tasks()

    def tearDown(self):
        patch.stopall()
        super().tearDown()

    def mock_common(self):
        patch('risp.risp_worker.worker.RISPWorker.clickhouse_client',
              new_callable=PropertyMock).start()
        self.worker.get_ri_sp_usage_expenses = MagicMock()
        self.worker.get_uncovered_usage_expenses = MagicMock()
        self.worker.insert_clickhouse_expenses = MagicMock()

        patch('risp.risp_worker.worker.RISPWorker.mongo_client',
              new_callable=PropertyMock).start()
        self.worker.get_offers_expenses_by_type = MagicMock()
        self.worker.get_resources_ids_map = MagicMock()
        self.worker.get_uncovered_raw_expenses = MagicMock()
        self.worker._ri_expected_cost_per_day = MagicMock()
        self.worker._sp_expected_cost_per_day = MagicMock()

        patch('risp.risp_worker.worker.RISPWorker.rest_cl',
              new_callable=PropertyMock).start()
        self.worker.rest_cl.risp_processing_task_list = MagicMock()

    def mock_ri_sp_ch_expenses(self, ri_sp_rows=None):
        if not ri_sp_rows:
            ri_sp_rows = []
        self.worker.get_ri_sp_usage_expenses.return_value = ri_sp_rows

    def mock_uncovered_ch_expenses(self, uncovered_rows=None):
        if not uncovered_rows:
            uncovered_rows = []
        self.worker.get_uncovered_usage_expenses.return_value = uncovered_rows

    @property
    def ri_raw_expenses(self):
        return self._ri_raw_expenses

    @ri_raw_expenses.setter
    def ri_raw_expenses(self, value):
        self._ri_raw_expenses = value

    @property
    def sp_raw_expenses(self):
        return self._sp_raw_expenses

    @sp_raw_expenses.setter
    def sp_raw_expenses(self, value):
        self._sp_raw_expenses = value

    @property
    def uncovered_raw_expenses(self):
        return self._uncovered_raw_expenses

    @uncovered_raw_expenses.setter
    def uncovered_raw_expenses(self, value):
        self._uncovered_raw_expenses = value

    @property
    def ri_exp_cost_raw_expenses(self):
        return self._ri_exp_cost_raw_expenses

    @ri_exp_cost_raw_expenses.setter
    def ri_exp_cost_raw_expenses(self, value):
        self._ri_exp_cost_raw_expenses = value

    @property
    def sp_exp_cost_raw_expenses(self):
        return self._sp_exp_cost_raw_expenses

    @sp_exp_cost_raw_expenses.setter
    def sp_exp_cost_raw_expenses(self, value):
        self._sp_exp_cost_raw_expenses = value

    def ri_sp_side_eff(self, *args):
        if args[0] == 'sp':
            return self.sp_raw_expenses
        elif args[0] == 'ri':
            return self.ri_raw_expenses

    def ri_expected_side_eff(self, *args):
        return self.ri_exp_cost_raw_expenses

    def sp_expected_side_eff(self, *args):
        return self.sp_exp_cost_raw_expenses

    def uncover_side_eff(self, *_args):
        return self.uncovered_raw_expenses

    def mock_mongo_raw(self):
        self.worker.get_offers_expenses_by_type.side_effect = self.ri_sp_side_eff
        self.worker.get_uncovered_raw_expenses.side_effect = self.uncover_side_eff
        self.worker._ri_expected_cost_per_day.side_effect = self.ri_expected_side_eff
        self.worker._sp_expected_cost_per_day.side_effect = self.sp_expected_side_eff

    def mock_mongo_uncovered_expenses(self):
        self.worker.get_uncovered_raw_expenses.side_effect = self.uncover_side_eff

    def mock_risp_tasks(self, tasks=None):
        if not tasks:
            tasks = []
        self.worker.rest_cl.risp_processing_task_list.return_value = (
            200, {'risp_processing_tasks': tasks})

    def mock_valid_risp_task(self):
        self.mock_risp_tasks([{
                'deleted_at': 0,
                'id': self.gen_id(),
                'created_at': 1681112868,
                'cloud_account_id': self.gen_id(),
                'start_date': 1672531200,
                'end_date': 1682812800
        }])

    @staticmethod
    def gen_id():
        return str(uuid.uuid4())

    def test_no_tasks(self):
        self.worker.rest_cl.risp_processing_task_list.return_value = (
            200, {'risp_processing_tasks': []})
        self.worker.process_task(self.task_body, self.rabbit_message)
        self.worker.insert_clickhouse_expenses.assert_not_called()

    def test_no_cloud_account(self):
        self.worker.rest_cl.risp_processing_task_list.return_value = (
            404, {})
        try:
            self.worker._process_task(self.task_body)
        except Exception as e:
            self.assertIsInstance(e, ValueError)
        self.worker.insert_clickhouse_expenses.assert_not_called()

    def test_no_ri_sp_expenses(self):
        self.mock_valid_risp_task()
        self.worker.process_task(self.task_body, self.rabbit_message)
        self.worker.insert_clickhouse_expenses.assert_not_called()

    def test_generate_ri_expenses(self):
        self.mock_valid_risp_task()
        self.ri_raw_expenses = [{
                '_id': {
                    'start_date': {
                        'month': 1,
                        'day': 1,
                        'year': 2023,
                    },
                    'end_date': {
                        'month': 1,
                        'day': 1,
                        'year': 2023,
                    },
                    'cloud_resource_id': 'cloud_resource_id_1',
                    'cloud_offer_id': 'cloud_ri_id',
                    'instance_type': 't2.small',
                },
                'usage_hours': ['1', '2'],
                'usage_seconds': ['1800', '900'],
                'on_demand_cost': ['5', '6'],
                'offer_cost': ['7', '8'],
                'ri_norm_factor': '9',
                'sp_rate': '123'
            }]
        self.ri_exp_cost_raw_expenses = [{
            'start_date': datetime(2023, 1, 1),
            'end_date': datetime(2023, 1, 31, 23, 59, 59),
            'reservation/TotalReservedNormalizedUnits': 732,
            'lineItem/NormalizationFactor': 5,
            'lineItem/UnblendedCost': 732,
            'reservation/AmortizedUpfrontFeeForBillingPeriod': 732,
            'lineItem/UsageStartDate': '2023-01-01T12:00:00Z',
            'resource_id': 'cloud_ri_id'
        }]
        self.worker.process_task(self.task_body, self.rabbit_message)
        call_args = self.worker.insert_clickhouse_expenses.call_args_list[0][0]
        self.assertEqual(call_args[0], [{
            'cloud_account_id': 'cloud_account_id',
            'resource_id': 'cloud_resource_id_1',
            'date': datetime(2023, 1, 1, 0, 0, tzinfo=timezone.utc),
            'instance_type': 't2.small',
            'offer_id': 'cloud_ri_id',
            'offer_type': 'ri',
            'on_demand_cost': 11.0,
            'offer_cost': 15.0,
            'usage': 3.75,  # 1 + 2 + 1800/3600 + 900/3600
            'ri_norm_factor': 9.0,
            'sp_rate': 123,
            'expected_cost': 120,  # 12 * 5 * ((732 + 732) / 732)
            'sign': 1
        }])

    def test_generate_ri_expenses_with_no_offer_resource(self):
        self.mock_valid_risp_task()
        self.ri_raw_expenses = [{
                '_id': {
                    'start_date': {
                        'month': 1,
                        'day': 1,
                        'year': 2023,
                    },
                    'end_date': {
                        'month': 1,
                        'day': 1,
                        'year': 2023,
                    },
                    'cloud_resource_id': 'cloud_resource_id_1',
                    'cloud_offer_id': 'cloud_ri_id',
                    'instance_type': 't2.small'
                },
                'usage_hours': ['1', '2'],
                'usage_seconds': ['1800', '900'],
                'on_demand_cost': ['5', '6'],
                'offer_cost': ['7', '8'],
                'ri_norm_factor': '9',
                'sp_rate': '123'
            }]
        self.worker.process_task(self.task_body, self.rabbit_message)
        self.worker.insert_clickhouse_expenses.assert_called_once_with([{
            'cloud_account_id': 'cloud_account_id',
            'resource_id': 'cloud_resource_id_1',
            'date': datetime(2023, 1, 1, 0, 0, tzinfo=timezone.utc),
            'instance_type': 't2.small',
            'offer_id': 'cloud_ri_id',
            'offer_type': 'ri',
            'on_demand_cost': 11.0,
            'offer_cost': 15.0,
            'usage': 3.75,  # 1 + 2 + 1800/3600 + 900/3600
            'ri_norm_factor': 9.0,
            'sp_rate': 123,
            'expected_cost': 0,
            'sign': 1
        }])

    def test_generate_sp_expenses(self):
        self.mock_valid_risp_task()
        self.sp_raw_expenses = [{
            '_id': {
                'start_date': {
                    'month': 1,
                    'day': 1,
                    'year': 2023,
                },
                'end_date': {
                    'month': 1,
                    'day': 1,
                    'year': 2023,
                },
                'cloud_resource_id': 'cloud_resource_id_1',
                'cloud_offer_id': 'cloud_sp_id',
                'instance_type': 't2.small',
            },
            'usage_hours': ['1', '2'],
            'usage_seconds': ['1800', '900'],
            'on_demand_cost': ['5', '6'],
            'offer_cost': ['7', '8'],
            'sp_rate': '123'
        }]
        self.sp_exp_cost_raw_expenses = [{
            'start_date': datetime(2023, 1, 1),
            'resource_id': 'cloud_sp_id',
            'savingsPlan/TotalCommitmentToDate': 100
        }]
        self.worker.process_task(self.task_body, self.rabbit_message)
        call_args = self.worker.insert_clickhouse_expenses.call_args_list[0][0]
        self.assertEqual(call_args[0], [{
            'cloud_account_id': 'cloud_account_id',
            'resource_id': 'cloud_resource_id_1',
            'date': datetime(2023, 1, 1, 0, 0, tzinfo=timezone.utc),
            'instance_type': 't2.small',
            'offer_id': 'cloud_sp_id',
            'offer_type': 'sp',
            'on_demand_cost': 11.0,
            'offer_cost': 15.0,
            'usage': 3.75,  # 1 + 2 + 1800/3600 + 900/3600
            'ri_norm_factor': 0.0,
            'sp_rate': 123,
            'expected_cost': 100,
            'sign': 1
        }])

    def test_generate_cancel_records(self):
        self.mock_valid_risp_task()
        self.sp_raw_expenses = [{
            '_id': {
                'start_date': {
                    'month': 1,
                    'day': 1,
                    'year': 2023,
                },
                'end_date': {
                    'month': 1,
                    'day': 1,
                    'year': 2023,
                },
                'cloud_resource_id': 'cloud_resource_id_1',
                'cloud_offer_id': 'cloud_sp_id',
                'instance_type': 't2.small'
            },
            'usage_hours': ['1', '2'],
            'usage_seconds': ['1800', '900'],
            'on_demand_cost': ['5', '6'],
            'offer_cost': ['7', '8'],
            'sp_rate': 123
        }]
        date = datetime(2023, 1, 1, 0, 0, tzinfo=timezone.utc)
        ch_expense = ('cloud_resource_id_1', date, 't2.small', 'cloud_sp_id',
                      123, 123, 123, 123, 123, 1)
        self.sp_exp_cost_raw_expenses = [
            {
                'start_date': date,
                'savingsPlan/TotalCommitmentToDate': 111,
                'resource_id': 'cloud_sp_id'
            }
        ]
        self.mock_ri_sp_ch_expenses([ch_expense])
        self.worker.process_task(self.task_body, self.rabbit_message)
        call_args = self.worker.insert_clickhouse_expenses.call_args_list[0][0]
        self.assertEqual(call_args[0], [
                {
                    'cloud_account_id': 'cloud_account_id',
                    'resource_id': 'cloud_resource_id_1',
                    'date': datetime(2023, 1, 1, 0, 0, tzinfo=timezone.utc),
                    'instance_type': 't2.small',
                    'offer_id': 'cloud_sp_id',
                    'offer_type': 'sp',
                    'on_demand_cost': 123,
                    'offer_cost': 123,
                    'usage': 1,
                    'ri_norm_factor': 123,
                    'sp_rate': 123,
                    'expected_cost': 123,
                    'sign': -1
                },
                {
                    'cloud_account_id': 'cloud_account_id',
                    'resource_id': 'cloud_resource_id_1',
                    'date': datetime(2023, 1, 1, 0, 0, tzinfo=timezone.utc),
                    'instance_type': 't2.small',
                    'offer_id': 'cloud_sp_id',
                    'offer_type': 'sp',
                    'on_demand_cost': 11.0,
                    'offer_cost': 15.0,
                    'usage': 3.75,  # 1 + 2 + 1800/3600 + 900/3600
                    'ri_norm_factor': 0.0,
                    'sp_rate': 123,
                    'expected_cost': 111,
                    'sign': 1
                }
            ]
        )

    def test_two_offers_on_one_resource(self):
        self.mock_valid_risp_task()
        self.sp_raw_expenses = [{
            '_id': {
                'start_date': {
                    'month': 1,
                    'day': 1,
                    'year': 2023,
                },
                'end_date': {
                    'month': 1,
                    'day': 1,
                    'year': 2023,
                },
                'cloud_resource_id': 'cloud_resource_id_1',
                'cloud_offer_id': 'cloud_sp_id',
                'instance_type': 't2.small'
            },
            'usage_hours': ['1', '2'],
            'usage_seconds': ['1800', '900'],
            'on_demand_cost': ['5', '6'],
            'offer_cost': ['7', '8'],
            'sp_rate': '123',
        }, {
            '_id': {
                'start_date': {
                    'month': 1,
                    'day': 1,
                    'year': 2023,
                },
                'end_date': {
                    'month': 1,
                    'day': 1,
                    'year': 2023,
                },
                'cloud_resource_id': 'cloud_resource_id_1',
                'cloud_offer_id': 'cloud_sp_id_1',
                'instance_type': 't2.small'
            },
            'usage_hours': ['1', '2'],
            'usage_seconds': ['1800', '900'],
            'on_demand_cost': ['5', '6'],
            'offer_cost': ['7', '8'],
            'sp_rate': '123'
        }]
        date = datetime(2023, 1, 1, 0, 0, tzinfo=timezone.utc)
        self.sp_exp_cost_raw_expenses = [
            {
                'start_date': date,
                'savingsPlan/TotalCommitmentToDate': 111,
                'resource_id': 'cloud_sp_id'
            },
            {
                'start_date': date,
                'savingsPlan/TotalCommitmentToDate': 99,
                'resource_id': 'cloud_sp_id_1'
            }
        ]
        ch_expense = ('cloud_resource_id_1', date, 't2.small', 'cloud_sp_id',
                      123, 123, 123, 123, 123, 1)
        self.mock_ri_sp_ch_expenses([ch_expense])
        self.worker.process_task(self.task_body, self.rabbit_message)
        call_args = self.worker.insert_clickhouse_expenses.call_args_list[0][0]
        self.assertEqual(call_args[0], [
                {
                    'cloud_account_id': 'cloud_account_id',
                    'resource_id': 'cloud_resource_id_1',
                    'date': datetime(2023, 1, 1, 0, 0, tzinfo=timezone.utc),
                    'instance_type': 't2.small',
                    'offer_id': 'cloud_sp_id',
                    'offer_type': 'sp',
                    'on_demand_cost': 123,
                    'offer_cost': 123,
                    'usage': 1,
                    'ri_norm_factor': 123,
                    'sp_rate': 123,
                    'expected_cost': 123,
                    'sign': -1
                },
                {
                    'cloud_account_id': 'cloud_account_id',
                    'resource_id': 'cloud_resource_id_1',
                    'date': datetime(2023, 1, 1, 0, 0, tzinfo=timezone.utc),
                    'instance_type': 't2.small',
                    'offer_id': 'cloud_sp_id',
                    'offer_type': 'sp',
                    'on_demand_cost': 11.0,
                    'offer_cost': 15.0,
                    'usage': 3.75,
                    'ri_norm_factor': 0.0,
                    'sp_rate': 123,
                    'expected_cost': 111,
                    'sign': 1
                },
                {
                    'cloud_account_id': 'cloud_account_id',
                    'resource_id': 'cloud_resource_id_1',
                    'date': datetime(2023, 1, 1, 0, 0, tzinfo=timezone.utc),
                    'instance_type': 't2.small',
                    'offer_id': 'cloud_sp_id_1',
                    'offer_type': 'sp',
                    'on_demand_cost': 11.0,
                    'offer_cost': 15.0,
                    'usage': 3.75,
                    'ri_norm_factor': 0.0,
                    'sp_rate': 123,
                    'expected_cost': 99,
                    'sign': 1
                }
            ]
        )

    def test_uncovered_generate_records(self):
        self.mock_valid_risp_task()
        self.uncovered_raw_expenses = [{
            'start_date': datetime(2023, 1, 1, 0, 0, tzinfo=timezone.utc),
            'resource_id': 'cloud_resource_id_1',
            'pricing/unit': 'Second',
            'lineItem/UsageAmount': 1800,
            'pricing/publicOnDemandCost': 10,
            'product/operatingSystem': 'Linux',
            'product/instanceType': 't2',
            'product/region': 'us-west-1'
        }, {
            'start_date': datetime(2023, 1, 1, 0, 0, tzinfo=timezone.utc),
            'resource_id': 'cloud_resource_id_2',
            'pricing/unit': 'hrs',
            'lineItem/UsageAmount': 3,
            'pricing/publicOnDemandCost': 30,
            'product/operatingSystem': 'Linux',
            'product/instanceType': 't2',
            'product/region': 'us-west-1'
        }, {
            'start_date': datetime(2023, 1, 1, 0, 0, tzinfo=timezone.utc),
            'resource_id': 'cloud_resource_id_2',
            'pricing/unit': 'hrs',
            'lineItem/UsageAmount': 2.5,
            'pricing/publicOnDemandCost': 25,
            'product/operatingSystem': 'Linux',
            'product/instanceType': 't2',
            'product/region': 'us-west-1'
        }
        ]
        ch_expense = ('t2', 'Linux', 'us-west-1', 'cloud_resource_id_1',
                      datetime(2023, 1, 1, 0, 0, tzinfo=timezone.utc),
                      123, 1)
        self.mock_uncovered_ch_expenses([ch_expense])
        self.worker.process_task(self.task_body, self.rabbit_message)
        self.worker.insert_clickhouse_expenses.assert_called_once_with([
                {
                    'cloud_account_id': 'cloud_account_id',
                    'date': datetime(2023, 1, 1, 0, 0, tzinfo=timezone.utc),
                    'resource_id': 'cloud_resource_id_1',
                    'instance_type': 't2',
                    'os': 'Linux',
                    'location': 'us-west-1',
                    'usage': 1,
                    'cost': 123,
                    'sign': -1
                },
                {
                    'cloud_account_id': 'cloud_account_id',
                    'date': datetime(2023, 1, 1, 0, 0, tzinfo=timezone.utc),
                    'resource_id': 'cloud_resource_id_1',
                    'instance_type': 't2',
                    'os': 'Linux',
                    'location': 'us-west-1',
                    'cost': 10,
                    'usage': 0.5,  # 1800 / 3600
                    'sign': 1
                },
                {
                    'cloud_account_id': 'cloud_account_id',
                    'date': datetime(2023, 1, 1, 0, 0, tzinfo=timezone.utc),
                    'resource_id': 'cloud_resource_id_2',
                    'instance_type': 't2',
                    'os': 'Linux',
                    'location': 'us-west-1',
                    'cost': 55.0,  # 25 + 30
                    'usage': 5.5,  # 2.5 + 3
                    'sign': 1
                }
            ],
            table='uncovered_usage'
        )

    def test_generate_empty(self):
        self.mock_valid_risp_task()
        self.worker._get_offer_date_map = MagicMock()
        self.sp_exp_cost_raw_expenses = [{
            'start_date': datetime(2023, 1, 1, tzinfo=timezone.utc),
            'resource_id': 'cloud_sp',
            'savingsPlan/TotalCommitmentToDate': 11
        }, {
            'start_date': datetime(2023, 1, 2, tzinfo=timezone.utc),
            'resource_id': 'cloud_sp',
            'savingsPlan/TotalCommitmentToDate': 22
        }]
        self.worker._get_offer_date_map.return_value = {
            'cloud_sp': [datetime(2023, 1, 1, tzinfo=timezone.utc)]
        }
        self.worker.process_task(self.task_body, self.rabbit_message)
        self.worker.insert_clickhouse_expenses.assert_called_once_with([{
            'cloud_account_id': 'cloud_account_id',
            'resource_id': '',
            'date': datetime(2023, 1, 2, 0, 0, tzinfo=timezone.utc),
            'instance_type': '',
            'offer_id': 'cloud_sp',
            'offer_type': 'sp',
            'on_demand_cost': 0,
            'offer_cost': 0,
            'usage': 0,
            'ri_norm_factor': 0.0,
            'sp_rate': 0,
            'expected_cost': 22,
            'sign': 1
        }])
