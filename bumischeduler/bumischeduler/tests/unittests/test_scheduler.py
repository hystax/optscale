import unittest

from datetime import datetime
from unittest.mock import patch, call, MagicMock

from bumischeduler.bumischeduler.controllers.schedule import (
    ScheduleController, RESCHEDULE_TIMEOUT)

GET_CHECKLISTS = ("bumischeduler.bumischeduler.controllers.schedule."
                  "ScheduleController.get_checklists")
CREATE_TASKS = ("bumischeduler.bumischeduler.controllers.schedule."
                "ScheduleController.create_tasks")


class TestScheduler(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.max_retries = 5
        self.task_timeout = 3600
        self.wait_timeout = 7200
        self.run_period = 10800
        patch('bumischeduler.bumischeduler.controllers.schedule.'
              'RestClient.checklist_update',
              lambda *args: (200, {'OK'})).start()
        patch('bumischeduler.bumischeduler.controllers.schedule.'
              'ScheduleController.get_bumi_worker_params',
              return_value={
                  'max_retries': str(self.max_retries),
                  'task_timeout': str(self.task_timeout),
                  'wait_timeout': str(self.wait_timeout),
                  'run_period': str(self.run_period)
              }).start()

    @patch(GET_CHECKLISTS)
    @patch(CREATE_TASKS)
    def test_no_schedules(self, p_create_tasks, p_get_checklists):
        p_get_checklists.return_value = []
        controller = ScheduleController()
        controller.generate_tasks()
        p_create_tasks.assert_has_calls([call([])])

    @patch(GET_CHECKLISTS)
    @patch(CREATE_TASKS)
    def test_initial(self, p_create_tasks, p_get_checklists):
        now = datetime.utcnow()
        checklist = {
            'id': 'aabe9d07-2eca-42de-9d2d-ad3984c4fb0f',
            'last_run': 0,
            'next_run': int(now.timestamp()) - 10,
            'last_completed': 0,
            'organization_id': 'e9ce024e-588c-4ce9-9147-b894111738e9'
        }
        p_get_checklists.return_value = [checklist]
        task = {
            'last_update': int(now.timestamp()),
            'tries_count': 0,
            'organization_id': checklist['organization_id'],
            'checklist_id': checklist['id'],
            'created_at': int(now.timestamp()),
            'state': 'created',
            'task_timeout': self.task_timeout,
            'wait_timeout': self.wait_timeout,
            'max_retries': self.max_retries
        }
        controller = ScheduleController(config=MagicMock())
        controller.generate_tasks()
        p_create_tasks.assert_has_calls([call([task])])

    @patch(GET_CHECKLISTS)
    @patch(CREATE_TASKS)
    def test_completed(self, p_create_tasks, p_get_checklists):
        now = datetime.utcnow()
        checklist = {
            'id': 'aabe9d07-2eca-42de-9d2d-ad3984c4fb0f',
            'last_run': int(now.timestamp()) - 10,
            'next_run': int(now.timestamp()) + 10,
            'last_completed': int(now.timestamp()) - 10,
            'organization_id': 'e9ce024e-588c-4ce9-9147-b894111738e9',
        }
        p_get_checklists.return_value = [checklist]
        controller = ScheduleController(config=MagicMock())
        controller.generate_tasks()
        p_create_tasks.assert_has_calls([call([])])

    @patch(GET_CHECKLISTS)
    @patch(CREATE_TASKS)
    def test_in_progress(self, p_create_tasks, p_get_checklists):
        now = datetime.utcnow()
        checklist = {
            'id': 'aabe9d07-2eca-42de-9d2d-ad3984c4fb0f',
            'last_run': int(now.timestamp()) - 10,
            'next_run': int(now.timestamp()),
            'last_completed': int(now.timestamp()) - 20,
            'organization_id': 'e9ce024e-588c-4ce9-9147-b894111738e9'
        }
        p_get_checklists.return_value = [checklist]
        controller = ScheduleController(config=MagicMock())
        controller.generate_tasks()
        p_create_tasks.assert_has_calls([call([])])

    @patch(GET_CHECKLISTS)
    @patch(CREATE_TASKS)
    def test_reschedule(self, p_create_tasks, p_get_checklists):
        now = datetime.utcnow()
        checklist = {
            'id': 'aabe9d07-2eca-42de-9d2d-ad3984c4fb0f',
            'last_run': int(now.timestamp()) - RESCHEDULE_TIMEOUT,
            'next_run': int(now.timestamp()),
            'last_completed': int(now.timestamp()) - RESCHEDULE_TIMEOUT - 10,
            'organization_id': 'e9ce024e-588c-4ce9-9147-b894111738e9'
        }
        p_get_checklists.return_value = [checklist]
        task = {
            'last_update': int(now.timestamp()),
            'tries_count': 0,
            'organization_id': checklist['organization_id'],
            'checklist_id': checklist['id'],
            'created_at': int(now.timestamp()),
            'state': 'created',
            'task_timeout': self.task_timeout,
            'wait_timeout': self.wait_timeout,
            'max_retries': self.max_retries
        }
        controller = ScheduleController(config=MagicMock())
        controller.generate_tasks()
        p_create_tasks.assert_has_calls([call([task])])
