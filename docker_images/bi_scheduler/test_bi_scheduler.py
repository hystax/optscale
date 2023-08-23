import uuid
import unittest

from optscale_client.config_client.client import Client as ConfigClient
from unittest.mock import MagicMock, PropertyMock, patch

from docker_images.bi_scheduler.scheduler import BIScheduler, DEFAULT_RUN_PERIOD, TASK_WAIT_TIMEOUT


class TestBIScheduler(unittest.TestCase):
    def setUp(self) -> None:
        self.config_cl = ConfigClient()
        self.config_cl.cluster_secret = MagicMock(return_value="secret")
        self.config_cl.bi_settings = MagicMock(return_value={
            'task_wait_timeout': TASK_WAIT_TIMEOUT,
            'exporter_run_period': DEFAULT_RUN_PERIOD
        })

        self.scheduler = BIScheduler(self.config_cl)
        patch('docker_images.bi_scheduler.scheduler.BIScheduler.rest_cl',
              new_callable=PropertyMock).start()
        self.scheduler.rest_cl.bi_list = MagicMock(
            return_value=(200, {'organization_bis': []}))
        self.scheduler._publish_tasks = MagicMock()
        self.next_run = int(self.scheduler.now.timestamp()) + DEFAULT_RUN_PERIOD

    def test_run_no_bis(self):
        self.scheduler.rest_cl.bi_list = MagicMock(
            return_value=(200, {'organization_bis': []}))
        self.scheduler.run()
        self.scheduler._publish_tasks.assert_called_once_with(
            [], self.next_run)

    def test_run(self):
        id_ = str(uuid.uuid4())
        for state in ['ACTIVE', 'SUCCESS', 'FAILED']:
            self.scheduler.rest_cl.bi_list = MagicMock(
                return_value=(200, {
                    'organization_bis': [{
                        "next_run": 1,
                        "status": state,
                        "id": id_
                    }]}))
            self.scheduler.run()
            self.scheduler._publish_tasks.assert_called_once_with(
                [id_], self.next_run)
            self.scheduler._publish_tasks.reset_mock()

    def test_recreate_hanging_task(self):
        id_ = str(uuid.uuid4())
        for state in ['RUNNING', 'QUEUED']:
            next_run = int(self.scheduler.now.timestamp()) - TASK_WAIT_TIMEOUT
            # task hangs in processing
            self.scheduler.rest_cl.bi_list = MagicMock(
                return_value=(200, {
                    'organization_bis': [{
                        "next_run": next_run,
                        "status": state,
                        "id": id_
                    }]}))
            self.scheduler.run()
            self.scheduler._publish_tasks.assert_called_once_with(
                [id_], self.next_run)
            self.scheduler._publish_tasks.reset_mock()

    def test_not_recreate_running_task(self):
        id_ = str(uuid.uuid4())
        for state in ['RUNNING', 'QUEUED']:
            next_run = int(self.scheduler.now.timestamp()) - TASK_WAIT_TIMEOUT + 10
            self.scheduler.rest_cl.bi_list = MagicMock(
                return_value=(200, {
                    'organization_bis': [{
                        "next_run": next_run,
                        "status": state,
                        "id": id_
                    }]}))
            self.scheduler.run()
            self.scheduler._publish_tasks.assert_called_once_with(
                [], self.next_run)
            self.scheduler._publish_tasks.reset_mock()

    def test_future_next_run(self):
        id_ = str(uuid.uuid4())
        for state in ['ACTIVE', 'SUCCESS', 'FAILED', 'RUNNING', 'QUEUED']:
            self.scheduler.rest_cl.bi_list = MagicMock(
                return_value=(200, {
                    'organization_bis': [{
                        "next_run": int(self.scheduler.now.timestamp()) + 100,
                        "status": state,
                        "id": id_
                    }]}))
            self.scheduler.run()
            self.scheduler._publish_tasks.assert_called_once_with(
                [], self.next_run)
            self.scheduler._publish_tasks.reset_mock()

    def test_several_bis(self):
        id_1 = str(uuid.uuid4())
        id_2 = str(uuid.uuid4())
        self.scheduler.rest_cl.bi_list = MagicMock(
            return_value=(200, {
                'organization_bis': [{
                    "next_run": 0,
                    "status": "ACTIVE",
                    "id": id_1
                }, {
                    "next_run": 0,
                    "status": "FAILED",
                    "id": id_2
                }
                ]}))
        self.scheduler.run()
        self.scheduler._publish_tasks.assert_called_once_with(
            [id_1, id_2], self.next_run)


if __name__ == '__main__':
    unittest.main()
