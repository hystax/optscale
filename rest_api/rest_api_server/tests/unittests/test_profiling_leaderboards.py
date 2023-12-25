import uuid
from rest_api.rest_api_server.tests.unittests.test_profiling_base import TestProfilingBase


class TestLeaderboardsApi(TestProfilingBase):

    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.org = self.client.organization_create({'name': "organization"})
        self.auth_user = self.gen_id()
        _, self.employee = self.client.employee_create(
            self.org['id'], {'name': 'employee',
                             'auth_user_id': self.auth_user})
        self.goal1 = self._create_goal(self.org['id'], key='goal1_key')
        self.goal2 = self._create_goal(self.org['id'], key='goal2_key')
        self.app1 = self._create_application(
            self.org['id'], self.employee['id'],
            goals=[self.goal1['id']])
        self.valid_leaderboard = {
            'primary_goal': self.goal1['id'],
            'other_goals': [],
            'grouping_tags': ['test_tag'],
            'group_by_hp': True,
            'filters': [
                 {
                    'id': self.goal1['id'],
                    'min': 1,
                    'max': 100
                 }
            ],
        }

    def test_create_leaderboard(self):
        code, resp = self.client.leaderboard_create(
            self.org['id'], self.app1['id'], self.valid_leaderboard)
        self.assertEqual(code, 201)
        primary_goal = self.valid_leaderboard.pop('primary_goal')
        self.assertEqual(resp['primary_goal']['id'], primary_goal)
        filters = self.valid_leaderboard.pop('filters')
        for k, v in filters[0].items():
            self.assertEqual(resp['filters'][0][k], v)
        for k, v in self.valid_leaderboard.items():
            self.assertEqual(resp[k], v)

    def test_create_req_params(self):
        for req in ['primary_goal', 'grouping_tags']:
            params = self.valid_leaderboard.copy()
            params.pop(req)
            code, resp = self.client.leaderboard_create(self.org['id'],
                                                        self.app1['id'], params)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0216')

    def test_create_invalid_type(self):
        for param in ['grouping_tags', 'other_goals', 'filters']:
            params = self.valid_leaderboard.copy()
            for value in ['test', 123, {'test': 123}]:
                params[param] = value
                code, resp = self.client.leaderboard_create(
                    self.org['id'], self.app1['id'], params)
                self.assertEqual(code, 400)
                self.verify_error_code(resp, 'OE0385')
        for param in ['primary_goal']:
            params = self.valid_leaderboard.copy()
            for value in [['test'], 123, {'test': 123}]:
                params[param] = value
                code, resp = self.client.leaderboard_create(
                    self.org['id'], self.app1['id'], params)
                self.assertEqual(code, 400)
                self.verify_error_code(resp, 'OE0214')
        for param in ['group_by_hp']:
            params = self.valid_leaderboard.copy()
            for value in ['', 32, 'err']:
                params[param] = value
                code, resp = self.client.leaderboard_create(
                    self.org['id'], self.app1['id'], params)
                self.assertEqual(code, 400)
                self.verify_error_code(resp, 'OE0226')

    def test_create_unexpected(self):
        for k in ['id', 'deleted_at', 'created_at', 'token', 'impostor']:
            params = self.valid_leaderboard.copy()
            params[k] = 'value'
            code, resp = self.client.leaderboard_create(
                self.org['id'], self.app1['id'], params)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0212')

    def test_create_invalid_filters(self):
        params = self.valid_leaderboard.copy()
        params['filters'] = [{'id': self.goal2['id'], 'test': 123}]
        code, resp = self.client.leaderboard_create(
            self.org['id'], self.app1['id'], params)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0212')

        params = self.valid_leaderboard.copy()
        params['other_goals'] = [str(uuid.uuid4())]
        params['filters'] = [{'id': str(uuid.uuid4()), 'min': 1, 'max': 123}]
        code, resp = self.client.leaderboard_create(
            self.org['id'], self.app1['id'], params)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0217')

        params = self.valid_leaderboard.copy()
        params['other_goals'] = [self.goal2['id']]
        params['filters'] = [{'id': self.goal2['id']}]
        code, resp = self.client.leaderboard_create(
            self.org['id'], self.app1['id'], params)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0217')

        params = self.valid_leaderboard.copy()
        params['other_goals'] = [self.goal2['id']]
        params['filters'] = [{'id': self.goal2['id']}]
        code, resp = self.client.leaderboard_create(
            self.org['id'], self.app1['id'], params)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0217')

        params = self.valid_leaderboard.copy()
        params['other_goals'] = [str(uuid.uuid4())]
        params['filters'] = [
            {'id': params['other_goals'][0], 'min': 11, 'max': 0}]
        code, resp = self.client.leaderboard_create(
            self.org['id'], self.app1['id'], params)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0541')

        params = self.valid_leaderboard.copy()
        params['other_goals'] = [self.goal2['id']]
        params['filters'] = [
            {'id': self.goal2['id'], 'min': None}]
        code, resp = self.client.leaderboard_create(
            self.org['id'], self.app1['id'], params)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0217')

    def test_create_negative_filters(self):
        min_v = -333
        max_v = -222
        params = self.valid_leaderboard.copy()
        params['other_goals'] = [self.goal2['id']]
        params['filters'] = [
            {'id': self.goal2['id'], 'min': min_v, 'max': max_v}]
        code, resp = self.client.leaderboard_create(
            self.org['id'], self.app1['id'], params)
        self.assertEqual(code, 201)
        self.assertEqual(resp['filters'][0]['min'], min_v)
        self.assertEqual(resp['filters'][0]['max'], max_v)

    def test_get_leaderboard(self):
        code, resp = self.client.leaderboard_get(
            self.org['id'], self.app1['id'])
        self.assertEqual(code, 200)
        self.assertEqual(resp, {})
        code, leaderboard = self.client.leaderboard_create(
            self.org['id'], self.app1['id'], self.valid_leaderboard)
        self.assertEqual(code, 201)
        code, resp = self.client.leaderboard_get(
            self.org['id'], self.app1['id'])
        self.assertEqual(code, 200)
        self.assertEqual(resp, leaderboard)

    def test_delete_leaderboard(self):
        code, leaderboard = self.client.leaderboard_create(
            self.org['id'], self.app1['id'], self.valid_leaderboard)
        self.assertEqual(code, 201)
        code, resp = self.client.leaderboard_delete(
            self.org['id'], leaderboard['application_id'])
        self.assertEqual(code, 204)
        code, resp = self.client.leaderboard_delete(
            self.org['id'], leaderboard['application_id'])
        self.assertEqual(code, 404)

    def test_update_unexpected(self):
        code, leaderboard = self.client.leaderboard_create(
            self.org['id'], self.app1['id'], self.valid_leaderboard)
        self.assertEqual(code, 201)
        for k in ['key', 'id']:
            code, resp = self.client.leaderboard_update(
                self.org['id'], leaderboard['application_id'],
                {k: 'value'})
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0212')

    def test_update_invalid(self):
        for param in ['created_at', 'deleted_at', 'id', 'impostor']:
            code, resp = self.client.leaderboard_update(
                self.org['id'], self.app1['id'], {param: 'value'})
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0212')

        for param in ['grouping_tags', 'other_goals', 'filters']:
            params = self.valid_leaderboard.copy()
            for value in ['test', 123, {'test': 123}]:
                params[param] = value
                code, resp = self.client.leaderboard_update(
                    self.org['id'], self.app1['id'], params)
                self.assertEqual(code, 400)
                self.verify_error_code(resp, 'OE0385')
        for param in ['primary_goal']:
            params = self.valid_leaderboard.copy()
            for value in [['test'], 123, {'test': 123}]:
                params[param] = value
                code, resp = self.client.leaderboard_update(
                    self.org['id'], self.app1['id'], params)
                self.assertEqual(code, 400)
                self.verify_error_code(resp, 'OE0214')
        for param in ['group_by_hp']:
            params = self.valid_leaderboard.copy()
            for value in ['', 32, 'err']:
                params[param] = value
                code, resp = self.client.leaderboard_update(
                    self.org['id'], self.app1['id'], params)
                self.assertEqual(code, 400)
                self.verify_error_code(resp, 'OE0226')

    def test_update(self):
        updates = {
            'primary_goal': self.goal2['id'],
            'other_goals': [self.goal1['id']],
            'grouping_tags': ['test_tag_2'],
            'group_by_hp': False,
            'filters': [
                 {
                    'id': self.goal1['id'],
                    'min': 1,
                    'max': 100
                 }
            ],

        }
        code, resp = self.client.leaderboard_update(
            self.org['id'], self.app1['id'], updates)
        self.assertEqual(code, 404)
        self.verify_error_code(resp, 'OE0002')

        code, leaderboard = self.client.leaderboard_create(
            self.org['id'], self.app1['id'], self.valid_leaderboard)
        self.assertEqual(code, 201)

        code, resp = self.client.leaderboard_update(
            self.org['id'], self.app1['id'], updates)
        self.assertEqual(code, 200)
        primary_goal = updates.pop('primary_goal')
        self.assertEqual(resp['primary_goal']['id'], primary_goal)
        other_goals = updates.pop('other_goals')
        self.assertEqual(resp['other_goals'][0]['id'], other_goals[0])
        filters = updates.pop('filters')
        for k, v in filters[0].items():
            self.assertEqual(resp['filters'][0][k], v)
        for k, v in updates.items():
            self.assertEqual(resp[k], v)

    def test_create_duplicate(self):
        code, leaderboard = self.client.leaderboard_create(
            self.org['id'], self.app1['id'], self.valid_leaderboard)
        self.assertEqual(code, 201)
        code, resp = self.client.leaderboard_create(
            self.org['id'], self.app1['id'], self.valid_leaderboard)
        self.assertEqual(code, 409)
        self.verify_error_code(resp, 'OE0549')

    def test_details(self):
        code, leaderboard = self.client.leaderboard_create(
            self.org['id'], self.app1['id'], self.valid_leaderboard)
        self.assertEqual(code, 201)

        code, resp = self.client.leaderboard_get(self.org['id'], self.app1[
            'id'], details=True)
        self.assertEqual(resp['details'], {})

    def test_create_with_zero_filter(self):
        params = self.valid_leaderboard.copy()
        params['filters'] = [{'id': params['primary_goal'], 'min': 0}]
        code, leaderboard = self.client.leaderboard_create(
            self.org['id'], self.app1['id'], params)
        self.assertEqual(code, 201)
        self.assertEqual(leaderboard['filters'][0]['min'], 0)

        app2 = self._create_application(
            self.org['id'], self.employee['id'], goals=[self.goal1['id']],
            key='app2key')
        params['filters'] = [{'id': params['primary_goal'], 'max': 0}]
        code, leaderboard = self.client.leaderboard_create(
            self.org['id'], app2['id'], params)
        self.assertEqual(code, 201)
        self.assertEqual(leaderboard['filters'][0]['max'], 0)
