import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from rest_api.rest_api_server.tests.unittests.test_profiling_base import TestProfilingBase

BYTES_IN_MB = 1024 * 1024


class TestExecutorsApi(TestProfilingBase):

    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.org = self.client.organization_create({'name': "organization"})
        patch('rest_api.rest_api_server.controllers.cloud_account.'
              'CloudAccountController._configure_report').start()
        self.user_id = self.gen_id()
        _, self.employee = self.client.employee_create(
            self.org['id'], {'name': 'name', 'auth_user_id': self.user_id})
        self._mock_auth_user(self.user_id)
        config = {
            'name': 'creds',
            'type': 'aws_cnr',
            'config': {
                'access_key_id': 'key',
                'secret_access_key': 'secret',
                'config_scheme': 'create_report'
            }
        }
        _, self.cloud_acc = self.create_cloud_account(
            self.org['id'], config, auth_user_id=self.user_id)

    def test_list_executors(self):
        code, task = self.client.task_create(
            self.org['id'], {
                'name': 'My test project',
                'key': 'test_project'
            })
        self.assertEqual(code, 201)
        valid_resource = {
            'cloud_resource_id': 'res_id_1',
            'name': 'resource_1',
            'resource_type': 'testo',
            'region': 'test_region',
            'service_name': 'test_service',
        }
        body = {
            'resources': [valid_resource],
        }
        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc['id'], body, behavior='skip_existing',
            return_resources=True)
        self.assertEqual(code, 200)
        code, resp = self.client.executor_list(self.org['id'], task['id'])
        self.assertEqual(code, 200)
        self.assertEqual(resp['executors'], [])
        self._create_run(self.org['id'], task['id'],
                         [valid_resource['cloud_resource_id']])
        code, resp = self.client.executor_list(self.org['id'], task['id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['executors']), 1)
        executor = resp['executors'][0]
        self.assertEqual(executor['instance_id'],
                         valid_resource['cloud_resource_id'])
        self.assertTrue(executor['discovered'])
        self.assertEqual(executor['resource']['cloud_account'], {
            'name': self.cloud_acc['name'], 'type': self.cloud_acc['type'],
            'id': self.cloud_acc['id']
        })
        self._create_run(self.org['id'], task['id'],
                         ['i-2', 'i-3'])
        code, resp = self.client.executor_list(self.org['id'], task['id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['executors']), 3)

    def test_executors_breakdown_params(self):
        code, resp = self.client.executors_breakdown_get(self.org['id'])
        self.assertEqual(code, 200)
        self.assertEqual(resp['breakdown'], {})

        code, task1 = self.client.task_create(
            self.org['id'], {'name': 'pr_1', 'key': 'k_1'})
        self.assertEqual(code, 201)
        code, task2 = self.client.task_create(
            self.org['id'], {'name': 'pr_2', 'key': 'k_2'})
        self.assertEqual(code, 201)
        run_1_start_ts = int(datetime.utcnow().timestamp())
        run_2_start_ts = run_1_start_ts - 24 * 3600
        run_3_start_ts = run_1_start_ts - 2 * 24 * 3600
        self._create_run(
            self.org['id'], task1['id'], ['i-1'],
            start=run_1_start_ts)
        self._create_run(
            self.org['id'], task1['id'], ['i-1'],
            start=run_1_start_ts)
        self._create_run(
            self.org['id'], task1['id'], ['i-2'],
            start=run_2_start_ts)
        self._create_run(
            self.org['id'], task2['id'], ['i-4'],
            start=run_3_start_ts)

        code, resp = self.client.executors_breakdown_get(
            self.org['id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['breakdown']), 3)
        for v in resp['breakdown'].values():
            self.assertEqual(v, 1)

    def test_list_executors_multi_task(self):
        code, resp = self.client.executor_list(self.org['id'])
        self.assertEqual(code, 200)
        self.assertEqual(resp, {'executors': []})

        code, task_1 = self.client.task_create(
            self.org['id'], {
                'name': 'My test project',
                'key': 'test_project'
            })
        self.assertEqual(code, 201)
        valid_resource_1 = {
            'cloud_resource_id': 'res_id_1',
            'name': 'resource_1',
            'resource_type': 'testo'
        }
        body = {'resources': [valid_resource_1]}
        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc['id'], body, behavior='skip_existing',
            return_resources=True)
        self.assertEqual(code, 200)
        self._create_run(self.org['id'], task_1['id'],
                         [valid_resource_1['cloud_resource_id']])

        code, task_2 = self.client.task_create(
            self.org['id'], {
                'name': 'My test project 2',
                'key': 'test_project_2'
            })
        valid_resource_2 = {
            'cloud_resource_id': 'res_id_2',
            'name': 'resource_2',
            'resource_type': 'test',
        }
        body = {'resources': [valid_resource_2]}
        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc['id'], body, behavior='skip_existing',
            return_resources=True)
        self.assertEqual(code, 200)
        self._create_run(self.org['id'], task_2['id'],
                         [valid_resource_2['cloud_resource_id']])

        code, resp = self.client.executor_list(self.org['id'], task_1['id'])
        self.assertEqual(len(resp['executors']), 1)
        executor = resp['executors'][0]
        self.assertEqual(executor['instance_id'],
                         valid_resource_1['cloud_resource_id'])

        code, resp = self.client.executor_list(self.org['id'], task_2['id'])
        self.assertEqual(len(resp['executors']), 1)
        executor = resp['executors'][0]
        self.assertEqual(executor['instance_id'],
                         valid_resource_2['cloud_resource_id'])
        for task_ids in [
            [task_1['id'], task_2['id']],
            None
        ]:
            code, resp = self.client.executor_list(self.org['id'], task_ids)
            self.assertEqual(len(resp['executors']), 2)
            cloud_resource_ids = set(map(
                lambda x: x['instance_id'], resp['executors']))
            self.assertEqual(len(cloud_resource_ids), 2)
            for r_id in cloud_resource_ids:
                self.assertTrue(r_id in [
                    valid_resource_1['cloud_resource_id'],
                    valid_resource_2['cloud_resource_id']
                ])

    def test_list_executors_run_id(self):
        code, task = self.client.task_create(
            self.org['id'], {
                'name': 'My test project',
                'key': 'test_project'
            })
        self.assertEqual(code, 201)
        valid_resource = {
            'cloud_resource_id': 'res_id_1',
            'name': 'resource_1',
            'resource_type': 'testo',
            'region': 'test_region',
            'service_name': 'test_service',
        }
        body = {
            'resources': [valid_resource],
        }
        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc['id'], body, behavior='skip_existing',
            return_resources=True)
        self.assertEqual(code, 200)
        r1 = self._create_run(self.org['id'], task['id'],
                              [valid_resource['cloud_resource_id']],
                              start=1000, finish=1001)
        r2 = self._create_run(self.org['id'], task['id'], ['i-2', 'i-3'],
                              start=1002, finish=1005)
        code, resp = self.client.executor_list(self.org['id'], task['id'])
        self.assertEqual(len(resp['executors']), 3)
        expected_last_seen_map = {'res_id_1': 1001, 'i-2': 1005, 'i-3': 1005}
        for e in resp['executors']:
            self.assertEqual(
                e['last_used'], expected_last_seen_map[e['instance_id']])

        code, resp = self.client.executor_list(
            self.org['id'], run_ids=r1['_id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['executors']), 1)
        self.assertEqual(resp['executors'][0]['instance_id'],
                         valid_resource['cloud_resource_id'])

        code, resp = self.client.executor_list(
            self.org['id'], run_ids=r2['_id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['executors']), 2)

        code, resp = self.client.executor_list(
            self.org['id'], task_ids=['some'],
            run_ids=[r1['_id'], r2['_id']])
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['executors']), 3)
