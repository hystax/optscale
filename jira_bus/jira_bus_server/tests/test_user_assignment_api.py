from jira_bus_server.tests.test_api_base import TestApiBase


class TestUserAssignmentApi(TestApiBase):
    def setUp(self):
        super().setUp()
        client = self.get_client(include_client_key=True)
        client.installed(self.installed_payload)

    def test_get_assignment(self):
        client = self.get_client(
            include_client_key=True, include_account_id=True,
            include_token=True)

        code, resp = client.user_assignment_get()
        self.assertEqual(code, 404)
        self.verify_error_code(resp, 'OJ0008')

        code, resp = client.user_assignment_create()
        self.assertEqual(code, 200)

        code, resp = client.user_assignment_get()
        self.assertEqual(code, 200)

    def test_create_and_recreate_assignment(self):
        client = self.get_client(
            include_client_key=True, include_account_id=True)

        code, resp = client.user_assignment_create()
        secret1 = resp.get('secret')
        self.assertEqual(code, 200)
        self.assertTrue(isinstance(secret1, str))

        code, resp = client.user_assignment_create()
        secret2 = resp.get('secret')
        self.assertEqual(code, 200)
        self.assertTrue(isinstance(secret2, str))
        self.assertNotEqual(secret1, secret2)

    def test_assign_auth_user(self):
        client = self.get_client(
            include_client_key=True, include_account_id=True,
            include_token=True)

        code, resp = client.user_assignment_create()
        self.assertEqual(code, 200)
        secret = resp.get('secret')

        code, resp = client.user_assignment_get()
        self.assertEqual(code, 200)
        self.assertEqual(resp.get('auth_user_id'), None)
        self.assertEqual(resp.get('jira_account_id'), self.account_id)

        code, resp = client.assign_auth_user(secret='not-a-secret')
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OJ0011')
        self.auth_cl_mock.user_update.assert_not_called()

        code, resp = client.assign_auth_user(secret=secret)
        self.auth_cl_mock.user_update.assert_called_once_with(
            self.auth_user_id, jira_connected=True)
        self.assertEqual(code, 204)

        code, resp = client.user_assignment_get()
        self.assertEqual(code, 200)
        self.assertEqual(resp.get('auth_user_id'), self.auth_user_id)
        self.assertEqual(resp.get('jira_account_id'), self.account_id)

    def test_delete_assignment(self):
        client = self.get_client(
            include_client_key=True, include_account_id=True,
            include_token=True)

        code, resp = client.user_assignment_create()
        self.assertEqual(code, 200)
        secret = resp.get('secret')

        code, resp = client.assign_auth_user(secret=secret)
        self.assertEqual(code, 204)
        self.auth_cl_mock.user_update.reset_mock()

        code, resp = client.user_assignment_get()
        self.assertEqual(code, 200)

        code, resp = client.user_assignment_delete()
        self.assertEqual(code, 204)
        self.auth_cl_mock.user_update.assert_called_once_with(
            self.auth_user_id, jira_connected=False)

        code, resp = client.user_assignment_get()
        self.assertEqual(code, 404)

        code, resp = client.user_assignment_delete()
        self.assertEqual(code, 204)

    def test_no_atlassian_auth(self):
        no_auth_client = self.get_client()

        code, resp = no_auth_client.user_assignment_get()
        self.assertEqual(code, 401)
        self.verify_error_code(resp, 'OJ0012')

        code, resp = no_auth_client.user_assignment_create()
        self.assertEqual(code, 401)
        self.verify_error_code(resp, 'OJ0012')

        code, resp = no_auth_client.user_assignment_delete()
        self.assertEqual(code, 401)
        self.verify_error_code(resp, 'OJ0012')

    def test_no_atlassian_account(self):
        no_account_client = self.get_client(include_client_key=True)

        code, resp = no_account_client.user_assignment_get()
        self.assertEqual(code, 401)
        self.verify_error_code(resp, 'OJ0016')

        code, resp = no_account_client.user_assignment_create()
        self.assertEqual(code, 401)
        self.verify_error_code(resp, 'OJ0016')

        code, resp = no_account_client.user_assignment_delete()
        self.assertEqual(code, 401)
        self.verify_error_code(resp, 'OJ0016')
