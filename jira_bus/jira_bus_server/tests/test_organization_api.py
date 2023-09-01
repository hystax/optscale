from jira_bus.jira_bus_server.tests.test_api_base import TestApiBase


class TestOrganizationApi(TestApiBase):
    def setUp(self):
        super().setUp()
        client = self.get_client(include_client_key=True, include_account_id=True)
        client.installed(self.installed_payload)
        _, resp = client.user_assignment_create()
        secret = resp.get("secret")
        client.assign_auth_user(secret=secret)

    def test_organization_list(self):
        client = self.get_client(include_client_key=True, include_account_id=True)
        organization_list_response = self.get_response_mock("organization_list")
        mocked_organizations_by_id = {
            x["id"]: x for x in organization_list_response["organizations"]
        }
        actions_resources_edit_partner_response = self.get_response_mock(
            "actions_resources_edit_partner"
        )
        edit_partner_ids = {
            x[1] for x in actions_resources_edit_partner_response["EDIT_PARTNER"]
        }
        self.rest_cl_mock.organization_list.return_value = (
            200,
            organization_list_response,
        )
        self.auth_cl_mock.action_resources_get.return_value = (
            200,
            actions_resources_edit_partner_response,
        )
        code, resp = client.organization_list()
        self.assertEqual(code, 200)
        for org in resp["organizations"]:
            self.assertTrue(org["id"] in mocked_organizations_by_id)
            self.assertEqual(org["name"], mocked_organizations_by_id[org["id"]]["name"])
            self.assertEqual(org["is_manager"], org["id"] in edit_partner_ids)

    def test_no_atlassian_auth(self):
        no_auth_client = self.get_client()
        code, resp = no_auth_client.organization_list()
        self.assertEqual(code, 401)
        self.verify_error_code(resp, "OJ0012")

    def test_no_atlassian_account(self):
        no_account_client = self.get_client(include_client_key=True)
        code, resp = no_account_client.organization_list()
        self.assertEqual(code, 401)
        self.verify_error_code(resp, "OJ0016")
