import uuid
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, PropertyMock, patch
from optscale_client.config_client.client import Client as ConfigClient
from docker_images.power_schedule.scheduler import PowerScheduler


class TestPSScheduler(unittest.TestCase):
    def setUp(self) -> None:
        self.config_cl = ConfigClient()
        self.config_cl.cluster_secret = MagicMock(return_value="secret")

        self.scheduler = PowerScheduler(self.config_cl)
        patch('docker_images.power_schedule.'
              'scheduler.PowerScheduler.rest_cl',
              new_callable=PropertyMock).start()
        self.scheduler.rest_cl.organization_list = MagicMock(
            return_value=(200, {'organizations': []}))
        self.scheduler.rest_cl.power_schedule_list = MagicMock(
            return_value=(200, {'power_schedules': []}))
        self.scheduler.publish_tasks = MagicMock()

    def test_no_orgs(self):
        self.scheduler.run()
        self.scheduler.rest_cl.power_schedule_list.assert_not_called()
        self.scheduler.publish_tasks.assert_not_called()

    def test_run_no_ps(self):
        self.scheduler.rest_cl.organization_list = MagicMock(
            return_value=(
                200, {'organizations': [{"id": "org_id"}]}))
        self.scheduler.run()
        self.scheduler.publish_tasks.assert_not_called()

    def test_several_ps(self):
        id_1 = str(uuid.uuid4())
        id_2 = str(uuid.uuid4())
        self.scheduler.rest_cl.organization_list = MagicMock(
            return_value=(
                200, {'organizations': [{"id": "org_id"}]}))
        self.scheduler.rest_cl.power_schedule_list = MagicMock(
            return_value=(200, {
                'power_schedules': [
                    {
                        'id': id_1,
                        'enabled': True,
                        'timezone': 'Europe/Vienna',
                        'start_date': 0,
                        'end_date': int(
                            (datetime.now() + timedelta(days=10)).timestamp())
                    },
                    {
                        "id": id_2,
                        'enabled': True,
                        'timezone': 'Europe/Vienna',
                        'start_date': 0,
                        'end_date': int(
                            (datetime.now() + timedelta(days=10)).timestamp())
                    }]}))
        self.scheduler.run()
        self.scheduler.publish_tasks.assert_called_once_with({id_1, id_2})

    def test_disabled(self):
        self.scheduler.rest_cl.organization_list = MagicMock(
            return_value=(
                200, {'organizations': [{"id": "org_id"}]}))
        self.scheduler.rest_cl.power_schedule_list = MagicMock(
            return_value=(200, {
                'power_schedules': [
                    {
                        'id': str(uuid.uuid4()),
                        'enabled': False,
                        'timezone': 'Europe/Vienna',
                        'start_date': 0,
                        'end_date': int(
                            (datetime.now() + timedelta(days=10)).timestamp())
                    }]}))
        self.scheduler.run()
        self.scheduler.publish_tasks.assert_not_called()

    def test_start_date(self):
        self.scheduler.rest_cl.organization_list = MagicMock(
            return_value=(
                200, {'organizations': [{"id": "org_id"}]}))
        self.scheduler.rest_cl.power_schedule_list = MagicMock(
            return_value=(200, {
                'power_schedules': [
                    {
                        'id': str(uuid.uuid4()),
                        'enabled': False,
                        'timezone': 'Europe/Vienna',
                        'start_date': int(
                            (datetime.now() + timedelta(days=10)).timestamp()),
                        'end_date': int(
                            (datetime.now() + timedelta(days=12)).timestamp())
                    }]}))
        self.scheduler.run()
        self.scheduler.publish_tasks.assert_not_called()

    def test_end_date(self):
        self.scheduler.rest_cl.organization_list = MagicMock(
            return_value=(
                200, {'organizations': [{"id": "org_id"}]}))
        self.scheduler.rest_cl.power_schedule_list = MagicMock(
            return_value=(200, {
                'power_schedules': [
                    {
                        'id': str(uuid.uuid4()),
                        'enabled': False,
                        'timezone': 'Europe/Vienna',
                        'start_date': 0,
                        'end_date': int(
                            (datetime.now() - timedelta(days=5)).timestamp())
                    }]}))
        self.scheduler.run()
        self.scheduler.publish_tasks.assert_not_called()

    def test_zero_end_date(self):
        self.scheduler.rest_cl.organization_list = MagicMock(
            return_value=(
                200, {'organizations': [{"id": "org_id"}]}))
        ps_id = str(uuid.uuid4())
        self.scheduler.rest_cl.power_schedule_list = MagicMock(
            return_value=(200, {
                'power_schedules': [
                    {
                        'id': ps_id,
                        'enabled': True,
                        'timezone': 'Europe/Vienna',
                        'start_date': 1,
                        'end_date': 0
                    }]}))
        self.scheduler.run()
        self.scheduler.publish_tasks.assert_called_once_with({ps_id})


if __name__ == '__main__':
    unittest.main()
