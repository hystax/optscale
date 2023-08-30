import uuid
from rest_api.rest_api_server.tests.unittests.test_api_base import TestApiBase


class TestSshKeysApi(TestApiBase):

    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.organization = self.client.organization_create({
            'name': 'test organization'})
        self.organization_id = self.organization['id']
        self.auth_user = self.gen_id()
        _, self.employee = self.client.employee_create(
            self.organization['id'], {'name': 'employee',
                                      'auth_user_id': self.auth_user})
        self._mock_auth_user(self.auth_user)
        self.valid_body = {'name': 'n1', 'key': 'ssh AAAAC3Nz ubuntu'}

    def test_create(self):
        code, ssh_key = self.client.ssh_key_create(self.employee['id'],
                                                   self.valid_body)
        self.assertEqual(code, 201)
        for k in ['key', 'name']:
            self.assertEqual(ssh_key[k], self.valid_body[k])
        self.assertIsNotNone(ssh_key['fingerprint'])

    def test_create_not_existing_employee(self):
        code, resp = self.client.ssh_key_create(
            str(uuid.uuid4()), self.valid_body)
        self.assertEqual(code, 404)
        self.verify_error_code(resp, 'OE0002')

    def test_create_forbidden(self):
        auth_user_2 = str(uuid.uuid4())
        _, employee2 = self.client.employee_create(
            self.organization['id'], {'name': 'employee2',
                                      'auth_user_id': auth_user_2})
        code, resp = self.client.ssh_key_create(employee2['id'],
                                                self.valid_body)
        self.assertEqual(code, 403)
        self.verify_error_code(resp, 'OE0234')

        self._mock_auth_user(auth_user_2)
        code, ssh_key = self.client.ssh_key_create(self.employee['id'],
                                                   self.valid_body)
        self.assertEqual(code, 403)
        self.verify_error_code(resp, 'OE0234')

    def test_create_unexpected_parameters(self):
        for k in ['fingerprint', 'another_param', 'deleted_at']:
            body = self.valid_body.copy()
            body[k] = 'some'
            code, resp = self.client.ssh_key_create(
                self.employee['id'], body)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0212')

    def test_create_not_provided_param(self):
        for k in ['key', 'name']:
            body = self.valid_body.copy()
            body.pop(k)
            code, resp = self.client.ssh_key_create(self.employee['id'], body)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0216')

    def test_create_invalid_name(self):
        for n, error in [
            (1, 'OE0214'), ('', 'OE0215'), (False, 'OE0214')
        ]:
            self.valid_body['name'] = n
            code, resp = self.client.ssh_key_create(
                self.employee['id'], self.valid_body)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, error)

    def test_create_invalid_default(self):
        code, _ = self.client.ssh_key_create(
            self.employee['id'], {'name': 'n0', 'key': 'ssh AAAAC3Nk ubuntu'})
        self.assertEqual(code, 201)

        for d in ['', 'asd', 2]:
            self.valid_body['default'] = d
            code, resp = self.client.ssh_key_create(
                self.employee['id'], self.valid_body)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0226')

    def test_create_invalid_key(self):
        for k in ['', 1, False, 'ssh wrong ssh']:
            self.valid_body['key'] = k
            code, resp = self.client.ssh_key_create(
                self.employee['id'], self.valid_body)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0507')

    def test_get(self):
        code, ssh_key = self.client.ssh_key_create(
            self.employee['id'], self.valid_body)
        self.assertEqual(code, 201)
        code, resp = self.client.ssh_key_get(ssh_key['id'])
        self.assertEqual(code, 200)
        self.assertEqual(resp, ssh_key)

    def test_get_another_employee(self):
        code, ssh_key = self.client.ssh_key_create(
            self.employee['id'], self.valid_body)
        self.assertEqual(code, 201)
        auth_user_2 = str(uuid.uuid4())
        _, employee2 = self.client.employee_create(
            self.organization['id'], {'name': 'employee2',
                                      'auth_user_id': auth_user_2})
        self._mock_auth_user(auth_user_2)
        code, resp = self.client.ssh_key_get(ssh_key['id'])
        self.assertEqual(code, 403)
        self.verify_error_code(resp, 'OE0234')

    def test_get_invalid(self):
        code, resp = self.client.ssh_key_get(str(uuid.uuid4()))
        self.assertEqual(code, 404)
        self.verify_error_code(resp, 'OE0002')

    def test_list(self):
        code, ssh_key1 = self.client.ssh_key_create(
            self.employee['id'], self.valid_body)
        self.assertEqual(code, 201)
        code, ssh_key2 = self.client.ssh_key_create(
            self.employee['id'], {'name': 'n0', 'key': 'ssh AAAAC3Nk ubuntu'})
        self.assertEqual(code, 201)

        code, resp = self.client.ssh_key_list(self.employee['id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['ssh_keys']), 2)
        for s in resp['ssh_keys']:
            self.assertTrue(s['id'] in [ssh_key1['id'], ssh_key2['id']])

    def test_list_invalid(self):
        code, resp = self.client.ssh_key_list(str(uuid.uuid4()))
        self.assertEqual(code, 404)
        self.verify_error_code(resp, 'OE0002')

    def test_list_another_employee(self):
        code, ssh_key = self.client.ssh_key_create(
            self.employee['id'], self.valid_body)
        self.assertEqual(code, 201)
        auth_user_2 = str(uuid.uuid4())
        _, employee2 = self.client.employee_create(
            self.organization['id'], {'name': 'employee2',
                                      'auth_user_id': auth_user_2})
        self._mock_auth_user(auth_user_2)
        code, resp = self.client.ssh_key_list(self.employee['id'])
        self.assertEqual(code, 403)
        self.verify_error_code(resp, 'OE0234')

    def test_patch(self):
        code, ssh_key = self.client.ssh_key_create(
            self.employee['id'], self.valid_body)
        self.assertEqual(code, 201)

        code, resp = self.client.ssh_key_update(
            ssh_key['id'], {'name': 'another'})
        self.assertEqual(code, 200)
        self.assertEqual(resp['name'], 'another')

    def test_patch_invalid(self):
        code, ssh_key = self.client.ssh_key_create(
            self.employee['id'], self.valid_body)
        self.assertEqual(code, 201)

        code, resp = self.client.ssh_key_update(
            str(uuid.uuid4()), {'name': 'another'})
        self.assertEqual(code, 404)
        self.verify_error_code(resp, 'OE0002')

        code, resp = self.client.ssh_key_update(ssh_key['id'], {'name': 1})
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0214')

        code, resp = self.client.ssh_key_update(ssh_key['id'],
                                                {'default': 'asd'})
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0226')

        for immutable in ['created_at', 'deleted_at', 'key',
                          'fingerprint', 'employee_id']:
            code, resp = self.client.ssh_key_update(
                ssh_key['id'],  {immutable: 'value'})
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0211')
        code, resp = self.client.ssh_key_update(ssh_key['id'],
                                                {'unexpected': 'value'})
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0212')

    def test_patch_another_employee(self):
        code, ssh_key = self.client.ssh_key_create(
            self.employee['id'], self.valid_body)
        self.assertEqual(code, 201)

        auth_user_2 = str(uuid.uuid4())
        _, employee2 = self.client.employee_create(
            self.organization['id'], {'name': 'employee2',
                                      'auth_user_id': auth_user_2})
        self._mock_auth_user(auth_user_2)

        code, resp = self.client.ssh_key_update(
            ssh_key['id'], {'name': 'another'})
        self.assertEqual(code, 403)
        self.verify_error_code(resp, 'OE0234')

    def test_delete_invaild(self):
        code, resp = self.client.ssh_key_delete(str(uuid.uuid4()))
        self.assertEqual(code, 404)
        self.verify_error_code(resp, 'OE0002')

    def test_delete_another_employee(self):
        code, ssh_key = self.client.ssh_key_create(
            self.employee['id'], self.valid_body)
        self.assertEqual(code, 201)

        auth_user_2 = str(uuid.uuid4())
        _, employee2 = self.client.employee_create(
            self.organization['id'], {'name': 'employee2',
                                      'auth_user_id': auth_user_2})
        self._mock_auth_user(auth_user_2)

        code, resp = self.client.ssh_key_delete(ssh_key['id'])
        self.assertEqual(code, 403)
        self.verify_error_code(resp, 'OE0234')

    def test_default_ssh_key(self):
        code, ssh_key1 = self.client.ssh_key_create(self.employee['id'],
                                                    self.valid_body)
        self.assertEqual(code, 201)
        self.assertTrue(ssh_key1['default'])
        code, employee = self.client.employee_get(self.employee['id'])
        self.assertEqual(code, 200)
        self.assertEqual(employee['default_ssh_key_id'], ssh_key1['id'])

        self.valid_body['key'] = 'ssh AAAAC3Nk ubuntu'
        self.valid_body['default'] = True
        code, ssh_key2 = self.client.ssh_key_create(self.employee['id'],
                                                    self.valid_body)
        self.assertEqual(code, 201)
        self.assertTrue(ssh_key2['default'])
        code, employee = self.client.employee_get(self.employee['id'])
        self.assertEqual(code, 200)
        self.assertEqual(employee['default_ssh_key_id'], ssh_key2['id'])

        code, resp = self.client.ssh_key_get(ssh_key1['id'])
        self.assertEqual(code, 200)
        self.assertFalse(resp['default'])

        code, resp = self.client.ssh_key_update(
            ssh_key2['id'], {'default': False})
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0508')

        code, resp = self.client.ssh_key_update(
            ssh_key1['id'], {'default': True})
        self.assertEqual(code, 200)
        self.assertTrue(resp['default'])
        code, employee = self.client.employee_get(self.employee['id'])
        self.assertEqual(code, 200)
        self.assertEqual(employee['default_ssh_key_id'], ssh_key1['id'])

        code, resp = self.client.ssh_key_get(ssh_key2['id'])
        self.assertEqual(code, 200)
        self.assertFalse(resp['default'])

        code, resp = self.client.ssh_key_delete(ssh_key1['id'])
        self.assertEqual(code, 424)
        self.verify_error_code(resp, 'OE0509')

        code, _ = self.client.ssh_key_delete(ssh_key2['id'])
        self.assertEqual(code, 204)
        code, _ = self.client.ssh_key_delete(ssh_key1['id'])
        self.assertEqual(code, 204)

    def test_employee_default_ssh_key_id(self):
        code, ssh_key1 = self.client.ssh_key_create(self.employee['id'],
                                                    self.valid_body)
        self.assertEqual(code, 201)
        self.assertTrue(ssh_key1['default'])

        auth_user_2 = self.gen_id()
        _, employee_2 = self.client.employee_create(
            self.organization['id'], {'name': 'employee',
                                      'auth_user_id': auth_user_2})
        self._mock_auth_user(auth_user_2)
        code, ssh_key2 = self.client.ssh_key_create(employee_2['id'],
                                                    self.valid_body)
        self.assertEqual(code, 201)
        self.assertTrue(ssh_key2['default'])

        code, _ = self.client.ssh_key_get(ssh_key1['id'])
        self.assertEqual(code, 403)
        code, resp = self.client.employee_list(self.organization_id)
        self.assertEqual(code, 200)
        # employee1, employee2, default_employee
        self.assertEqual(len(resp['employees']), 3)
        employee_default_ssh_map = {
            self.employee['id']: ssh_key1['id'],
            employee_2['id']: ssh_key2['id']
        }
        for e in resp['employees']:
            def_key = employee_default_ssh_map.get(e['id'])
            self.assertEqual(e['default_ssh_key_id'], def_key)
