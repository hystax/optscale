import datetime
import uuid

from unittest.mock import patch

from rest_api.rest_api_server.tests.unittests.test_profiling_base import (
    TestProfilingBase)


class TestDatasetApi(TestProfilingBase):
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
            'labels': ['test', 'demo'],
            'timespan_from': 1698740386,
            'timespan_to': 1698741386
        }

    def test_create(self):
        code, dataset = self.client.dataset_create(
            self.organization_id, self.valid_dataset)
        self.assertEqual(code, 201)
        for k, v in self.valid_dataset.items():
            self.assertEqual(dataset[k], v)
        self.assertTrue('token' not in dataset)

    def test_create_incorrect_timespan(self):
        valid_dataset = self.valid_dataset.copy()
        valid_dataset['timespan_from'] = int(
            datetime.datetime.utcnow().timestamp()) + 100
        code, dataset = self.client.dataset_create(
            self.organization_id, valid_dataset)
        self.assertEqual(code, 400)

    def test_create_incorrect(self):
        incorrect_updates = {
            'name': [1],
            'path': True,
            'labels': 3,
            'description': {'text': 'Some description'},
        }
        for k, v in incorrect_updates.items():
            valid_dataset = self.valid_dataset.copy()
            valid_dataset[k] = v
            code, _ = self.client.dataset_create(
                self.organization_id, valid_dataset)
            self.assertEqual(code, 400, k)

    def test_create_unexpected(self):
        valid_dataset = self.valid_dataset.copy()
        valid_dataset['extra'] = 'value'
        code, res = self.client.dataset_create(
            self.organization_id, valid_dataset)
        self.assertEqual(code, 400)
        self.assertEqual(res.get('error', {}).get('error_code'), 'OE0212')

        valid_dataset = self.valid_dataset.copy()
        for k in ['training_set', 'validation_set']:
            valid_dataset[k] = {}
            code, res = self.client.dataset_create(
                self.organization_id, valid_dataset)
            self.assertEqual(code, 400)
            self.assertEqual(res.get('error', {}).get('error_code'), 'OE0212')

    def test_create_missing(self):
        valid_dataset = self.valid_dataset.copy()
        # remove the only required field from payload
        valid_dataset.pop('path')
        code, res = self.client.dataset_create(
            self.organization_id, valid_dataset)
        self.assertEqual(code, 400)
        self.assertEqual(res.get('error', {}).get('error_code'), 'OE0216')

    def test_get(self):
        code, dataset = self.client.dataset_create(
            self.organization_id, self.valid_dataset)
        self.assertEqual(code, 201)
        code, resp = self.client.dataset_get(
            self.organization_id, dataset['id'])
        self.assertEqual(code, 200)
        self.assertEqual(resp, dataset)

    def test_get_nonexisting(self):
        code, _ = self.client.dataset_get(
            self.organization_id, str(uuid.uuid4()))
        self.assertEqual(code, 404)

    def test_delete(self):
        code, dataset = self.client.dataset_create(
            self.organization_id, self.valid_dataset)
        self.assertEqual(code, 201)
        code, resp = self.client.dataset_delete(
            self.organization_id, dataset['id'])
        self.assertEqual(code, 204)
        code, resp = self.client.dataset_delete(
            self.organization_id, dataset['id'])
        self.assertEqual(code, 404)

    def test_delete_nonexisting(self):
        code, _ = self.client.dataset_delete(
            self.organization_id, str(uuid.uuid4()))
        self.assertEqual(code, 404)

    def test_update(self):
        code, dataset = self.client.dataset_create(
            self.organization_id, self.valid_dataset)
        self.assertEqual(code, 201)
        updates = {
            'name': 'new_name',
            'description': 'new_description',
            'labels': ['new', 'labels'],
            'timespan_from': int(datetime.datetime(2024, 12, 11).timestamp()),
            'timespan_to': int(datetime.datetime(2024, 12, 11).timestamp()),
        }
        code, dataset = self.client.dataset_update(
            self.organization_id, dataset['id'], updates)
        self.assertEqual(code, 200)
        for k, v in updates.items():
            self.assertEqual(dataset[k], v)

    def test_update_nonexisting(self):
        updates = {
            'name': 'new_name',
        }
        code, _ = self.client.dataset_update(
            self.organization_id, str(uuid.uuid4()), updates)
        self.assertEqual(code, 404)

    def test_update_incorrect(self):
        code, dataset = self.client.dataset_create(
            self.organization_id, self.valid_dataset)
        self.assertEqual(code, 201)
        updates_base = {
            'name': [0],
            'description': False,
            'labels': -1,
            'timespan_from': 'test',
            'timespan_to': {'key': 'value'}
        }
        for k, v in updates_base.items():
            updates = {k: v}
            code, _ = self.client.dataset_update(
                self.organization_id, dataset['id'], updates)
            self.assertEqual(code, 400)

    def test_update_reset(self):
        code, dataset = self.client.dataset_create(
            self.organization_id, self.valid_dataset)
        self.assertEqual(code, 201)
        updates = ['name', 'description', 'labels', 'timespan_from',
                   'timespan_to']
        for k in updates:
            updates = {k: None}
            code, dataset_ = self.client.dataset_update(
                self.organization_id, dataset['id'], updates)
            self.assertEqual(code, 200)
            self.assertIsNone(dataset_[k])

    def test_update_empty(self):
        code, dataset = self.client.dataset_create(
            self.organization_id, self.valid_dataset)
        self.assertEqual(code, 201)
        updates = {
            'name': '',
            'description': '',
            'labels': [],
            'timespan_from': None,
            'timespan_to': None
        }
        for k, v in updates.items():
            updates = {k: v}
            code, dataset_ = self.client.dataset_update(
                self.organization_id, dataset['id'], updates)
            self.assertEqual(code, 200)
            self.assertEqual(dataset_[k], v)

    def test_update_unexpected(self):
        code, dataset = self.client.dataset_create(
            self.organization_id, self.valid_dataset)
        self.assertEqual(code, 201)
        code, res = self.client.dataset_update(
            self.organization_id, dataset['id'], {'extra': 'value'})
        self.assertEqual(code, 400)
        self.assertEqual(res.get('error', {}).get('error_code'), 'OE0212')

    def test_list_empty(self):
        code, res = self.client.dataset_list(self.organization_id)
        self.assertEqual(code, 200)
        self.assertFalse(res.get('datasets', []))

    def test_list(self):
        code, dataset = self.client.dataset_create(
            self.organization_id, self.valid_dataset)
        self.assertEqual(code, 201)
        code, res = self.client.dataset_list(self.organization_id)
        self.assertEqual(code, 200)
        self.assertTrue(res.get('datasets', []))
        for d in res['datasets']:
            self.assertEqual(dataset['id'], d['id'])
            self.assertEqual(dataset['name'], d['name'])
            self.assertEqual(dataset['path'], d['path'])
            self.assertEqual(dataset['description'], d['description'])
            self.assertEqual(dataset['labels'], d['labels'])

    def test_list_bulk(self):
        code, dataset_1 = self.client.dataset_create(
            self.organization_id, self.valid_dataset)
        self.assertEqual(code, 201)
        code, dataset_2 = self.client.dataset_create(
            self.organization_id, self.valid_dataset)
        self.assertEqual(code, 201)
        code, dataset_3 = self.client.dataset_create(
            self.organization_id, self.valid_dataset)
        self.assertEqual(code, 201)
        code, res = self.client.dataset_list(self.organization_id)
        self.assertEqual(len(res['datasets']), 3)

        code, res = self.client.dataset_list(self.organization_id,
                                             dataset_ids=[dataset_2['id']])
        self.assertEqual(len(res['datasets']), 1)
        self.assertEqual(res['datasets'][0]['id'], dataset_2['id'])

        dataset_ids = [dataset_1['id'], dataset_3['id']]
        code, res = self.client.dataset_list(self.organization_id,
                                             dataset_ids=dataset_ids)
        self.assertEqual(len(res['datasets']), 2)
        for d in res['datasets']:
            self.assertTrue(d['id'] in dataset_ids)

    def test_list_deleted(self):
        code, dataset = self.client.dataset_create(
            self.organization_id, self.valid_dataset)
        self.assertEqual(code, 201)
        code, _ = self.client.dataset_delete(
            self.organization_id, dataset['id'])
        code, res = self.client.dataset_list(self.organization_id)
        self.assertEqual(code, 200)
        self.assertFalse(res.get('datasets', []))
