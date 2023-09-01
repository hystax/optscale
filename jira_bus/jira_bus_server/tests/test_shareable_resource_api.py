from unittest.mock import patch

from jira_bus.jira_bus_server.tests.test_api_base import TestApiBase
from jira_bus.jira_bus_server.utils import gen_id


class TestShareableResourceApi(TestApiBase):
    def setUp(self):
        super().setUp()
        client = self.get_client(include_client_key=True, include_account_id=True)
        client.installed(self.installed_payload)
        _, resp = client.user_assignment_create()
        secret = resp.get("secret")
        client.assign_auth_user(secret=secret)
        client.organization_assignment_create(organization_id=self.organization_id)
        employee_id = gen_id()
        patch(
            "jira_bus.jira_bus_server.controllers.shareable_resource."
            "ShareableResourceController._get_employee_id",
            return_value=employee_id,
        ).start()

    def test_list_shareable_resources(self):
        client = self.get_client(include_client_key=True, include_account_id=True)

        allowed_action_get_response = self.get_response_mock("allowed_action_get")
        self.rest_cl_mock.shareable_resources_list.return_value = (
            200,
            self.get_response_mock("shareable_resources_list"),
        )
        self.auth_cl_mock.allowed_action_get.return_value = (
            200,
            allowed_action_get_response,
        )

        code, resp = client.shareable_resource_list()
        self.assertEqual(code, 200)
        expected_permissions = {True: "allowed", False: "forbidden"}
        for resource in resp["shareable_resources"]:
            self.assertEqual(
                resource["book_permission"],
                expected_permissions[
                    "BOOK_ENVIRONMENTS" in allowed_action_get_response[resource["id"]]
                ],
            )
            self.assertIn("current_booking", resource)
            self.assertIn("current_attachment", resource)

        client.user_assignment_delete()

        code, resp = client.shareable_resource_list()
        self.assertEqual(code, 200)
        for resource in resp["shareable_resources"]:
            self.assertEqual(resource["book_permission"], "no_login")
            self.assertIn("current_booking", resource)
            self.assertIn("current_attachment", resource)

    def test_issue_scope_list(self):
        no_issue_client = self.get_client(
            include_client_key=True, include_account_id=True
        )
        issue_client = self.get_client(
            include_client_key=True, include_account_id=True, include_issue_key=True
        )

        shareable_resources_list_response = self.get_response_mock(
            "shareable_resources_list"
        )
        self.rest_cl_mock.shareable_resources_list.return_value = (
            200,
            shareable_resources_list_response,
        )
        self.auth_cl_mock.allowed_action_get.return_value = (
            200,
            self.get_response_mock("allowed_action_get"),
        )

        code, _ = no_issue_client.shareable_resource_list(current_issue=False)
        self.rest_cl_mock.shareable_resources_list.assert_called_once_with(
            self.organization_id, {}
        )
        self.assertEqual(code, 200)

        self.rest_cl_mock.shareable_resources_list.reset_mock()

        code, _ = issue_client.shareable_resource_list(current_issue=True)
        self.assertEqual(code, 200)
        issue_filters = {
            "client_key": self.client_key,
            "project_key": self.project_key,
            "issue_number": self.issue_number,
        }
        self.rest_cl_mock.shareable_resources_list.assert_called_once_with(
            self.organization_id, issue_filters
        )

    def test_no_atlassian_auth(self):
        no_auth_client = self.get_client()

        code, resp = no_auth_client.shareable_resource_list(current_issue=False)
        self.assertEqual(code, 401)
        self.verify_error_code(resp, "OJ0012")

        code, resp = no_auth_client.shareable_resource_list(current_issue=True)
        self.assertEqual(code, 401)
        self.verify_error_code(resp, "OJ0012")

    def test_no_atlassian_account(self):
        no_account_client = self.get_client(include_client_key=True)

        code, resp = no_account_client.shareable_resource_list(current_issue=False)
        self.assertEqual(code, 401)
        self.verify_error_code(resp, "OJ0016")

        code, resp = no_account_client.shareable_resource_list(current_issue=True)
        self.assertEqual(code, 401)
        self.verify_error_code(resp, "OJ0016")

    def test_no_issue_context(self):
        no_account_client = self.get_client(
            include_client_key=True, include_account_id=True
        )

        self.rest_cl_mock.shareable_resources_list.return_value = (
            200,
            self.get_response_mock("shareable_resources_list"),
        )
        self.auth_cl_mock.allowed_action_get.return_value = (
            200,
            self.get_response_mock("allowed_action_get"),
        )

        code, resp = no_account_client.shareable_resource_list(current_issue=False)
        self.assertEqual(code, 200)

        code, resp = no_account_client.shareable_resource_list(current_issue=True)
        self.assertEqual(code, 401)
        self.verify_error_code(resp, "OJ0022")
