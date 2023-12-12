from datetime import datetime
from unittest.mock import patch
from freezegun import freeze_time

from katara.katara_service.models.models import (
    Recipient, Report, ReportFormat, Schedule)
from katara.katara_service.controllers.schedule import ScheduleController
from katara.katara_service.tests.unittests.test_controller_base import (
    TestControllerBase
)

BULK_SIZE = "katara.katara_service.controllers.schedule.BULK_SIZE"
PUT_TASK = "katara.katara_service.controllers.schedule." \
           "ScheduleController.put_tasks"


class TestScheduler(TestControllerBase):

    def generate_schedules(self, schedules_count):
        reports = []
        schedules = []
        if schedules_count > 0:
            recipient = Recipient(
                role_purpose='optscale_engineer',
                scope_id='some scope')
            self.db_session.add(recipient)

            for i in range(schedules_count):
                report = Report(
                    module_name=f'some_module_{i}',
                    name=f'test report_{i}',
                    report_format=ReportFormat.html)
                self.db_session.add(report)
                reports.append(report)
            self.db_session.flush()
            with freeze_time(datetime(2020, 8, 5)):
                for j in range(schedules_count):
                    schedule = Schedule(
                        crontab='*/5 * * * *',
                        recipient_id=recipient.id,
                        report_id=reports[j].id)
                    self.db_session.add(schedule)
                    schedules.append(schedule)
                self.db_session.commit()
        return schedules

    @patch(PUT_TASK)
    def test_no_schedules(self, p_put_tasks):
        self.generate_schedules(0)
        controller = ScheduleController(db_session=self.db_session)
        controller.generate_tasks()
        self.assertEqual(0, p_put_tasks.call_count)

    @patch(PUT_TASK)
    def test_below_bulk_schedules(self, p_put_tasks):
        self.generate_schedules(2)
        controller = ScheduleController(db_session=self.db_session)
        controller.generate_tasks()
        self.assertEqual(1, p_put_tasks.call_count)

    @patch(PUT_TASK)
    @patch(BULK_SIZE, 4)
    def test_upper_bulk_schedules_1(self, p_put_tasks):
        self.generate_schedules(5)
        controller = ScheduleController(db_session=self.db_session)
        controller.generate_tasks()
        self.assertEqual(2, p_put_tasks.call_count)

    @patch(PUT_TASK)
    @patch(BULK_SIZE, 2)
    def test_upper_bulk_schedules_2(self, p_put_tasks):
        self.generate_schedules(51)
        controller = ScheduleController(db_session=self.db_session)
        controller.generate_tasks()
        self.assertEqual(26, p_put_tasks.call_count)
