import uuid
from datetime import datetime
from unittest.mock import patch

from rest_api_server.tests.unittests.test_api_base import TestApiBase


class TestK8sRightsizing(TestApiBase):
    def setUp(self, version='v2'):
        super().setUp(version)
        patch('config_client.client.Client.metroculus_url').start()
        _, self.org = self.client.organization_create({'name': "organization"})
        self.org_id = self.org['id']
        self.valid_kubernetes_cloud_acc = {
            'name': 'k8s cloud_acc',
            'type': 'kubernetes_cnr',
            'config': {
                'user': 'user',
                'password': 'password',
                'cost_model': {
                    'cpu_hourly_cost': 0.002,
                    'memory_hourly_cost': 0.001
                }
            }
        }
        self.auth_user_id_1 = self.gen_id()
        _, self.employee1 = self.client.employee_create(
            self.org_id,
            {'name': 'name1', 'auth_user_id': self.auth_user_id_1})
        patch('rest_api_server.controllers.cloud_account.'
              'CloudAccountController._configure_report').start()
        _, self.cloud_acc1 = self.create_cloud_account(
            self.org_id, self.valid_kubernetes_cloud_acc,
            auth_user_id=self.auth_user_id_1)
        now = int(datetime.utcnow().timestamp())
        self.base_payload = {
            'start_date': now, 'end_date': now + 12345}

    def test_metrics_invalid_dates(self):
        validation_params = [
            ('start_date', int(datetime.utcnow().timestamp()) + 1000000,
             'OE0446'),
            ('start_date', 'aaa', 'OE0217'),
            ('start_date', None, 'OE0216'),
            ('end_date', 'aaa', 'OE0217')
        ]
        for (key, value, error_code) in validation_params:
            payload = self.base_payload.copy()
            payload[key] = value
            code, res = self.client.k8s_rightsizing_get(self.org_id, payload)
            self.assertEqual(code, 400)
            self.assertEqual(res['error']['error_code'], error_code)

    def test_metrics_nonexistent_cloud_acc_id(self):
        payload = self.base_payload.copy()
        payload['cloud_account_id'] = str(uuid.uuid4())
        code, res = self.client.k8s_rightsizing_get(self.org_id, payload)
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0005')

    @patch('metroculus_client.client.Client.get_k8s_metrics')
    def test_metrics_empty(self, p_get_k8s_metrics):
        p_get_k8s_metrics.return_value = (200, {})
        payload = self.base_payload.copy()
        code, res = self.client.k8s_rightsizing_get(self.org_id, payload)
        self.assertEqual(code, 200)
        self.assertTrue(isinstance(res, dict))
        self.assertEqual(res, {'start_date': payload['start_date'],
                               'end_date': payload['end_date'],
                               'k8s_app_rightsizing': []})

    @patch('metroculus_client.client.Client.get_k8s_metrics')
    def test_k8s_metrics(self, p_get_k8s_metrics):
        payload = self.base_payload.copy()
        p_get_k8s_metrics.return_value = (
            200, {
                'start_date': payload['start_date'],
                'end_date': payload['end_date'],
                self.cloud_acc1['id']: [
                    {
                        "resource_id": "b060d3ce-b19e-423b-bfe0-dbb082e73630",
                        "average_pod_cpu_used": 0.029059039428830147,
                        "pod_cpu_provision": 3.0,
                        "pod_cpu_requests": 3.0,
                        "total_pod_cpu_requests": 9.0,
                        "average_pod_memory_used": 1118208.0,
                        "pod_memory_provision": 524288000.0,
                        "pod_memory_requests": 73400320.0,
                        "total_pod_memory_requests_gb": 2.2,
                        "total_pod_cpu_used": 2204.360654234886,
                        "total_pod_memory_used": 84825022464.0,
                        "namespace_cpu_provision_used": 0.0,
                        "namespace_memory_provision_used": 0.0,
                        "namespace_quota_cpu_provision_hard": 0.0,
                        "namespace_quota_memory_provision_hard": 0.0,
                        "namespace_quota_cpu_provision_medium": 0.0,
                        "namespace_quota_memory_provision_medium": 0.0,
                        "namespace_quota_cpu_provision_low": 0.0,
                        "namespace_quota_memory_provision_low": 0.0,
                        "namespace_cpu_requests_used": 0.0,
                        "namespace_memory_requests_used": 0.0,
                        "namespace_quota_cpu_requests_hard": 0.0,
                        "namespace_quota_memory_requests_hard": 0.0,
                        "namespace_quota_cpu_requests_medium": 0.0,
                        "namespace_quota_memory_requests_medium": 0.0,
                        "namespace_quota_cpu_requests_low": 0.0,
                        "namespace_quota_memory_requests_low": 0.0
                    },
                    {
                        "resource_id": "54f12c27-92ab-48c4-aa48-bc93d27bf49d",
                        "average_pod_cpu_used": 0.02814026176929474,
                        "pod_cpu_provision": 3.0,
                        "pod_cpu_requests": 2.0,
                        "total_pod_cpu_requests": 6.0,
                        "average_pod_memory_used": 770048.0,
                        "pod_memory_provision": 524288000.0,
                        "pod_memory_requests": 524288000.0,
                        "total_pod_memory_requests_gb": 2.2,
                        "total_pod_cpu_used": 2134.6639907360077,
                        "total_pod_memory_used": 58414301184.0,
                        "namespace_cpu_provision_used": 0.0,
                        "namespace_memory_provision_used": 0.0,
                        "namespace_quota_cpu_provision_hard": 0.0,
                        "namespace_quota_memory_provision_hard": 0.0,
                        "namespace_quota_cpu_provision_medium": 0.0,
                        "namespace_quota_memory_provision_medium": 0.0,
                        "namespace_quota_cpu_provision_low": 0.0,
                        "namespace_quota_memory_provision_low": 0.0,
                        "namespace_cpu_requests_used": 0.0,
                        "namespace_memory_requests_used": 0.0,
                        "namespace_quota_cpu_requests_hard": 0.0,
                        "namespace_quota_memory_requests_hard": 0.0,
                        "namespace_quota_cpu_requests_medium": 0.0,
                        "namespace_quota_memory_requests_medium": 0.0,
                        "namespace_quota_cpu_requests_low": 0.0,
                        "namespace_quota_memory_requests_low": 0.0
                    },
                    {
                        "resource_id": "835cc259-833c-4dcd-9c75-7b15caae682a",
                        "average_pod_cpu_used": 0.012218659743666649,
                        "pod_cpu_provision": 0.0,
                        "pod_cpu_requests": 0.0,
                        "total_pod_cpu_requests": 0.0,
                        "average_pod_memory_used": 491520.0,
                        "pod_memory_provision": 0.0,
                        "pod_memory_requests": 0.0,
                        "total_pod_memory_requests_gb": 0.0,
                        "total_pod_cpu_used": 926.8831110596657,
                        "total_pod_memory_used": 37285724160.0,
                        "namespace_cpu_provision_used": 0.0,
                        "namespace_memory_provision_used": 0.0,
                        "namespace_quota_cpu_provision_hard": 0.0,
                        "namespace_quota_memory_provision_hard": 0.0,
                        "namespace_quota_cpu_provision_medium": 0.0,
                        "namespace_quota_memory_provision_medium": 0.0,
                        "namespace_quota_cpu_provision_low": 0.0,
                        "namespace_quota_memory_provision_low": 0.0,
                        "namespace_cpu_requests_used": 0.0,
                        "namespace_memory_requests_used": 0.0,
                        "namespace_quota_cpu_requests_hard": 0.0,
                        "namespace_quota_memory_requests_hard": 0.0,
                        "namespace_quota_cpu_requests_medium": 0.0,
                        "namespace_quota_memory_requests_medium": 0.0,
                        "namespace_quota_cpu_requests_low": 0.0,
                        "namespace_quota_memory_requests_low": 0.0
                    }
                ]
            }
        )
        code, res = self.client.k8s_rightsizing_get(self.org_id,
                                                    payload)
        self.assertEqual(code, 200)
        self.assertTrue(isinstance(res, dict))
        self.assertNotEqual(res, {})

    def test_k8s_metrics_unexpected_params(self):
        payload = self.base_payload.copy()
        payload['new_param'] = 4
        code, res = self.client.k8s_rightsizing_get(self.org_id,
                                                    payload)
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0212')
