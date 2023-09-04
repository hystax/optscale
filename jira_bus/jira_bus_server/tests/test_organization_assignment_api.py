from jira_bus.jira_bus_server.exceptions import Err
from jira_bus.jira_bus_server.tests.test_api_base import TestApiBase
from jira_bus.jira_bus_server.utils import gen_id

from tools.optscale_exceptions.http_exc import OptHTTPError


class TestOrganizationAssignmentApi(TestApiBase):
    def setUp(self):
        super().setUp()
        client = self.get_client(include_client_key=True, include_account_id=True)
        client.installed(self.installed_payload)
        _, resp = client.user_assignment_create()
        secret = resp.get("secret")
        client.assign_auth_user(secret=secret)

    def test_get_assignment(self):
        client = self.get_client(include_client_key=True, include_account_id=True)

        code, resp = client.organization_assignment_get()
        self.assertEqual(code, 404)
        self.verify_error_code(resp, "OJ0019")

        code, resp = client.organization_assignment_create(
            organization_id=self.organization_id
        )
        self.assertEqual(code, 204)

        code, resp = client.organization_assignment_get()
        self.assertEqual(code, 200)
        self.assertEqual(resp["organization_id"], self.organization_id)
        self.assertNotIn("details", resp)

        self.rest_cl_mock.organization_get.return_value = (
            200,
            self.get_response_mock("organization_get"),
        )
        code, resp = client.organization_assignment_get(details=True)
        self.assertEqual(code, 200)
        self.assertEqual(resp["organization_id"], self.organization_id)
        self.assertIn("details", resp)

    def test_create_and_recreate_assignment(self):
        client = self.get_client(include_client_key=True, include_account_id=True)
        organization1_id = gen_id()
        organization2_id = gen_id()

        self.m_optscale_permission.side_effect = OptHTTPError(401, Err.OJ0018, [])

        code, resp = client.organization_assignment_create(
            organization_id=organization1_id
        )
        self.assertEqual(code, 401)
        self.verify_error_code(resp, "OJ0018")

        self.m_optscale_permission.side_effect = None

        code, resp = client.organization_assignment_create(
            organization_id=organization1_id
        )
        self.assertEqual(code, 204)

        code, resp = client.organization_assignment_create(
            organization_id=organization1_id
        )
        self.assertEqual(code, 204)

        code, resp = client.organization_assignment_create(
            organization_id=organization2_id
        )
        self.assertEqual(code, 204)

        def has_permission_only_for_organization1(
            action, type, resource_id, auth_token=None
        ):  # noqa
            if resource_id != organization1_id:
                raise OptHTTPError(401, Err.OJ0018, [])

        self.m_optscale_permission.side_effect = has_permission_only_for_organization1

        code, resp = client.organization_assignment_create(
            organization_id=organization1_id
        )
        self.assertEqual(code, 401)
        self.verify_error_code(resp, "OJ0018")

        def has_permission_only_for_organization2(
            action, type, resource_id, auth_token=None
        ):  # noqa
            if resource_id != organization2_id:
                raise OptHTTPError(401, Err.OJ0018, [])

        self.m_optscale_permission.side_effect = has_permission_only_for_organization2

        code, resp = client.organization_assignment_create(
            organization_id=organization1_id
        )
        self.assertEqual(code, 401)
        self.verify_error_code(resp, "OJ0018")

        self.m_optscale_permission.side_effect = None

        code, resp = client.organization_assignment_create(
            organization_id=organization1_id
        )
        self.assertEqual(code, 204)

    def test_delete_assignment(self):
        client = self.get_client(include_client_key=True, include_account_id=True)

        code, resp = client.organization_assignment_create(
            organization_id=self.organization_id
        )
        self.assertEqual(code, 204)

        self.m_optscale_permission.side_effect = OptHTTPError(401, Err.OJ0018, [])

        code, resp = client.organization_assignment_delete()
        self.assertEqual(code, 401)
        self.verify_error_code(resp, "OJ0018")

        self.m_optscale_permission.side_effect = None

        code, resp = client.organization_assignment_delete()
        self.assertEqual(code, 204)

        code, resp = client.organization_assignment_delete()
        self.assertEqual(code, 204)

    def test_no_atlassian_auth(self):
        no_auth_client = self.get_client()

        code, resp = no_auth_client.organization_assignment_get()
        self.assertEqual(code, 401)
        self.verify_error_code(resp, "OJ0012")

        code, resp = no_auth_client.organization_assignment_create(self.organization_id)
        self.assertEqual(code, 401)
        self.verify_error_code(resp, "OJ0012")

        code, resp = no_auth_client.organization_assignment_delete()
        self.assertEqual(code, 401)
        self.verify_error_code(resp, "OJ0012")

    def test_no_atlassian_account(self):
        no_account_client = self.get_client(include_client_key=True)

        code, resp = no_account_client.organization_assignment_get()
        self.assertEqual(code, 404)

        code, resp = no_account_client.organization_assignment_create(
            self.organization_id
        )
        self.assertEqual(code, 401)
        self.verify_error_code(resp, "OJ0016")

        code, resp = no_account_client.organization_assignment_delete()
        self.assertEqual(code, 401)
        self.verify_error_code(resp, "OJ0016")
