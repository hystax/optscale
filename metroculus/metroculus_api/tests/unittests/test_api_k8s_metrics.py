from unittest.mock import patch
from datetime import datetime, timedelta
from metroculus.metroculus_api.tests.unittests.test_api_base import TestBase
from metroculus.metroculus_api.utils import seconds_to_hour


class TestK8sMetricsAPI(TestBase):
    def setUp(self):
        super().setUp()
        self.start_date = datetime(2022, 5, 1)
        self.end_date = datetime(2022, 5, 30)

    @staticmethod
    def mock_metroculus(return_value=None):
        if not return_value:
            return_value = []
        patch(
            'metroculus.metroculus_api.controllers.k8s_metric.K8sMetricsController.'
            '_get_metrics',
            return_value=return_value).start()

    def test_invalid_cloud_account_id(self):
        for cl_acc_id in [None, '']:
            code, resp = self.client.get_k8s_metrics(
                cl_acc_id, int(self.start_date.timestamp()),
                int(self.end_date.timestamp()))
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OM0008')

    def test_zero_start_date(self):
        self.mock_metroculus()
        code, resp = self.client.get_k8s_metrics(
            'ca_id', 0, int(self.end_date.timestamp()))
        self.assertEqual(code, 200, resp)

    def test_invalid_start_date(self):
        for start_date_value, expected_error in [
            (None, 'OM0008'),
            ('', 'OM0006'),
            (self.start_date, 'OM0006'),
            (self.start_date.timestamp(), 'OM0006'),
            (-1, 'OM0006'),
        ]:
            code, resp = self.client.get_k8s_metrics(
                'ca_id', start_date_value, int(self.end_date.timestamp()))
            self.assertEqual(code, 400)
            self.verify_error_code(resp, expected_error)

    def test_unauthorized(self):
        self.client.secret = ''
        code, resp = self.client.get_k8s_metrics(
            'ca_id', int(self.start_date.timestamp()),
            int(self.end_date.timestamp()))
        self.assertEqual(code, 401)

    def test_bad_secret(self):
        self.client.secret = 'wrong'
        code, resp = self.client.get_k8s_metrics(
            'ca_id', int(self.start_date.timestamp()),
            int(self.end_date.timestamp()))
        self.assertEqual(code, 403)

    def test_empty_bd(self):
        self.mock_metroculus()
        start_date, end_date, cloud_acc_id = (
            int(self.start_date.timestamp()), int(self.end_date.timestamp()),
            'ca_id')
        code, resp = self.client.get_k8s_metrics(
            cloud_acc_id, int(self.start_date.timestamp()),
            int(self.end_date.timestamp()))
        self.assertEqual(code, 200)
        self.assertEqual(resp, {'start_date': start_date, 'end_date': end_date,
                                cloud_acc_id: []})

    def test_get_date_by_period(self):
        data = [
            ('res_id_1', 0.6445, 60366848, 3, 2.8, 2.8, 262144000, 262144000,
             262144000, 2.6445, 60366848, 12, 12884901888, 8, 8589934592, 4,
             6442450944, 2.6445, 60366848, 12, 12884901888, 8, 8589934592, 4,
             6442450944),
            ('res_id_2', 0.5445, 20366848, 2, 2, 2, 162144000, 162144000,
             162144000, 2.6445, 60366848, 12, 12884901888, 8, 8589934592, 4,
             6442450944, 2.6445, 60366848, 12, 12884901888, 8, 8589934592, 4,
             6442450944),
            ('res_id_3', 0.6, 60366848, 2, 2, 2, 262144000, 262144000,
             262144000, 2.6445, 60366848, 12, 12884901888, 8, 8589934592, 4,
             6442450944, 2.6445, 60366848, 12, 12884901888, 8, 8589934592, 4,
             6442450944),
            ('res_id_4', 0.5, 40366848, 2, 2, 2, 262144000, 262144000,
             262144000, 2.6445, 60366848, 12, 12884901888, 8, 8589934592, 4,
             6442450944, 2.6445, 60366848, 12, 12884901888, 8, 8589934592, 4,
             6442450944),
            ('res_id_5', 0.6, 50366848, 2, 2, 2, 262144000, 262144000,
             262144000, 2.6445, 60366848, 12, 12884901888, 8, 8589934592, 4,
             6442450944, 2.6445, 60366848, 12, 12884901888, 8, 8589934592, 4,
             6442450944),
            ('res_id_6', 0.6, 60366848, 2, 2, 2, 262144000, 262144000,
             262144000, 2.6445, 60366848, 12, 12884901888, 8, 8589934592, 4,
             6442450944, 2.6445, 60366848, 12, 12884901888, 8, 8589934592, 4,
             6442450944),
        ]
        self.mock_metroculus(data)
        # no scale
        end_date = self.start_date + timedelta(hours=12)
        start_timestamp = int(self.start_date.timestamp())
        end_timestamp = int(end_date.timestamp())
        code, resp = self.client.get_k8s_metrics(
            'ca_id', start_timestamp, end_timestamp)
        self.assertEqual(code, 200)
        ca_resp = resp['ca_id']
        period = seconds_to_hour(end_timestamp - start_timestamp)
        result_ca_resp = [{
            'resource_id': item[0],
            'average_pod_cpu_used': item[1],
            'average_pod_memory_used': item[2],
            'pod_cpu_provision': item[3],
            'pod_cpu_requests': item[4],
            'pod_memory_provision': item[6],
            'pod_memory_requests': item[7],
            'total_pod_cpu_requests': item[5] * period,
            'total_pod_memory_requests': item[8] * period,
            'total_pod_cpu_used': item[1] * period,
            'total_pod_memory_used': item[2] * period,
            'namespace_cpu_provision_used': item[9],
            'namespace_memory_provision_used': item[10],
            'namespace_quota_cpu_provision_hard': item[11],
            'namespace_quota_memory_provision_hard': item[12],
            'namespace_quota_cpu_provision_medium': item[13],
            'namespace_quota_memory_provision_medium': item[14],
            'namespace_quota_cpu_provision_low': item[15],
            'namespace_quota_memory_provision_low': item[16],
            'namespace_cpu_requests_used': item[17],
            'namespace_memory_requests_used': item[18],
            'namespace_quota_cpu_requests_hard': item[19],
            'namespace_quota_memory_requests_hard': item[20],
            'namespace_quota_cpu_requests_medium': item[21],
            'namespace_quota_memory_requests_medium': item[22],
            'namespace_quota_cpu_requests_low': item[23],
            'namespace_quota_memory_requests_low': item[24]
        } for item in data]
        self.assertListEqual(result_ca_resp, ca_resp)
