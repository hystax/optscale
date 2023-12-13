import json
import uuid
from unittest.mock import patch

from katara.katara_service.models.models import TaskState
from katara.katara_service.tests.unittests.test_api_base import TestBase


PUT_TASK = "katara.katara_service.controllers.schedule." \
           "ScheduleController.put_tasks"


class TestTasktApi(TestBase):

    def test_task_get(self):
        tasks = self.generate_tasks(1)
        code, task = self.client.task_get(tasks[0].id)
        self.assertEqual(code, 200)
        self.assertEqual(tasks[0].id, task['id'])

    def test_task_get_expanded(self):
        tasks = self.generate_tasks(1)
        code, task = self.client.task_get(tasks[0].id, expanded=True)
        self.assertEqual(code, 200)
        self.assertEqual(tasks[0].id, task['id'])
        self.assertNotEqual(None, task['schedule'])

    def test_task_get_expanded_no_schedule(self):
        tasks = self.generate_tasks(1)
        code, _ = self.client.schedule_delete(tasks[0].schedule_id)
        self.assertEqual(code, 204)
        code, task = self.client.task_get(tasks[0].id, expanded=True)
        self.assertEqual(code, 200)
        self.assertEqual(tasks[0].id, task['id'])
        self.assertEqual(None, task['schedule'])

    def test_task_get_nonexisting(self):
        id_ = str(uuid.uuid4())
        code, _ = self.client.task_get(id_)
        self.assertEqual(code, 404)

    def test_task_update(self):
        tasks = self.generate_tasks(1)
        new_state = TaskState.error.value
        code, task = self.client.task_update(
            tasks[0].id, state=new_state)
        self.assertEqual(code, 200)
        self.assertEqual(new_state, task['state'])

        new_result = json.dumps(task)
        code, task = self.client.task_update(
            tasks[0].id, result=new_result)
        self.assertEqual(code, 200)
        self.assertEqual(new_result, task['result'])

    def test_task_update_completed(self):
        tasks = self.generate_tasks(1)
        new_state = TaskState.completed.value
        code, task = self.client.task_update(
            tasks[0].id, state=new_state)
        self.assertEqual(code, 200)
        self.assertEqual(new_state, task['state'])
        self.assertNotEqual(None, task['completed_at'])

    def test_task_update_wrong_result(self):
        tasks = self.generate_tasks(1)
        new_result = {
            "k1": "v1",
            "k2": "v2"
        }
        code, _ = self.client.task_update(
            tasks[0].id, result=new_result)
        self.assertEqual(code, 400)

    def test_task_update_restriction(self):
        tasks = self.generate_tasks(1)
        code, _ = self.client.task_update(
            tasks[0].id, schedule_id=str(uuid.uuid4()))
        self.assertEqual(code, 400)

    @patch(PUT_TASK)
    def test_task_create(self, p_put_tasks):
        schedules = self.generate_schedules(1)
        task_payload = {
            'schedule_id': schedules[0].id
        }
        code, _ = self.client.tasks_create([task_payload])
        self.assertEqual(code, 201)
        self.assertEqual(1, p_put_tasks.call_count)

    @patch(PUT_TASK)
    def test_task_create_several(self, p_put_tasks):
        schedules = self.generate_schedules(2)
        task_payload = [
            {
                'schedule_id': schedules[0].id
            },
            {
                'schedule_id': schedules[1].id
            }
        ]
        code, tasks = self.client.tasks_create(task_payload)
        self.assertEqual(code, 201)
        self.assertEqual(len(task_payload), len(tasks))
        self.assertEqual(1, p_put_tasks.call_count)

    @patch(PUT_TASK)
    def test_task_create_parent(self, p_put_tasks):
        schedules = self.generate_schedules(1)
        task_payload = {
            'schedule_id': schedules[0].id
        }
        code, tasks = self.client.tasks_create([task_payload])
        self.assertEqual(1, p_put_tasks.call_count)
        task_payload = {
            'schedule_id': schedules[0].id,
            'parent_id': tasks[0]['id']
        }
        code, tasks2 = self.client.tasks_create([task_payload])
        self.assertEqual(code, 201)
        self.assertEqual(2, p_put_tasks.call_count)
        self.assertEqual(tasks2[0]['parent_id'],
                         tasks[0]['id'])

    @patch(PUT_TASK)
    def test_task_create_nonexisting_parent(self, _p_put_tasks):
        schedules = self.generate_schedules(1)
        task_payload = {
            'schedule_id': schedules[0].id,
            'parent_id': str(uuid.uuid4())
        }
        code, _ = self.client.tasks_create([task_payload])
        self.assertEqual(code, 404)

    @patch(PUT_TASK)
    def test_task_create_nonexisting_schedule(self, p_put_tasks):
        task_payload = {
            'schedule_id': str(uuid.uuid4())
        }
        code, _ = self.client.tasks_create([task_payload])
        self.assertEqual(code, 404)
        self.assertEqual(0, p_put_tasks.call_count)

    @patch(PUT_TASK)
    def test_task_create_completed(self, _p_put_tasks):
        schedules = self.generate_schedules(1)
        task_payload = {
            'schedule_id': schedules[0].id,
            'state': 'completed'
        }
        code, _ = self.client.tasks_create([task_payload])
        self.assertEqual(code, 400)
