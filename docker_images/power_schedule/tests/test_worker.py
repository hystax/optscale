import uuid
import unittest
import pytz
from datetime import datetime, timedelta
from freezegun import freeze_time
from mongomock import MongoClient
from unittest.mock import MagicMock, PropertyMock, patch
from optscale_client.config_client.client import Client as ConfigClient
from docker_images.power_schedule.worker import (
    PowerScheduleWorker, PowerScheduleReasons)


class TestPSWorker(unittest.TestCase):
    def setUp(self) -> None:
        self.config_cl = ConfigClient()
        self.config_cl.cluster_secret = MagicMock(return_value="secret")
        self.worker = PowerScheduleWorker(None, self.config_cl)
        patch('docker_images.power_schedule.'
              'worker.PowerScheduleWorker.rest_cl',
              new_callable=PropertyMock).start()
        self.worker.rest_cl.cloud_account_get = MagicMock(
            return_value=(200, {
                'id': str(uuid.uuid4()),
                'type': 'aws_cnr',
                'config': {}
            }))
        self.ps_id = str(uuid.uuid4())
        self.valid_ps = {
            'id': self.ps_id,
            'enabled': True,
            'start_date': 0,
            'end_date': int((datetime.now() + timedelta(days=10)).timestamp()),
            'power_on': '22:00',
            'power_off': '11:00',
            'timezone': 'Asia/Yerevan',
            'last_eval': 0,
            'last_run': 0,
            'last_run_error': None
        }
        self.worker.rest_cl.power_schedule_get = MagicMock(
            return_value=(200, self.valid_ps))
        self.worker.rest_cl.power_schedule_update = MagicMock(
            return_value=(200, {}))
        self.mongo_cl = MongoClient()
        self.worker.mongo_cl = self.mongo_cl
        patch('docker_images.power_schedule.'
              'worker.PowerScheduleWorker._cloud_action').start()
        self.message = MagicMock()
        self.default_result = {
            'start_instance': 0,
            'stop_instance': 0,
            'error': 0,
            'excluded': 0,
            'reason': None
        }

    def test_outdated_schedule(self):
        ps = self.valid_ps.copy()
        ps['start_date'] = 0
        ps['end_date'] = 1
        self.worker.rest_cl.power_schedule_get = MagicMock(
            return_value=(200, ps))

        self.worker.process_task(
            body={'power_schedule_id': self.ps_id},
            message=self.message)
        result = self.default_result.copy()
        result['reason'] = PowerScheduleReasons.OUTDATED
        self.assertEqual(result, self.worker.result)
        self.worker.rest_cl.power_schedule_update.assert_called_once()
        self.assertIn(
            'last_eval',
            self.worker.rest_cl.power_schedule_update.call_args[0][1])
        self.assertNotIn(
            'last_run',
            self.worker.rest_cl.power_schedule_update.call_args[0][1])
        self.assertNotIn(
            'last_run_error',
            self.worker.rest_cl.power_schedule_update.call_args[0][1])

    def test_schedule_with_zero_end_date(self):
        ps = self.valid_ps.copy()
        ps['start_date'] = 1
        ps['end_date'] = 0
        ps['power_on'] = '04:00'
        ps['power_off'] = '02:00'
        self.worker.rest_cl.power_schedule_get = MagicMock(
            return_value=(200, ps))
        ps_tz = pytz.timezone(ps['timezone'])
        now = datetime.now(ps_tz).replace(
            hour=3, minute=0, second=0, microsecond=0)
        with freeze_time(now):
            self.worker.process_task(
                body={'power_schedule_id': self.ps_id},
                message=self.message)
        result = self.default_result.copy()
        result['reason'] = PowerScheduleReasons.NO_RESOURCES
        self.assertEqual(result, self.worker.result)
        self.worker.rest_cl.power_schedule_update.assert_called_once()
        self.assertIn(
            'last_eval',
            self.worker.rest_cl.power_schedule_update.call_args[0][1])
        self.assertIn(
            'last_run',
            self.worker.rest_cl.power_schedule_update.call_args[0][1])
        self.assertEqual(
            self.worker.rest_cl.power_schedule_update.call_args[0][1][
                'last_run_error'], None)
        self.worker.rest_cl.power_schedule_update.reset_mock()

    def test_disabled_schedule(self):
        ps = self.valid_ps.copy()
        ps['enabled'] = False
        self.worker.rest_cl.power_schedule_get = MagicMock(
            return_value=(200, ps))

        self.worker.process_task(
            body={'power_schedule_id': self.ps_id},
            message=self.message)
        result = self.default_result.copy()
        result['reason'] = PowerScheduleReasons.DISABLED
        self.assertEqual(result, self.worker.result)
        self.worker.rest_cl.power_schedule_update.assert_called_once()
        self.assertIn(
            'last_eval',
            self.worker.rest_cl.power_schedule_update.call_args[0][1])
        self.assertNotIn(
            'last_run',
            self.worker.rest_cl.power_schedule_update.call_args[0][1])
        self.assertNotIn(
            'last_run_error',
            self.worker.rest_cl.power_schedule_update.call_args[0][1])

    def test_excluded_resources(self):
        # not active instance
        self.mongo_cl.restapi.resources.insert_one({
            '_id': str(uuid.uuid4()),
            'cloud_resource_id': 'cloud_resource_id',
            'power_schedule': self.ps_id,
            'resource_type': 'Instance'
        })
        ps = self.valid_ps.copy()
        ps_tz = pytz.timezone(ps['timezone'])
        now = datetime.now(ps_tz).replace(
            hour=3, minute=0, second=0, microsecond=0)
        ps['power_on'] = '04:00'
        ps['power_off'] = '02:00'
        self.worker.rest_cl.power_schedule_get = MagicMock(
            return_value=(200, ps))

        with freeze_time(now):
            self.worker.process_task(
                body={'power_schedule_id': self.ps_id},
                message=self.message)

        result = self.default_result.copy()
        result['excluded'] = 1
        self.assertEqual(result, self.worker.result)
        self.worker.rest_cl.power_schedule_update.assert_called_once()
        self.assertIn(
            'last_eval',
            self.worker.rest_cl.power_schedule_update.call_args[0][1])
        self.assertIn(
            'last_run',
            self.worker.rest_cl.power_schedule_update.call_args[0][1])
        self.assertEqual(
            self.worker.rest_cl.power_schedule_update.call_args[0][1][
                'last_run_error'], None)
        resources = list(self.mongo_cl.restapi.resources.find())
        for resource in resources:
            self.assertNotIn('power_schedule', resource)

    def test_stop_instance(self):
        self.mongo_cl.restapi.resources.insert_one({
            '_id': str(uuid.uuid4()),
            'cloud_resource_id': 'cloud_resource_id',
            'power_schedule': self.ps_id,
            'active': True,
            'resource_type': 'Instance'
        })
        self.mongo_cl.restapi.resources.insert_one({
            '_id': str(uuid.uuid4()),
            'cloud_resource_id': 'cloud_resource_id',
            'power_schedule': self.ps_id,
            'active': True,
            'resource_type': 'Instance'
        })
        # (last_eval, now, power_on, power_off)
        cases = [
            (1, 3, 4, 2),
            (1, 4, 2, 3),
            (2, 4, 1, 3),
        ]
        ps = self.valid_ps.copy()
        ps_tz = pytz.timezone(ps['timezone'])
        base_date = datetime.now(ps_tz).replace(
            hour=0, minute=0, second=0, microsecond=0)
        for case in cases:
            last_eval_h, now_h, power_on_h, power_off_h = case
            last_eval = int(base_date.replace(hour=last_eval_h).astimezone(
                pytz.utc).timestamp())
            ps['last_eval'] = last_eval
            now = base_date.replace(hour=now_h)
            power_on = '%s:00' % power_on_h
            power_off = '%s:00' % power_off_h
            ps['power_on'] = power_on
            ps['power_off'] = power_off
            self.worker.rest_cl.power_schedule_get = MagicMock(
                return_value=(200, ps))

            with freeze_time(now):
                self.worker.process_task(
                    body={'power_schedule_id': self.ps_id},
                    message=self.message)

            result = self.default_result.copy()
            result['stop_instance'] = 2
            self.assertEqual(result, self.worker.result)
            self.worker.rest_cl.power_schedule_update.assert_called_once()
            self.assertIn(
                'last_eval',
                self.worker.rest_cl.power_schedule_update.call_args[0][1])
            self.assertIn(
                'last_run',
                self.worker.rest_cl.power_schedule_update.call_args[0][1])
            self.assertEqual(
                self.worker.rest_cl.power_schedule_update.call_args[0][1][
                    'last_run_error'], None)
            self.worker.rest_cl.power_schedule_update.reset_mock()

    def test_start_instance(self):
        self.mongo_cl.restapi.resources.insert_one({
            '_id': str(uuid.uuid4()),
            'cloud_resource_id': 'cloud_resource_id',
            'power_schedule': self.ps_id,
            'active': True,
            'resource_type': 'Instance'
        })
        # (last_run, now, power_on, power_off)
        cases = [
            (1, 3, 2, 4),
            (1, 4, 3, 2),
            (2, 4, 3, 1),
        ]
        ps = self.valid_ps.copy()
        ps_tz = pytz.timezone(ps['timezone'])
        base_date = datetime.now(ps_tz).replace(
            hour=0, minute=0, second=0, microsecond=0)
        for case in cases:
            last_run_h, now_h, power_on_h, power_off_h = case
            last_run = int(base_date.replace(hour=last_run_h).astimezone(
                pytz.utc).timestamp())
            ps['last_run'] = last_run
            now = base_date.replace(hour=now_h)
            power_on = '%s:00' % power_on_h
            power_off = '%s:00' % power_off_h
            ps['power_on'] = power_on
            ps['power_off'] = power_off
            self.worker.rest_cl.power_schedule_get = MagicMock(
                return_value=(200, ps))

            with freeze_time(now):
                self.worker.process_task(
                    body={'power_schedule_id': self.ps_id},
                    message=self.message)

            result = self.default_result.copy()
            result['start_instance'] = 1
            self.assertEqual(result, self.worker.result)
            self.worker.rest_cl.power_schedule_update.assert_called_once()
            self.assertIn(
                'last_eval',
                self.worker.rest_cl.power_schedule_update.call_args[0][1])
            self.assertIn(
                'last_run',
                self.worker.rest_cl.power_schedule_update.call_args[0][1])
            self.assertEqual(
                self.worker.rest_cl.power_schedule_update.call_args[0][1][
                    'last_run_error'], None)
            self.worker.rest_cl.power_schedule_update.reset_mock()

    def test_no_changes(self):
        self.mongo_cl.restapi.resources.insert_one({
            '_id': str(uuid.uuid4()),
            'cloud_resource_id': 'cloud_resource_id',
            'power_schedule': self.ps_id,
            'active': True,
            'resource_type': 'Instance'
        })
        # (last_run, now, power_on, power_off)
        cases = [
            (1, 2, 3, 4),
            (1, 2, 4, 3),
            (2, 3, 4, 1),
            (2, 3, 1, 4),
            (3, 4, 1, 2),
            (3, 4, 2, 1),
        ]
        ps = self.valid_ps.copy()
        ps_tz = pytz.timezone(ps['timezone'])
        base_date = datetime.now(ps_tz).replace(
            hour=0, minute=0, second=0, microsecond=0)
        for case in cases:
            last_eval_h, now_h, power_on_h, power_off_h = case
            last_eval = int(base_date.replace(hour=last_eval_h).astimezone(
                pytz.utc).timestamp())
            ps['last_eval'] = last_eval
            now = base_date.replace(hour=now_h)
            power_on = '%s:00' % power_on_h
            power_off = '%s:00' % power_off_h
            ps['power_on'] = power_on
            ps['power_off'] = power_off
            self.worker.rest_cl.power_schedule_get = MagicMock(
                return_value=(200, ps))

            with freeze_time(now):
                self.worker.process_task(
                    body={'power_schedule_id': self.ps_id},
                    message=self.message)

            result = self.default_result.copy()
            result['reason'] = PowerScheduleReasons.NO_CHANGES
            self.assertEqual(result, self.worker.result)
            self.worker.rest_cl.power_schedule_update.assert_called_once()
            self.assertIn(
                'last_eval',
                self.worker.rest_cl.power_schedule_update.call_args[0][1])
            self.assertNotIn(
                'last_run',
                self.worker.rest_cl.power_schedule_update.call_args[0][1])
            self.assertNotIn(
                'last_run_error',
                self.worker.rest_cl.power_schedule_update.call_args[0][1])
            self.worker.rest_cl.power_schedule_update.reset_mock()

    def test_no_resources(self):
        ps = self.valid_ps.copy()
        ps_tz = pytz.timezone(ps['timezone'])
        now = datetime.now(ps_tz).replace(
            hour=3, minute=0, second=0, microsecond=0)
        ps['power_on'] = '04:00'
        ps['power_off'] = '02:00'
        self.worker.rest_cl.power_schedule_get = MagicMock(
            return_value=(200, ps))

        with freeze_time(now):
            self.worker.process_task(
                body={'power_schedule_id': self.ps_id},
                message=self.message)

        result = self.default_result.copy()
        result['reason'] = PowerScheduleReasons.NO_RESOURCES
        self.assertEqual(result, self.worker.result)
        self.worker.rest_cl.power_schedule_update.assert_called_once()
        self.assertIn(
            'last_eval',
            self.worker.rest_cl.power_schedule_update.call_args[0][1])
        self.assertIn(
            'last_run',
            self.worker.rest_cl.power_schedule_update.call_args[0][1])
        self.assertIn(
            'last_run_error',
            self.worker.rest_cl.power_schedule_update.call_args[0][1])

    def test_cloud_error(self):
        def raise_exc(*args):
            raise Exception('error')

        patch('docker_images.power_schedule.'
              'worker.PowerScheduleWorker._cloud_action',
              side_effect=raise_exc).start()
        self.mongo_cl.restapi.resources.insert_one({
            '_id': str(uuid.uuid4()),
            'cloud_resource_id': 'cloud_resource_id',
            'power_schedule': self.ps_id,
            'resource_type': 'Instance',
            'active': True,
        })
        ps = self.valid_ps.copy()
        ps_tz = pytz.timezone(ps['timezone'])
        now = datetime.now(ps_tz).replace(
            hour=3, minute=0, second=0, microsecond=0)
        ps['power_on'] = '04:00'
        ps['power_off'] = '02:00'
        self.worker.rest_cl.power_schedule_get = MagicMock(
            return_value=(200, ps))

        with freeze_time(now):
            self.worker.process_task(
                body={'power_schedule_id': self.ps_id},
                message=self.message)

        result = self.default_result.copy()
        result['error'] = 1
        result['reason'] = 'error'
        self.assertEqual(result, self.worker.result)
        self.worker.rest_cl.power_schedule_update.assert_called_once()
        self.assertIn(
            'last_eval',
            self.worker.rest_cl.power_schedule_update.call_args[0][1])
        self.assertIn(
            'last_run',
            self.worker.rest_cl.power_schedule_update.call_args[0][1])
        self.assertIn(
            'last_run_error',
            self.worker.rest_cl.power_schedule_update.call_args[0][1])

        # error reset on successful run
        patch('docker_images.power_schedule.'
              'worker.PowerScheduleWorker._cloud_action').start()
        self.worker.rest_cl.power_schedule_update.reset_mock()
        with freeze_time(now):
            self.worker.process_task(
                body={'power_schedule_id': self.ps_id},
                message=self.message)
        result = self.default_result.copy()
        result['stop_instance'] = 1
        self.assertEqual(result, self.worker.result)
        self.worker.rest_cl.power_schedule_update.assert_called_once()
        self.assertIn(
            'last_eval',
            self.worker.rest_cl.power_schedule_update.call_args[0][1])
        self.assertIn(
            'last_run',
            self.worker.rest_cl.power_schedule_update.call_args[0][1])
        self.assertEqual(
            self.worker.rest_cl.power_schedule_update.call_args[0][1][
                'last_run_error'], None)


if __name__ == '__main__':
    unittest.main()
