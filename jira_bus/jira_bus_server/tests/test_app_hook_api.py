from unittest.mock import patch

from jira_bus.jira_bus_server.tests.test_api_base import TestApiBase


class TestAppHookApi(TestApiBase):
    def setUp(self):
        super().setUp()
        client = self.get_client(include_client_key=True, include_account_id=True)
        client.installed(self.installed_payload)
        _, resp = client.user_assignment_create()
        secret = resp.get("secret")
        client.assign_auth_user(secret=secret)
        client.organization_assignment_create(organization_id=self.organization_id)

    def test_issue_hooks(self):
        client = self.get_client(include_client_key=True)

        issue_payload = {"fake_payload": 123}
        issue_details = (self.project_key, self.issue_number, "Backlog")
        patch(
            "jira_bus.jira_bus_server.controllers.app_hook.AppHookController."
            "_parse_issue_payload",
            return_value=issue_details,
        ).start()

        issue_attachment_list_response = self.get_response_mock("issue_attachment_list")
        self.rest_cl_mock.jira_issue_attachment_list.return_value = (
            200,
            issue_attachment_list_response,
        )

        code, resp = client.issue_updated(issue_payload)
        self.assertEqual(code, 204)
        self.assertEqual(
            self.rest_cl_mock.jira_issue_attachment_update.call_count,
            len(issue_attachment_list_response["jira_issue_attachments"]),
        )

        code, resp = client.issue_deleted(issue_payload)
        self.assertEqual(code, 204)
        self.assertEqual(
            self.rest_cl_mock.jira_issue_attachment_delete.call_count,
            len(issue_attachment_list_response["jira_issue_attachments"]),
        )

    def test_no_atlassian_auth(self):
        no_auth_client = self.get_client()
        issue_payload = {"fake_payload": 123}

        code, resp = no_auth_client.issue_updated(issue_payload)
        self.assertEqual(code, 401)
        self.verify_error_code(resp, "OJ0012")

        code, resp = no_auth_client.issue_deleted(issue_payload)
        self.assertEqual(code, 401)
        self.verify_error_code(resp, "OJ0012")
