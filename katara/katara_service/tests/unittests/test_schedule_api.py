import uuid

from katara.katara_service.tests.unittests.test_api_base import TestBase


class TestScheduleApi(TestBase):
    def setUp(self):
        super().setUp()

    def test_schedule_get(self):
        schedules = self.generate_schedules(1)
        code, schedule = self.client.schedule_get(schedules[0].id)
        self.assertEqual(code, 200)
        self.assertEqual(schedules[0].id, schedule['id'])

    def test_schedule_get_nonexisting(self):
        id = str(uuid.uuid4())
        code, _ = self.client.schedule_get(id)
        self.assertEqual(code, 404)

    def test_schedule_delete(self):
        schedules = self.generate_schedules(1)
        code, _ = self.client.schedule_delete(schedules[0].id)
        self.assertEqual(code, 204)

    def test_schedule_update(self):
        schedules = self.generate_schedules(1)
        new_crontab = '*/2 * * * *'
        code, schedule = self.client.schedule_update(
            schedules[0].id, crontab=new_crontab)
        self.assertEqual(code, 200)
        self.assertEqual(new_crontab, schedule['crontab'])

    def test_schedule_update_wrong_crontab(self):
        schedules = self.generate_schedules(1)
        new_crontab = 'str'
        code, _ = self.client.schedule_update(
            schedules[0].id, crontab=new_crontab)
        self.assertEqual(code, 400)

    def test_schedule_update_restriction(self):
        schedules = self.generate_schedules(1)
        code, _ = self.client.schedule_update(
            schedules[0].id, recipient_id=str(uuid.uuid4()))
        self.assertEqual(code, 400)

    def test_schedule_create(self):
        report = self.generate_reports(1)[0]
        recipient = self.generate_recipients(1)[0]
        crontab = '*/2 * * * *'
        code, schedule = self.client.schedule_create(
            crontab=crontab, recipient_id=recipient.id, report_id=report.id)
        self.assertEqual(code, 201)
        self.assertEqual(crontab, schedule['crontab'])
        self.assertEqual(recipient.id, schedule['recipient_id'])
        self.assertEqual(report.id, schedule['report_id'])

    def test_schedule_create_wrong_crontab(self):
        report = self.generate_reports(1)[0]
        recipient = self.generate_recipients(1)[0]
        crontab = 'str'
        code, _ = self.client.schedule_create(
            crontab=crontab, recipient_id=recipient.id, report_id=report.id)
        self.assertEqual(code, 400)

    def test_schedule_create_nonexistent_report(self):
        report_id = str(uuid.uuid4())
        recipient = self.generate_recipients(1)[0]
        crontab = '*/2 * * * *'
        code, _ = self.client.schedule_create(
            crontab=crontab, recipient_id=recipient.id, report_id=report_id)
        self.assertEqual(code, 404)

    def test_schedule_create_nonexistent_recipient(self):
        report = self.generate_reports(1)[0]
        recipient_id = str(uuid.uuid4())
        crontab = '*/2 * * * *'
        code, _ = self.client.schedule_create(
            crontab=crontab, recipient_id=recipient_id, report_id=report.id)
        self.assertEqual(code, 404)

    def test_schedule_list(self):
        report = self.generate_reports(1)[0]
        recipient = self.generate_recipients(1)[0]
        crontab = '*/2 * * * *'
        _, schedule = self.client.schedule_create(
            crontab=crontab, recipient_id=recipient.id, report_id=report.id)
        code, api_recipients = self.client.schedule_list(
            recipient_id=recipient.id)
        self.assertEqual(code, 200)
        self.assertEqual(
            api_recipients['schedules'][0]['id'], schedule['id'])

    def test_schedule_list_nonexisting_recipient(self):
        report = self.generate_reports(1)[0]
        recipient = self.generate_recipients(1)[0]
        crontab = '*/2 * * * *'
        _, schedule = self.client.schedule_create(
            crontab=crontab, recipient_id=recipient.id, report_id=report.id)
        code, api_recipients = self.client.schedule_list(
            recipient_id=str(uuid.uuid4()))
        self.assertEqual(code, 200)
        self.assertEqual(len(api_recipients['schedules']), 0)

    def test_schedule_list_by_report(self):
        reports = self.generate_reports(2)
        recipients = self.generate_recipients(2)
        crontab = '*/2 * * * *'
        schedules = []
        for i in range(2):
            _, schedule = self.client.schedule_create(
                crontab=crontab, recipient_id=recipients[i].id, report_id=reports[i].id)
            schedules.append(schedule)
        code, api_recipients = self.client.schedule_list(
            recipient_id=recipients[1].id, report_id=reports[1].id)
        self.assertEqual(code, 200)
        self.assertEqual(len(api_recipients['schedules']), 1)
        self.assertEqual(api_recipients['schedules'][0]['id'], schedules[1]['id'])
