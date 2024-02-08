import uuid
from unittest.mock import patch
from datetime import datetime, timedelta
from requests import HTTPError
from requests.models import Response
from freezegun import freeze_time
from rest_api.rest_api_server.tests.unittests.test_profiling_base import (
    TestProfilingBase)


class TestApplicationApi(TestProfilingBase):

    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.org = self.client.organization_create({'name': "organization"})
        self.valid_application = {
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
            params = self.valid_application.copy()
            params.pop(req)
            code, resp = self.client.application_create(self.org['id'], params)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0216')
            params[req] = ''
            code, resp = self.client.application_create(self.org['id'], params)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0215')
            params[req] = 1
            code, resp = self.client.application_create(self.org['id'], params)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0214')

    def test_create_invalid_goals(self):
        params = self.valid_application.copy()
        params['goals'] = 'invaild'
        code, resp = self.client.application_create(self.org['id'], params)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0385')

    def test_create_unexpected(self):
        for k in ['id', 'another']:
            params = self.valid_application.copy()
            params[k] = 'value'
            code, resp = self.client.application_create(self.org['id'], params)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0212')

    def test_create_application(self):
        code, resp = self.client.application_create(
            self.org['id'], self.valid_application)
        self.assertEqual(code, 201)
        goal_1 = self._create_goal(self.org['id'], 'goal_1')
        goal_2 = self._create_goal(self.org['id'], 'goal_2')
        self.valid_application['key'] = 'test_2'
        body = self.valid_application.copy()
        body['goals'] = list(map(lambda x: x['id'], [goal_1, goal_2]))
        code, resp = self.client.application_create(self.org['id'], body)
        self.assertEqual(code, 201)
        for k, v in self.valid_application.items():
            self.assertEqual(resp[k], v)
        goals = resp['goals']
        self.assertEqual(len(goals), 2)
        for goal in goals:
            self.assertTrue(goal['id'] in [goal_1['id'], goal_2['id']])

    def test_list_application(self):
        code, resp = self.client.application_list(self.org['id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['applications']), 0)
        code, app1 = self.client.application_create(
            self.org['id'], {
                'name': 'My app 1',
                'key': 'test_app_1'
            })
        self.assertEqual(code, 201)
        code, app2 = self.client.application_create(
            self.org['id'], {
                'name': 'My app 2',
                'key': 'test_app_2'
            })
        self.assertEqual(code, 201)

        code, resp = self.client.application_list(self.org['id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['applications']), 2)
        for k in list(map(lambda x: x['id'], resp['applications'])):
            self.assertTrue(k in [app1['id'], app2['id']])

    def test_get_application(self):
        code, app = self.client.application_create(
            self.org['id'], self.valid_application)
        self.assertEqual(code, 201)
        code, resp = self.client.application_get(self.org['id'], '123')
        self.assertEqual(code, 404)
        self.verify_error_code(resp, 'OE0002')

        code, resp = self.client.application_get(self.org['id'], app['id'])
        self.assertEqual(code, 200)
        self.assertEqual(resp, app)

    def test_delete_application(self):
        code, app = self.client.application_create(
            self.org['id'], self.valid_application)
        self.assertEqual(code, 201)
        code, resp = self.client.application_delete(self.org['id'], app['id'])
        self.assertEqual(code, 204)
        code, resp = self.client.application_delete(self.org['id'], app['id'])
        self.assertEqual(code, 404)

    def test_update_unexpected(self):
        for k in ['goals', 'id']:
            code, resp = self.client.application_update(
                self.org['id'], '123', {k: 'value'})
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0212')

    def test_update_invalid(self):
        code, app = self.client.application_create(
            self.org['id'], self.valid_application)
        self.assertEqual(code, 201)

        code, resp = self.client.application_update(
            self.org['id'], '123', {'name': 'new'})
        self.assertEqual(code, 404)
        self.verify_error_code(resp, 'OE0002')

        code, resp = self.client.application_update(
            self.org['id'], app['id'], {'name': 123})
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0214')

        code, resp = self.client.application_update(
            self.org['id'], app['id'], {'name': ''})
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0215')

        for k in ['attach', 'detach']:
            code, resp = self.client.application_update(
                self.org['id'], app['id'], {k: 'value'})
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0385')

            code, resp = self.client.application_update(
                self.org['id'], app['id'], {k: [123]})
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0214')

    def test_update(self):
        goal_1 = self._create_goal(self.org['id'], 'goal_1')
        goal_2 = self._create_goal(self.org['id'], 'goal_2')
        goal_3 = self._create_goal(self.org['id'], 'goal_3')
        goal_4 = self._create_goal(self.org['id'], 'goal_4')
        self.valid_application['goals'] = [goal_1['id'], goal_4['id']]
        code, app = self.client.application_create(
            self.org['id'], self.valid_application)
        self.assertEqual(code, 201)
        self.assertEqual(len(app['goals']), 2)
        updates = {
            'name': 'new_name',
            'attach': [goal_2['id'], goal_3['id']],
            'detach': [goal_1['id']]
        }
        code, resp = self.client.application_update(
            self.org['id'], app['id'], updates)
        self.assertEqual(code, 200)
        self.assertEqual(resp['name'], updates['name'])
        self.assertEqual(len(resp['goals']), 3)
        for g in [goal_2['id'], goal_3['id'], goal_4['id']]:
            self.assertTrue(g in list(map(lambda x: x['id'], resp['goals'])))

    def test_update_reset(self):
        code, app = self.client.application_create(
            self.org['id'], self.valid_application)
        self.assertEqual(code, 201)

        code, resp = self.client.application_update(
            self.org['id'], app['id'], {'description': None})
        self.assertEqual(code, 200)
        self.assertIsNone(resp['description'])

        code, resp = self.client.application_update(
            self.org['id'], app['id'], {'name': None})
        self.assertEqual(code, 400)
        code, resp = self.client.application_update(
            self.org['id'], app['id'], {'attach': None})
        self.assertEqual(code, 400)

    def test_update_empty(self):
        code, app = self.client.application_create(
            self.org['id'], self.valid_application)
        self.assertEqual(code, 201)

        code, resp = self.client.application_update(
            self.org['id'], app['id'], {'description': ''})
        self.assertEqual(code, 200)

        code, resp = self.client.application_update(
            self.org['id'], app['id'], {'attach': []})
        self.assertEqual(code, 400)

    def test_detach_last(self):
        goal_1 = self._create_goal(self.org['id'], 'goal_1')
        self.valid_application['goals'] = [goal_1['id']]
        code, app = self.client.application_create(
            self.org['id'], self.valid_application)
        self.assertEqual(code, 201)
        self.assertEqual(len(app['goals']), 1)
        updates = {
            'name': 'new_name',
            'detach': [goal_1['id']]
        }
        code, resp = self.client.application_update(
            self.org['id'], app['id'], updates)
        self.assertEqual(code, 200)
        self.assertEqual(resp['name'], updates['name'])
        self.assertEqual(len(resp['goals']), 0)

    def test_update_owner(self):
        code, app = self.client.application_create(
            self.org['id'], self.valid_application)
        self.assertEqual(code, 201)

        updates = {
            'name': 'new_name',
            'owner_id': str(uuid.uuid4())
        }
        code, resp = self.client.application_update(
            self.org['id'], app['id'], updates)
        self.assertEqual(code, 404)
        self.verify_error_code(resp, 'OE0002')

        _, employee2 = self.client.employee_create(
            self.org['id'], {'name': 'name2', 'auth_user_id': str(uuid.uuid4())})
        updates['owner_id'] = employee2['id']
        code, resp = self.client.application_update(
            self.org['id'], app['id'], updates)
        self.assertEqual(code, 200)
        self.assertEqual(resp['name'], updates['name'])
        self.assertEqual(resp['owner']['id'], employee2['id'])

    def test_app_status(self):
        code, app = self.client.application_create(
            self.org['id'], self.valid_application)
        self.assertEqual(code, 201)
        code, resp = self.client.application_get(self.org['id'], app['id'])
        self.assertEqual(code, 200)
        self.assertEqual(resp['status'], 'created')

        for run_state, expected_status in enumerate([
            'running', 'completed', 'failed'
        ], start=1):
            self._create_run(
                self.org['id'], app['id'], ['i-1'], state=run_state)
            _, resp = self.client.application_get(self.org['id'], app['id'])
            self.assertEqual(resp['status'], expected_status)

    def test_application_executors(self):
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
            cloud_acc['id'], body, behavior='skip_existing',
            return_resources=True)
        self.assertEqual(code, 200)
        now = datetime.utcnow().timestamp()
        # create 2nd run earlier then 1st one
        self._create_run(self.org['id'], app['id'], ['i-1'],
                         start=now - 2, finish=now)
        self._create_run(self.org['id'], app['id'],
                         [valid_resource['cloud_resource_id']],
                         start=now - 5, finish=now - 3)
        code, resp = self.client.application_get(self.org['id'], app['id'])
        self.assertEqual(code, 200)
        self.assertEqual(resp['runs_count'], 2)
        self.assertEqual(resp['last_run_executor']['instance_id'], 'i-1')
        self.assertIsNone(resp['last_run_executor']['resource'])

        self._create_run(self.org['id'], app['id'],
                         [valid_resource['cloud_resource_id']],
                         start=now - 1, finish=now)
        code, resp = self.client.application_get(self.org['id'], app['id'])
        self.assertEqual(code, 200)
        self.assertEqual(resp['runs_count'], 3)
        self.assertEqual(resp['last_run_executor']['instance_id'],
                         valid_resource['cloud_resource_id'])
        for k, v in valid_resource.items():
            self.assertEqual(resp['last_run_executor']['resource'][k], v)

    def test_create_app_duplicate(self):
        code, app = self.client.application_create(
            self.org['id'], self.valid_application)
        self.assertEqual(code, 201)

        code, app = self.client.application_create(
            self.org['id'], self.valid_application)
        self.assertEqual(code, 409)

    def test_update_on_arcee_conflict_err(self):
        code, app = self.client.application_create(
            self.org['id'], self.valid_application)
        self.assertEqual(code, 201)

        def raise_409(*_args, **_kwargs):
            err = HTTPError('Goal is used in leaderboard')
            err.response = Response()
            err.response.status_code = 409
            raise err

        patch('rest_api.rest_api_server.controllers.base.'
              'BaseProfilingTokenController.arcee_client.application_update',
              side_effect=raise_409).start()

        code, resp = self.client.application_update(
            self.org['id'], app['id'], {'name': 'name'})
        self.assertEqual(code, 409)
        self.assertEqual(resp['error']['error_code'], 'OE0556')

    def test_application_last_run_and_history(self):
        goal_1 = self._create_goal(self.org['id'], 'loss')
        self.valid_application['goals'] = [goal_1['id']]
        code, app = self.client.application_create(
            self.org['id'], self.valid_application)
        self.assertEqual(code, 201)
        self.assertEqual(len(app['goals']), 1)
        now = datetime.utcnow().timestamp()
        self._create_run(self.org['id'], app['id'], ['i-1'],
                         start=now - 2, finish=now, data={'loss': 10})
        # second created run should be first
        self._create_run(self.org['id'], app['id'], ['i-2'], start=now - 5,
                         finish=now - 3, data={'loss': 55})
        code, resp = self.client.application_get(self.org['id'], app['id'])
        self.assertEqual(code, 200)
        self.assertEqual(resp['last_run'], now - 2)
        self.assertEqual(resp['last_run_executor']['instance_id'], 'i-1')
        run_goal = resp['run_goals'][0]
        self.assertEqual(run_goal['last_run_value'], 10)
        self.assertEqual(run_goal['history'], [55, 10])

    def test_application_description_length(self):
        valid_application = self.valid_application.copy()
        max_len_description = ''.join('x' for _ in range(0, 1000))
        valid_application['description'] = max_len_description
        code, app = self.client.application_create(
            self.org['id'], valid_application)
        self.assertEqual(code, 201)
        self.assertTrue(len(app['description']), 1000)

        valid_application['description'] = max_len_description + 'x'
        code, resp = self.client.application_create(
            self.org['id'], valid_application)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0215')

        code, resp = self.client.application_update(
            self.org['id'], app['id'], {
                'description': valid_application['description']
            }
        )
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0215')

        code, resp = self.client.application_update(
            self.org['id'], app['id'], {
                'description': valid_application['description'][2:]
            }
        )
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['description']), 999)

    def test_get_invalid_params(self):
        code, app = self.client.application_create(
            self.org['id'], self.valid_application)
        self.assertEqual(code, 201)
        for value in ['invalid', True]:
            code, resp = self.client.application_get(
                self.org['id'], app['id'], last_runs=value)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0217')
            code, resp = self.client.application_get(
                self.org['id'], app['id'], last_leaderboards=value)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0217')

    def test_application_last_runs(self):
        code, app = self.client.application_create(
            self.org['id'], self.valid_application)
        self.assertEqual(code, 201)
        now = int(datetime(2024, 10, 10, 12, 15).timestamp())
        self._create_run(self.org['id'], app['id'], ['i-1'],
                         start=now - 2, finish=now, data={'loss': 10})
        self._create_run(self.org['id'], app['id'], ['i-2'], start=now - 5,
                         finish=now - 3, data={'loss': 55})
        code, resp = self.client.application_get(self.org['id'], app['id'])
        self.assertEqual(code, 200)
        self.assertIsNone(resp.get('last_runs'))

        code, resp = self.client.application_get(self.org['id'], app['id'],
                                                 last_runs=1)
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['last_runs']), 1)
        self.assertEqual(resp['last_runs'][0]['finish'], now)

        code, resp = self.client.application_get(self.org['id'], app['id'],
                                                 last_runs=10)
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['last_runs']), 2)

    def test_application_last_leaderboards(self):
        _, app = self.client.application_create(
            self.org['id'], self.valid_application)
        goal1 = self._create_goal(self.org['id'], key='goal1_key')
        leaderboard = {
            'primary_goal': goal1['id'],
            'other_goals': [],
            'grouping_tags': ['test_tag'],
            'group_by_hp': True,
            'filters': [
                 {
                    'id': goal1['id'],
                    'min': 1,
                    'max': 100
                 }
            ],
        }
        _, leaderboard = self.client.leaderboard_create(
            self.org['id'], app['id'], leaderboard)
        valid_dataset = {
            'path': 's3://ml-bucket/dataset',
            'name': 'Test',
            'description': 'Test ML dataset',
            'labels': ['test', 'demo'],
            'training_set': {
                'path': 's3://ml-bucket/training_set',
                'timespan_from': 1698740386,
                'timespan_to': 1698741386
            },
            'validation_set': {
                'path': 's3://ml-bucket/validation_set',
                'timespan_from': 1698740386,
                'timespan_to': 1698741386
            }
        }
        _, dataset = self.client.dataset_create(self.org['id'], valid_dataset)
        dt = datetime(2023, 10, 10)
        with freeze_time(dt + timedelta(days=1)):
            self.client.leaderboard_dataset_create(
                self.org['id'], "test", leaderboard['id'], [dataset['id']])
        with freeze_time(dt):
            self.client.leaderboard_dataset_create(
                self.org['id'], "test2", leaderboard['id'], [dataset['id']])
        code, resp = self.client.application_get(self.org['id'], app['id'])
        self.assertEqual(code, 200)
        self.assertIsNone(resp.get('last_leaderboards'))

        code, resp = self.client.application_get(
            self.org['id'], app['id'], last_leaderboards=1)
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['last_leaderboards']), 1)
        self.assertEqual(resp['last_leaderboards'][0]['name'], 'test')

        code, resp = self.client.application_get(
            self.org['id'], app['id'], last_leaderboards=10)
        self.assertEqual(len(resp['last_leaderboards']), 2)
