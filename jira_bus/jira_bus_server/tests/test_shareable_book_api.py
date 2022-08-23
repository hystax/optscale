from unittest.mock import patch

from jira_bus_server.tests.test_api_base import TestApiBase
from jira_bus_server.utils import gen_id


class TestShareableBookApi(TestApiBase):
    def setUp(self):
        super().setUp()
        client = self.get_client(
            include_client_key=True, include_account_id=True)
        client.installed(self.installed_payload)
        _, resp = client.user_assignment_create()
        secret = resp.get('secret')
        client.assign_auth_user(secret=secret)
        client.organization_assignment_create(
            organization_id=self.organization_id)

    def test_create_booking(self):
        client = self.get_client(
            include_client_key=True, include_account_id=True)

        employee_id = gen_id()
        resource_id = gen_id()

        expected_params = {
            'organization_id': self.organization_id,
            'params': {
                'resource_id': resource_id,
                'acquired_by_id': employee_id,
                'jira_auto_release': True,
            }
        }

        patch(
            'jira_bus_server.controllers.shareable_book.'
            'ShareableBookController._get_employee_id',
            return_value=employee_id).start()
        shareable_book_create_response = self.get_response_mock(
            'shareable_book_create')
        self.rest_cl_mock.shareable_book_create.return_value = (
            200, shareable_book_create_response)

        code, resp = client.shareable_book_create(resource_id, {})
        self.assertEqual(code, 200)
        self.assertEqual(resp['id'], shareable_book_create_response['id'])
        self.rest_cl_mock.shareable_book_create.assert_called_once_with(
            **expected_params)

        self.rest_cl_mock.shareable_book_create.reset_mock()
        expected_params['params']['jira_auto_release'] = False

        code, resp = client.shareable_book_create(resource_id, {
            'jira_auto_release': False})
        self.assertEqual(code, 200)
        self.assertEqual(resp['id'], shareable_book_create_response['id'])
        self.rest_cl_mock.shareable_book_create.assert_called_once_with(
            **expected_params)

    def test_release_booking(self):
        client = self.get_client(
            include_client_key=True, include_account_id=True)
        booking_id = gen_id()
        code, _ = client.shareable_book_release(booking_id)
        self.assertEqual(code, 204)
        self.rest_cl_mock.shareable_book_release.assert_called_once()

    def test_delete_booking(self):
        client = self.get_client(
            include_client_key=True, include_account_id=True)
        booking_id = gen_id()
        code, _ = client.shareable_book_delete(booking_id)
        self.assertEqual(code, 204)
        self.rest_cl_mock.shareable_book_delete.assert_called_once_with(
            booking_id)

    def test_no_atlassian_auth(self):
        no_auth_client = self.get_client()

        code, resp = no_auth_client.shareable_book_create(gen_id(), {})
        self.assertEqual(code, 401)
        self.verify_error_code(resp, 'OJ0012')

        code, resp = no_auth_client.shareable_book_release(gen_id())
        self.assertEqual(code, 401)
        self.verify_error_code(resp, 'OJ0012')

        code, resp = no_auth_client.shareable_book_delete(gen_id())
        self.assertEqual(code, 401)
        self.verify_error_code(resp, 'OJ0012')

    def test_no_atlassian_account(self):
        no_account_client = self.get_client(include_client_key=True)

        code, resp = no_account_client.shareable_book_create(gen_id(), {})
        self.assertEqual(code, 401)
        self.verify_error_code(resp, 'OJ0016')

        code, resp = no_account_client.shareable_book_release(gen_id())
        self.assertEqual(code, 401)
        self.verify_error_code(resp, 'OJ0016')

        code, resp = no_account_client.shareable_book_delete(gen_id())
        self.assertEqual(code, 401)
        self.verify_error_code(resp, 'OJ0016')
