from jira_bus.jira_bus_server.constants import APP_KEY
from jira_bus.jira_bus_server.tests.test_api_base import TestApiBase


class TestAppDescriptorApi(TestApiBase):
    def test_app_descriptor(self):
        no_auth_client = self.get_client()
        code, resp = no_auth_client.app_descriptor("example.com")
        self.assertEqual(code, 200)
        self.assertEqual(resp["baseUrl"], "https://example.com")
        self.assertEqual(resp["key"], APP_KEY)
