import tornado.testing
from unittest.mock import patch
import uuid

from katara_service.models.models import *
from katara_service.main import make_app, Roles
from katara_service.models.db_factory import DBType, DBFactory
from katara_service.models.db_base import BaseDB

import katara_client.client


class TestBase(tornado.testing.AsyncHTTPTestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._db_session = None

    def get_app(self):
        return make_app(DBType.Test, Roles.api, '127.0.0.1', 80)

    @property
    def db_session(self):
        db = DBFactory(DBType.Test, None).db
        engine = db.engine
        if not self._db_session:
            self._db_session = BaseDB.session(engine)()
        return self._db_session

    def setUp(self):
        super().setUp()
        secret = gen_id()
        patch('config_client.client.Client.cluster_secret',
              return_value=secret).start()
        http_provider = katara_client.client.FetchMethodHttpProvider(
            self.fetch, rethrow=False)
        self.client = katara_client.client.Client(
            http_provider=http_provider)
        self.client.secret = secret

    def tearDown(self):
        DBFactory.clean_type(DBType.Test)
        super().tearDown()

    def generate_reports(self, count=1):
        session = self.db_session
        reports = []
        for i in range(count):
            report = Report(module_name='module_%s' % i,
                            name='report_%s' % i,
                            report_format=ReportFormat.html)
            session.add(report)
            reports.append(report)
        session.commit()
        return reports

    def generate_recipients(self, count=1):
        session = self.db_session
        recipients = []
        for i in range(count):
            recipient = Recipient(
                role_purpose='optscale_manager',
                scope_id=str(uuid.uuid4()))
            session.add(recipient)
            recipients.append(recipient)
        session.commit()
        return recipients

    def generate_schedules(self, schedules_count):
        reports = self.generate_reports(schedules_count)
        recipients = self.generate_recipients(schedules_count)
        schedules = []
        for i in range(schedules_count):
            schedule = Schedule(
                crontab='*/5 * * * *',
                recipient_id=recipients[i].id,
                report_id=reports[i].id)
            self.db_session.add(schedule)
            schedules.append(schedule)
        self.db_session.commit()
        return schedules

    def generate_tasks(self, tasks_count):
        schedules = self.generate_schedules(tasks_count)
        tasks = []
        for i in range(tasks_count):
            task = Task(
                schedule_id=schedules[i].id)
            self.db_session.add(task)
            tasks.append(task)
        self.db_session.commit()
        return tasks
