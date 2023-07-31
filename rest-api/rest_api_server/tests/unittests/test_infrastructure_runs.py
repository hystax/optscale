import uuid

from datetime import datetime

from rest_api_server.tests.unittests.test_infrastructure_base import (
    TestInfrastructureBase)


class TestRunsApi(TestInfrastructureBase):
    def setUp(self, version='v2'):
        super().setUp(version)
        _, template = self.client.template_create(
            self.organization_id, self.valid_template)
        self.template_id = template['id']
        _, runset = self.client.runset_create(
            self.organization_id, self.template_id, self.valid_runset)
        self.runset_id = runset['id']
        self.instance_id = 'i-1'

    def test_list_insider_cost(self):
        code, _ = self.client.runset_list(
            self.organization_id, self.template_id)
        self.assertEqual(code, 200)
        now = int(datetime.utcnow().timestamp())
        self._create_run(
            self.organization_id, self.application_id, self.runset_id,
            [self.instance_id], start=now - 60, finish=now-10)
        code, runs = self.client.runset_run_list(
            self.organization_id, self.runset_id)
        self.assertEqual(code, 200)
        runs = runs.get('runs', [])
        self.assertTrue(len(runs) > 0)
        for run in runs:
            self.assertTrue(isinstance(run.get('status'), str))
            self.assertEqual(run.get('duration'), 50)
            executors = run.get('executors', [])
            self.assertTrue(executors)
            for executor in executors:
                # Hardcoded based on duration and flavor cost
                # (hourly cost is 0.224)
                self.assertEqual(executor.get('total_cost'), 0.0031)
            goals = run.get('goals', [])
            self.assertTrue(goals)

    def test_list_deleted_app(self):
        code, _ = self.client.runset_list(
            self.organization_id, self.template_id)
        self.assertEqual(code, 200)
        now = int(datetime.utcnow().timestamp())
        self._create_run(
            self.organization_id, self.application_id, self.runset_id,
            [self.instance_id], start=now - 60, finish=now-10)
        self.client.application_delete(
            self.organization_id, self.application_id)
        code, runs = self.client.runset_run_list(
            self.organization_id, self.runset_id)
        self.assertEqual(code, 200)

    def test_list_deleted_ca(self):
        code, _ = self.client.runset_list(
            self.organization_id, self.template_id)
        self.assertEqual(code, 200)
        now = int(datetime.utcnow().timestamp())
        self._create_run(
            self.organization_id, self.application_id, self.runset_id,
            [self.instance_id], start=now - 60, finish=now-10)
        self.client.cloud_account_delete(self.cloud_account_id)
        code, runs = self.client.runset_run_list(
            self.organization_id, self.runset_id)
        self.assertEqual(code, 200)

    def test_list_raw_cost(self):
        code, _ = self.client.runset_list(
            self.organization_id, self.template_id)
        self.assertEqual(code, 200)
        now = int(datetime.utcnow().timestamp())
        run_start = now - 60
        run_end = now - 10
        self._create_run(
            self.organization_id, self.application_id, self.runset_id,
            [self.instance_id], start=run_start, finish=run_end)
        cost = 1.23
        raw_data = [
            {
                'start_date': datetime.fromtimestamp(run_start),
                'end_date': datetime.fromtimestamp(run_end),
                'cost': cost,
                'cloud_account_id': self.cloud_account_id,
                'resource_id': self.instance_id
            }
        ]
        self.raw_expenses.insert_many(raw_data)
        code, runs = self.client.runset_run_list(
            self.organization_id, self.runset_id)
        self.assertEqual(code, 200)
        runs = runs.get('runs', [])
        self.assertEqual(len(runs), 1)
        for run in runs:
            self.assertEqual(run.get('duration'), 50)
            executors = run.get('executors', [])
            self.assertTrue(executors)
            for executor in executors:
                self.assertEqual(executor.get('total_cost'), cost)

    def test_list_nonexisting(self):
        code, runs = self.client.runset_run_list(
            self.organization_id, str(uuid.uuid4()))
        self.assertEqual(code, 404)
