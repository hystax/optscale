from datetime import datetime, timezone, timedelta
from unittest.mock import patch
from freezegun import freeze_time
from rest_api.rest_api_server.tests.unittests.test_api_base import TestApiBase


class TestPowerSchedule(TestApiBase):

    def setUp(self, version="v2"):
        super().setUp(version)
        _, self.org = self.client.organization_create({"name": "partner"})
        self.org_id_1 = self.org["id"]
        self.auth_user = self.gen_id()
        patch('rest_api.rest_api_server.controllers.cloud_account.'
              'CloudAccountController._configure_report').start()
        patch('rest_api.rest_api_server.controllers.base.BaseController.'
              'get_user_id',
              return_value=self.auth_user).start()
        _, self.employee = self.client.employee_create(
            self.org['id'], {'name': 'employee_1',
                             'auth_user_id': self.auth_user})
        self.cloud_acc_dict = {
            'name': 'my cloud_acc',
            'type': 'aws_cnr',
            'config': {
                'access_key_id': 'key',
                'secret_access_key': 'secret',
                'bucket_name': 'name',
                'config_scheme': 'create_report',
            }
        }
        code, self.cloud_acc = self.create_cloud_account(
            self.org_id_1, self.cloud_acc_dict,
            auth_user_id=self.auth_user)
        start_date = int(
            (datetime.now(tz=timezone.utc) - timedelta(days=10)).timestamp())
        end_date = int(
            (datetime.now(tz=timezone.utc) + timedelta(days=10)).timestamp())
        self.valid_ps = {
            'power_off': '10:33',
            'power_on': '11:22',
            'timezone': 'Europe/Vienna',
            'start_date': start_date,
            'end_date': end_date,
            'name': 'my schedule',
            'enabled': True
        }

    def create_cloud_resource(self, cloud_account_id, employee_id=None,
                              pool_id=None, resource_type='Instance',
                              name='test_resource', power_schedule=None,
                              active=False):
        now = int(datetime.utcnow().timestamp())
        resource = {
            'cloud_resource_id': self.gen_id(),
            'name': name,
            'resource_type': resource_type,
            'employee_id': employee_id,
            'pool_id': pool_id,
            'last_seen': now,
            'first_seen': now,
            'region': 'us-east-1',
            'power_schedule': power_schedule,
            'active': active
        }
        code, resource = self.cloud_resource_create(
            cloud_account_id, resource)
        self.assertEqual(code, 201)
        return resource

    def test_create_ps(self):
        code, res = self.client.power_schedule_create(
            self.org_id_1, self.valid_ps)
        self.assertEqual(201, code)
        self.assertTrue(res['enabled'])
        self.assertEqual(res['resources_count'], 0)
        for k, v in self.valid_ps.items():
            self.assertEqual(res[k], v)
        self.assertEqual(res['last_run'], 0)
        self.assertEqual(res['last_eval'], 0)

    def test_create_no_start_date(self):
        ps = self.valid_ps.copy()
        ps.pop('start_date', None)
        code, res = self.client.power_schedule_create(
            self.org_id_1, ps)
        self.assertEqual(201, code)
        # start_date set to current time
        self.assertNotEqual(res['start_date'], 0)

    def test_create_no_end_date(self):
        ps = self.valid_ps.copy()
        ps.pop('end_date', None)
        code, res = self.client.power_schedule_create(
            self.org_id_1, ps)
        self.assertEqual(201, code)
        # end_date set to 0
        self.assertEqual(res['end_date'], 0)

    def test_create_invalid_params(self):
        for param in ['name', 'timezone']:
            for value in [123, {}, []]:
                params = self.valid_ps.copy()
                params[param] = value
                code, res = self.client.power_schedule_create(
                    self.org_id_1, params)
                self.assertEqual(code, 400)
                self.assertEqual(res['error']['error_code'], 'OE0214')

        for param in ['power_on', 'power_off']:
            for value in [123, {}, []]:
                params = self.valid_ps.copy()
                params[param] = value
                code, res = self.client.power_schedule_create(
                    self.org_id_1, params)
                self.assertEqual(code, 400)
                self.assertEqual(res['error']['error_code'], 'OE0550')

        for param in ['start_date', 'end_date']:
            for value in ['123', {}, []]:
                params = self.valid_ps.copy()
                params[param] = value
                code, res = self.client.power_schedule_create(
                    self.org_id_1, params)
                self.assertEqual(code, 400)
                self.assertEqual(res['error']['error_code'], 'OE0223')

        for value in ['123', {}, []]:
            params = self.valid_ps.copy()
            params['enabled'] = value
            code, res = self.client.power_schedule_create(
                self.org_id_1, params)
            self.assertEqual(code, 400)
            self.assertEqual(res['error']['error_code'], 'OE0226')

        for param in ['power_off', 'power_on']:
            for value in ['25:12', '22.11', '123', '22:121']:
                params = self.valid_ps.copy()
                params[param] = value
                code, res = self.client.power_schedule_create(
                    self.org_id_1, params)
                self.assertEqual(code, 400)
                self.assertEqual(res['error']['error_code'], 'OE0550')

        params = self.valid_ps.copy()
        params['power_on'] = '22:22'
        params['power_off'] = '22:22'
        code, res = self.client.power_schedule_create(
            self.org_id_1, params)
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0552')

        now = int(datetime.now(tz=timezone.utc).timestamp())
        params = self.valid_ps.copy()
        params['end_date'] = now - 10000
        code, res = self.client.power_schedule_create(
            self.org_id_1, params)
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0461')

        params = self.valid_ps.copy()
        params['end_date'] = now + 1000
        params['start_date'] = now + 2000
        code, res = self.client.power_schedule_create(
            self.org_id_1, params)
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0541')

        params = self.valid_ps.copy()
        params['end_date'] = now + 2000
        params['start_date'] = now + 2000
        code, res = self.client.power_schedule_create(
            self.org_id_1, params)
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0541')

        params = self.valid_ps.copy()
        for value in ['deleted_at', 'last_run_error']:
            params[value] = 'test'
            code, res = self.client.power_schedule_create(
                self.org_id_1, params)
            self.assertEqual(code, 400)
            self.assertEqual(res['error']['error_code'], 'OE0211')

        params = self.valid_ps.copy()
        params['unexpected'] = 'test'
        code, res = self.client.power_schedule_create(self.org_id_1, params)
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0212')

        for length in [0, 256]:
            name = ''.join('x' for _ in range(length))
            params = self.valid_ps.copy()
            params['name'] = name
            code, res = self.client.power_schedule_create(self.org_id_1, params)
            self.assertEqual(code, 400)
            self.assertEqual(res['error']['error_code'], 'OE0215')

    def test_create_required(self):
        for param in ['name', 'power_on', 'power_off', 'timezone']:
            params = self.valid_ps.copy()
            params.pop(param, None)
            code, res = self.client.power_schedule_create(
                self.org_id_1, params)
            self.assertEqual(code, 400)
            self.assertEqual(res['error']['error_code'], 'OE0216')

    def test_create_duplicate(self):
        code, res = self.client.power_schedule_create(
            self.org_id_1, self.valid_ps)
        self.assertEqual(201, code)
        code, res = self.client.power_schedule_create(
            self.org_id_1, self.valid_ps)
        self.assertEqual(409, code)
        self.assertEqual(res['error']['error_code'], 'OE0149')

    def test_update_ps(self):
        code, ps = self.client.power_schedule_create(
            self.org_id_1, self.valid_ps)
        self.assertEqual(201, code)
        updates = {
            'power_off': '11:44',
            'power_on': '23:59',
            'timezone': 'Europe/Vienna',
            'start_date': int(datetime.now(tz=timezone.utc).timestamp()),
            'end_date': int(datetime.now(tz=timezone.utc).timestamp()) + 10000,
            'name': 'my schedule 1',
            'enabled': False,
            'last_eval': 12,
            'last_run': 12,
            'last_run_error': 'error'
        }
        code, res = self.client.power_schedule_update(ps['id'], updates)
        self.assertEqual(200, code)
        for k, v in updates.items():
            self.assertEqual(res[k], v)

        code, res = self.client.power_schedule_update('123', updates)
        self.assertEqual(404, code)
        self.assertEqual(res['error']['error_code'], 'OE0002')

    def test_update_invalid_params(self):
        code, ps = self.client.power_schedule_create(
            self.org_id_1, self.valid_ps)
        self.assertEqual(201, code)
        updates = {
            'power_off': '11:44',
            'power_on': '23:59',
            'timezone': 'Europe/Vienna',
            'start_date': int(datetime.utcnow().timestamp()),
            'name': 'my schedule 1',
            'enabled': False,
            'last_eval': 12,
            'last_run': 12,
            'last_run_error': 'error'
        }
        for param in ['name', 'timezone']:
            for value in [123, {}, []]:
                params = updates.copy()
                params[param] = value
                code, res = self.client.power_schedule_update(
                    ps['id'], params)
                self.assertEqual(code, 400)
                self.assertEqual(res['error']['error_code'], 'OE0214')

        for param in ['power_on', 'power_off']:
            for value in ['28:22', '22:99', '21.21', '222:22', '21:199', '123',
                          123, {}, []]:
                params = updates.copy()
                params[param] = value
                code, res = self.client.power_schedule_update(
                    ps['id'], params)
                self.assertEqual(code, 400)
                self.assertEqual(res['error']['error_code'], 'OE0550')

        params = updates.copy()
        params['power_on'] = '10:10'
        params['power_off'] = '10:10'
        code, res = self.client.power_schedule_update(
            ps['id'], params)
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0552')

        for param in ['start_date', 'end_date']:
            for value in ['123', {}, []]:
                params = updates.copy()
                params['end_date'] = int(datetime.now(
                    tz=timezone.utc).timestamp()) + 10000
                params[param] = value
                code, res = self.client.power_schedule_update(
                    ps['id'], params)
                self.assertEqual(code, 400)
                self.assertEqual(res['error']['error_code'], 'OE0223')

        params = updates.copy()
        now = int(datetime.now(tz=timezone.utc).timestamp())
        params['start_date'] = now + 10000
        params['end_date'] = now + 10000
        code, res = self.client.power_schedule_update(
            ps['id'], params)
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0541')

        for value in ['123', {}, []]:
            params = updates.copy()
            params['enabled'] = value
            code, res = self.client.power_schedule_update(
                ps['id'], params)
            self.assertEqual(code, 400)
            self.assertEqual(res['error']['error_code'], 'OE0226')

        now = int(datetime.now(tz=timezone.utc).timestamp())
        params = updates.copy()
        params['start_date'] = 0
        params['end_date'] = now - 10000
        code, res = self.client.power_schedule_update(
            ps['id'], params)
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0461')

        params = updates.copy()
        params['end_date'] = now + 10000
        params['start_date'] = now + 20000
        code, res = self.client.power_schedule_update(
            ps['id'], params)
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0541')

        params = updates.copy()
        params['unexpected'] = 'test'
        code, res = self.client.power_schedule_update(
            ps['id'], params)
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0212')

        for length in [0, 256]:
            name = ''.join('x' for _ in range(length))
            params = updates.copy()
            params['name'] = name
            code, res = self.client.power_schedule_update(ps['id'], params)
            self.assertEqual(code, 400)
            self.assertEqual(res['error']['error_code'], 'OE0215')

    def test_update_outdated(self):
        end_date = datetime.now(timezone.utc) - timedelta(days=1)
        ps = self.valid_ps.copy()
        ps['start_date'] = 0
        ps['end_date'] = int(end_date.timestamp())
        with freeze_time(end_date - timedelta(days=1)):
            code, ps = self.client.power_schedule_create(
                 self.org_id_1, ps)
        self.assertEqual(201, code)

        code, resp = self.client.power_schedule_update(
            ps['id'], params={'enabled': False})
        self.assertEqual(code, 200)
        self.assertFalse(resp['enabled'])

    def test_update_duplicate(self):
        params = self.valid_ps.copy()
        code, _ = self.client.power_schedule_create(
            self.org_id_1, params)
        self.assertEqual(201, code)
        params['name'] = 'test'
        code, ps = self.client.power_schedule_create(
            self.org_id_1, params)
        self.assertEqual(201, code)
        updates = {'name': self.valid_ps['name']}
        code, res = self.client.power_schedule_update(ps['id'], updates)
        self.assertEqual(409, code)
        self.assertEqual(res['error']['error_code'], 'OE0149')

    def test_delete_ps(self):
        code, ps = self.client.power_schedule_create(
            self.org_id_1, self.valid_ps)
        self.assertEqual(201, code)
        resource = self.create_cloud_resource(self.cloud_acc['id'],
                                              power_schedule=ps['id'])

        code, _ = self.client.power_schedule_delete(ps['id'])
        self.assertEqual(204, code)
        resource_db = self.resources_collection.find_one(
            {'_id': resource['id']})
        self.assertNotIn('power_schedule', resource_db)

        code, res = self.client.power_schedule_delete('123')
        self.assertEqual(404, code)
        self.assertEqual(res['error']['error_code'], 'OE0002')

    def test_get_ps(self):
        code, ps = self.client.power_schedule_create(
            self.org_id_1, self.valid_ps)
        self.assertEqual(201, code)
        code, ps = self.client.power_schedule_get(ps['id'])
        self.assertEqual(200, code)
        for k, v in self.valid_ps.items():
            self.assertEqual(ps[k], v)
        self.assertEqual(ps['resources_count'], 0)

        self.create_cloud_resource(self.cloud_acc['id'],
                                   power_schedule=ps['id'])
        code, ps = self.client.power_schedule_get(ps['id'])
        self.assertEqual(200, code)
        self.assertEqual(ps['resources_count'], 1)
        self.assertEqual(ps['resources'][0]['power_schedule'], ps['id'])

        code, res = self.client.power_schedule_get('123')
        self.assertEqual(404, code)
        self.assertEqual(res['error']['error_code'], 'OE0002')

    def test_list_ps(self):
        code, resp = self.client.power_schedule_list(self.org_id_1)
        self.assertEqual(200, code)
        self.assertEqual(resp['power_schedules'], [])

        code, ps = self.client.power_schedule_create(
            self.org_id_1, self.valid_ps)
        self.assertEqual(201, code)
        code, resp = self.client.power_schedule_list(self.org_id_1)
        self.assertEqual(200, code)
        self.assertEqual(resp['power_schedules'][0]['resources_count'], 0)

        self.create_cloud_resource(self.cloud_acc['id'],
                                   power_schedule=ps['id'])
        code, resp = self.client.power_schedule_list(self.org_id_1)
        self.assertEqual(200, code)
        self.assertEqual(resp['power_schedules'][0]['resources_count'], 1)

        code, resp = self.client.power_schedule_list('123')
        self.assertEqual(404, code)
        self.assertEqual(resp['error']['error_code'], 'OE0002')

    def test_ps_actions(self):
        code, ps = self.client.power_schedule_create(
            self.org_id_1, self.valid_ps)
        self.assertEqual(201, code)
        resource = self.create_cloud_resource(
            self.cloud_acc['id'], active=True)['id']
        body = {
            'action': 'attach',
            'instance_id': [resource]
        }
        code, resp = self.client.power_schedule_actions(
            ps['id'], body)
        self.assertEqual(code, 200)
        self.assertEqual(resp['failed'], [])
        self.assertEqual(resp['succeeded'], [resource])
        schedule = self.resources_collection.find_one(
            {'_id': resource})['power_schedule']
        self.assertEqual(schedule, ps['id'])

        body = {
            'action': 'detach',
            'instance_id': [resource]
        }
        code, resp = self.client.power_schedule_actions(
            ps['id'], body)
        self.assertEqual(code, 200)
        self.assertEqual(resp['failed'], [])
        self.assertEqual(resp['succeeded'], [resource])
        schedule = self.resources_collection.find_one(
            {'_id': resource})
        self.assertIsNone(schedule.get('power_schedule'))

    def test_ps_actions_invalid(self):
        code, ps = self.client.power_schedule_create(
            self.org_id_1, self.valid_ps)
        self.assertEqual(201, code)
        resource = self.create_cloud_resource(
            self.cloud_acc['id'], active=True)['id']
        body = {
            'action': 'attach',
            'instance_id': [resource]
        }

        for value in ['test', 123, {}, []]:
            params = body.copy()
            params['action'] = value
            code, resp = self.client.power_schedule_actions(
                ps['id'], params)
            self.assertEqual(code, 400)
            self.assertEqual(resp['error']['error_code'], 'OE0217')

        for value in ['test', 123]:
            params = body.copy()
            params['instance_id'] = value
            code, resp = self.client.power_schedule_actions(
                ps['id'], params)
            self.assertEqual(code, 400)
            self.assertEqual(resp['error']['error_code'], 'OE0385')

        params = body.copy()
        params['instance_id'] = ['123']
        code, resp = self.client.power_schedule_actions(
            ps['id'], params)
        self.assertEqual(code, 200)
        self.assertEqual(resp['failed'], ['123'])
        self.assertEqual(resp['succeeded'], [])

        params = body.copy()
        params['instance_id'] = []
        code, resp = self.client.power_schedule_actions(
                ps['id'], params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0216')

    def test_ps_action_not_found(self):
        resource = self.create_cloud_resource(
            self.cloud_acc['id'], active=True)['id']
        body = {
            'action': 'attach',
            'instance_id': [resource]
        }
        code, resp = self.client.power_schedule_actions(
                'test', body)
        self.assertEqual(code, 404)
        self.assertEqual(resp['error']['error_code'], 'OE0002')

    def test_ps_methods(self):
        code, _ = self.client.patch(self.client.power_schedules_url(
            organization_id=self.org_id_1), {})
        self.assertEqual(code, 405)
        code, _ = self.client.delete(self.client.power_schedules_url(
            organization_id=self.org_id_1))
        self.assertEqual(code, 405)
        code, _ = self.client.post(
            self.client.power_schedules_url(id_='test'), {})
        self.assertEqual(code, 405)
        code, _ = self.client.patch(
            self.client.power_schedules_actions_url(id_='test'), {})
        self.assertEqual(code, 405)
        code, _ = self.client.delete(
            self.client.power_schedules_actions_url(id_='test'))
        self.assertEqual(code, 405)
        code, _ = self.client.get(
            self.client.power_schedules_actions_url(id_='test'), {})
        self.assertEqual(code, 405)

    def test_update_ps_with_res_with_policy(self):
        code, schedule = self.client.power_schedule_create(
            self.org_id_1, self.valid_ps)
        self.assertEqual(201, code)
        policy = {
            'limit': 0,
            'type': 'ttl'
        }
        code, policy = self.client.pool_policy_create(
            self.org['pool_id'], policy)
        self.assertEqual(code, 201)
        self.create_cloud_resource(
            self.cloud_acc['id'], active=True, pool_id=self.org['pool_id'],
            power_schedule=schedule['id'])
        code, resp = self.client.power_schedule_update(schedule['id'],
                                                       {'name': 'new name'})
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['resources'][0]['details']['policies']), 1)
