import uuid
from datetime import datetime
from unittest.mock import patch
from rest_api_server.tests.unittests.test_api_base import TestApiBase


class TestTrafficProcessingTaskApi(TestApiBase):

    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.org = self.client.organization_create(
            {'name': "organization"})
        patch('rest_api_server.controllers.cloud_account.'
              'CloudAccountController._configure_report').start()
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
            'type': 'azure_cnr',
            'config': {
                'subscription_id': 'id',
                'secret': 'secret',
                'client_id': 'id',
                'tenant': 't',
            }
        }
        self.auth_user_id_1 = self.gen_id()
        _, self.employee1 = self.client.employee_create(
            self.org['id'],
            {'name': 'name1', 'auth_user_id': self.auth_user_id_1})
        _, self.cloud_acc1 = self.create_cloud_account(
            self.org['id'], cloud_acc1, auth_user_id=self.auth_user_id_1)
        _, self.cloud_acc2 = self.create_cloud_account(
            self.org['id'], cloud_acc2, auth_user_id=self.auth_user_id_1)
        self.valid_body = {
            'start_date': int(datetime(2021, 1, 1).timestamp()),
            'end_date': int(datetime(2021, 1, 2).timestamp())
        }

    def test_create(self):
        code, resp = self.client.traffic_processing_task_create(
            self.cloud_acc1['id'], self.valid_body)
        self.assertEqual(code, 201)
        self.assertEqual(resp['start_date'], self.valid_body['start_date'])
        self.assertEqual(resp['end_date'], self.valid_body['end_date'])

    def test_create_without_params(self):
        for k in ['start_date', 'end_date']:
            params = self.valid_body.copy()
            params.pop(k)
            code, resp = self.client.traffic_processing_task_create(
                self.cloud_acc1['id'], params)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0216')

    def test_create_invalid_params(self):
        for p in ['start_date', 'end_date']:
            params = self.valid_body.copy()
            params[p] = 2 ** 31
            code, resp = self.client.traffic_processing_task_create(
                self.cloud_acc1['id'], params)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0224')
            for k in ['123', '']:
                params[p] = k
                code, resp = self.client.traffic_processing_task_create(
                    self.cloud_acc1['id'], params)
                self.assertEqual(code, 400)
                self.verify_error_code(resp, 'OE0223')

    def test_create_invalid_range(self):
        params = {
            'start_date': 2,
            'end_date': 1
        }
        code, resp = self.client.traffic_processing_task_create(
            self.cloud_acc1['id'], params)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0446')

    def test_create_cloud_account_id_in_body(self):
        self.valid_body['cloud_account_id'] = '123'
        code, resp = self.client.traffic_processing_task_create(
            self.cloud_acc1['id'], self.valid_body)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0456')

    def test_create_immutable_params(self):
        for immutable in ['deleted_at', 'created_at', 'id']:
            body = self.valid_body.copy()
            body[immutable] = 'test'
            code, resp = self.client.traffic_processing_task_create(
                self.cloud_acc1['id'], body)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0211')

    def test_create_unexpected_params(self):
        self.valid_body['unex'] = '123'
        code, resp = self.client.traffic_processing_task_create(
            self.cloud_acc1['id'], self.valid_body)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0212')

    def test_create_invalid_cloud_acc(self):
        for cloud_account_id in [str(uuid.uuid4()), '123', 132]:
            code, resp = self.client.traffic_processing_task_create(
                cloud_account_id, self.valid_body)
            self.assertEqual(code, 404)
            self.verify_error_code(resp, 'OE0002')

    def test_create_duplicate(self):
        code, resp = self.client.traffic_processing_task_create(
            self.cloud_acc1['id'], self.valid_body)
        self.assertEqual(code, 201)

        body = {
            'start_date': self.valid_body['start_date'] - 1,
            'end_date': self.valid_body['end_date'] + 1
        }
        code, resp = self.client.traffic_processing_task_create(
            self.cloud_acc1['id'], body)
        self.assertEqual(code, 201)

        code, resp = self.client.traffic_processing_task_create(
            self.cloud_acc1['id'], self.valid_body)
        self.assertEqual(code, 409)
        self.verify_error_code(resp, 'OE0519')

    def test_empty_list(self):
        code, resp = self.client.traffic_processing_task_list(
            self.cloud_acc1['id'])
        self.assertEqual(code, 200)
        self.assertEqual(resp['traffic_processing_tasks'], [])

    def test_list(self):
        code, task1 = self.client.traffic_processing_task_create(
            self.cloud_acc1['id'], self.valid_body)
        self.assertEqual(code, 201)
        self.valid_body['end_date'] += 1
        code, task1_1 = self.client.traffic_processing_task_create(
            self.cloud_acc1['id'], self.valid_body)
        self.assertEqual(code, 201)
        code, task2 = self.client.traffic_processing_task_create(
            self.cloud_acc2['id'], self.valid_body)
        self.assertEqual(code, 201)

        code, resp = self.client.traffic_processing_task_list(
            self.cloud_acc1['id'])
        self.assertEqual(code, 200)
        tasks = resp['traffic_processing_tasks']
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0]['id'], task1['id'])
        self.assertEqual(tasks[1]['id'], task1_1['id'])

        code, resp = self.client.traffic_processing_task_list(
            self.cloud_acc2['id'])
        self.assertEqual(code, 200)
        tasks = resp['traffic_processing_tasks']
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]['id'], task2['id'])

        # non-existing cloud account id should result in 404
        code, resp = self.client.traffic_processing_task_list(
            'non-existing-account-id')
        self.assertEqual(code, 404)
        self.verify_error_code(resp, 'OE0002')

        # deleted cloud account should result in 404
        code, _ = self.client.cloud_account_delete(self.cloud_acc1['id'])
        self.assertEqual(code, 204)
        code, resp = self.client.traffic_processing_task_list(
            self.cloud_acc1['id'])
        self.assertEqual(code, 404)
        self.verify_error_code(resp, 'OE0002')

        # empty cloud account id should result in 404
        code, _ = self.client.traffic_processing_task_list(None)
        self.assertEqual(code, 404)

    def test_delete_not_existing(self):
        code, resp = self.client.traffic_processing_task_delete('fake')
        self.assertEqual(code, 404)
        self.verify_error_code(resp, 'OE0002')

    def test_delete(self):
        code, task = self.client.traffic_processing_task_create(
            self.cloud_acc1['id'], self.valid_body)
        self.assertEqual(code, 201)
        code, _ = self.client.traffic_processing_task_delete(task['id'])
        self.assertEqual(code, 204)
        code, resp = self.client.traffic_processing_task_list(
            self.cloud_acc1['id'])
        self.assertEqual(resp['traffic_processing_tasks'], [])

    def test_403(self):
        self.client.secret = None
        code, _ = self.client.traffic_processing_task_create(
            self.cloud_acc1['id'], self.valid_body)
        self.assertEqual(code, 403)
        code, _ = self.client.traffic_processing_task_list(
            self.cloud_acc1['id'])
        self.assertEqual(code, 403)
        code, _ = self.client.traffic_processing_task_delete('fake')
        self.assertEqual(code, 403)
