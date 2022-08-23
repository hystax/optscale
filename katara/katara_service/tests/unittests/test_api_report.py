import uuid

from katara_service.tests.unittests.test_api_base import TestBase


class TestReportApi(TestBase):
    def setUp(self):
        super().setUp()

    def test_report_get(self):
        reports = self.generate_reports(1)
        code, report = self.client.report_get(reports[0].id)
        self.assertEqual(code, 200)
        self.assertEqual(reports[0].id, report['id'])

    def test_report_get_nonexisting(self):
        id = str(uuid.uuid4())
        code, _ = self.client.report_get(id)
        self.assertEqual(code, 404)

    def test_report_list(self):
        reports = self.generate_reports(3)
        code, api_reports = self.client.report_list()
        self.assertEqual(code, 200)
        self.assertEqual(len(api_reports['reports']), len(reports))

    def test_report_list_empty(self):
        code, api_reports = self.client.report_list()
        self.assertEqual(code, 200)
        self.assertEqual(len(api_reports['reports']), 0)
