import uuid
from datetime import datetime
from unittest.mock import patch

from rest_api.rest_api_server.tests.unittests.test_api_base import TestApiBase


class TestResourceMetrics(TestApiBase):
    def setUp(self, version='v2'):
        super().setUp(version)
        patch('optscale_client.config_client.client.Client.metroculus_url').start()
        _, self.org = self.client.organization_create(
            {'name': "partner_test"})
        valid_aws_creds = {
            'name': 'my creds',
            'type': 'aws_cnr',
            'config': {
                'access_key_id': 'key',
                'secret_access_key': 'secret',
                'config_scheme': 'create_report'
            }
        }
        self.user_id = self.gen_id()
        _, self.employee = self.client.employee_create(
            self.org['id'], {'name': 'Eliot Alderson', 'auth_user_id': self.user_id})
        patch('rest_api.rest_api_server.controllers.cloud_account.'
              'CloudAccountController._configure_report').start()
        _, cloud_account = self.create_cloud_account(
            self.org['id'], valid_aws_creds, auth_user_id=self.user_id)
        self.valid_resource = {
            'cloud_resource_id': self.gen_id(),
            'name': 'test_resource',
            'resource_type': 'test_type',
            'employee_id': self.employee['id'],
            'pool_id': self.org['pool_id']
        }
        _, self.resource = self._create_cloud_resource(
            cloud_account['id'], self.valid_resource)

        now = int(datetime.utcnow().timestamp())
        self.base_payload = {
            'start_date': now, 'end_date': now + 12345, 'interval': 900}

    def _create_cloud_resource(self, cloud_acc_id, params, active=True,
                               valid_until=None, request_id=None):
        code, resource = self.cloud_resource_create(
            cloud_acc_id, params)
        if active:
            self.resources_collection.update_one(
                filter={
                    '_id': resource['id']
                },
                update={'$set': {
                    'last_seen': int(datetime.utcnow().timestamp() - 1),
                    'active': True
                }}
            )
        return code, resource

    def test_metrics_interval_multiplier(self):
        payload = self.base_payload.copy()
        for interval in [899, 901, 2000]:
            payload['interval'] = interval
            code, res = self.client.resource_metrics_get(
                self.resource['id'], payload)
            self.assertEqual(code, 400)
            self.assertEqual(res['error']['error_code'], 'OE0474')

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
            code, res = self.client.resource_metrics_get(
                self.resource['id'], payload)
            self.assertEqual(code, 400)
            self.assertEqual(res['error']['error_code'], error_code)

    def test_metrics_nonexistent_resource(self):
        payload = self.base_payload.copy()
        code, res = self.client.resource_metrics_get(
            str(uuid.uuid4()), payload)
        self.assertEqual(code, 404)
        self.assertEqual(res['error']['error_code'], 'OE0002')

    @patch('optscale_client.metroculus_client.client.Client.get_metrics')
    def test_metrics_empty(self, p_get_metrics):
        p_get_metrics.return_value = (200, {})
        payload = self.base_payload.copy()
        code, res = self.client.resource_metrics_get(
            self.resource['id'], payload)
        self.assertEqual(code, 200)
        self.assertTrue(isinstance(res, dict))
        self.assertEqual(res, {})

    @patch('optscale_client.metroculus_client.client.Client.get_metrics')
    def test_metrics(self, p_get_metrics):
        p_get_metrics.return_value = (
            200, {
                'cpu': [
                    {
                        'date': 1625097600,
                        'value': 24
                    },
                    {
                        'date': 1625098500,
                        'value': 22
                    },
                    {
                        'date': 1625099400,
                        'value': 12
                    }
                ]
            }
        )
        payload = self.base_payload.copy()
        code, res = self.client.resource_metrics_get(self.resource['id'], payload)
        self.assertEqual(code, 200)
        self.assertTrue(isinstance(res, dict))
        self.assertNotEqual(res, {})
