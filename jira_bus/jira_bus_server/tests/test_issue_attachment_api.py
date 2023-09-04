from unittest.mock import patch

from jira_bus.jira_bus_server.exceptions import Err
from jira_bus.jira_bus_server.tests.test_api_base import TestApiBase
from jira_bus.jira_bus_server.utils import gen_id

from tools.optscale_exceptions.common_exc import NotFoundException


class TestIssueAttachmentApi(TestApiBase):
    def setUp(self):
        super().setUp()
        client = self.get_client(include_client_key=True, include_account_id=True)
        client.installed(self.installed_payload)
        _, resp = client.user_assignment_create()
        secret = resp.get("secret")
        client.assign_auth_user(secret=secret)
        client.organization_assignment_create(organization_id=self.organization_id)

    def test_create_attachment(self):
        client = self.get_client(
            include_client_key=True, include_account_id=True, include_issue_key=True
        )

        self.atlassian_cl_mock.issue().get.return_value = self.get_response_mock(
            "get_issue_with_status_and_transitions"
        )

        employee_id = gen_id()
        resource_id = gen_id()
        existing_booking_id = gen_id()
        manually_specified_booking_id = gen_id()

        patch(
            "jira_bus.jira_bus_server.controllers.issue_attachment."
            "IssueAttachmentController._get_employee_id",
            return_value=employee_id,
        ).start()
        p_find_existing_booking = patch(
            "jira_bus.jira_bus_server.controllers.issue_attachment."
            "IssueAttachmentController._find_existing_booking",
            return_value=existing_booking_id,
        ).start()

        jira_issue_attachment_create_response = self.get_response_mock(
            "jira_issue_attachment_create"
        )
        self.rest_cl_mock.jira_issue_attachment_create.return_value = (
            200,
            jira_issue_attachment_create_response,
        )

        code, resp = client.issue_attachment_create(resource_id, {})
        self.assertEqual(code, 200)
        self.assertEqual(resp["id"], jira_issue_attachment_create_response["id"])
        p_find_existing_booking.assert_called_once()
        self.rest_cl_mock.jira_issue_attachment_create.assert_called_once()

        self.rest_cl_mock.reset_mock()
        p_find_existing_booking.reset_mock()

        code, resp = client.issue_attachment_create(
            resource_id, {"booking_id": manually_specified_booking_id}
        )
        self.assertEqual(code, 200)
        p_find_existing_booking.assert_not_called()
        self.rest_cl_mock.jira_issue_attachment_create.assert_called_once()

        self.rest_cl_mock.reset_mock()
        p_find_existing_booking.reset_mock()
        p_find_existing_booking.side_effect = NotFoundException(Err.OJ0025, [])

        code, resp = client.issue_attachment_create(resource_id, {})
        self.assertEqual(code, 404)
        p_find_existing_booking.assert_called_once()

    def test_update_attachment(self):
        client = self.get_client(
            include_client_key=True, include_account_id=True, include_issue_key=True
        )
        attachment_id = gen_id()
        params = {"auto_detach_status": "Backlog"}
        code, _ = client.issue_attachment_update(attachment_id, params)
        self.assertEqual(code, 204)
        self.rest_cl_mock.jira_issue_attachment_update.assert_called_once_with(
            attachment_id, params
        )

    def test_delete_attachment(self):
        client = self.get_client(
            include_client_key=True, include_account_id=True, include_issue_key=True
        )
        attachment_id = gen_id()
        code, _ = client.issue_attachment_delete(attachment_id)
        self.assertEqual(code, 204)
        self.rest_cl_mock.jira_issue_attachment_delete.assert_called_once_with(
            attachment_id
        )

    def test_no_atlassian_auth(self):
        no_auth_client = self.get_client()

        code, resp = no_auth_client.issue_attachment_create(gen_id(), {})
        self.assertEqual(code, 401)
        self.verify_error_code(resp, "OJ0012")

        code, resp = no_auth_client.issue_attachment_update(gen_id(), {})
        self.assertEqual(code, 401)
        self.verify_error_code(resp, "OJ0012")

        code, resp = no_auth_client.issue_attachment_delete(gen_id())
        self.assertEqual(code, 401)
        self.verify_error_code(resp, "OJ0012")

    def test_no_atlassian_account(self):
        no_account_client = self.get_client(include_client_key=True)

        code, resp = no_account_client.issue_attachment_create(gen_id(), {})
        self.assertEqual(code, 401)
        self.verify_error_code(resp, "OJ0016")

        code, resp = no_account_client.issue_attachment_update(gen_id(), {})
        self.assertEqual(code, 401)
        self.verify_error_code(resp, "OJ0016")

        code, resp = no_account_client.issue_attachment_delete(gen_id())
        self.assertEqual(code, 401)
        self.verify_error_code(resp, "OJ0016")

    def test_no_issue_context(self):
        no_account_client = self.get_client(
            include_client_key=True, include_account_id=True
        )

        code, resp = no_account_client.issue_attachment_create(gen_id(), {})
        self.assertEqual(code, 401)
        self.verify_error_code(resp, "OJ0022")
