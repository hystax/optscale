from unittest.mock import ANY, patch, call
from rest_api.rest_api_server.tests.unittests.test_api_base import TestApiBase


class TestDisconnectSurvey(TestApiBase):
    def setUp(self, version='v2'):
        super().setUp(version)
        self.org_name = "partner_test"
        _, self.org = self.client.organization_create(
            {'name': self.org_name})
        self.org_id = self.org['id']
        self.auth_user = self.gen_id()
        self.valid_employee = {
            'name': 'Eliot Alderson', 'auth_user_id': self.auth_user
        }
        _, self.employee = self.client.employee_create(
            self.org_id, self.valid_employee)
        patch('rest_api.rest_api_server.controllers.base.BaseController.'
              'get_user_id', return_value=self.auth_user).start()

    def test_disconnect_survey(self):
        m_email_send = self.mock_email_send_enable()
        payload = {
            "question1": "answer1",
            "question2": "answer2"
        }

        code, resp = self.client.disconnect_survey_submit(
            self.org_id,
            "Disconnect Survey",
            payload
        )
        m_email_send.assert_called_once_with(
            ANY, ANY, template_type='disconnect_survey',
            template_params=ANY)
        self.assertEqual(code, 204)

    def _generate_big_dict(self, num):
        def _ids():
            for _ in range(num):
                yield self.gen_id()
        return {id_: id_ for id_ in _ids()}

    def test_disconnect_survey_payload_too_big(self):
        payload = self._generate_big_dict(500)
        code, resp = self.client.disconnect_survey_submit(
            self.org_id,
            "Disconnect Survey",
            payload
        )
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0547')

    def test_disconnect_survey_payload_invalid_format(self):
        payload = 'inval1d'
        code, resp = self.client.disconnect_survey_submit(
            self.org_id,
            "Disconnect Survey",
            payload
        )
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0426')

    def test_disconnect_survey_missing_argument(self):
        body = {
            "survey_type": "test",
        }
        code, resp = self.client.post(
            self.client.disconnect_survey_url(self.org_id), body
        )
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0548')

    def test_disconnect_survey_unexpected_argument(self):
        body = {
            "survey_type": "test",
            "payload": dict(),
            "unexpected_arg": 1,
        }
        code, resp = self.client.post(
            self.client.disconnect_survey_url(self.org_id), body
        )
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0212')

    def test_disconnect_org_not_found(self):
        code, resp = self.client.disconnect_survey_submit(
            self.gen_id(),  # non-existing org id
            "Disconnect Survey",
            dict()
        )
        self.assertEqual(code, 404)
