import uuid
from unittest.mock import patch
from datetime import datetime, timedelta, timezone
from requests import HTTPError
from requests.models import Response
from freezegun import freeze_time
from rest_api.rest_api_server.tests.unittests.test_profiling_base import (
    TestProfilingBase)


class TestTaskApi(TestProfilingBase):

    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.org = self.client.organization_create({'name': "organization"})
        self.valid_task = {
            'name': 'My test project',
            'key': 'test_project',
            'description': 'Test description'
        }
        auth_user = str(uuid.uuid4())
        _, self.employee = self.client.employee_create(
            self.org['id'], {'name': 'name1', 'auth_user_id': auth_user})
        patch('rest_api.rest_api_server.controllers.base.BaseController.'
              'get_user_id', return_value=auth_user).start()

    def test_create_req_params(self):
        for req in ['key', 'name']:
            params = self.valid_task.copy()
            params.pop(req)
            code, resp = self.client.task_create(self.org['id'], params)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0216')
            params[req] = ''
            code, resp = self.client.task_create(self.org['id'], params)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0215')
            params[req] = 1
            code, resp = self.client.task_create(self.org['id'], params)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0214')

    def test_create_invalid_metrics(self):
        params = self.valid_task.copy()
        params['metrics'] = 'invaild'
        code, resp = self.client.task_create(self.org['id'], params)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0385')

    def test_create_unexpected(self):
        for k in ['id', 'another']:
            params = self.valid_task.copy()
            params[k] = 'value'
            code, resp = self.client.task_create(self.org['id'], params)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0212')

    def test_create_task(self):
        code, resp = self.client.task_create(
            self.org['id'], self.valid_task)
        self.assertEqual(code, 201)
        metric_1 = self._create_metric(self.org['id'], 'metric_1')
        metric_2 = self._create_metric(self.org['id'], 'metric_2')
        self.valid_task['key'] = 'test_2'
        body = self.valid_task.copy()
        body['metrics'] = list(map(lambda x: x['id'], [metric_1, metric_2]))
        code, resp = self.client.task_create(self.org['id'], body)
        self.assertEqual(code, 201)
        for k, v in self.valid_task.items():
            self.assertEqual(resp[k], v)
        metrics = resp['metrics']
        self.assertEqual(len(metrics), 2)
        for metric in metrics:
            self.assertTrue(metric['id'] in [metric_1['id'], metric_2['id']])

    def test_list_task(self):
        code, resp = self.client.task_list(self.org['id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['tasks']), 0)
        code, task1 = self.client.task_create(
            self.org['id'], {
                'name': 'My task 1',
                'key': 'test_task_1'
            })
        self.assertEqual(code, 201)
        code, task2 = self.client.task_create(
            self.org['id'], {
                'name': 'My task 2',
                'key': 'test_task_2'
            })
        self.assertEqual(code, 201)

        code, resp = self.client.task_list(self.org['id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['tasks']), 2)
        for k in list(map(lambda x: x['id'], resp['tasks'])):
            self.assertTrue(k in [task1['id'], task2['id']])

    def test_get_task(self):
        code, task = self.client.task_create(
            self.org['id'], self.valid_task)
        self.assertEqual(code, 201)
        code, resp = self.client.task_get(self.org['id'], '123')
        self.assertEqual(code, 404)
        self.verify_error_code(resp, 'OE0002')

        code, resp = self.client.task_get(self.org['id'], task['id'])
        self.assertEqual(code, 200)
        self.assertEqual(resp, task)

    def test_delete_task(self):
        code, task = self.client.task_create(
            self.org['id'], self.valid_task)
        self.assertEqual(code, 201)
        code, _ = self.client.task_delete(self.org['id'], task['id'])
        self.assertEqual(code, 204)
        code, _ = self.client.task_delete(self.org['id'], task['id'])
        self.assertEqual(code, 404)

    def test_update_unexpected(self):
        for k in ['metrics', 'id']:
            code, resp = self.client.task_update(
                self.org['id'], '123', {k: 'value'})
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0212')

    def test_update_invalid(self):
        code, task = self.client.task_create(
            self.org['id'], self.valid_task)
        self.assertEqual(code, 201)

        code, resp = self.client.task_update(
            self.org['id'], '123', {'name': 'new'})
        self.assertEqual(code, 404)
        self.verify_error_code(resp, 'OE0002')

        code, resp = self.client.task_update(
            self.org['id'], task['id'], {'name': 123})
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0214')

        code, resp = self.client.task_update(
            self.org['id'], task['id'], {'name': ''})
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0215')

        for k in ['attach', 'detach']:
            code, resp = self.client.task_update(
                self.org['id'], task['id'], {k: 'value'})
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0385')

            code, resp = self.client.task_update(
                self.org['id'], task['id'], {k: [123]})
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0214')

    def test_update(self):
        metric_1 = self._create_metric(self.org['id'], 'metric_1')
        metric_2 = self._create_metric(self.org['id'], 'metric_2')
        metric_3 = self._create_metric(self.org['id'], 'metric_3')
        metric_4 = self._create_metric(self.org['id'], 'metric_4')
        self.valid_task['metrics'] = [metric_1['id'], metric_4['id']]
        code, task = self.client.task_create(self.org['id'], self.valid_task)
        self.assertEqual(code, 201)
        self.assertEqual(len(task['metrics']), 2)
        updates = {
            'name': 'new_name',
            'attach': [metric_2['id'], metric_3['id']],
            'detach': [metric_1['id']]
        }
        code, resp = self.client.task_update(
            self.org['id'], task['id'], updates)
        self.assertEqual(code, 200)
        self.assertEqual(resp['name'], updates['name'])
        self.assertEqual(len(resp['metrics']), 3)
        for g in [metric_2['id'], metric_3['id'], metric_4['id']]:
            self.assertTrue(g in list(map(lambda x: x['id'], resp['metrics'])))

    def test_update_reset(self):
        code, task = self.client.task_create(self.org['id'], self.valid_task)
        self.assertEqual(code, 201)

        code, resp = self.client.task_update(
            self.org['id'], task['id'], {'description': None})
        self.assertEqual(code, 200)
        self.assertIsNone(resp['description'])

        code, _ = self.client.task_update(
            self.org['id'], task['id'], {'name': None})
        self.assertEqual(code, 400)
        code, _ = self.client.task_update(
            self.org['id'], task['id'], {'attach': None})
        self.assertEqual(code, 400)

    def test_update_empty(self):
        code, task = self.client.task_create(self.org['id'], self.valid_task)
        self.assertEqual(code, 201)

        code, _ = self.client.task_update(
            self.org['id'], task['id'], {'description': ''})
        self.assertEqual(code, 200)

        code, _ = self.client.task_update(
            self.org['id'], task['id'], {'attach': []})
        self.assertEqual(code, 400)

    def test_detach_last(self):
        metric_1 = self._create_metric(self.org['id'], 'metric_1')
        self.valid_task['metrics'] = [metric_1['id']]
        code, task = self.client.task_create(
            self.org['id'], self.valid_task)
        self.assertEqual(code, 201)
        self.assertEqual(len(task['metrics']), 1)
        updates = {
            'name': 'new_name',
            'detach': [metric_1['id']]
        }
        code, resp = self.client.task_update(
            self.org['id'], task['id'], updates)
        self.assertEqual(code, 200)
        self.assertEqual(resp['name'], updates['name'])
        self.assertEqual(len(resp['metrics']), 0)

    def test_update_owner(self):
        code, task = self.client.task_create(self.org['id'], self.valid_task)
        self.assertEqual(code, 201)

        updates = {
            'name': 'new_name',
            'owner_id': str(uuid.uuid4())
        }
        code, resp = self.client.task_update(
            self.org['id'], task['id'], updates)
        self.assertEqual(code, 404)
        self.verify_error_code(resp, 'OE0002')

        _, employee2 = self.client.employee_create(
            self.org['id'], {'name': 'name2', 'auth_user_id': str(uuid.uuid4())})
        updates['owner_id'] = employee2['id']
        code, resp = self.client.task_update(
            self.org['id'], task['id'], updates)
        self.assertEqual(code, 200)
        self.assertEqual(resp['name'], updates['name'])
        self.assertEqual(resp['owner']['id'], employee2['id'])

    def test_task_status(self):
        code, task = self.client.task_create(self.org['id'], self.valid_task)
        self.assertEqual(code, 201)
        code, resp = self.client.task_get(self.org['id'], task['id'])
        self.assertEqual(code, 200)
        self.assertEqual(resp['status'], 'created')
        dt = int(datetime(2024, 2, 2).timestamp())
        for run_state, expected_status in enumerate([
            'running', 'completed', 'failed'
        ], start=1):
            start = dt + run_state
            finish = start + 1
            self._create_run(
                self.org['id'], task['id'], ['i-1'], state=run_state,
                start=start, finish=finish)
            _, resp = self.client.task_get(self.org['id'], task['id'])
            self.assertEqual(resp['status'], expected_status)

    def test_task_executors(self):
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
            cloud_acc['id'], body, behavior='skip_existing',
            return_resources=True)
        self.assertEqual(code, 200)
        now = datetime.utcnow().timestamp()
        # create 2nd run earlier then 1st one
        self._create_run(self.org['id'], task['id'], ['i-1'],
                         start=now - 2, finish=now)
        self._create_run(self.org['id'], task['id'],
                         [valid_resource['cloud_resource_id']],
                         start=now - 5, finish=now - 3)
        code, resp = self.client.task_get(self.org['id'], task['id'])
        self.assertEqual(code, 200)
        self.assertEqual(resp['runs_count'], 2)
        self.assertEqual(resp['last_run_executor']['instance_id'], 'i-1')
        self.assertIsNone(resp['last_run_executor']['resource'])

        self._create_run(self.org['id'], task['id'],
                         [valid_resource['cloud_resource_id']],
                         start=now - 1, finish=now)
        code, resp = self.client.task_get(self.org['id'], task['id'])
        self.assertEqual(code, 200)
        self.assertEqual(resp['runs_count'], 3)
        self.assertEqual(resp['last_run_executor']['instance_id'],
                         valid_resource['cloud_resource_id'])
        for k, v in valid_resource.items():
            self.assertEqual(resp['last_run_executor']['resource'][k], v)

    def test_create_task_duplicate(self):
        code, task = self.client.task_create(
            self.org['id'], self.valid_task)
        self.assertEqual(code, 201)

        code, task = self.client.task_create(
            self.org['id'], self.valid_task)
        self.assertEqual(code, 409)

    def test_update_on_arcee_conflict_err(self):
        code, task = self.client.task_create(
            self.org['id'], self.valid_task)
        self.assertEqual(code, 201)

        def raise_409(*_args, **_kwargs):
            err = HTTPError('Metric is used in leaderboard')
            err.response = Response()
            err.response.status_code = 409
            raise err

        patch('rest_api.rest_api_server.controllers.base.'
              'BaseProfilingTokenController.arcee_client.task_update',
              side_effect=raise_409).start()

        code, resp = self.client.task_update(
            self.org['id'], task['id'], {'name': 'name'})
        self.assertEqual(code, 409)
        self.assertEqual(resp['error']['error_code'], 'OE0556')

    def test_task_last_run_and_history(self):
        metric_1 = self._create_metric(self.org['id'], 'loss')
        self.valid_task['metrics'] = [metric_1['id']]
        code, task = self.client.task_create(
            self.org['id'], self.valid_task)
        self.assertEqual(code, 201)
        self.assertEqual(len(task['metrics']), 1)
        now = datetime.utcnow().timestamp()
        self._create_run(self.org['id'], task['id'], ['i-1'],
                         start=now - 2, finish=now, data={'loss': 10})
        # second created run should be first
        self._create_run(self.org['id'], task['id'], ['i-2'], start=now - 5,
                         finish=now - 3, data={'loss': 55})
        code, resp = self.client.task_get(self.org['id'], task['id'])
        self.assertEqual(code, 200)
        self.assertEqual(resp['last_run'], now - 2)
        self.assertEqual(resp['last_run_executor']['instance_id'], 'i-1')
        run_metric = resp['run_metrics'][0]
        self.assertEqual(run_metric['last_run_value'], 10)
        self.assertEqual(run_metric['history'], [55, 10])

    def test_task_description_length(self):
        valid_task = self.valid_task.copy()
        max_len_description = ''.join('x' for _ in range(0, 1000))
        valid_task['description'] = max_len_description
        code, task = self.client.task_create(
            self.org['id'], valid_task)
        self.assertEqual(code, 201)
        self.assertTrue(len(task['description']), 1000)

        valid_task['description'] = max_len_description + 'x'
        code, resp = self.client.task_create(
            self.org['id'], valid_task)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0215')

        code, resp = self.client.task_update(
            self.org['id'], task['id'], {
                'description': valid_task['description']
            }
        )
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0215')

        code, resp = self.client.task_update(
            self.org['id'], task['id'], {
                'description': valid_task['description'][2:]
            }
        )
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['description']), 999)

    def test_get_invalid_params(self):
        code, task = self.client.task_create(
            self.org['id'], self.valid_task)
        self.assertEqual(code, 201)
        for value in ['invalid', True]:
            code, resp = self.client.task_get(
                self.org['id'], task['id'], last_runs=value)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0217')
            code, resp = self.client.task_get(
                self.org['id'], task['id'], last_leaderboards=value)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0217')

    def test_task_last_runs(self):
        code, task = self.client.task_create(
            self.org['id'], self.valid_task)
        self.assertEqual(code, 201)
        now = int(datetime(2024, 10, 10, 12, 15).timestamp())
        self._create_run(self.org['id'], task['id'], ['i-1'],
                         start=now - 2, finish=now, data={'loss': 10})
        self._create_run(self.org['id'], task['id'], ['i-2'], start=now - 5,
                         finish=now - 3, data={'loss': 55})
        code, resp = self.client.task_get(self.org['id'], task['id'])
        self.assertEqual(code, 200)
        self.assertIsNone(resp.get('last_runs'))

        code, resp = self.client.task_get(self.org['id'], task['id'],
                                          last_runs=1)
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['last_runs']), 1)
        self.assertEqual(resp['last_runs'][0]['finish'], now)

        code, resp = self.client.task_get(self.org['id'], task['id'],
                                          last_runs=10)
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['last_runs']), 2)
        self.assertTrue(resp['last_runs'][0]['start'], now - 2)
        self.assertTrue(resp['last_runs'][1]['start'], now - 3)

    def test_task_last_leaderboards(self):
        _, task = self.client.task_create(
            self.org['id'], self.valid_task)
        metric1 = self._create_metric(self.org['id'], key='metric1_key')
        leaderboard = {
            'primary_metric': metric1['id'],
            'other_metrics': [],
            'grouping_tags': ['test_tag'],
            'group_by_hp': True,
            'filters': [
                 {
                    'id': metric1['id'],
                    'min': 1,
                    'max': 100
                 }
            ],
        }
        _, leaderboard = self.client.leaderboard_create(
            self.org['id'], task['id'], leaderboard)
        valid_dataset = {
            'path': 's3://ml-bucket/dataset',
            'name': 'Test',
            'description': 'Test ML dataset',
            'labels': ['test', 'demo'],
            'timespan_from': 1698740386,
            'timespan_to': 1698741386
        }
        _, dataset = self.client.dataset_create(self.org['id'], valid_dataset)
        dt = datetime(2023, 10, 10, tzinfo=timezone.utc)
        with freeze_time(dt + timedelta(days=1)):
            self.client.leaderboard_dataset_create(
                self.org['id'], leaderboard['id'], {
                    'name': "test",
                    'dataset_ids': [dataset['id']]
                })
        with freeze_time(dt):
            self.client.leaderboard_dataset_create(
                self.org['id'], leaderboard['id'], {
                    'name': "test2",
                    'dataset_ids': [dataset['id']]
                })
        code, resp = self.client.task_get(self.org['id'], task['id'])
        self.assertEqual(code, 200)
        self.assertIsNone(resp.get('last_leaderboards'))

        code, resp = self.client.task_get(
            self.org['id'], task['id'], last_leaderboards=1)
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['last_leaderboards']), 1)
        self.assertEqual(resp['last_leaderboards'][0]['name'], 'test')

        code, resp = self.client.task_get(
            self.org['id'], task['id'], last_leaderboards=10)
        self.assertEqual(len(resp['last_leaderboards']), 2)
        self.assertEqual(resp['last_leaderboards'][0]['created_at'],
                         int((dt + timedelta(days=1)).timestamp()))
        self.assertEqual(resp['last_leaderboards'][1]['created_at'],
                         int(dt.timestamp()))
