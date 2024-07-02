import uuid
from rest_api.rest_api_server.tests.unittests.test_profiling_base import (
    TestProfilingBase)


class TestArtifactsApi(TestProfilingBase):

    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.org = self.client.organization_create({'name': "organization"})
        self.valid_artifact = {
            'run_id': str(uuid.uuid4()),
            'name': 'My test project',
            'path': 'test/path',
            'description': 'Test description',
            'tags': {'tag': 'tag'}
        }

    def test_create_artifact(self):
        code, resp = self.client.artifact_create(
            self.org['id'], self.valid_artifact)
        self.assertEqual(code, 201)
        for k, v in self.valid_artifact.items():
            self.assertEqual(v, resp[k])

    def test_create_required(self):
        code, resp = self.client.artifact_create(self.org['id'], {})
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0216')
        for param in ['run_id', 'path']:
            body = {
                'path': 'path',
                'run_id': 'run_id'
            }
            params = body.copy()
            params.pop(param, None)
            code, resp = self.client.artifact_create(self.org['id'], params)
            self.assertEqual(code, 400)
            self.assertEqual(resp['error']['error_code'], 'OE0216')

            for value in [1, {'test': 1}, ['test']]:
                body[param] = value
                code, resp = self.client.artifact_create(self.org['id'], body)
                self.assertEqual(code, 400)
                self.assertEqual(resp['error']['error_code'], 'OE0214')

    def test_create_invalid_params(self):
        for param in ['description', 'name']:
            for value in [1, {'test': 1}, ['test']]:
                body = {
                    'path': 'path',
                    'run_id': 'run_id',
                    param: value
                }
                code, resp = self.client.artifact_create(self.org['id'], body)
                self.assertEqual(code, 400)
                self.assertEqual(resp['error']['error_code'], 'OE0214')

        for value in [1, 'test', ['test']]:
            body = {
                'path': 'path',
                'run_id': 'run_id',
                'tags': value
            }
            code, resp = self.client.artifact_create(self.org['id'], body)
            self.assertEqual(code, 400)
            self.assertEqual(resp['error']['error_code'], 'OE0344')

    def test_create_unexpected(self):
        for param in ['created_at', '_id', 'token', 'unexpected']:
            body = {
                'path': 'path',
                'run_id': 'run_id',
                param: 'test'
            }
            code, resp = self.client.artifact_create(self.org['id'], body)
            self.assertEqual(code, 400)
            self.assertEqual(resp['error']['error_code'], 'OE0212')

    def test_list_artifacts(self):
        code, artifact = self.client.artifact_create(
            self.org['id'], self.valid_artifact)
        self.assertEqual(code, 201)
        code, resp = self.client.artifacts_get(
            self.org['id'], run_id=[self.valid_artifact['run_id']],
            created_at_gt=0, created_at_lt=artifact['created_at'] + 1, limit=1,
            start_from=0
        )
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['artifacts']), 1)
        self.assertEqual(resp['artifacts'][0]['id'], artifact['id'])

    def test_list_artifacts_invalid_params(self):
        for param in ['created_at_gt', 'created_at_lt', 'start_from', 'limit']:
            code, resp = self.client.artifacts_get(self.org['id'],
                                                   **{param: 'test'})
            self.assertEqual(code, 400)
            self.assertEqual(resp['error']['error_code'], 'OE0217')

            code, resp = self.client.artifacts_get(self.org['id'],
                                                   **{param: 2**64})
            self.assertEqual(code, 400)
            self.assertEqual(resp['error']['error_code'], 'OE0224')

    def test_list_empty(self):
        code, resp = self.client.artifacts_get(self.org['id'])
        self.assertEqual(code, 200)
        self.assertEqual(resp['artifacts'], [])

    def test_patch(self):
        code, artifact = self.client.artifact_create(
            self.org['id'], self.valid_artifact)
        self.assertEqual(code, 201)
        body = {'name': 'new'}
        code, resp = self.client.artifact_update(
            self.org['id'], artifact['id'], **body)
        self.assertEqual(code, 200)
        self.assertEqual(resp['name'], body['name'])

    def test_patch_empty(self):
        code, artifact = self.client.artifact_create(
            self.org['id'], self.valid_artifact)
        self.assertEqual(code, 201)
        code, resp = self.client.artifact_update(
            self.org['id'], artifact['id'], **{})
        self.assertEqual(code, 200)
        for k, v in self.valid_artifact.items():
            self.assertEqual(resp[k], v)

    def test_patch_invalid_params(self):
        code, artifact = self.client.artifact_create(
            self.org['id'], self.valid_artifact)
        self.assertEqual(code, 201)
        for param in ['description', 'name', 'path']:
            for value in [1, {'test': 1}, ['test']]:
                body = {
                    param: value
                }
                code, resp = self.client.artifact_update(
                    self.org['id'], artifact['id'], **body)
                self.assertEqual(code, 400)
                self.assertEqual(resp['error']['error_code'], 'OE0214')
        for value in [1, 'test', ['test']]:
            body = {
                'tags': value
            }
            code, resp = self.client.artifact_update(
                self.org['id'], artifact['id'], **body)
            self.assertEqual(code, 400)
            self.assertEqual(resp['error']['error_code'], 'OE0344')

    def test_patch_unexpected(self):
        code, artifact = self.client.artifact_create(
            self.org['id'], self.valid_artifact)
        self.assertEqual(code, 201)
        for param in ['created_at', '_id', 'run_id', 'token', 'unexpected']:
            body = {
                param: 'test'
            }
            code, resp = self.client.artifact_update(
                self.org['id'], artifact['id'], **body)
            self.assertEqual(code, 400)
            self.assertEqual(resp['error']['error_code'], 'OE0212')

    def test_patch_not_existing(self):
        body = {'name': 'new'}
        code, resp = self.client.artifact_update(
            self.org['id'], 'artifact_id', **body)
        self.assertEqual(code, 404)
        self.assertEqual(resp['error']['error_code'], 'OE0002')

    def test_get(self):
        code, artifact = self.client.artifact_create(
            self.org['id'], self.valid_artifact)
        self.assertEqual(code, 201)
        code, resp = self.client.artifact_get(self.org['id'], artifact['id'])
        self.assertEqual(code, 200)
        for k, v in self.valid_artifact.items():
            self.assertEqual(resp[k], v)

    def test_get_not_existing(self):
        code, resp = self.client.artifact_get(self.org['id'], 'artifact_id')
        self.assertEqual(code, 404)
        self.assertEqual(resp['error']['error_code'], 'OE0002')

    def test_delete(self):
        code, artifact = self.client.artifact_create(
            self.org['id'], self.valid_artifact)
        self.assertEqual(code, 201)
        code, resp = self.client.artifact_delete(
            self.org['id'], artifact['id'])
        self.assertEqual(code, 204)

    def test_delete_not_existing(self):
        code, resp = self.client.artifact_delete(
            self.org['id'], 'artifact_id')
        self.assertEqual(code, 404)
        self.assertEqual(resp['error']['error_code'], 'OE0002')
