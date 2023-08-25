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
        self.mock_common()
        self.mock_ch_expenses()
        self.mock_mongo_offers_raw_expenses()
        self.mock_risp_tasks()
        self._ri_raw_expenses = []
        self._sp_raw_expenses = []

    def tearDown(self):
        patch.stopall()
        super().tearDown()

    def mock_common(self):
        patch('risp.risp_worker.worker.RISPWorker.clickhouse_client',
              new_callable=PropertyMock).start()
        self.worker.get_clickhouse_expenses = MagicMock()
        self.worker.insert_clickhouse_expenses = MagicMock()

        patch('risp.risp_worker.worker.RISPWorker.mongo_client',
              new_callable=PropertyMock).start()
        self.worker.get_offers_expenses_by_type = MagicMock()
        self.worker.get_resources_ids_map = MagicMock()

        patch('risp.risp_worker.worker.RISPWorker.rest_cl',
              new_callable=PropertyMock).start()
        self.worker.rest_cl.risp_processing_task_list = MagicMock()

    def mock_ch_expenses(self, ri_sp_rows=None):
        if not ri_sp_rows:
            ri_sp_rows = []
        self.worker.get_clickhouse_expenses.return_value = ri_sp_rows

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

    def ri_sp_side_eff(self, *args):
        if args[0] == 'sp':
            return self.sp_raw_expenses
        elif args[0] == 'ri':
            return self.ri_raw_expenses

    def mock_mongo_offers_raw_expenses(self):
        self.worker.get_offers_expenses_by_type.side_effect = self.ri_sp_side_eff

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
                },
                'usage_hours': ['1', '2'],
                'usage_seconds': ['1800', '900'],
                'on_demand_cost': ['5', '6'],
                'offer_cost': ['7', '8'],
            }]
        self.worker.process_task(self.task_body, self.rabbit_message)
        self.worker.insert_clickhouse_expenses.assert_called_once_with([{
            'cloud_account_id': 'cloud_account_id',
            'resource_id': 'cloud_resource_id_1',
            'date': datetime(2023, 1, 1, 0, 0, tzinfo=timezone.utc),
            'offer_id': 'cloud_ri_id',
            'offer_type': 'ri',
            'on_demand_cost': 11.0,
            'offer_cost': 15.0,
            'usage': 3.75,  # 1 + 2 + 1800/3600 + 900/3600
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
                },
                'usage_hours': ['1', '2'],
                'usage_seconds': ['1800', '900'],
                'on_demand_cost': ['5', '6'],
                'offer_cost': ['7', '8'],
            }]
        self.worker.process_task(self.task_body, self.rabbit_message)
        self.worker.insert_clickhouse_expenses.assert_called_once_with([{
            'cloud_account_id': 'cloud_account_id',
            'resource_id': 'cloud_resource_id_1',
            'date': datetime(2023, 1, 1, 0, 0, tzinfo=timezone.utc),
            'offer_id': 'cloud_ri_id',
            'offer_type': 'ri',
            'on_demand_cost': 11.0,
            'offer_cost': 15.0,
            'usage': 3.75,  # 1 + 2 + 1800/3600 + 900/3600
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
            },
            'usage_hours': ['1', '2'],
            'usage_seconds': ['1800', '900'],
            'on_demand_cost': ['5', '6'],
            'offer_cost': ['7', '8'],
        }]
        self.worker.process_task(self.task_body, self.rabbit_message)
        self.worker.insert_clickhouse_expenses.assert_called_once_with([{
            'cloud_account_id': 'cloud_account_id',
            'resource_id': 'cloud_resource_id_1',
            'date': datetime(2023, 1, 1, 0, 0, tzinfo=timezone.utc),
            'offer_id': 'cloud_sp_id',
            'offer_type': 'sp',
            'on_demand_cost': 11.0,
            'offer_cost': 15.0,
            'usage': 3.75,  # 1 + 2 + 1800/3600 + 900/3600
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
            },
            'usage_hours': ['1', '2'],
            'usage_seconds': ['1800', '900'],
            'on_demand_cost': ['5', '6'],
            'offer_cost': ['7', '8'],
        }]
        ch_expense = ('cloud_resource_id_1',
                      datetime(2023, 1, 1, 0, 0, tzinfo=timezone.utc),
                      'cloud_sp_id', 123, 123, 1)
        self.mock_ch_expenses([ch_expense])
        self.worker.process_task(self.task_body, self.rabbit_message)
        self.worker.insert_clickhouse_expenses.assert_called_once_with([
                {
                    'cloud_account_id': 'cloud_account_id',
                    'resource_id': 'cloud_resource_id_1',
                    'date': datetime(2023, 1, 1, 0, 0, tzinfo=timezone.utc),
                    'offer_id': 'cloud_sp_id',
                    'offer_type': 'sp',
                    'on_demand_cost': 123,
                    'offer_cost': 123,
                    'usage': 1,
                    'sign': -1
                },
                {
                    'cloud_account_id': 'cloud_account_id',
                    'resource_id': 'cloud_resource_id_1',
                    'date': datetime(2023, 1, 1, 0, 0, tzinfo=timezone.utc),
                    'offer_id': 'cloud_sp_id',
                    'offer_type': 'sp',
                    'on_demand_cost': 11.0,
                    'offer_cost': 15.0,
                    'usage': 3.75,  # 1 + 2 + 1800/3600 + 900/3600
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
            },
            'usage_hours': ['1', '2'],
            'usage_seconds': ['1800', '900'],
            'on_demand_cost': ['5', '6'],
            'offer_cost': ['7', '8'],
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
            },
            'usage_hours': ['1', '2'],
            'usage_seconds': ['1800', '900'],
            'on_demand_cost': ['5', '6'],
            'offer_cost': ['7', '8'],
        }]
        ch_expense = ('cloud_resource_id_1',
                      datetime(2023, 1, 1, 0, 0, tzinfo=timezone.utc),
                      'cloud_sp_id', 123, 123, 1)
        self.mock_ch_expenses([ch_expense])
        self.worker.process_task(self.task_body, self.rabbit_message)
        self.worker.insert_clickhouse_expenses.assert_called_once_with([
                {
                    'cloud_account_id': 'cloud_account_id',
                    'resource_id': 'cloud_resource_id_1',
                    'date': datetime(2023, 1, 1, 0, 0, tzinfo=timezone.utc),
                    'offer_id': 'cloud_sp_id',
                    'offer_type': 'sp',
                    'on_demand_cost': 123,
                    'offer_cost': 123,
                    'usage': 1,
                    'sign': -1
                },
                {
                    'cloud_account_id': 'cloud_account_id',
                    'resource_id': 'cloud_resource_id_1',
                    'date': datetime(2023, 1, 1, 0, 0, tzinfo=timezone.utc),
                    'offer_id': 'cloud_sp_id',
                    'offer_type': 'sp',
                    'on_demand_cost': 11.0,
                    'offer_cost': 15.0,
                    'usage': 3.75,
                    'sign': 1
                },
                {
                    'cloud_account_id': 'cloud_account_id',
                    'resource_id': 'cloud_resource_id_1',
                    'date': datetime(2023, 1, 1, 0, 0, tzinfo=timezone.utc),
                    'offer_id': 'cloud_sp_id_1',
                    'offer_type': 'sp',
                    'on_demand_cost': 11.0,
                    'offer_cost': 15.0,
                    'usage': 3.75,
                    'sign': 1
                }
            ]
        )
