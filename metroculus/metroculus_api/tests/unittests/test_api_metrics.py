from unittest.mock import patch
from datetime import datetime, timedelta
from metroculus.metroculus_api.tests.unittests.test_api_base import TestBase


class TestMetricsAPI(TestBase):
    def setUp(self):
        super().setUp()
        self.start_date = datetime(2021, 5, 1)
        self.end_date = datetime(2021, 5, 30)

    @staticmethod
    def mock_metroculus(return_value=None):
        if not return_value:
            return_value = []
        patch(
            'metroculus.metroculus_api.controllers.metrics.MetricsController.'
            '_get_metrics',
            return_value=return_value).start()

    def generate_metroculus_data(
            self,
            metrics,
            start_date=None,
            end_date=None):
        if not start_date:
            start_date = self.start_date
        if not end_date:
            end_date = self.end_date
        result = []
        for metric in metrics:
            dt = start_date
            while dt <= end_date:
                result.append((metric, 5, dt))
                dt = dt + timedelta(seconds=900)
        return result

    def test_invalid_cloud_account_id(self):
        for cl_acc_id in [None, '']:
            code, resp = self.client.get_metrics(
                cl_acc_id, 'res_1', int(self.start_date.timestamp()),
                int(self.end_date.timestamp()))
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OM0008')

    def test_invalid_cloud_resource_id(self):
        for resource_id in ['', None]:
            code, resp = self.client.get_metrics(
                'ca_id', resource_id, int(self.start_date.timestamp()),
                int(self.end_date.timestamp()))
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OM0008')

    def test_zero_start_date(self):
        self.mock_metroculus()
        code, resp = self.client.get_metrics(
            'ca_id', 'r_id', 0,
            int(self.end_date.timestamp()))
        self.assertEqual(code, 200, resp)

    def test_invalid_start_date(self):
        for start_date_value, expected_error in [
            (None, 'OM0008'),
            ('', 'OM0006'),
            (self.start_date, 'OM0006'),
            (self.start_date.timestamp(), 'OM0006'),
            (-1, 'OM0006'),
        ]:
            code, resp = self.client.get_metrics(
                'ca_id', 'r_id', start_date_value,
                int(self.end_date.timestamp()))
            self.assertEqual(code, 400)
            self.verify_error_code(resp, expected_error)

    def test_invalid_interval(self):
        for interval_value, expected_error in [
            ('', 'OM0006'),
            ('asd', 'OM0006'),
            (901, 'OM0006'),
            (-1, 'OM0006'),
            (0, 'OM0006'),
        ]:
            code, resp = self.client.get_metrics(
                'ca_id', 'r_id', int(self.start_date.timestamp()),
                int(self.end_date.timestamp()), interval_value)
            self.assertEqual(code, 400, interval_value)
            self.verify_error_code(resp, expected_error)

    def test_unauthorized(self):
        self.client.secret = ''
        code, resp = self.client.get_metrics(
            'ca_id', 'r_id', int(self.start_date.timestamp()),
            int(self.end_date.timestamp()))
        self.assertEqual(code, 401)

    def test_bad_secret(self):
        self.client.secret = 'wrong'
        code, resp = self.client.get_metrics(
            'ca_id', 'r_id', int(self.start_date.timestamp()),
            int(self.end_date.timestamp()))
        self.assertEqual(code, 403)

    def test_empty_bd(self):
        self.mock_metroculus()
        code, resp = self.client.get_metrics(
            'ca_id', 'r_id', int(self.start_date.timestamp()),
            int(self.end_date.timestamp()))
        self.assertEqual(code, 200)
        self.assertEqual(resp, {})

    def test_scale_interval(self):
        # 5 points every 15 min
        start_date = self.start_date
        end_date = self.start_date + timedelta(days=1)
        data = self.generate_metroculus_data(['cpu', 'ram'],
                                             start_date, end_date)
        self.mock_metroculus(data)
        # 1 day | 96 points | not scaled interval
        code, resp = self.client.get_metrics(
            'ca_id', 'r_id', int(start_date.timestamp()),
            int(end_date.timestamp()))
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['cpu']), 96)
        self.assertEqual(len(resp['ram']), 96)
        self.assertEqual(datetime.fromtimestamp(resp['cpu'][0]['date']),
                         start_date + timedelta(seconds=900))
        self.assertEqual(datetime.fromtimestamp(resp['cpu'][-1]['date']),
                         end_date)

        data = self.generate_metroculus_data(['cpu', 'ram'])
        self.mock_metroculus(data)
        # 1 month | 58 points | interval scaled to 12 hours
        code, resp = self.client.get_metrics(
            'ca_id', 'r_id', int(self.start_date.timestamp()),
            int(self.end_date.timestamp()))
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['cpu']), 58)
        self.assertEqual(len(resp['ram']), 58)
        self.assertEqual(datetime.fromtimestamp(resp['cpu'][0]['date']),
                         self.start_date + timedelta(hours=12))
        self.assertEqual(datetime.fromtimestamp(resp['cpu'][-1]['date']),
                         self.end_date)

        # 1 month | 29 points | not scaled interval (24 hours passed)
        code, resp = self.client.get_metrics(
            'ca_id', 'r_id', int(self.start_date.timestamp()),
            int(self.end_date.timestamp()), interval=86400)
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['cpu']), 29)
        self.assertEqual(len(resp['ram']), 29)
        self.assertEqual(datetime.fromtimestamp(resp['cpu'][0]['date']),
                         self.start_date + timedelta(hours=24))
        self.assertEqual(datetime.fromtimestamp(resp['cpu'][-1]['date']),
                         self.end_date)

    def test_scale_avg_value(self):
        data = [
            ('cpu', 120, self.start_date),  # not in range
            ('cpu', 2, self.start_date + timedelta(hours=1, minutes=15)),
            ('cpu', 2, self.start_date + timedelta(hours=1, minutes=30)),
            ('cpu', 4, self.start_date + timedelta(hours=1, minutes=45)),
            ('cpu', 4, self.start_date + timedelta(hours=2)),
            ('cpu', 6, self.start_date + timedelta(hours=4, minutes=15)),
            ('cpu', 6, self.start_date + timedelta(hours=4, minutes=30)),
            ('cpu', 6, self.start_date + timedelta(hours=7)),
            ('cpu', 9, self.start_date + timedelta(hours=8)),
            ('cpu', 12, self.start_date + timedelta(hours=9)),
            ('cpu', 24, self.start_date + timedelta(hours=10)),
        ]
        self.mock_metroculus(data)
        # no scale
        end_date = self.start_date + timedelta(hours=12)
        code, resp = self.client.get_metrics(
            'ca_id', 'r_id', int(self.start_date.timestamp()),
            int(end_date.timestamp()))
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['cpu']), len(data) - 1)
        for i, r in enumerate(resp['cpu']):
            self.assertEqual(r['value'], data[i + 1][1])

        # scale to one hrs
        code, resp = self.client.get_metrics(
            'ca_id', 'r_id', int(self.start_date.timestamp()),
            int(end_date.timestamp()), 3600)
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['cpu']), 6)
        # (2 + 2 + 4 + 4) / 4
        self.assertEqual(resp['cpu'][0]['value'], 3)
        # (6 + 6) / 2
        self.assertEqual(resp['cpu'][1]['value'], 6)
        # 6 / 1
        self.assertEqual(resp['cpu'][2]['value'], 6)
        # 9 / 1
        self.assertEqual(resp['cpu'][3]['value'], 9)
        # 12 / 1
        self.assertEqual(resp['cpu'][4]['value'], 12)
        # 24 / 1
        self.assertEqual(resp['cpu'][5]['value'], 24)

        # scale to 3 hrs
        code, resp = self.client.get_metrics(
            'ca_id', 'r_id', int(self.start_date.timestamp()),
            int(end_date.timestamp()), 10800)
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['cpu']), 4)
        # (2 + 2 + 4 + 4) / 4
        self.assertEqual(resp['cpu'][0]['value'], 3)
        # (6 + 6) / 2
        self.assertEqual(resp['cpu'][1]['value'], 6)
        # (6 + 9 + 12 ) / 3
        self.assertEqual(resp['cpu'][2]['value'], 9)
        # 24 / 1
        self.assertEqual(resp['cpu'][3]['value'], 24)
