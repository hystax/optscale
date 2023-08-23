import uuid
from unittest.mock import patch

from keeper.report_server.tests.unittests.test_api_base import TestReportBase


class TesApiFeedback(TestReportBase):

    def setUp(self, *args, **kwargs):
        super().setUp()
        patch('keeper.report_server.handlers.v2.base.AuthClient.type_list').start()
        patch('keeper.report_server.controllers.event_base.EventBaseController.get_user_id_by_token',
              return_value=str(uuid.uuid4())).start()

    @patch("keeper.report_server.controllers.feedback.Feedback")
    def test_submit_feedback(self, p_feedback):
        patch(
            'keeper.report_server.handlers.v2.base.Config').start()
        p_feedback.return_value.to_dict.return_value = {
            "id": "44b141a8f3820c2e18491a11"}
        feedback = {
            'email': 'test@email.com',
            'url': 'test',
            'text': 'Lorem Ipsum',
        }
        code, response = self.client.feedback_submit(**feedback)
        self.assertEqual(code, 201)

    def test_submit_feedback_invalid_meta(self):
        feedback = {
            'email': 'test@email.com',
            'url': 'test',
            'text': 'Lorem Ipsum',
            'metadata': 123
        }
        code, response = self.client.feedback_submit(**feedback)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['reason'],
                         '"metadata" should be a string with valid JSON')

    @patch(
        "keeper.report_server.controllers.feedback.FeedbackController.list")
    def test_example_feedbacks_list(self, p_fdbck_list):
        p_fdbck_list.return_value = []
        code, response = self.client.feedbacks_list()
        self.assertEqual(code, 200)
