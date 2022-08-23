from unittest.mock import patch
from datetime import datetime
from metroculus_api.tests.unittests.test_api_base import TestBase


class TestAvgMetricsAPI(TestBase):
    def setUp(self):
        super().setUp()
        self.start_date = datetime(2021, 5, 1)
        self.end_date = datetime(2021, 5, 30)

    @staticmethod
    def mock_metroculus(return_value=None):
        if not return_value:
            return_value = []
        patch('metroculus_api.controllers.agr_metrics.AgrMetricsController.'
              '_get_agr_metrics', return_value=return_value).start()

    def test_invalid_cloud_account_id(self):
        for cl_acc_id in [None, '']:
            code, resp = self.client.get_aggregated_metrics(
                cl_acc_id, 'res_1', int(self.start_date.timestamp()),
                int(self.end_date.timestamp()))
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OM0008')

    def test_invalid_cloud_resource_id(self):
        for resource_ids in ['', [], None, ['', '1']]:
            code, resp = self.client.get_aggregated_metrics(
                'ca_id', resource_ids, int(self.start_date.timestamp()),
                int(self.end_date.timestamp()))
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OM0008')

    def test_zero_start_date(self):
        self.mock_metroculus()
        code, resp = self.client.get_aggregated_metrics(
            'ca_id', 'r_id', 0,
            int(self.end_date.timestamp()), ['cpu'])
        self.assertEqual(code, 200, resp)

    def test_invalid_start_date(self):
        for start_date_value, expected_error in [
            (None, 'OM0008'),
            ('', 'OM0006'),
            (self.start_date, 'OM0006'),
            (self.start_date.timestamp(), 'OM0006'),
            (-1, 'OM0006'),
        ]:
            code, resp = self.client.get_aggregated_metrics(
                'ca_id', 'r_id', start_date_value,
                int(self.end_date.timestamp()))
            self.assertEqual(code, 400)
            self.verify_error_code(resp, expected_error)

    def test_invalid_meter_name(self):
        for meter_names in ['name_0', ['name_1', 'name_2']]:
            code, resp = self.client.get_aggregated_metrics(
                'ca_id', 'r_id', int(self.start_date.timestamp()),
                int(self.end_date.timestamp()), meter_names)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OM0006')

    def test_unauthorized(self):
        self.client.secret = ''
        code, resp = self.client.get_aggregated_metrics(
            'ca_id', 'r_id', int(self.start_date.timestamp()),
            int(self.end_date.timestamp()))
        self.assertEqual(code, 401)

    def test_bad_secret(self):
        self.client.secret = 'wrong'
        code, resp = self.client.get_aggregated_metrics(
            'ca_id', 'r_id', int(self.start_date.timestamp()),
            int(self.end_date.timestamp()))
        self.assertEqual(code, 403)

    def test_empty_bd(self):
        self.mock_metroculus()
        code, resp = self.client.get_aggregated_metrics(
            'ca_id', 'r_id', int(self.start_date.timestamp()),
            int(self.end_date.timestamp()))
        self.assertEqual(code, 200)
        self.assertEqual(resp, {})

    def test_agr_metrics(self):
        self.mock_metroculus([
            ('res_1', 'cpu', 34, 50, [20, 40]),
            ('res_2', 'cpu', 25, 50, [20, 40]),
            ('res_3', 'cpu', 28, 50, [20, 40]),
            ('res_1', 'ram', 2000, 3000, [1800, 2600]),
            ('res_2', 'ram', 3000, 4500, [1800, 4300]),
            ('res_3', 'network_in_io', 128, 250, [120, 200]),
        ])
        code, resp = self.client.get_aggregated_metrics(
            'ca_id', ['res_1', 'res_2', 'res_3'],
            int(self.start_date.timestamp()),
            int(self.end_date.timestamp()))
        self.assertEqual(200, code)
        self.assertEqual(resp, {
            'res_1': {
                'cpu': {'avg': 34, 'max': 50, 'qtl50': 20, 'qtl99': 40},
                'ram': {'avg': 2000, 'max': 3000, 'qtl50': 1800, 'qtl99': 2600}
            },
            'res_2': {
                'cpu': {'avg': 25, 'max': 50, 'qtl50': 20, 'qtl99': 40},
                'ram': {'avg': 3000, 'max': 4500, 'qtl50': 1800, 'qtl99': 4300}
            },
            'res_3': {
                'cpu': {'avg': 28, 'max': 50, 'qtl50': 20, 'qtl99': 40},
                'network_in_io': {'avg': 128, 'max': 250, 'qtl50': 120, 'qtl99': 200}
            }
        })

        code, resp = self.client.get_aggregated_metrics(
            'ca_id', 'r_id', int(self.start_date.timestamp()),
            int(self.end_date.timestamp()), 'cpu')
        self.assertEqual(code, 200)
        self.assertEqual(resp, {
            'res_1': {'cpu': {'avg': 34, 'max': 50, 'qtl50': 20, 'qtl99': 40}},
            'res_2': {'cpu': {'avg': 25, 'max': 50, 'qtl50': 20, 'qtl99': 40}},
            'res_3': {'cpu': {'avg': 28, 'max': 50, 'qtl50': 20, 'qtl99': 40}}
        })

        code, resp = self.client.get_aggregated_metrics(
            'ca_id', 'r_id', int(self.start_date.timestamp()),
            int(self.end_date.timestamp()), ['ram', 'network_in_io'])
        self.assertEqual(code, 200)
        self.assertEqual(resp, {
            'res_1': {'ram': {'avg': 2000, 'max': 3000, 'qtl50': 1800, 'qtl99': 2600}},
            'res_2': {'ram': {'avg': 3000, 'max': 4500, 'qtl50': 1800, 'qtl99': 4300}},
            'res_3': {'network_in_io': {'avg': 128, 'max': 250, 'qtl50': 120, 'qtl99': 200}}
        })
