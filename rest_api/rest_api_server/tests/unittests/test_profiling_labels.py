import uuid
from datetime import datetime, timedelta
from unittest.mock import patch

from freezegun import freeze_time

from rest_api.rest_api_server.tests.unittests.test_profiling_base import (
    TestProfilingBase)


class TestLabelApi(TestProfilingBase):
    def setUp(self, version='v2'):
        super().setUp(version)
        _, org = self.client.organization_create({'name': "organization"})
        self.organization_id = org['id']
        auth_user = self.gen_id()
        _, employee = self.client.employee_create(
            self.organization_id, {'name': 'employee',
                                   'auth_user_id': auth_user})
        self.employee_id = employee['id']
        patch('rest_api.rest_api_server.controllers.base.BaseController.'
              'get_user_id', return_value=auth_user).start()
        user = {
            'id': auth_user,
            'display_name': 'default',
            'email': 'email@email.com',
        }
        patch('rest_api.rest_api_server.handlers.v1.base.BaseAuthHandler._get_user_info',
              return_value=user).start()
        self.valid_dataset = {
            'path': 's3://ml-bucket/dataset',
            'name': 'Test',
            'description': 'Test ML dataset',
            'labels': ['test', 'demo']
        }

    def test_list_no_dataset(self):
        code, res = self.client.labels_list(self.organization_id)
        self.assertEqual(code, 200)
        self.assertFalse(res.get('labels', []))

    def test_list_dataset_no_labels(self):
        valid_dataset = self.valid_dataset
        valid_dataset['labels'] = []
        code, dataset = self.client.dataset_create(
            self.organization_id, valid_dataset)
        self.assertEqual(code, 201)
        code, res = self.client.labels_list(self.organization_id)
        self.assertEqual(code, 200)
        self.assertFalse(res.get('labels', []))

    def test_list_dataset_deleted(self):
        code, dataset = self.client.dataset_create(
            self.organization_id, self.valid_dataset)
        self.assertEqual(code, 201)
        code, _ = self.client.dataset_delete(
            self.organization_id, dataset['id'])
        code, res = self.client.labels_list(self.organization_id)
        self.assertEqual(code, 200)
        self.assertFalse(res.get('labels', []))

    def test_list(self):
        for x in range(5):
            valid_dataset = self.valid_dataset.copy()
            valid_dataset['path'] = str(uuid.uuid4())
            code, dataset = self.client.dataset_create(
                self.organization_id, valid_dataset)
            self.assertEqual(code, 201)
        code, res = self.client.labels_list(self.organization_id)
        self.assertEqual(code, 200)
        self.assertListEqual(res.get('labels', []), self.valid_dataset['labels'])

    def test_list_order(self):
        labels_string = 'abcde'
        for x in range(len(labels_string)):
            valid_dataset = self.valid_dataset.copy()
            valid_dataset['path'] = labels_string[x]
            valid_dataset['labels'] = list(labels_string[x: x + 2])
            with freeze_time(datetime(2020, 1, 15) + timedelta(days=x)):
                code, dataset = self.client.dataset_create(
                    self.organization_id, valid_dataset)
                self.assertEqual(code, 201)
        code, res = self.client.labels_list(self.organization_id)
        self.assertEqual(code, 200)
        self.assertListEqual(res.get('labels', []), list(labels_string[::-1]))
