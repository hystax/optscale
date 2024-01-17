import uuid
from rest_api.rest_api_server.tests.unittests.test_profiling_base import TestProfilingBase
from unittest.mock import patch
from datetime import datetime, timezone, timedelta
from freezegun import freeze_time

BYTES_IN_MB = 1024 * 1024


class TestRunsApi(TestProfilingBase):

    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.org = self.client.organization_create({'name': "organization"})
        self.auth_user = str(uuid.uuid4())
        _, self.employee = self.client.employee_create(
            self.org['id'], {'name': 'name1', 'auth_user_id': self.auth_user})
        patch('rest_api.rest_api_server.controllers.base.BaseController.'
              'get_user_id', return_value=self.auth_user).start()
        self.git_data = {
            'remote': "git@github.com:hystax/optscale_arcee.git",
            'branch': "feature/ml_leaderboard",
            'commit_id': "1fde95d5664ae9e542610993e17ee81b135b55c0",
            'status': "dirty"
        }

    def test_get_run(self):
        code, resp = self.client.run_get(self.org['id'], '123')
        self.assertEqual(code, 404)
        self.verify_error_code(resp, 'OE0002')

        goal_1 = self._create_goal(self.org['id'], 'loss')
        goal_2 = self._create_goal(self.org['id'], 'goal_2')
        code, app = self.client.application_create(
            self.org['id'], {
                'name': 'My test project',
                'key': 'test_project',
                'goals': [goal_1['id'], goal_2['id']]
            })
        self.assertEqual(code, 201)
        run = self._create_run(self.org['id'],
                               app['id'],
                               ['i-1', 'i-2'],
                               's3://ml-bucket/dataset',
                               data={'step': 2000, 'loss': 55})
        code, resp = self.client.run_get(self.org['id'], run['_id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['executors']), 2)
        self.assertEqual(len(resp['goals']), 2)
        self.assertTrue(resp['dataset'])

    def test_get_run_git_data(self):
        goal_1 = self._create_goal(self.org['id'], 'loss')
        goal_2 = self._create_goal(self.org['id'], 'goal_2')
        code, app = self.client.application_create(
            self.org['id'], {
                'name': 'My test project',
                'key': 'test_project',
                'goals': [goal_1['id'], goal_2['id']]
            })
        self.assertEqual(code, 201)
        run = self._create_run(self.org['id'],
                               app['id'],
                               ['i-1', 'i-2'],
                               's3://ml-bucket/dataset',
                               data={'step': 2000, 'loss': 55},
                               git=self.git_data)
        code, resp = self.client.run_get(self.org['id'], run['_id'])
        self.assertEqual(code, 200)
        self.assertEqual(resp['git'], self.git_data)

    def test_get_run_console_data(self):
        goal_1 = self._create_goal(self.org['id'], 'loss')
        goal_2 = self._create_goal(self.org['id'], 'goal_2')
        code, app = self.client.application_create(
            self.org['id'], {
                'name': 'My test project',
                'key': 'test_project',
                'goals': [goal_1['id'], goal_2['id']]
            })
        self.assertEqual(code, 201)
        run = self._create_run(self.org['id'],
                               app['id'],
                               ['i-1', 'i-2'],
                               's3://ml-bucket/dataset',
                               data={'step': 2000, 'loss': 55},
                               git=self.git_data)
        code, resp = self.client.run_get(self.org['id'], run['_id'])
        self.assertEqual(code, 200)
        self.assertIsNone(resp['console'])

        console_data = {
            'output': 'output',
            'error': 'error'
        }
        self._create_console(run['_id'], **console_data)
        code, resp = self.client.run_get(self.org['id'], run['_id'])
        self.assertEqual(code, 200)
        self.assertEqual(resp['console'], console_data)

    def test_get_run_no_datasets(self):
        goal_1 = self._create_goal(self.org['id'], 'loss')
        goal_2 = self._create_goal(self.org['id'], 'goal_2')
        code, app = self.client.application_create(
            self.org['id'], {
                'name': 'My test project',
                'key': 'test_project',
                'goals': [goal_1['id'], goal_2['id']]
            })
        self.assertEqual(code, 201)
        run = self._create_run(self.org['id'],
                               app['id'],
                               ['i-1', 'i-2'],
                               data={'step': 2000, 'loss': 55})
        code, resp = self.client.run_get(self.org['id'], run['_id'])
        self.assertEqual(code, 200)
        self.assertIsNone(resp['dataset'])

    def test_get_run_deleted_dataset(self):
        goal_1 = self._create_goal(self.org['id'], 'loss')
        goal_2 = self._create_goal(self.org['id'], 'goal_2')
        code, app = self.client.application_create(
            self.org['id'], {
                'name': 'My test project',
                'key': 'test_project',
                'goals': [goal_1['id'], goal_2['id']]
            })
        self.assertEqual(code, 201)
        run = self._create_run(self.org['id'],
                               app['id'],
                               ['i-1', 'i-2'],
                               's3://ml-bucket/dataset',
                               data={'step': 2000, 'loss': 55})
        code, resp = self.client.dataset_list(self.org['id'])
        self.assertEqual(code, 200)
        for dataset in resp['datasets']:
            code, _ = self.client.dataset_delete(self.org['id'], dataset['id'])
            self.assertEqual(code, 204)
        code, resp = self.client.run_get(self.org['id'], run['_id'])
        self.assertEqual(code, 200)
        self.assertTrue(resp.get('dataset', {}).get('deleted'))

    def test_get_runset_run(self):
        goal_1 = self._create_goal(self.org['id'], 'loss')
        goal_2 = self._create_goal(self.org['id'], 'goal_2')
        code, app = self.client.application_create(
            self.org['id'], {
                'name': 'My test project',
                'key': 'test_project',
                'goals': [goal_1['id'], goal_2['id']]
            })
        self.assertEqual(code, 201)
        run = self._create_run(self.org['id'],
                               app['id'],
                               ['i-1', 'i-2'],
                               data={'step': 2000, 'loss': 55},
                               runset_id=str(uuid.uuid4()),
                               runset_name='test')
        code, resp = self.client.run_get(self.org['id'], run['_id'])
        self.assertEqual(code, 200)
        self.assertTrue(resp.get('runset'))
        self.assertEqual(run['runset_id'], resp['runset'].get('id'))
        self.assertEqual(run['runset_name'], resp['runset'].get('name'))

    def test_runs_breakdown_params(self):
        code, resp = self.client.run_breakdown_get(self.org['id'], '123')
        self.assertEqual(code, 404)
        self.verify_error_code(resp, 'OE0002')

        code, app = self.client.application_create(
            self.org['id'], {
                'name': 'My test project',
                'key': 'test_project',
            })
        run = self._create_run(self.org['id'],
                               app['id'], ['i-1', 'i-2'],
                               start=0.8, finish=9.8)
        code, resp = self.client.run_breakdown_get(self.org['id'], run['_id'])
        self.assertEqual(code, 200)
        self.assertEqual(resp['milestones'], [])
        self.assertEqual(resp['stages'], [])
        self.assertEqual(len(resp['breakdown']), 10)

        br_timestamps = [int(x) for x in list(resp['breakdown'].keys())]
        self.assertEqual(int(min(br_timestamps)), 1)
        self.assertEqual(int(max(br_timestamps)), 10)
        for k in resp['breakdown'].values():
            self.assertEqual(k['metrics'], {})
            self.assertEqual(k['data'], {})

        self._create_log(run['_id'], 2, data={'loss': 10}, instance_id='i-1')
        self._create_proc_stats(
            run['_id'], 2, 'i-1', 4, 100, 2, 50 * BYTES_IN_MB, gpu_load=5,
            gpu_memory_free=10, gpu_memory_used=15, gpu_memory_total=20)
        self._create_log(run['_id'], 2.2, data={'loss': 20}, instance_id='i-1')
        self._create_proc_stats(
            run['_id'], 2.6, 'i-1', 6, 200, 3, 70 * BYTES_IN_MB, gpu_load=10,
            gpu_memory_free=20, gpu_memory_used=30, gpu_memory_total=40)
        self._create_log(run['_id'], 3, data={'loss': 50}, instance_id='i-2')
        self._create_proc_stats(
            run['_id'], 2.9, 'i-2', 10, 300, 4, 120 * BYTES_IN_MB, gpu_load=20,
            gpu_memory_free=40, gpu_memory_used=60, gpu_memory_total=80)

        code, resp = self.client.run_breakdown_get(self.org['id'], run['_id'])
        self.assertEqual(code, 200)
        breakdowns = resp['breakdown']
        br_2 = breakdowns.pop('2')
        self.assertEqual(br_2['metrics'], {
            'ram': 100.0, 'cpu': 4.0, 'executors_count': 1, 'process_cpu': 2.0,
            'process_ram': 50.0, 'gpu_load': 5.0, 'gpu_memory_free': 10.0,
            'gpu_memory_total': 20.0, 'gpu_memory_used': 15.0
        })
        self.assertEqual(br_2['data'], {})
        br_3 = breakdowns.pop('3')
        self.assertEqual(br_3['metrics'], {
            'ram': 250.0, 'cpu': 8.0, 'executors_count': 2, 'process_cpu': 3.5,
            'process_ram': 95.0, 'gpu_load': 15.0, 'gpu_memory_free': 30.0,
            'gpu_memory_total': 60.0, 'gpu_memory_used': 45.0
        })
        self.assertEqual(br_3['data'], {})
        for br in breakdowns.values():
            self.assertEqual(br['metrics'], {})
            self.assertEqual(br['data'], {})

        goal_1 = self._create_goal(self.org['id'], 'loss', name='Model loss')
        code, resp = self.client.application_update(
            self.org['id'], app['id'], {'attach': [goal_1['id']]})
        self.assertEqual(code, 200)
        code, resp = self.client.run_breakdown_get(self.org['id'], run['_id'])
        self.assertEqual(code, 200)
        breakdowns = resp['breakdown']
        br_2 = breakdowns.pop('2')
        self.assertEqual(br_2['metrics'], {
            'ram': 100, 'cpu': 4, 'executors_count': 1, 'process_cpu': 2.0,
            'process_ram': 50.0, 'gpu_load': 5.0, 'gpu_memory_free': 10.0,
            'gpu_memory_total': 20.0, 'gpu_memory_used': 15.0
        })
        self.assertEqual(
            br_2['data'], {'loss': 10})
        br_3 = breakdowns.pop('3')
        self.assertEqual(br_3['metrics'], {
            'ram': 250, 'cpu': 8, 'executors_count': 2, 'process_cpu': 3.5,
            'process_ram': 95.0, 'gpu_load': 15.0, 'gpu_memory_free': 30.0,
            'gpu_memory_total': 60.0, 'gpu_memory_used': 45.0
        })
        self.assertEqual(
            br_3['data'], {'loss': 35})
        for br in breakdowns.values():
            self.assertEqual(br['metrics'], {})
            self.assertEqual(br['data'], {})

    def test_application_run_cost(self):
        patch('rest_api.rest_api_server.controllers.cloud_account.'
              'CloudAccountController._configure_report').start()
        user_id = self.gen_id()
        _, employee = self.client.employee_create(
            self.org['id'], {'name': 'name', 'auth_user_id': user_id})
        self._mock_auth_user(user_id)
        config = {
            'name': 'creds',
            'type': 'aws_cnr',
            'config': {
                'access_key_id': 'key',
                'secret_access_key': 'secret',
                'config_scheme': 'create_report'
            }
        }
        _, cloud_acc = self.create_cloud_account(
            self.org['id'], config, auth_user_id=user_id)
        res_1 = {
            'cloud_resource_id': 'res_id_1',
            'name': 'resource_1',
            'resource_type': 'test1',
            'region': 'test_region',
            'service_name': 'test_service',
        }
        res_2 = {
            'cloud_resource_id': 'res_id_2',
            'name': 'resource_2',
            'resource_type': 'test2',
            'region': 'test_region',
            'service_name': 'test_service',
        }
        body = {
            'resources': [res_1, res_2],
        }
        code, result = self.cloud_resource_create_bulk(
            cloud_acc['id'], body, behavior='skip_existing',
            return_resources=True)
        self.assertEqual(code, 200)
        raw_data = [
            {
                'start_date': datetime(2022, 5, 15, 12),
                'end_date': datetime(2022, 5, 15, 16),
                'cost': 120,
                'cloud_account_id': cloud_acc['id'],
                'resource_id': res_1['cloud_resource_id']
            },
            {
                'start_date': datetime(2022, 5, 15),
                'end_date': datetime(2022, 5, 16),
                'cost': 179,
                'cloud_account_id': cloud_acc['id'],
                'resource_id': res_2['cloud_resource_id']
            },
            {
                'start_date': datetime(2022, 5, 15, 15),
                'end_date': datetime(2022, 5, 15, 16),
                'lineItem/UsageAmount': '1',
                'cost': 1,
                'box_usage': True,
                'cloud_account_id': cloud_acc['id'],
                'resource_id': res_2['cloud_resource_id']
            },
        ]
        self.raw_expenses.insert_many(raw_data)
        resource_ids_map = {
            r['cloud_resource_id']: r['id'] for r in result['resources']
        }
        for raw in raw_data:
            self.expenses.append({
                'resource_id': resource_ids_map[raw['resource_id']],
                'cost': raw['cost'],
                'date': int(raw['start_date'].timestamp()),
                'cloud_account_id': raw['cloud_account_id'],
                'sign': 1
            })
        code, app = self.client.application_create(
            self.org['id'], {
                'name': 'My test project',
                'key': 'test_project',
            })
        self._create_run(
            self.org['id'], app['id'],
            [res_1['cloud_resource_id'], res_2['cloud_resource_id']],
            start=int(datetime(
                2022, 5, 15, 14, tzinfo=timezone.utc).timestamp()),
            finish=int(datetime(
                2022, 5, 15, 15, tzinfo=timezone.utc).timestamp()))
        code, resp = self.client.application_get(self.org['id'], app['id'])
        self.assertEqual(code, 200)
        self.assertEqual(resp['last_run_cost'], 185)
        self.assertEqual(resp['total_cost'], 185)

        dt_start = datetime.utcnow() - timedelta(days=15)
        self._create_run(
            self.org['id'], app['id'],
            [res_1['cloud_resource_id']],
            start=int(dt_start.timestamp()),
            finish=int((dt_start + timedelta(hours=1)).timestamp()))
        code, resp = self.client.application_get(self.org['id'], app['id'])
        self.assertEqual(code, 200)
        self.assertEqual(resp['last_run_cost'], 5)
        self.assertEqual(resp['total_cost'], 190)

    def test_list_run_git_data(self):
        goal_1 = self._create_goal(self.org['id'], 'loss')
        code, app = self.client.application_create(
            self.org['id'], {
                'name': 'My test project',
                'key': 'test_project',
                'goals': [goal_1['id']]
            })
        self.assertEqual(code, 201)
        run_1 = self._create_run(self.org['id'],
                                 app['id'], ['i-1'],
                                 data={'step': 1500, 'loss': 55},
                                 start=int(datetime(2022, 5, 15).timestamp()),
                                 git=self.git_data)
        run_2 = self._create_run(self.org['id'],
                                 app['id'], ['i-2'],
                                 data={'step': 2000, 'loss': 70},
                                 start=int(datetime(2022, 5, 20).timestamp()),
                                 git=None)
        code, resp = self.client.run_list(self.org['id'], app['id'])
        self.assertEqual(len(resp['runs']), 2)
        for run in resp['runs']:
            self.assertTrue('git' in run)

    def test_list_run(self):
        goal_1 = self._create_goal(self.org['id'], 'loss')
        code, app = self.client.application_create(
            self.org['id'], {
                'name': 'My test project',
                'key': 'test_project',
                'goals': [goal_1['id']]
            })
        self.assertEqual(code, 201)
        code, resp = self.client.run_list(self.org['id'], app['id'])
        self.assertEqual(code, 200)
        self.assertEqual(resp['runs'], [])
        run_1 = self._create_run(self.org['id'],
                                 app['id'], ['i-1'],
                                 data={'step': 1500, 'loss': 55},
                                 start=int(datetime(2022, 5, 15).timestamp()))
        run_2 = self._create_run(self.org['id'],
                                 app['id'], ['i-2'],
                                 data={'step': 2000, 'loss': 70},
                                 start=int(datetime(2022, 5, 20).timestamp()))
        code, resp = self.client.run_list(self.org['id'], app['id'])
        self.assertEqual(len(resp['runs']), 2)

        end_dt = int(datetime(2022, 5, 17).timestamp())
        code, resp = self.client.run_list(self.org['id'], app['id'],
                                          end_date=end_dt)
        self.assertEqual(len(resp['runs']), 1)
        self.assertEqual(resp['runs'][0]['id'], run_1['_id'])

        start_dt = int(datetime(2022, 5, 17).timestamp())
        code, resp = self.client.run_list(self.org['id'], app['id'],
                                          start_date=start_dt)
        self.assertEqual(len(resp['runs']), 1)
        self.assertEqual(resp['runs'][0]['id'], run_2['_id'])

    def test_run_without_executor(self):
        code, app = self.client.application_create(
            self.org['id'], {
                'name': 'My test project',
                'key': 'test_project',
            })
        self.assertEqual(code, 201)
        code, resp = self.client.run_list(self.org['id'], app['id'])
        self.assertEqual(code, 200)
        self.assertEqual(resp['runs'], [])
        run_1 = self._create_run(self.org['id'],
                                 app['id'],
                                 data={'step': 2000, 'loss': 70},
                                 start=int(datetime(2022, 5, 20).timestamp()))
        code, resp = self.client.run_list(self.org['id'], app['id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['runs']), 1)
        self.assertEqual(resp['runs'][0]['executors'], [])

        code, resp = self.client.application_get(self.org['id'], app['id'])
        self.assertEqual(code, 200)
        self.assertEqual(resp['runs_count'], 1)

    def test_not_completed_run_breakdown(self):
        code, app = self.client.application_create(
            self.org['id'], {
                'name': 'My test project',
                'key': 'test_project',
            })
        now = int(datetime(2022, 5, 10).timestamp())
        run = self._create_run(self.org['id'], app['id'], [],
                               start=now, finish=None)
        code, resp = self.client.run_breakdown_get(self.org['id'], run['_id'])
        self.assertEqual(code, 200)
        self.assertEqual(
            resp['breakdown'], {
                str(now): {'metrics': {}, 'data': {}}
            })

    def test_run_breakdown_metrics(self):
        code, app = self.client.application_create(
            self.org['id'], {
                'name': 'My test project',
                'key': 'test_project',
            })
        run = self._create_run(self.org['id'],
                               app['id'], ['i-1', 'i-2'],
                               start=1001, finish=1005)
        self._create_log(run['_id'], 1001.77, data={'loss': 10})
        self._create_proc_stats(
            run['_id'], 1002, 'i-1', 2, 50, 1, 1 * BYTES_IN_MB, gpu_load=20,
            gpu_memory_free=40, gpu_memory_used=60, gpu_memory_total=80)
        self._create_log(run['_id'], 1003, data={'loss': 20})
        self._create_proc_stats(
            run['_id'], 1002.8, 'i-1', 4, 100, 2, 2 * BYTES_IN_MB, gpu_load=30,
            gpu_memory_free=50, gpu_memory_used=70, gpu_memory_total=90)
        code, resp = self.client.run_breakdown_get(self.org['id'], run['_id'])
        self.assertEqual(code, 200)
        breakdown = resp['breakdown']
        self.assertEqual(len(breakdown), 5)
        self.assertEqual(breakdown['1001'], {'metrics': {}, 'data': {}})
        self.assertEqual(breakdown['1002'], {'metrics': {
            'ram': 50.0, 'cpu': 2.0, 'executors_count': 1, 'process_cpu': 1.0,
            'process_ram': 1.0, 'gpu_load': 20.0, 'gpu_memory_free': 40.0,
            'gpu_memory_total': 80.0, 'gpu_memory_used': 60.0}, 'data': {}})
        self.assertEqual(breakdown['1003'], {'metrics': {
            'ram': 100.0, 'cpu': 4.0, 'executors_count': 1, 'process_cpu': 2.0,
            'process_ram': 2.0, 'gpu_load': 30.0, 'gpu_memory_free': 50.0,
            'gpu_memory_total': 90.0, 'gpu_memory_used': 70.0}, 'data': {}})
        self.assertEqual(breakdown['1004'], {'metrics': {}, 'data': {}})
        self.assertEqual(breakdown['1005'], {'metrics': {}, 'data': {}})

    def test_not_completed_run_applications(self):
        patch('rest_api.rest_api_server.controllers.cloud_account.'
              'CloudAccountController._configure_report').start()
        user_id = self.gen_id()
        _, employee = self.client.employee_create(
            self.org['id'], {'name': 'name', 'auth_user_id': user_id})
        self._mock_auth_user(user_id)
        config = {
            'name': 'creds',
            'type': 'aws_cnr',
            'config': {
                'access_key_id': 'key',
                'secret_access_key': 'secret',
                'config_scheme': 'create_report'
            }
        }
        _, cloud_acc = self.create_cloud_account(
            self.org['id'], config, auth_user_id=user_id)
        res_1 = {
            'cloud_resource_id': 'res_id_1',
            'name': 'resource_1',
            'resource_type': 'test1',
            'region': 'test_region',
            'service_name': 'test_service',
        }
        body = {
            'resources': [res_1],
        }
        self.cloud_resource_create_bulk(
            cloud_acc['id'], body, behavior='skip_existing',
            return_resources=True)
        now_dt = datetime(2022, 5, 10)
        now = int(now_dt.timestamp())
        code, app = self.client.application_create(
            self.org['id'], {
                'name': 'My test project',
                'key': 'test_project',
            })
        run1 = self._create_run(self.org['id'], app['id'], ['res_id_1'],
                                start=now - 5, finish=now - 1)
        run2 = self._create_run(self.org['id'], app['id'], ['res_id_1'],
                                start=now, finish=None, state=1)
        with freeze_time(now_dt + timedelta(hours=1)):
            code, resp = self.client.run_get(self.org['id'], run1['_id'])
            self.assertEqual(code, 200)
            self.assertEqual(resp['duration'], 4)
            code, resp = self.client.run_get(self.org['id'], run2['_id'])
            self.assertEqual(code, 200)
            self.assertEqual(resp['duration'], 3600)
            code, resp_get = self.client.application_get(self.org['id'], app['id'])
            self.assertEqual(code, 200)
            self.assertEqual(resp_get['runs_count'], 2)
            self.assertEqual(resp_get['last_run_duration'], 3600)
            self.assertEqual(resp_get['last_run'], now)
            self.assertEqual(resp_get['last_successful_run'], now - 5)

            code, resp_list = self.client.application_list(self.org['id'])
            self.assertEqual(code, 200)
            applications = resp_list['applications']
            self.assertEqual(len(applications), 1)
            self.assertEqual(applications[0], resp_get)

    def test_not_completed_run_cost(self):
        patch('rest_api.rest_api_server.controllers.cloud_account.'
              'CloudAccountController._configure_report').start()
        user_id = self.gen_id()
        _, employee = self.client.employee_create(
            self.org['id'], {'name': 'name', 'auth_user_id': user_id})
        self._mock_auth_user(user_id)
        config = {
            'name': 'creds',
            'type': 'aws_cnr',
            'config': {
                'access_key_id': 'key',
                'secret_access_key': 'secret',
                'config_scheme': 'create_report'
            }
        }
        _, cloud_acc = self.create_cloud_account(
            self.org['id'], config, auth_user_id=user_id)
        res_1 = {
            'cloud_resource_id': 'res_id_1',
            'name': 'resource_1',
            'resource_type': 'test1',
            'region': 'test_region',
            'service_name': 'test_service',
        }
        res_2 = {
            'cloud_resource_id': 'res_id_2',
            'name': 'resource_2',
            'resource_type': 'test2',
            'region': 'test_region',
            'service_name': 'test_service',
        }
        body = {
            'resources': [res_1, res_2],
        }
        code, result = self.cloud_resource_create_bulk(
            cloud_acc['id'], body, behavior='skip_existing',
            return_resources=True)
        self.assertEqual(code, 200)
        raw_data = [
            {
                'start_date': datetime(2022, 5, 15, 12),
                'end_date': datetime(2022, 5, 15, 16),
                'cost': 120,
                'cloud_account_id': cloud_acc['id'],
                'resource_id': res_1['cloud_resource_id']
            },
            {
                'start_date': datetime(2022, 5, 15),
                'end_date': datetime(2022, 5, 16),
                'cost': 179,
                'cloud_account_id': cloud_acc['id'],
                'resource_id': res_2['cloud_resource_id']
            },
            {
                'start_date': datetime(2022, 5, 15, 15),
                'end_date': datetime(2022, 5, 15, 16),
                'identity/TimeInterval': '2017-11-01T00:00:00Z/2017-11-01T01:00:00Z',
                'cost': 200,
                'box_usage': True,
                'cloud_account_id': cloud_acc['id'],
                'resource_id': res_2['cloud_resource_id']
            },
        ]
        self.raw_expenses.insert_many(raw_data)
        resource_ids_map = {
            r['cloud_resource_id']: r['id'] for r in result['resources']
        }
        for raw in raw_data:
            self.expenses.append({
                'resource_id': resource_ids_map[raw['resource_id']],
                'cost': raw['cost'],
                'date': int(raw['start_date'].timestamp()),
                'cloud_account_id': raw['cloud_account_id'],
                'sign': 1
            })

        code, app = self.client.application_create(
            self.org['id'], {
                'name': 'My test project',
                'key': 'test_project',
            })
        with freeze_time(datetime(2022, 5, 16)):
            self._create_run(
                self.org['id'], app['id'],
                [res_2['cloud_resource_id']],
                start=int(datetime(
                    2022, 5, 15, 14).timestamp()),
                finish=None, state=3)
            code, resp = self.client.application_get(self.org['id'], app['id'])
            self.assertEqual(code, 200)
            self.assertEqual(resp['last_run_cost'], 0)
            self.assertIsNone(resp['last_run_duration'])

            self._create_run(
                self.org['id'], app['id'],
                [res_1['cloud_resource_id']],
                start=int(datetime(
                    2022, 5, 15, 14).timestamp()),
                finish=None, state=1)
            code, resp = self.client.application_get(self.org['id'], app['id'])
            self.assertEqual(code, 200)
            self.assertEqual(resp['last_run_cost'], 50)
            self.assertEqual(resp['last_run_duration'], 10 * 3600)
        with freeze_time(datetime(2022, 5, 17)):
            code, resp = self.client.application_get(self.org['id'], app['id'])
            self.assertEqual(code, 200)
            self.assertEqual(resp['last_run_cost'], 50 + 120)
            self.assertEqual(resp['last_run_duration'], (10 + 24) * 3600)

    def test_run_error_reraise(self):
        code, resp = self.client.run_get(self.org['id'], str(uuid.uuid4()))
        self.assertEqual(code, 404)
        self.verify_error_code(resp, 'OE0002')
        code, resp = self.client.run_breakdown_get(self.org['id'], str(uuid.uuid4()))
        self.assertEqual(code, code)
        self.verify_error_code(resp, 'OE0002')

        _, org2 = self.client.organization_create({'name': "organization_2"})
        auth_user2 = str(uuid.uuid4())
        _, employee2 = self.client.employee_create(
            org2['id'], {'name': 'name2', 'auth_user_id': auth_user2})
        patch('rest_api.rest_api_server.controllers.base.BaseController.'
              'get_user_id', return_value=auth_user2).start()
        _, app = self.client.application_create(
            org2['id'], {
                'name': 'My test project',
                'key': 'test_project',
            })
        other_run = self._create_run(org2['id'], app['id'], ['res_id_1'])

        patch('rest_api.rest_api_server.controllers.base.BaseController.'
              'get_user_id', return_value=self.auth_user).start()
        code, resp = self.client.run_get(self.org['id'], other_run['_id'])
        self.assertEqual(code, 403)
        self.verify_error_code(resp, 'OE0234')
        code, resp = self.client.run_breakdown_get(self.org['id'],
                                                   other_run['_id'])
        self.assertEqual(code, 403)
        self.verify_error_code(resp, 'OE0234')

    def test_breakdown_zero_proc(self):
        code, app = self.client.application_create(
            self.org['id'], {
                'name': 'My test project',
                'key': 'test_project',
            })
        run = self._create_run(self.org['id'], app['id'], ['i-1'],
                               start=1, finish=3)
        code, resp = self.client.run_breakdown_get(self.org['id'], run['_id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['breakdown']), 3)
        for v in resp['breakdown'].values():
            self.assertEqual(v, {'metrics': {}, 'data': {}})

        self._create_proc_stats(
            run['_id'], 2, 'i-1', 0, 0, 0, 0, gpu_load=0,
            gpu_memory_free=0, gpu_memory_used=0, gpu_memory_total=0)
        code, resp = self.client.run_breakdown_get(self.org['id'], run['_id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['breakdown']), 3)
        br_2 = resp['breakdown'].pop('2')
        for v in resp['breakdown'].values():
            self.assertEqual(v, {'metrics': {}, 'data': {}})
        self.assertEqual(br_2, {
            'data': {},
            'metrics': {
                'executors_count': 1,
                'cpu': 0.0,
                'gpu_load': 0.0,
                'gpu_memory_free': 0.0,
                'gpu_memory_total': 0.0,
                'gpu_memory_used': 0.0,
                'process_cpu': 0.0,
                'process_ram': 0.0,
                'ram': 0.0}
        })

    def test_breakdown_goals_aggregate_func(self):
        goal_1 = self._create_goal(self.org['id'], 'avg', func='avg')
        goal_2 = self._create_goal(self.org['id'], 'sum', func='sum')
        goal_3 = self._create_goal(self.org['id'], 'max', func='max')
        goal_4 = self._create_goal(self.org['id'], 'last', func='last')
        valid_application = {
            'name': 'My test project',
            'key': 'test_project',
            'goals': [goal_1['id'], goal_2['id'], goal_3['id'], goal_4['id']]
        }
        code, app = self.client.application_create(
            self.org['id'], valid_application)
        self.assertEqual(code, 201)
        self.assertEqual(len(app['goals']), 4)
        now = int(datetime.utcnow().timestamp())
        run = self._create_run(self.org['id'], app['id'], ['i-1'],
                               start=now - 2, finish=now)
        for dt, val in [
            (now - 2, 10), (now - 1, 20), (now - 1, 30), (now, 50), (now, 40)
        ]:
            self._create_log(
                run['_id'], dt, data={
                    k: val for k in ['avg', 'sum', 'max', 'last']
                }, instance_id='i-1')
        code, resp = self.client.run_breakdown_get(self.org['id'], run['_id'])
        self.assertEqual(code, 200)
        self.assertEqual(resp['breakdown'][str(now - 2)]['data'],
                         {'avg': 10.0, 'sum': 10, 'max': 10, 'last': 10})
        self.assertEqual(resp['breakdown'][str(now - 1)]['data'],
                         {'avg': 25.0, 'sum': 50, 'max': 30, 'last': 30})
        self.assertEqual(resp['breakdown'][str(now)]['data'],
                         {'avg': 45.0, 'sum': 90, 'max': 50, 'last': 40})
