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
        code, app = self.client.application_create(
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
        code, resp = self.client.executor_list(self.org['id'], app['id'])
        self.assertEqual(code, 200)
        self.assertEqual(resp['executors'], [])
        self._create_run(self.org['id'], app['id'],
                         [valid_resource['cloud_resource_id']])
        code, resp = self.client.executor_list(self.org['id'], app['id'])
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
        self._create_run(self.org['id'], app['id'],
                         ['i-2', 'i-3'])
        code, resp = self.client.executor_list(self.org['id'], app['id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['executors']), 3)

    def test_executors_breakdown_params(self):
        code, resp = self.client.executors_breakdown_get(self.org['id'],
                                                         breakdown_by=None)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0216')

        for br in [123, '123']:
            code, resp = self.client.executors_breakdown_get(
                self.org['id'], breakdown_by=br)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0217')

        for br in ['executors_count', 'cpu', 'ram']:
            code, resp = self.client.executors_breakdown_get(
                self.org['id'], breakdown_by=br)
            self.assertEqual(code, 200)
            self.assertEqual(
                resp, {'breakdown': {}, 'breakdown_by': br})

        code, app1 = self.client.application_create(
            self.org['id'], {'name': 'pr_1', 'key': 'k_1'})
        self.assertEqual(code, 201)
        code, app2 = self.client.application_create(
            self.org['id'], {'name': 'pr_2', 'key': 'k_2'})
        self.assertEqual(code, 201)
        run_1_1 = self._create_run(self.org['id'], app1['id'], [])
        run_1_2 = self._create_run(self.org['id'], app1['id'], [])

        dt1 = datetime(2022, 2, 5, tzinfo=timezone.utc)
        dt2 = dt1 + timedelta(days=2)
        dt1 = int(dt1.timestamp())
        dt2 = int(dt2.timestamp())
        self._create_proc_stats(
            run_1_1['_id'], dt1, 'i-1', 10, 100, 5, 25 * BYTES_IN_MB,
            gpu_load=10, gpu_memory_free=20, gpu_memory_used=10,
            gpu_memory_total=100)
        self._create_proc_stats(
            run_1_1['_id'], dt1, 'i-2', 20, 200, 10, 50 * BYTES_IN_MB,
            gpu_load=20, gpu_memory_free=60, gpu_memory_used=40,
            gpu_memory_total=120)
        self._create_proc_stats(
            run_1_2['_id'], dt2, 'i-3', 30, 300, 15, 75 * BYTES_IN_MB,
            gpu_load=30, gpu_memory_free=40, gpu_memory_used=50,
            gpu_memory_total=80)

        run_2_1 = self._create_run(self.org['id'], app2['id'], [])
        self._create_proc_stats(
            run_2_1['_id'], dt2, 'i-1', 40, 400, 20, 100 * BYTES_IN_MB,
            gpu_load=40, gpu_memory_free=50, gpu_memory_used=30,
            gpu_memory_total=90)

        for br, expected in [
            ('executors_count', {str(dt1): 2, str(dt2): 2}),
            ('cpu', {str(dt1): 15.0, str(dt2): 35.0}),
            ('ram', {str(dt1): 150.0, str(dt2): 350.0}),
            ('process_cpu', {str(dt1): 7.5, str(dt2): 17.5}),
            ('process_ram', {str(dt1): 37.5, str(dt2): 87.5}),
            ('gpu_load', {str(dt1): 15.0, str(dt2): 35.0}),
            ('gpu_memory_free', {str(dt1): 40.0, str(dt2): 45.0}),
            ('gpu_memory_used', {str(dt1): 25.0, str(dt2): 40.0}),
            ('gpu_memory_total', {str(dt1): 110.0, str(dt2): 85.0})
        ]:
            code, resp = self.client.executors_breakdown_get(
                self.org['id'], breakdown_by=br)
            self.assertEqual(code, 200)
            self.assertDictEqual(
                resp, {'breakdown': expected, 'breakdown_by': br})

    def test_list_executors_multi_app(self):
        code, resp = self.client.executor_list(self.org['id'])
        self.assertEqual(code, 200)
        self.assertEqual(resp, {'executors': []})

        code, app_1 = self.client.application_create(
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
        self._create_run(self.org['id'], app_1['id'],
                         [valid_resource_1['cloud_resource_id']])

        code, app_2 = self.client.application_create(
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
        self._create_run(self.org['id'], app_2['id'],
                         [valid_resource_2['cloud_resource_id']])

        code, resp = self.client.executor_list(self.org['id'], app_1['id'])
        self.assertEqual(len(resp['executors']), 1)
        executor = resp['executors'][0]
        self.assertEqual(executor['instance_id'],
                         valid_resource_1['cloud_resource_id'])

        code, resp = self.client.executor_list(self.org['id'], app_2['id'])
        self.assertEqual(len(resp['executors']), 1)
        executor = resp['executors'][0]
        self.assertEqual(executor['instance_id'],
                         valid_resource_2['cloud_resource_id'])
        for app_ids in [
            [app_1['id'], app_2['id']],
            None
        ]:
            code, resp = self.client.executor_list(self.org['id'], app_ids)
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
        code, app = self.client.application_create(
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
        r1 = self._create_run(self.org['id'], app['id'],
                              [valid_resource['cloud_resource_id']],
                              start=1000, finish=1001)
        r2 = self._create_run(self.org['id'], app['id'], ['i-2', 'i-3'],
                              start=1002, finish=1005)
        code, resp = self.client.executor_list(self.org['id'], app['id'])
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
            self.org['id'], application_ids=['some'],
            run_ids=[r1['_id'], r2['_id']])
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['executors']), 3)
