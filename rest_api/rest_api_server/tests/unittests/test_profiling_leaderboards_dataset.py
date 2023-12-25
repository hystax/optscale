from rest_api.rest_api_server.tests.unittests.test_profiling_base import TestProfilingBase


class TestLeaderboardDatasetApi(TestProfilingBase):

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
        _, resp = self.client.leaderboard_create(
            self.org['id'], self.app1['id'], self.valid_leaderboard)
        self.leaderboard_id = resp["id"]
        self.organization_id = self.org['id']
        self.valid_dataset = {
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
        _, dataset = self.client.dataset_create(
            self.organization_id, self.valid_dataset)
        self.dataset_ids = [dataset['id']]
        self.leaderboard_dataset = self.client.leaderboard_dataset_create(
            self.organization_id,
            "test", self.leaderboard_id,
            self.dataset_ids)
        _, self.lds = self.leaderboard_dataset

    def test_update_leaderboard_dataset(self):
        code, _ = self.client.leaderboard_dataset_update(
            self.organization_id,
            self.lds["id"],
            name="new name"
        )
        self.assertEqual(code, 200)

    def test_create_leaderboard_dataset(self):
        code, _ = self.leaderboard_dataset
        self.assertEqual(code, 201)

    def test_get_leaderboard_dataset(self):
        code, _ = self.client.leaderboard_dataset_get(
            self.organization_id,
            self.lds["id"],
        )
        self.assertEqual(code, 200)

    def test_get_leaderboard_dataset_details(self):
        code, dslb = self.client.leaderboard_dataset_get(
            self.organization_id,
            self.lds["id"],
            details=True
        )
        self.assertEqual(code, 200)
        details = dslb.get("details")
        self.assertEqual(details, [])

    def test_delete_leaderboard_dataset(self):
        _, lbds = self.leaderboard_dataset = self.client.leaderboard_dataset_create(
            self.organization_id,
            "test1", self.leaderboard_id,
            self.dataset_ids)

        code, _ = self.client.leaderboard_dataset_delete(
            self.organization_id,
            lbds["id"],
        )
        self.assertEqual(code, 204)

    def test_generate_leaderboard(self):
        code, resp = self.client.leaderboard_generate(
            self.organization_id,
            self.lds["id"],
        )
        self.assertEqual(code, 200)
        self.assertEqual(resp, [])

    def test_create_lbds_invalid_ds(self):
        code, resp = self.client.leaderboard_dataset_create(
            self.organization_id,
            "test", self.leaderboard_id,
            'test')
        self.assertEqual(code, 400)
        self.verify_error_code(resp, "OE0385")
        code, resp = self.client.leaderboard_dataset_create(
            self.organization_id,
            "test", self.leaderboard_id,
            [9, ])
        self.assertEqual(code, 400)
        self.verify_error_code(resp, "OE0214")
        code, resp = self.client.leaderboard_dataset_create(
            self.organization_id,
            9, self.leaderboard_id,
            ["t"])
        self.assertEqual(code, 400)
        self.verify_error_code(resp, "OE0214")

    def test_list_leaderboard_datasets(self):
        code, resp = self.client.leaderboard_dataset_list(
            self.organization_id,
            self.leaderboard_id,
        )
        self.assertEqual(code, 200)
        self.assertEqual(len(resp), 1)
