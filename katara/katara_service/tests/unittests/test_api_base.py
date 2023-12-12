import uuid
from unittest.mock import patch

import tornado.testing

from optscale_client.katara_client.client import (
    FetchMethodHttpProvider,
    Client as KataraClient
)

from katara.katara_service.models.models import (
    Recipient, Report, ReportFormat, Schedule, Task
)
from katara.katara_service.main import make_app, Roles
from katara.katara_service.models.db_factory import DBType, DBFactory
from katara.katara_service.models.db_base import BaseDB
from katara.katara_service.utils import gen_id


class TestBase(tornado.testing.AsyncHTTPTestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._db_session = None

    def get_app(self):
        return make_app(DBType.TEST, Roles.api, '127.0.0.1', 80)

    @property
    def db_session(self):
        db = DBFactory(DBType.TEST, None).db
        engine = db.engine
        if not self._db_session:
            self._db_session = BaseDB.session(engine)()
        return self._db_session

    def setUp(self):
        super().setUp()
        secret = gen_id()
        patch('optscale_client.config_client.client.Client.cluster_secret',
              return_value=secret).start()
        http_provider = FetchMethodHttpProvider(self.fetch, rethrow=False)
        self.client = KataraClient(http_provider=http_provider)
        self.client.secret = secret

    def tearDown(self):
        DBFactory.clean_type(DBType.TEST)
        super().tearDown()

    def generate_reports(self, count=1):
        session = self.db_session
        reports = []
        for i in range(count):
            report = Report(module_name=f'module_{i}',
                            name=f'report_{i}',
                            report_format=ReportFormat.html)
            session.add(report)
            reports.append(report)
        session.commit()
        return reports

    def generate_recipients(self, count=1):
        session = self.db_session
        recipients = []
        for _ in range(count):
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
