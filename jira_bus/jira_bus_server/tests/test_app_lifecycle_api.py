from jira_bus_server.tests.test_api_base import TestApiBase


class TestAppLifecycleApi(TestApiBase):

    def test_app_installed_and_reinstalled(self):
        no_auth_client = self.get_client()
        code, resp = no_auth_client.installed(self.installed_payload)
        self.assertEqual(code, 401)
        self.verify_error_code(resp, 'OJ0012')

        client = self.get_client(include_client_key=True)

        code, resp = client.installed(self.installed_payload)
        self.assertEqual(code, 204)

        code, resp = client.installed(self.installed_payload)
        self.assertEqual(code, 204)
