from jira_bus_server.tests.test_api_base import TestApiBase


class TestIssueInfoApi(TestApiBase):
    def setUp(self):
        super().setUp()
        client = self.get_client(include_client_key=True)
        client.installed(self.installed_payload)

    def test_get_info(self):
        client = self.get_client(
            include_client_key=True, include_issue_key=True)
        self.atlassian_cl_mock.issue().get.return_value = (
            self.get_response_mock('get_issue_with_status_and_transitions'))
        code, resp = client.issue_info_get()
        self.assertEqual(code, 200)
        self.assertEqual(resp['issue_key'], self.issue_key)
        self.assertEqual(resp['project_key'], self.project_key)
        self.assertEqual(resp['issue_number'], self.issue_number)
        link = self.installed_payload['baseUrl'] + '/browse/' + self.issue_key
        self.assertEqual(resp['issue_link'], link)
        self.assertIsInstance(resp['available_statuses'], list)
        self.assertIsInstance(resp['current_status'], str)

    def test_no_atlassian_auth(self):
        no_auth_client = self.get_client()
        code, resp = no_auth_client.issue_info_get()
        self.assertEqual(code, 401)
        self.verify_error_code(resp, 'OJ0012')

    def test_no_issue_context(self):
        no_issue_client = self.get_client(include_client_key=True)
        code, resp = no_issue_client.issue_info_get()
        self.assertEqual(code, 401)
        self.verify_error_code(resp, 'OJ0022')
