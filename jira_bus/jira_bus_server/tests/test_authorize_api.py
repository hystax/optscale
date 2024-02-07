from jira_bus.jira_bus_server.tests.test_api_base import TestApiBase


class TestAuthorizeApi(TestApiBase):
    def setUp(self):
        super().setUp()
        client = self.get_client(include_client_key=True)
        client.installed(self.installed_payload)

    def test_authorize(self):
        client = self.get_client(include_client_key=True)
        code, resp = client.authorize({})
        self.assertEqual(code, 200)

    def test_authorize_forbidden(self):
        client = self.get_client()
        code, resp = client.authorize({})
        self.assertEqual(code, 403)
        self.verify_error_code(resp, "OJ0018")
