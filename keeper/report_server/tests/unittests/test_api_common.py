from keeper.report_server.tests.unittests.test_api_base import TestReportBase


class TestCommonApi(TestReportBase):
    def test_invalid_url(self):
        code, response = self.client.post('invalid', {})
        self.assertEqual(code, 404)
        self.assertEqual(response['error']['reason'], 'Not Found')
