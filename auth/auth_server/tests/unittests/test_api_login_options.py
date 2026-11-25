from unittest.mock import patch, PropertyMock

from auth.auth_server.tests.unittests.test_api_base import TestAuthBase


class TestLoginOptions(TestAuthBase):
    def setUp(self, version="v2"):
        super().setUp(version=version)

    def test_email_not_provided(self):
        code, resp = self.client.login_options('')
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OA0032')

    def test_unexpected_parameter(self):
        code, resp = self.client.post(
            self.client.login_options_url(),
            {'email': 'customer@domain.com', 'password': 'pass'})
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OA0022')

    def test_email_invalid(self):
        code, resp = self.client.login_options(123456)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OA0033')

    def test_resolve(self):
        code, resp = self.client.login_options('customer@domain.com')
        self.assertEqual(code, 200)
        self.assertEqual(resp['methods'], ['password'])
        self.assertEqual(resp['sso']['state'], 'not_configured')
