import uuid
from unittest.mock import patch
from rest_api.rest_api_server.tests.unittests.test_profiling_base import (
    TestProfilingBase)


class TestModelApi(TestProfilingBase):

    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.org = self.client.organization_create({'name': "organization"})
        self.valid_model = {
            'name': 'My test project',
            'key': 'test_project',
            'description': 'Test description',
            'tags': {'tag': 'tag'}
        }
        auth_user = str(uuid.uuid4())
        _, self.employee = self.client.employee_create(
            self.org['id'], {'name': 'name1', 'auth_user_id': auth_user})
        patch('rest_api.rest_api_server.controllers.base.BaseController.'
              'get_user_id', return_value=auth_user).start()

    def test_create_model(self):
        code, resp = self.client.model_create(
            self.org['id'], self.valid_model)
        self.assertEqual(code, 201)
        for k, v in self.valid_model.items():
            self.assertEqual(v, resp[k])

        body = {'key': 'key'}
        code, resp = self.client.model_create(self.org['id'], body)
        self.assertEqual(code, 201)
        self.assertEqual(body['key'], resp['key'])

    def test_create_key(self):
        code, resp = self.client.model_create(self.org['id'], {})
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0216')

        for value in [1, {'test': 1}, ['test']]:
            body = {'key': value}
            code, resp = self.client.model_create(self.org['id'], body)
            self.assertEqual(code, 400)
            self.assertEqual(resp['error']['error_code'], 'OE0214')

    def test_create_invalid_params(self):
        for param in ['description', 'key', 'name']:
            for value in [1, {'test': 1}, ['test']]:
                body = {
                    'key': 'key',
                    param: value
                }
                code, resp = self.client.model_create(self.org['id'], body)
                self.assertEqual(code, 400)
                self.assertEqual(resp['error']['error_code'], 'OE0214')

        for value in [1, 'test', ['test']]:
            body = {
                'key': 'key',
                'tags': value
            }
            code, resp = self.client.model_create(self.org['id'], body)
            self.assertEqual(code, 400)
            self.assertEqual(resp['error']['error_code'], 'OE0344')

    def test_create_unexpected(self):
        for param in ['created_at', '_id', 'token', 'unexpected']:
            body = {
                'key': 'key',
                param: 'test'
            }
            code, resp = self.client.model_create(self.org['id'], body)
            self.assertEqual(code, 400)
            self.assertEqual(resp['error']['error_code'], 'OE0212')

    def test_list_models(self):
        code, model = self.client.model_create(
            self.org['id'], self.valid_model)
        self.assertEqual(code, 201)
        code, version = self.client.model_version_create(
            self.org['id'], model['id'], 'run_id', {'aliases': ['test']})
        code, resp = self.client.models_get(self.org['id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['models']), 1)
        for k, v in model.items():
            self.assertEqual(resp['models'][0][k], v)
        self.assertEqual(resp['models'][0]['last_version']['id'],
                         version['id'])
        self.assertEqual(resp['models'][0]['aliased_versions'][0]['id'],
                         version['id'])

    def test_list_empty(self):
        code, resp = self.client.models_get(self.org['id'])
        self.assertEqual(code, 200)
        self.assertEqual(resp, {'models': []})

    def test_patch(self):
        code, model = self.client.model_create(
            self.org['id'], self.valid_model)
        self.assertEqual(code, 201)
        body = {'name': 'new'}
        code, resp = self.client.model_update(
            self.org['id'], model['id'], **body)
        self.assertEqual(code, 200)
        self.assertEqual(resp['name'], body['name'])

    def test_patch_empty(self):
        code, model = self.client.model_create(
            self.org['id'], self.valid_model)
        self.assertEqual(code, 201)
        code, resp = self.client.model_update(
            self.org['id'], model['id'], **{})
        self.assertEqual(code, 200)
        for k, v in self.valid_model.items():
            self.assertEqual(resp[k], v)

    def test_patch_invalid_params(self):
        code, model = self.client.model_create(
            self.org['id'], self.valid_model)
        self.assertEqual(code, 201)
        for param in ['description', 'name']:
            for value in [1, {'test': 1}, ['test']]:
                body = {
                    param: value
                }
                code, resp = self.client.model_update(
                    self.org['id'], model['id'], **body)
                self.assertEqual(code, 400)
                self.assertEqual(resp['error']['error_code'], 'OE0214')
        for value in [1, 'test', ['test']]:
            body = {
                'tags': value
            }
            code, resp = self.client.model_update(
                self.org['id'], model['id'], **body)
            self.assertEqual(code, 400)
            self.assertEqual(resp['error']['error_code'], 'OE0344')

    def test_patch_unexpected(self):
        code, model = self.client.model_create(self.org['id'], self.valid_model)
        self.assertEqual(code, 201)
        for param in ['created_at', '_id', 'key', 'token', 'unexpected']:
            body = {
                param: 'test'
            }
            code, resp = self.client.model_update(
                self.org['id'], model['id'], **body)
            self.assertEqual(code, 400)
            self.assertEqual(resp['error']['error_code'], 'OE0212')

    def test_patch_not_existing(self):
        body = {'name': 'new'}
        code, resp = self.client.model_update(
            self.org['id'], 'model_id', **body)
        self.assertEqual(code, 404)
        self.assertEqual(resp['error']['error_code'], 'OE0002')

    def test_get_with_version(self):
        code, model = self.client.model_create(
            self.org['id'], self.valid_model)
        self.assertEqual(code, 201)
        code, _ = self.client.model_version_create(
            self.org['id'], model['id'], 'run_id', {})
        self.assertEqual(code, 201)

        code, resp = self.client.model_get(self.org['id'], model['id'])
        self.assertEqual(code, 200)
        for k, v in self.valid_model.items():
            self.assertEqual(resp[k], v)
        self.assertEqual(len(resp['versions']), 1)

    def test_get(self):
        code, model = self.client.model_create(
            self.org['id'], self.valid_model)
        self.assertEqual(code, 201)
        code, resp = self.client.model_get(self.org['id'], model['id'])
        self.assertEqual(code, 200)
        for k, v in self.valid_model.items():
            self.assertEqual(resp[k], v)

    def test_get_not_existing(self):
        code, resp = self.client.model_get(self.org['id'], 'model_id')
        self.assertEqual(code, 404)
        self.assertEqual(resp['error']['error_code'], 'OE0002')

    def test_delete(self):
        code, model = self.client.model_create(
            self.org['id'], self.valid_model)
        self.assertEqual(code, 201)
        code, resp = self.client.model_delete(self.org['id'], model['id'])
        self.assertEqual(code, 204)

    def test_delete_not_existing(self):
        code, resp = self.client.model_delete(self.org['id'], 'model_id')
        self.assertEqual(code, 404)
        self.assertEqual(resp['error']['error_code'], 'OE0002')
