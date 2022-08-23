import uuid
from datetime import datetime
from freezegun import freeze_time
from rest_api_server.tests.unittests.test_api_base import TestApiBase


class TestOrganizationLimitHits(TestApiBase):
    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.org = self.client.organization_create(
            {'name': "partner_test"})
        self.org_id = self.org['id']
        self.org_name = self.org['name']
        user_id = self.gen_id()
        self.valid_employee = {
            'name': 'Eliot Alderson', 'auth_user_id': user_id
        }
        _, self.employee = self.client.employee_create(
            self.org_id, self.valid_employee)
        self.employee_id = self.employee['id']
        self.pool_id = self.org['pool_id']
        self.pool_name = self.org_name
        self._mock_auth_user(user_id)
        _, self.deleted_org = self.client.organization_create(
            {'name': "deleted"})
        self.delete_organization(self.deleted_org['id'])
        self.constraint = self.create_org_constraint(self.org_id, self.pool_id)
        self.valid_hit_params = {
            "constraint_limit": 31.11,
            "value": 93.33,
            "constraint_id": self.constraint['id'],
            "run_result": {
                'average': 0, 'today': 93.33,
                'breakdown': {}
            }
        }

    def test_create_limit_hit(self):
        code, resp = self.client.organization_limit_hit_create(
            self.org_id, self.valid_hit_params)
        self.assertEqual(code, 201)

    def test_create_limit_hit_no_run_result(self):
        valid_hit_params = self.valid_hit_params.copy()
        valid_hit_params.pop('run_result')
        code, resp = self.client.organization_limit_hit_create(
            self.org_id, valid_hit_params)
        self.assertEqual(code, 201)

    def test_create_limit_hit_incorrect_run_result(self):
        valid_hit_params = self.valid_hit_params.copy()
        valid_hit_params['run_result'] = 'run_result'
        code, resp = self.client.organization_limit_hit_create(
            self.org_id, valid_hit_params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0344')

    def test_create_limit_hit_with_created_at(self):
        params = self.valid_hit_params.copy()
        now = int(datetime.utcnow().timestamp())
        params['created_at'] = now
        code, resp = self.client.organization_limit_hit_create(
            self.org_id, params)
        self.assertEqual(code, 201)
        self.assertEqual(resp['created_at'], now)

    def test_create_invalid_org(self):
        code, resp = self.client.organization_limit_hit_create(
            '123', self.valid_hit_params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0217')

    def test_create_nonexistent_org(self):
        code, resp = self.client.organization_limit_hit_create(
            str(uuid.uuid4()), self.valid_hit_params)
        self.assertEqual(code, 404)
        self.assertEqual(resp['error']['error_code'], 'OE0002')

    def test_create_deleted_org(self):
        code, resp = self.client.organization_limit_hit_create(
            self.deleted_org['id'], self.valid_hit_params)
        self.assertEqual(code, 404)
        self.assertEqual(resp['error']['error_code'], 'OE0002')

    def test_create_unexpected(self):
        params = self.valid_hit_params.copy()
        params['unexpected'] = 'param'
        code, resp = self.client.organization_limit_hit_create(
            self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0212')

    def test_create_missing_params(self):
        required_params = self.valid_hit_params.copy()
        required_params.pop('run_result')
        for key in required_params.keys():
            params = required_params.copy()
            params.pop(key, None)
            code, resp = self.client.organization_limit_hit_create(
                self.org_id, params)
            self.assertEqual(code, 400)
            self.assertEqual(resp['error']['error_code'], 'OE0216', key)

    def test_create_duplicated(self):
        with freeze_time(datetime(2022, 1, 1)):
            self.create_org_limit_hit(self.org_id, self.pool_id,
                                      constraint_id=self.constraint['id'])
            code, resp = self.client.organization_limit_hit_create(
                self.org_id, self.valid_hit_params)
        self.assertEqual(code, 409)
        self.assertEqual(resp['error']['error_code'], 'OE0516')

    def test_create_invalid_constraint_limit(self):
        params = self.valid_hit_params.copy()
        params['constraint_limit'] = '123'
        code, resp = self.client.organization_limit_hit_create(
            self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0466')

    def test_create_invalid_value(self):
        params = self.valid_hit_params.copy()
        params['value'] = '123'
        code, resp = self.client.organization_limit_hit_create(
            self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0466')

    def test_create_constraint_from_other_org(self):
        constr = self.create_org_constraint(self.org_id, self.pool_id)
        _, org = self.client.organization_create({'name': "test"})
        params = self.valid_hit_params.copy()
        params['constraint_id'] = constr['id']
        code, resp = self.client.organization_limit_hit_create(
            org['id'], params)
        self.assertEqual(code, 404)
        self.assertEqual(resp['error']['error_code'], 'OE0002')

    def test_create_invalid_constraint_id(self):
        params = self.valid_hit_params.copy()
        params['constraint_id'] = '123'
        code, resp = self.client.organization_limit_hit_create(
            self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0217')

    def test_create_nonexistent_constraint_id(self):
        params = self.valid_hit_params.copy()
        params['constraint_id'] = str(uuid.uuid4())
        code, resp = self.client.organization_limit_hit_create(
            self.org_id, params)
        self.assertEqual(code, 404)
        self.assertEqual(resp['error']['error_code'], 'OE0002')

    def test_create_deleted_constraint(self):
        constr = self.create_org_constraint(self.org_id, self.pool_id,
                                            deleted=True)
        params = self.valid_hit_params.copy()
        params['constraint_id'] = constr['id']
        code, resp = self.client.organization_limit_hit_create(
            self.org_id, params)
        self.assertEqual(code, 404)
        self.assertEqual(resp['error']['error_code'], 'OE0002')

    def test_list_hits(self):
        self.create_org_limit_hit(self.org_id, self.pool_id,
                                  constraint_id=self.constraint['id'],
                                  deleted=True)
        self.create_org_limit_hit(
            self.org_id, self.pool_id, constraint_id=self.constraint['id'],
            created_at=int(datetime(2022, 1, 1).timestamp()))
        code, resp = self.client.organization_limit_hit_list(self.org_id)
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['organization_limit_hits']), 1)
        self.assertEqual(resp['organization_limit_hits'][0]['constraint_id'],
                         self.constraint['id'])

    def test_list_hits_with_invalid_org(self):
        code, resp = self.client.organization_limit_hit_list('123')
        self.assertEqual(code, 404)
        self.assertEqual(resp['error']['error_code'], 'OE0002')

    def test_list_hits_with_deleted_org(self):
        code, resp = self.client.organization_limit_hit_list(
            self.deleted_org['id'])
        self.assertEqual(code, 404)
        self.assertEqual(resp['error']['error_code'], 'OE0002')

    def test_list_with_constraint_id(self):
        self.create_org_limit_hit(self.org_id, self.pool_id,
                                  constraint_id=self.constraint['id'])
        constr = self.create_org_constraint(self.org_id, self.pool_id)
        self.create_org_limit_hit(self.org_id, self.pool_id,
                                  constraint_id=constr['id'])
        code, resp = self.client.organization_limit_hit_list(
            self.org_id, constraint_id=constr['id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['organization_limit_hits']), 1)
        self.assertEqual(resp['organization_limit_hits'][0]['constraint_id'],
                         constr['id'])

    def test_list_hits_with_invalid_constraint_id(self):
        code, resp = self.client.organization_limit_hit_list(
            self.org_id, constraint_id=123)
        self.assertEqual(code, 404)
        self.assertEqual(resp['error']['error_code'], 'OE0002')

    def test_list_hits_with_deleted_constraint_id(self):
        constr = self.create_org_constraint(self.org_id, self.pool_id,
                                            deleted=True)
        code, resp = self.client.organization_limit_hit_list(
            self.org_id, constraint_id=constr['id'])
        self.assertEqual(code, 404)
        self.assertEqual(resp['error']['error_code'], 'OE0002')

    def test_list_hits_with_constraint_id_from_other_org(self):
        constr = self.create_org_constraint(self.org_id, self.pool_id)
        _, org = self.client.organization_create({'name': 'test'})
        code, resp = self.client.organization_limit_hit_list(
            org['id'], constraint_id=constr['id'])
        self.assertEqual(code, 404)
        self.assertEqual(resp['error']['error_code'], 'OE0002')

    def test_update_hit(self):
        hit = self.create_org_limit_hit(self.org_id, self.pool_id,
                                        constraint_id=self.constraint['id'])
        limit = 22.22
        value = 44.44
        run_result = {
            'average': 10, 'today': value,
            'breakdown': {int(datetime.utcnow().timestamp()): 10}
        }
        params = {"constraint_limit": limit, "value": value,
                  'run_result': run_result}
        code, resp = self.client.organization_limit_hit_update(
            hit['id'], params)
        self.assertEqual(code, 200)
        self.assertEqual(resp['constraint_limit'], limit)
        self.assertEqual(resp['value'], value)
        self.assertTrue(resp.get('run_result', {}))

    def test_update_hit_no_run_result(self):
        hit = self.create_org_limit_hit(self.org_id, self.pool_id,
                                        constraint_id=self.constraint['id'])
        params = {"constraint_limit": 22.22, "value": 44.44}
        code, resp = self.client.organization_limit_hit_update(
            hit['id'], params)
        self.assertEqual(code, 200)

    def test_update_hit_incorrect_run_result(self):
        hit = self.create_org_limit_hit(self.org_id, self.pool_id,
                                        constraint_id=self.constraint['id'])
        params = {"constraint_limit": 22.22, "value": 44.44,
                  "run_result": "run_result"}
        code, resp = self.client.organization_limit_hit_update(
            hit['id'], params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0344')

    def test_update_unexpected(self):
        hit = self.create_org_limit_hit(self.org_id, self.pool_id,
                                        constraint_id=self.constraint['id'])
        params = {"unexpected": "param"}
        code, resp = self.client.organization_limit_hit_update(
            hit['id'], params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0212')

    def test_update_empty(self):
        hit = self.create_org_limit_hit(self.org_id, self.pool_id,
                                        constraint_id=self.constraint['id'])
        params = {}
        code, resp = self.client.organization_limit_hit_update(
            hit['id'], params)
        self.assertEqual(code, 200)

    def test_update_immutable(self):
        hit = self.create_org_limit_hit(self.org_id, self.pool_id,
                                        constraint_id=self.constraint['id'])
        for p in ['deleted_at', 'created_at', 'constraint_id',
                  'organization_id']:
            params = {p: '123'}
            code, resp = self.client.organization_limit_hit_update(
                hit['id'], params)
            self.assertEqual(code, 400)
            self.assertEqual(resp['error']['error_code'], 'OE0211')

    def test_not_allowed(self):
        hit = self.create_org_limit_hit(self.org_id, self.pool_id,
                                        constraint_id=self.constraint['id'])
        code, res = self.client.post(
            self.client.organization_limit_hit_url(hit['id']), {})
        self.assertEqual(code, 405)

        code, res = self.client.delete(
            self.client.organization_limit_hit_url(hit['id']))
        self.assertEqual(code, 405)

        code, res = self.client.patch(
            self.client.organization_limit_hit_url(org_id=self.org_id), {})
        self.assertEqual(code, 405)
