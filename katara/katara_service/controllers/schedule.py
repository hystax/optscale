import datetime
import logging
import croniter
from sqlalchemy import and_, exists
from sqlalchemy.exc import IntegrityError
from kombu import Connection as QConnection, Exchange
from kombu.pools import producers

from katara.katara_service.controllers.base import BaseController
from katara.katara_service.controllers.base_async import (
    BaseAsyncControllerWrapper
)
from katara.katara_service.exceptions import Err
from katara.katara_service.models.models import (
    Schedule, Task, Recipient, Report)

from tools.optscale_exceptions.common_exc import (
    NotFoundException,
    WrongArgumentsException,
    ConflictException
)


LOG = logging.getLogger(__name__)
BULK_SIZE = 2000
ROUTING_KEY = 'katara-task'
RETRY_POLICY = {'max_retries': 15, 'interval_start': 0,
                'interval_step': 1, 'interval_max': 3}


class ScheduleController(BaseController):
    def _get_model_type(self):
        return Schedule

    def put_tasks(self, tasks):
        params = self._config.read_branch('/rabbit')
        queue_conn = QConnection(f'amqp://{params["user"]}:{params["pass"]}@'
                                 f'{params["host"]}:{params["port"]}',
                                 transport_options=RETRY_POLICY)

        task_exchange = Exchange('katara-tasks', type='direct')
        with producers[queue_conn].acquire(block=True) as producer:
            for task in tasks:
                task_params = {
                    'task_id': task.id,
                    'last_update': int(
                        datetime.datetime.utcnow().timestamp()),
                    'tries_count': 0
                }
                producer.publish(
                    task_params,
                    serializer='json',
                    exchange=task_exchange,
                    declare=[task_exchange],
                    routing_key=ROUTING_KEY,
                    retry=True,
                    retry_policy=RETRY_POLICY
                )

    def generate_tasks(self):
        now = datetime.datetime.utcnow()
        schedules = self.session.query(
            Schedule.id, Schedule.crontab).filter(
            and_(
                Schedule.next_run <= int(now.timestamp()),
                Schedule.next_run != Schedule.last_run
            )
        ).all()
        schedules_count = len(schedules)
        LOG.info('Processing %s schedules', schedules_count)
        tasks = []
        schedules_updates = []
        try:
            for i, schedule in enumerate(schedules, start=1):
                task = Task(schedule_id=schedule[0])
                tasks.append(task)
                cron = croniter.croniter(schedule[1], now)
                next_run = cron.get_next(datetime.datetime)
                schedules_updates.append({
                    Schedule.id.name: schedule[0],
                    Schedule.next_run.name: int(next_run.timestamp())})
                if i % BULK_SIZE == 0 or i == schedules_count:
                    self.session.bulk_update_mappings(Schedule,
                                                      schedules_updates)
                    self.session.bulk_save_objects(tasks)
                    self.session.commit()
                    self.put_tasks(tasks)
                    tasks.clear()
                    schedules_updates.clear()
        except Exception as ex:
            LOG.exception("Tasks generation failed: %s", str(ex))
            raise
        finally:
            self.session.close()

    @staticmethod
    def _check_crontab(crontab):
        try:
            croniter.croniter(crontab, datetime.datetime.utcnow())
        except ValueError:
            raise WrongArgumentsException(Err.OKA0006, [crontab])

    def _validate(self, schedule, is_new=True, **kwargs):
        if is_new:
            for model, fk_key in [(Recipient, 'recipient_id'),
                                  (Report, 'report_id')]:
                fk_id = kwargs.get(fk_key)
                query = self.session.query(exists().where(
                    model.id == fk_id))
                object_exists = query.scalar()
                if not object_exists:
                    raise NotFoundException(
                        Err.OKA0004, [model.__name__.capitalize(), fk_id])
        query = self.session.query(exists().where(
            and_(*(schedule.get_uniqueness_filter(is_new)))))
        schedule_exist = query.scalar()
        if schedule_exist:
            raise ConflictException(
                Err.OKA0005,
                [schedule.report_id, schedule.recipient_id,
                 schedule.crontab])

        if kwargs.get('crontab'):
            self._check_crontab(schedule.crontab)

    def create(self, **kwargs):
        self.check_create_restrictions(**kwargs)
        self._check_crontab(kwargs.get('crontab'))
        model_type = self._get_model_type()
        item = model_type(**kwargs)
        self._validate(item, is_new=True, **kwargs)
        LOG.info("Creating %s with parameters %s", model_type.__name__,
                 kwargs)

        self.session.add(item)
        try:
            self.session.commit()
        except IntegrityError as ex:
            raise WrongArgumentsException(Err.OKA0017, [str(ex)])
        return item


class ScheduleAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return ScheduleController
