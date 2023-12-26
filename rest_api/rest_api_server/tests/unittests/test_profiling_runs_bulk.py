import uuid
from rest_api.rest_api_server.tests.unittests.test_profiling_base import TestProfilingBase
from unittest.mock import patch


class TestRunsBulkApi(TestProfilingBase):

    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.org = self.client.organization_create({'name': "organization"})
        self.auth_user = str(uuid.uuid4())
        _, self.employee = self.client.employee_create(
            self.org['id'], {'name': 'name1', 'auth_user_id': self.auth_user})
        patch('rest_api.rest_api_server.controllers.base.BaseController.'
              'get_user_id', return_value=self.auth_user).start()
        _, self.app = self.client.application_create(
            self.org['id'], {
                'name': 'My test project',
                'key': 'test_project',
                'goals': []
            })

    def test_get_run_bulk(self):
        run1 = self._create_run(
            self.org['id'],
            self.app['id'],
            ['i-1', 'i-2'],
            's3://ml-bucket/dataset',
            data={'step': 1, 'loss': 0})
        run2 = self._create_run(
            self.org['id'],
            self.app['id'],
            ['i-1', 'i-2'],
            's3://ml-bucket/dataset',
            data={'step': 1, 'loss': 0})
        run3 = self._create_run(
            self.org['id'],
            self.app['id'],
            ['i-1', 'i-2'],
            's3://ml-bucket/dataset',
            data={'step': 1, 'loss': 0})
        code, runs = self.client.runs_bulk_get(
            self.org['id'],
            self.app['id'], [
                run1['_id'],
                run2['_id'],
                run3['_id']
            ])
        self.assertEqual(code, 200)
        self.assertEqual(len(runs), 3)
        resp_runs_ids = [x['id'] for x in runs]
        for run_id in [run1['_id'], run2['_id'], run3['_id']]:
            self.assertIn(run_id, resp_runs_ids)

    def test_runs_not_provided(self):
        code, resp = self.client.runs_bulk_get(
            self.org['id'],
            self.app['id'], [])
        self.assertEqual(code, 200)
        self.assertEqual(resp, [])
