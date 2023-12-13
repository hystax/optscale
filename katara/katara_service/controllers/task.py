from datetime import datetime
import json
import logging

from sqlalchemy import exists
from sqlalchemy.exc import IntegrityError

from katara.katara_service.controllers.base import BaseController
from katara.katara_service.controllers.base_async import (
    BaseAsyncControllerWrapper
)
from katara.katara_service.controllers.schedule import ScheduleController
from katara.katara_service.exceptions import Err
from katara.katara_service.models.models import (
    Task,
    Schedule,
    TaskState
)

from tools.optscale_exceptions.common_exc import (
    WrongArgumentsException,
    NotFoundException
)


LOG = logging.getLogger(__name__)


class TaskController(BaseController):
    def _get_model_type(self):
        return Task

    def delete(self, item_id):
        # no tasks deletion
        raise NotImplementedError

    def create(self, tasks_payload):
        tasks = []
        for task_payload in tasks_payload:
            self.check_create_restrictions(**task_payload)
            item = Task(**task_payload)
            self._validate(item, is_new=True, **task_payload)
            LOG.info("Creating %s with parameters %s", Task.__name__,
                     task_payload)
            tasks.append(item)
        try:
            self.session.bulk_save_objects(tasks)
            self.session.commit()
        except IntegrityError as ex:
            raise WrongArgumentsException(Err.OKA0017, [str(ex)])
        sched_ctl = ScheduleController(
            config=self._config, db_session=self.session)
        sched_ctl.put_tasks(tasks)
        return tasks

    def _check_parent_exists(self, parent_id):
        query = self.session.query(exists().where(
            Task.id == parent_id))
        object_exists = query.scalar()
        if not object_exists:
            raise NotFoundException(
                Err.OKA0004,
                [Task.__name__.capitalize(), parent_id])

    def _validate(self, task, is_new=True, **kwargs):
        if kwargs.get('schedule_id'):
            query = self.session.query(exists().where(
                Schedule.id == task.schedule_id))
            object_exists = query.scalar()
            if not object_exists:
                raise NotFoundException(
                    Err.OKA0004,
                    [Schedule.__name__.capitalize(), task.schedule_id])
        if kwargs.get('parent_id'):
            self._check_parent_exists(task.parent_id)
        if kwargs.get('result'):
            try:
                json.loads(task.result)
            except (TypeError, ValueError, json.decoder.JSONDecodeError):
                raise WrongArgumentsException(Err.OKA0018, [])
        if is_new and kwargs.get('state') == TaskState.completed.value:
            raise WrongArgumentsException(
                Err.OKA0022, [TaskState.completed.value])

    def edit(self, item_id, **kwargs):
        self.check_update_restrictions(**kwargs)
        try:
            task = self.get(item_id)
            if kwargs:
                self.session.expunge(task)
                for key, value in kwargs.items():
                    setattr(task, key, value)
                self._validate(task, is_new=False, **kwargs)
                if task.state == TaskState.completed.value:
                    now = int(datetime.utcnow().timestamp())
                    task.completed_at = now
                    self.session.add(task)
                    # child obj changes are possible only if obj in session
                    task.schedule.last_run = now
                self.session.add(task)
                self.session.commit()
        except IntegrityError as ex:
            self.session.rollback()
            raise WrongArgumentsException(Err.OKA0017, [str(ex)])
        return task


class TaskAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return TaskController
