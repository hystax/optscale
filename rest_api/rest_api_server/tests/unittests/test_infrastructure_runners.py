import uuid

from datetime import datetime

from rest_api.rest_api_server.tests.unittests.test_infrastructure_base import (
    TestInfrastructureBase)


class TestRunnersApi(TestInfrastructureBase):
    def setUp(self, version='v2'):
        super().setUp(version)
        _, template = self.client.template_create(
            self.organization_id, self.valid_template)
        self.template_id = template['id']
        self.valid_runset = {
            'task_id': self.task_id,
            'cloud_account_id': self.cloud_account_id,
            'region_id': 'us-east-1',
            'instance_type': 'm5',
            'name_prefix': 'test_prefix',
            'tags': {
                'template': 'test'
            },
            'commands': 'echo hello world',
            'hyperparameters': {
                'MODEL_URL': 'https://example.com/model/url',
                'DATASET_URL': 'https://example.com/dataset/url',
                'LEARNING_RATE': '1'
            },
            'destroy_conditions': {
                "max_budget": self.valid_template['budget'],
                "reached_goals": True,
                "max_duration": 123456
            }
        }
        _, runset = self.client.runset_create(
            self.organization_id, self.template_id, self.valid_runset)
        self.runset_id = runset['id']

    def test_list_insider_cost(self):
        code, runners = self.client.runners_list(
            self.organization_id, self.runset_id)
        self.assertEqual(code, 200)
        runners = runners.get('runners', [])
        self.assertTrue(len(runners) > 0)
        for runner in runners:
            self.assertTrue(isinstance(runner.get('state'), str))
            self.assertTrue(isinstance(runner.get('cloud_account'), dict))
            self.assertTrue(isinstance(runner.get('instance_size'), dict))
            self.assertTrue(isinstance(runner.get('region'), dict))
            self.assertEqual(runner.get('duration'), 100)
            # Hardcoded based on duration and flavor cost (hourly cost is 0.224)
            self.assertEqual(runner.get('cost'), 0.0062)

    def test_list_raw_cost(self):
        code, runners = self.client.runners_list(
            self.organization_id, self.runset_id)
        self.assertEqual(code, 200)
        runners = runners.get('runners', [])
        self.assertTrue(len(runners) > 0)
        instance_id, started_at, destroyed_at, insider_cost = (
            None, None, None, None)
        for runner in runners:
            instance_id = runner['instance_id']
            started_at = runner['started_at']
            destroyed_at = runner['destroyed_at']
            insider_cost = runner.get('cost')
        raw_cost = 1.23
        raw_data = [
            {
                'start_date': datetime.fromtimestamp(started_at),
                'end_date': datetime.fromtimestamp(destroyed_at),
                'cost': raw_cost,
                'cloud_account_id': self.cloud_account_id,
                'resource_id': instance_id
            }
        ]
        self.raw_expenses.insert_many(raw_data)
        code, runners = self.client.runners_list(
            self.organization_id, self.runset_id)
        self.assertEqual(code, 200)
        runners = runners.get('runners', [])
        self.assertTrue(len(runners) > 0)
        for runner in runners:
            self.assertNotEqual(runner.get('cost'), insider_cost)
            self.assertEqual(runner.get('cost'), raw_cost)

    def test_list_nonexisting(self):
        code, runners = self.client.runners_list(
            self.organization_id, str(uuid.uuid4()))
        self.assertEqual(code, 404)

    def test_list_deleted_ca(self):
        code, _ = self.client.cloud_account_delete(self.cloud_account_id)
        self.assertEqual(code, 204)
        code, runners = self.client.runners_list(
            self.organization_id, self.runset_id)
        self.assertEqual(code, 200)
        runners = runners.get('runners', [])
        self.assertTrue(len(runners) > 0)
        for runner in runners:
            if runner['cloud_account']['id'] == self.cloud_account_id:
                self.assertTrue(runner['cloud_account']['deleted'])

    def test_list_deleted_task(self):
        code, _ = self.client.task_delete(self.organization_id, self.task_id)
        self.assertEqual(code, 204)
        code, runners = self.client.runners_list(
            self.organization_id, self.runset_id)
        self.assertEqual(code, 200)
        runners = runners.get('runners', [])
        self.assertTrue(len(runners) > 0)
