from unittest.mock import patch
from rest_api.rest_api_server.tests.unittests.test_profiling_base import (
    TestProfilingBase)


class TestTagApi(TestProfilingBase):
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

    def test_list_no_runs(self):
        code, task = self.client.task_create(
            self.organization_id, {
                'name': 'My test project',
                'key': 'test_project',
                'metrics': []
            })
        self.assertEqual(code, 201)
        code, res = self.client.tags_list(self.organization_id, task['id'])
        self.assertEqual(code, 200)
        self.assertFalse(res.get('tags', []))

    def test_list_no_labels(self):
        code, task = self.client.task_create(
            self.organization_id, {
                'name': 'My test project',
                'key': 'test_project',
                'metrics': []
            })
        self.assertEqual(code, 201)
        self._create_run(self.organization_id, task['id'], tags={})
        code, res = self.client.tags_list(self.organization_id, task['id'])
        self.assertEqual(code, 200)
        self.assertFalse(res.get('tags', []))

    def test_list_invalid_task(self):
        code, res = self.client.tags_list(self.organization_id, 'task_id')
        self.assertEqual(code, 404)
        self.assertEqual(res['error']['error_code'], 'OE0002')

    def test_list_invalid_org(self):
        code, res = self.client.tags_list('org_id', 'task_id')
        self.assertEqual(code, 404)
        self.assertEqual(res['error']['error_code'], 'OE0002')

    def test_list_tags(self):
        code, task = self.client.task_create(
            self.organization_id, {
                'name': 'My test project',
                'key': 'test_project',
                'metrics': []
            })
        self.assertEqual(code, 201)
        self._create_run(self.organization_id, task['id'], tags={'test': 1})
        self._create_run(self.organization_id, task['id'], tags={'test1': 1})
        code, task2 = self.client.task_create(
            self.organization_id, {
                'name': 'My test project',
                'key': 'test_project2',
                'metrics': []
            })
        self.assertEqual(code, 201)
        self._create_run(self.organization_id, task2['id'], tags={'test2': 1})
        code, res = self.client.tags_list(self.organization_id, task['id'])
        self.assertEqual(code, 200)
        for tag in ['test', 'test1']:
            self.assertIn(tag, res['tags'])
