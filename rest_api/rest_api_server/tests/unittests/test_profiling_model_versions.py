import uuid
from unittest.mock import patch
from rest_api.rest_api_server.tests.unittests.test_profiling_base import (
    TestProfilingBase)


class TestModelVersionApi(TestProfilingBase):

    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.org = self.client.organization_create({'name': "organization"})
        self.valid_model_version = {
            'path': 'path',
            'version': '1',
            'aliases': ['best']
        }
        auth_user = str(uuid.uuid4())
        _, self.employee = self.client.employee_create(
            self.org['id'], {'name': 'name1', 'auth_user_id': auth_user})
        patch('rest_api.rest_api_server.controllers.base.BaseController.'
              'get_user_id', return_value=auth_user).start()

    def test_create_model_version(self):
        code, resp = self.client.model_version_create(
            self.org['id'], 'run_id', 'model_id', self.valid_model_version)
        self.assertEqual(code, 201)
        for k, v in self.valid_model_version.items():
            self.assertEqual(v, resp[k])

        code, resp = self.client.model_version_create(
            self.org['id'], 'run_id1', 'model_id1', {})
        self.assertEqual(code, 201)

    def test_create_model_version_duplicate(self):
        code, resp = self.client.model_version_create(
            self.org['id'], 'run_id', 'model_id', self.valid_model_version)
        self.assertEqual(code, 201)
        for k, v in self.valid_model_version.items():
            self.assertEqual(v, resp[k])

        code, resp = self.client.model_version_create(
            self.org['id'], 'run_id', 'model_id', {})
        self.assertEqual(code, 409)
        self.assertEqual(resp['error']['error_code'], 'OE0557')

    def test_create_invalid_params(self):
        for param in ['path', 'version']:
            for value in [1, {'test': 1}, ['test']]:
                body = {
                    param: value
                }
                code, resp = self.client.model_version_create(
                    self.org['id'], 'run_id', 'model_id', body)
                self.assertEqual(code, 400)
                self.assertEqual(resp['error']['error_code'], 'OE0214')

        for value in [1, 'test', {'test': 1}]:
            body = {
                'aliases': value
            }
            code, resp = self.client.model_version_create(
                self.org['id'], 'run_id', 'model_id', body)
            self.assertEqual(code, 400)
            self.assertEqual(resp['error']['error_code'], 'OE0385')

        for value in [1, 'test', ['test']]:
            body = {
                'tags': value
            }
            code, resp = self.client.model_version_update(
                self.org['id'], 'run_id', 'model_id', **body)
            self.assertEqual(code, 400)
            self.assertEqual(resp['error']['error_code'], 'OE0344')

    def test_create_unexpected(self):
        for param in ['deleted_at', '_id', 'unexpected']:
            body = {
                param: 'test'
            }
            code, resp = self.client.model_version_create(
                self.org['id'], 'run_id', 'model_id', body)
            self.assertEqual(code, 400)
            self.assertEqual(resp['error']['error_code'], 'OE0212')

    def test_patch_model_version(self):
        code, _ = self.client.model_version_create(
            self.org['id'], 'run_id', 'model_id', self.valid_model_version)
        self.assertEqual(code, 201)
        body = {'path': 'new'}
        code, resp = self.client.model_version_update(
            self.org['id'], 'run_id', 'model_id', **body)
        self.assertEqual(code, 200)
        self.assertEqual(resp['path'], body['path'])

    def test_patch_invalid_params(self):
        code, model = self.client.model_version_create(
            self.org['id'], 'run_id', 'model_id', self.valid_model_version)
        self.assertEqual(code, 201)
        for param in ['path', 'version']:
            for value in [1, {'test': 1}, ['test']]:
                body = {
                    param: value
                }
                code, resp = self.client.model_version_update(
                    self.org['id'], 'run_id', 'model_id', **body)
                self.assertEqual(code, 400)
                self.assertEqual(resp['error']['error_code'], 'OE0214')

        for value in [1, 'test', {'test': 1}]:
            body = {
                'aliases': value
            }
            code, resp = self.client.model_version_update(
                self.org['id'], 'run_id', 'model_id', **body)
            self.assertEqual(code, 400)
            self.assertEqual(resp['error']['error_code'], 'OE0385')

        for value in [1, 'test', ['test']]:
            body = {
                'tags': value
            }
            code, resp = self.client.model_version_update(
                self.org['id'], 'run_id', 'model_id', **body)
            self.assertEqual(code, 400)
            self.assertEqual(resp['error']['error_code'], 'OE0344')

    def test_patch_unexpected(self):
        code, model_version = self.client.model_version_create(
            self.org['id'], 'run_id', 'model_id', self.valid_model_version)
        self.assertEqual(code, 201)
        for param in ['deleted_at', '_id', 'unexpected']:
            body = {
                param: 'test'
            }
            code, resp = self.client.model_version_update(
                self.org['id'], model_version['run_id'],
                model_version['model_id'], **body)
            self.assertEqual(code, 400)
            self.assertEqual(resp['error']['error_code'], 'OE0212')

    def test_patch_not_existing(self):
        body = {'version': '1'}
        code, resp = self.client.model_version_update(
            self.org['id'], 'run_id', 'model_id', **body)
        self.assertEqual(code, 404)
        self.assertEqual(resp['error']['error_code'], 'OE0002')

    def test_delete(self):
        code, model_version = self.client.model_version_create(
            self.org['id'], 'run_id', 'model_id', self.valid_model_version)
        self.assertEqual(code, 201)
        code, resp = self.client.model_version_delete(
            self.org['id'], model_version['run_id'],
            model_version['model_id'])
        self.assertEqual(code, 204)

    def test_get(self):
        code, model_version = self.client.get(
            self.client.run_model_version_url(
                self.org['id'], 'run_id', 'model_id'))
        self.assertEqual(code, 405)

    def test_delete_not_existing(self):
        code, resp = self.client.model_version_delete(
            self.org['id'], 'run_id', 'model_id')
        self.assertEqual(code, 404)
        self.assertEqual(resp['error']['error_code'], 'OE0002')

    def test_get_model_versions_by_task(self):
        code, resp = self.client.model_versions_by_task(
            self.org['id'], 'task_id')
        self.assertEqual(code, 200)
        self.assertEqual(resp['model_versions'], [])

    def test_get_model_versions_by_task_empty(self):
        code, task = self.client.task_create(
            self.org['id'], {'key': 'test_project', 'name': 'test'})
        self.assertEqual(code, 201)
        run = self._create_run(self.org['id'], task['id'])
        code, model = self.client.model_create(self.org['id'], {'key': 'key'})
        code, model_version = self.client.model_version_create(
            self.org['id'], run['_id'], model['id'], self.valid_model_version)
        self.assertEqual(code, 201)

        code, resp = self.client.model_versions_by_task(
            self.org['id'], task['id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['model_versions']), 1)
