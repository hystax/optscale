from unittest.mock import patch
from datetime import datetime
from metroculus.metroculus_api.tests.unittests.test_api_base import TestBase


class TestActivityBreakdownAPI(TestBase):
    def setUp(self):
        super().setUp()
        self.start_date = datetime(2021, 5, 1)
        self.end_date = datetime(2021, 5, 30)

    @staticmethod
    def mock_metroculus(return_value=None):
        if not return_value:
            return_value = []
        patch('metroculus.metroculus_api.controllers.activity_breakdown.'
              'ActivityBreakdownController._get_activity_breakdown',
              return_value=return_value).start()

    def test_invalid_cloud_account_id(self):
        for cl_acc_id in [None, '']:
            code, resp = self.client.get_activity_breakdown(
                cl_acc_id, 'res_1', int(self.start_date.timestamp()),
                int(self.end_date.timestamp()))
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OM0008')

    def test_invalid_cloud_resource_id(self):
        for resource_ids in ['', [], None, ['', '1']]:
            code, resp = self.client.get_activity_breakdown(
                'ca_id', resource_ids, int(self.start_date.timestamp()),
                int(self.end_date.timestamp()))
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OM0008')

    def test_zero_start_date(self):
        self.mock_metroculus()
        code, resp = self.client.get_activity_breakdown(
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
            code, resp = self.client.get_activity_breakdown(
                'ca_id', 'r_id', start_date_value,
                int(self.end_date.timestamp()))
            self.assertEqual(code, 400)
            self.verify_error_code(resp, expected_error)

    def test_invalid_meter_name(self):
        for meter_names in ['name_0', ['name_1', 'name_2']]:
            code, resp = self.client.get_activity_breakdown(
                'ca_id', 'r_id', int(self.start_date.timestamp()),
                int(self.end_date.timestamp()), meter_names)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OM0006')

    def test_empty_meter_names(self):
        meter_names = []
        code, resp = self.client.get_activity_breakdown(
            'ca_id', 'r_id', int(self.start_date.timestamp()),
            int(self.end_date.timestamp()), meter_names)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OM0008')

    def test_unauthorized(self):
        self.client.secret = ''
        code, resp = self.client.get_activity_breakdown(
            'ca_id', 'r_id', int(self.start_date.timestamp()),
            int(self.end_date.timestamp()))
        self.assertEqual(code, 401)

    def test_bad_secret(self):
        self.client.secret = 'wrong'
        code, resp = self.client.get_activity_breakdown(
            'ca_id', 'r_id', int(self.start_date.timestamp()),
            int(self.end_date.timestamp()))
        self.assertEqual(code, 403)

    def test_empty_bd(self):
        self.mock_metroculus()
        code, resp = self.client.get_activity_breakdown(
            'ca_id', 'r_id', int(self.start_date.timestamp()),
            int(self.end_date.timestamp()), ['cpu'])
        self.assertEqual(code, 200)
        self.assertEqual(resp, {})

    def test_activity_breakdown(self):
        self.mock_metroculus([
            ('res_1', 'cpu', 34, 1, 1),
            ('res_1', 'cpu', 35, 1, 2),
            ('res_2', 'cpu', 25, 1, 1),
        ])
        code, resp = self.client.get_activity_breakdown(
            'ca_id', ['res_1', 'res_2'],
            int(self.start_date.timestamp()),
            int(self.end_date.timestamp()),
            ['cpu'],
        )
        self.assertEqual(200, code)
        nulls_matrix = [None] * 7 * 24
        res1_cpu = nulls_matrix.copy()
        res1_cpu[1] = 34
        res1_cpu[2] = 35
        res2_cpu = nulls_matrix.copy()
        res2_cpu[1] = 25
        self.assertEqual(resp, {
            'res_1': {
                'cpu': res1_cpu,
            },
            'res_2': {
                'cpu': res2_cpu,
            },
        })
