from rest_api.rest_api_server.tests.unittests.test_profiling_base import TestProfilingBase


class TestLeaderboardApi(TestProfilingBase):

    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.org = self.client.organization_create({'name': "organization"})
        self.auth_user = self.gen_id()
        _, self.employee = self.client.employee_create(
            self.org['id'], {'name': 'employee',
                             'auth_user_id': self.auth_user})
        self.metric1 = self._create_metric(self.org['id'], key='metric1_key')
        self.metric2 = self._create_metric(self.org['id'], key='metric2_key')
        self.task1 = self._create_task(
            self.org['id'], self.employee['id'],
            metrics=[self.metric1['id']])
        self.valid_leaderboard_template = {
            'primary_metric': self.metric1['id'],
            'other_metrics': [],
            'grouping_tags': ['test_tag'],
            'group_by_hp': True,
            'filters': [
                 {
                    'id': self.metric1['id'],
                    'min': 1,
                    'max': 100
                 }
            ],
        }
        _, resp = self.client.leaderboard_template_create(
            self.org['id'], self.task1['id'], self.valid_leaderboard_template)
        self.leaderboard_template_id = resp["id"]
        self.organization_id = self.org['id']
        self.valid_dataset = {
            'path': 's3://ml-bucket/dataset',
            'name': 'Test',
            'description': 'Test ML dataset',
            'labels': ['test', 'demo'],
            'timespan_from': 1698740386,
            'timespan_to': 1698741386
        }
        _, dataset = self.client.dataset_create(
            self.organization_id, self.valid_dataset)
        self.dataset_ids = [dataset['id']]
        self.leaderboard = self.client.leaderboard_create(
            self.organization_id,
            self.leaderboard_template_id,
            params={
                'name': 'test',
                'dataset_ids': self.dataset_ids
            })
        _, self.lds = self.leaderboard

    def test_update_leaderboard(self):
        code, _ = self.client.leaderboard_update(
            self.organization_id,
            self.lds["id"],
            params={
                'name': 'new_name'
            }
        )
        self.assertEqual(code, 200)

    def test_create_leaderboard(self):
        code, _ = self.leaderboard
        self.assertEqual(code, 201)

    def test_get_leaderboard(self):
        code, resp = self.client.leaderboard_get(
            self.organization_id,
            self.lds["id"],
        )
        self.assertEqual(code, 200)
        expected_result = self.valid_leaderboard_template.copy()
        expected_result['primary_metric'] = self.metric1
        expected_result['filters'][0]['name'] = self.metric1['name']
        for k, v in expected_result.items():
            self.assertEqual(resp.get(k), v)

    def test_get_leaderboard_details(self):
        code, dslb = self.client.leaderboard_get(
            self.organization_id,
            self.lds["id"],
            details=True
        )
        self.assertEqual(code, 200)
        details = dslb.get("details")
        self.assertEqual(details, [])

    def test_delete_leaderboard(self):
        _, lbds = self.leaderboard = self.client.leaderboard_create(
            self.organization_id,
            self.leaderboard_template_id,
            params={
                'name': 'test1',
                'dataset_ids': self.dataset_ids
            }
        )

        code, _ = self.client.leaderboard_delete(
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
        code, resp = self.client.leaderboard_create(
            self.organization_id,
            self.leaderboard_template_id,
            params={
                'name': 'test',
                'dataset_ids': 'test'
            })
        self.assertEqual(code, 400)
        self.verify_error_code(resp, "OE0385")
        code, resp = self.client.leaderboard_create(
            self.organization_id,
            self.leaderboard_template_id,
            params={
                'name': 'test',
                'dataset_ids': [9, ]
            })
        self.assertEqual(code, 400)
        self.verify_error_code(resp, "OE0214")
        code, resp = self.client.leaderboard_create(
            self.organization_id,
            self.leaderboard_template_id,
            params={
                'name': 9,
                'dataset_ids': ["t"]
            })
        self.assertEqual(code, 400)
        self.verify_error_code(resp, "OE0214")

    def test_list_leaderboards(self):
        code, resp = self.client.leaderboard_list(
            self.organization_id,
            self.leaderboard_template_id,
        )
        self.assertEqual(code, 200)
        self.assertEqual(len(resp), 1)

    def test_invalid_dataset_coverage_rules(self):
        for cr in ['test', 123, ['some']]:
            code, resp = self.client.leaderboard_create(
                self.organization_id,
                self.leaderboard_template_id,
                params={
                    'name': 'test',
                    'dataset_ids': self.dataset_ids,
                    'dataset_coverage_rules': cr
                })
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0344')

            self.client.leaderboard_update(
                self.organization_id,
                self.lds["id"],
                params={
                    'dataset_coverage_rules': cr
                }
            )
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0344')
        for invalid in [0, -1, 1000]:
            code, resp = self.client.leaderboard_create(
                self.organization_id,
                self.leaderboard_template_id,
                params={
                    'name': 'test',
                    'dataset_ids': self.dataset_ids,
                    'dataset_coverage_rules': {
                        'some': invalid
                    }
                })
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0224')
        code, resp = self.client.leaderboard_create(
            self.organization_id,
            self.leaderboard_template_id,
            params={
                'name': 'test',
                'dataset_ids': self.dataset_ids,
                'dataset_coverage_rules': {
                    'some': 'test'
                }
            })
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0223')

    def test_dataset_coverage_rules(self):
        rules = {'some': 1, 'another': 2}
        code, leaderboard = self.client.leaderboard_create(
            self.organization_id,
            self.leaderboard_template_id,
            params={
                'name': 'test',
                'dataset_ids': self.dataset_ids,
                'dataset_coverage_rules': rules
            })
        self.assertEqual(code, 201)
        self.assertEqual(leaderboard['dataset_coverage_rules'], rules)
        for upd_value, expected in [
            (None, None),
            ({}, {}),
            ({'another': 1}, {'another': 1})
        ]:
            code, resp = self.client.leaderboard_update(
                self.organization_id,
                leaderboard["id"],
                params={
                    'dataset_coverage_rules': upd_value
                }
            )
            self.assertEqual(code, 200)
            self.assertEqual(resp['dataset_coverage_rules'], expected)
