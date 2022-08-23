from jira_bus_server.tests.test_api_base import TestApiBase
from jira_bus_server.utils import gen_id


class TestOrganizationStatusApi(TestApiBase):
    def setUp(self):
        super().setUp()
        client = self.get_client(
            include_client_key=True, include_account_id=True)
        client.installed(self.installed_payload)
        _, resp = client.user_assignment_create()
        secret = resp.get('secret')
        client.assign_auth_user(secret=secret)

    def test_organization_status(self):
        client = self.get_client(include_token=True, include_client_key=True,
                                 include_account_id=True)

        code, resp = client.organization_status_get(self.organization_id)
        self.assertEqual(code, 200)
        self.assertEqual(resp['connected'], False)
        self.assertEqual(resp['connected_tenants'], [])

        client.organization_assignment_create(self.organization_id)

        code, resp = client.organization_status_get(self.organization_id)
        self.assertEqual(code, 200)
        self.assertEqual(resp['connected'], True)
        connected_tenant = resp['connected_tenants'][0]
        display_url = (self.installed_payload.get('displayUrl') or
                       self.installed_payload['baseUrl'])
        self.assertEqual(connected_tenant['client_key'], self.client_key)
        self.assertEqual(connected_tenant['display_url'], display_url)
