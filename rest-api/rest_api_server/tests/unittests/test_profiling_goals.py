from rest_api_server.tests.unittests.test_profiling_base import TestProfilingBase


class TestGoalsApi(TestProfilingBase):

    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.org = self.client.organization_create({'name': "organization"})
        self.valid_goal = {
            'target_value': 0.7,
            'tendency': 'more',
            'key': 'test_name',
            'name': 'Test goal',
            'function': 'avg'
        }

    def test_create_req_params(self):
        for req in ['tendency', 'name', 'key', 'function']:
            params = self.valid_goal.copy()
            params.pop(req)
            code, resp = self.client.goal_create(self.org['id'], params)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0216')
            params[req] = ''
            code, resp = self.client.goal_create(self.org['id'], params)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0215')
            params[req] = 1
            code, resp = self.client.goal_create(self.org['id'], params)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0214')
        params = self.valid_goal.copy()
        params.pop('target_value')
        code, resp = self.client.goal_create(self.org['id'], params)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0216')

        params['target_value'] = ''
        code, resp = self.client.goal_create(self.org['id'], params)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0466')

        params['target_value'] = 1231821321312.0
        code, resp = self.client.goal_create(self.org['id'], params)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0224')

        params = self.valid_goal.copy()
        params['tendency'] = 'some_value'
        code, resp = self.client.goal_create(self.org['id'], params)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0217')

    def test_create_unexpected(self):
        for k in ['id', 'another']:
            params = self.valid_goal.copy()
            params[k] = 'value'
            code, resp = self.client.goal_create(self.org['id'], params)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0212')

    def test_create_goal(self):
        code, resp = self.client.goal_create(
            self.org['id'], self.valid_goal)
        self.assertEqual(code, 201)
        self.valid_goal['func'] = self.valid_goal.pop('function')
        for k, v in self.valid_goal.items():
            self.assertEqual(resp[k], v)

    def test_list_goals(self):
        code, resp = self.client.goal_list(self.org['id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['goals']), 0)

        code, goal1 = self.client.goal_create(
            self.org['id'], {
                'target_value': 0.7,
                'tendency': 'more',
                'key': 'test_name',
                'name': 'Test goal',
                'function': 'avg'
            })
        self.assertEqual(code, 201)
        code, goal2 = self.client.goal_create(
            self.org['id'], {
                'target_value': 0.7,
                'tendency': 'less',
                'key': 'test_name_2',
                'name': 'Test goal 2',
                'function': 'avg'
            })
        self.assertEqual(code, 201)

        code, resp = self.client.goal_list(self.org['id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['goals']), 2)
        for k in list(map(lambda x: x['id'], resp['goals'])):
            self.assertTrue(k in [goal1['id'], goal2['id']])

    def test_get_goal(self):
        code, resp = self.client.goal_get(self.org['id'], '123')
        self.assertEqual(code, 404)
        self.verify_error_code(resp, 'OE0002')

        code, goal = self.client.goal_create(
            self.org['id'], self.valid_goal)
        self.assertEqual(code, 201)
        code, resp = self.client.goal_get(self.org['id'], goal['id'])
        self.assertEqual(code, 200)
        self.assertEqual(resp, goal)

    def test_delete_goal(self):
        code, goal = self.client.goal_create(
            self.org['id'], self.valid_goal)
        self.assertEqual(code, 201)
        code, resp = self.client.goal_delete(self.org['id'], goal['id'])
        self.assertEqual(code, 204)
        code, resp = self.client.goal_delete(self.org['id'], goal['id'])
        self.assertEqual(code, 404)

    def test_update_unexpected(self):
        code, goal = self.client.goal_create(
            self.org['id'], self.valid_goal)
        self.assertEqual(code, 201)
        for k in ['key', 'id']:
            code, resp = self.client.goal_update(
                self.org['id'], goal['id'], {k: 'value'})
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0212')

    def test_update_invalid(self):
        code, resp = self.client.goal_update(
            self.org['id'], '123', {'name': 123})
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0214')

        code, resp = self.client.goal_update(
            self.org['id'], '123', {'name': ''})
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0215')

        code, resp = self.client.goal_update(
            self.org['id'], '123', {'target_value': 'value'})
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0466')

        code, resp = self.client.goal_update(
            self.org['id'], '123', {'tendency': 'value'})
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0217')

    def test_update(self):
        code, goal = self.client.goal_create(
            self.org['id'], self.valid_goal)
        self.assertEqual(code, 201)

        updates = {
            'target_value': 0.6,
            'tendency': 'less',
            'name': 'Another goal name'
        }
        code, resp = self.client.goal_update(
            self.org['id'], '123', updates)
        self.assertEqual(code, 404)
        self.verify_error_code(resp, 'OE0002')

        code, resp = self.client.goal_update(
            self.org['id'], goal['id'], updates)
        self.assertEqual(code, 200)
        for k, v in updates.items():
            self.assertEqual(resp[k], v)

    def test_create_duplicate(self):
        code, goal = self.client.goal_create(
            self.org['id'], self.valid_goal)
        self.assertEqual(code, 201)
        code, resp = self.client.goal_create(
            self.org['id'], self.valid_goal)
        self.assertEqual(code, 409)
        self.verify_error_code(resp, 'OE0535')
