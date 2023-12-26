import uuid
from datetime import datetime, timedelta
from freezegun import freeze_time
from unittest.mock import patch, ANY, call

from rest_api.google_calendar_client.client import CalendarException
from tools.optscale_exceptions.http_exc import OptHTTPError
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.tests.unittests.test_api_base import TestApiBase


class TestCalendarSynchronizationsApi(TestApiBase):
    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.org = self.client.organization_create({'name': 'organization'})
        self.org_id = self.org['id']
        self.pool_id = self.org['pool_id']

        auth_user = self.gen_id()
        code, self.employee = self.client.employee_create(
            self.org['id'], {'name': 'employee_1',
                             'auth_user_id': auth_user})
        patch('rest_api.rest_api_server.controllers.base.BaseController.'
              'get_user_id', return_value=auth_user).start()
        patch('optscale_client.config_client.client.Client.google_calendar_service_enabled',
              return_value=True).start()
        patch('optscale_client.config_client.client.Client.google_calendar_service_key',
              return_value={}).start()

        patch('rest_api.rest_api_server.controllers.cloud_account.'
              'CloudAccountController._configure_report').start()
        self.cloud_acc_dict = {
            'name': 'my cloud_acc',
            'type': 'aws_cnr',
            'config': {
                'access_key_id': 'key',
                'secret_access_key': 'secret',
                'bucket_name': 'name',
                'config_scheme': 'create_report',
            }
        }
        code, self.cloud_acc = self.create_cloud_account(
            self.org_id, self.cloud_acc_dict,
            auth_user_id=auth_user)

        self.valid_calendar_sync_payload = {
            'organization_id': self.org_id,
            'calendar_id': str(uuid.uuid4().hex)
        }
        self.p_availability_check = patch(
            'rest_api.rest_api_server.controllers.calendar_synchronization.'
            'CalendarSynchronizationController._check_calendar_availability')
        self.p_availability_check.start()

    def _create_resource(self):
        resource = {
            'cloud_resource_id': str(uuid.uuid4()),
            'name': 'resource',
            'resource_type': 'Instance',
            'employee_id': self.employee['id'],
            'region': 'us-west-1',
            'pool_id': self.pool_id
        }
        code, created_res = self.cloud_resource_create(
            self.cloud_acc['id'], resource)

        self.resources_collection.update_one(
            filter={
                '_id': created_res['id']
            },
            update={'$set': {
                'shareable': True}}
        )
        created_res['shareable'] = True
        return created_res

    @staticmethod
    def booking_check_side_effect(action, *args, **kwargs):
        if action == 'BOOK_ENVIRONMENTS':
            raise OptHTTPError(403, Err.OE0234, [])
        else:
            return {}

    def test_list(self):
        code, c_sync = self.client.calendar_synchronization_create(
            self.valid_calendar_sync_payload)
        self.assertEqual(code, 201)
        code, res = self.client.calendar_synchronization_list()
        self.assertEqual(code, 200)
        self.assertTrue(isinstance(res, dict))
        c_syncs = res.get('calendar_synchronizations', [])
        self.assertTrue(len(c_syncs), 1)
        self.assertDictEqual(c_sync, c_syncs.pop())
        for c_sync in c_syncs:
            self.assertIsNotNone(c_sync['shareable_link'])

    def test_list_empty(self):
        code, res = self.client.calendar_synchronization_list()
        self.assertEqual(code, 200)
        self.assertTrue(isinstance(res, dict))
        self.assertEqual(len(res.get('calendar_synchronizations', [])), 0)

    def test_get_wrong_org(self):
        code, res = self.client.organization_calendar_get(
            str(uuid.uuid4()))
        self.assertEqual(code, 404)
        self.assertEqual(res['error']['error_code'], 'OE0002')

    def test_get_deleted_org(self):
        patch('rest_api.rest_api_server.controllers.employee.'
              'EmployeeController.delete').start()
        code, _ = self.client.organization_delete(self.org_id)
        self.assertEqual(code, 204)
        code, res = self.client.organization_calendar_get(
            self.org_id)
        self.assertEqual(code, 404)
        self.assertEqual(res['error']['error_code'], 'OE0002')

    def test_get_no_calendar(self):
        code, res = self.client.organization_calendar_get(self.org_id)
        self.assertEqual(code, 200)
        self.assertIsNone(res.get('service_account'))
        self.assertIsNone(res.get('calendar_synchronization'))

    def test_get(self):
        code, c_sync = self.client.calendar_synchronization_create(
            self.valid_calendar_sync_payload)
        self.assertEqual(code, 201)
        code, res = self.client.organization_calendar_get(self.org_id)
        self.assertEqual(code, 200)
        self.assertIsNone(res.get('service_account'))
        self.assertDictEqual(c_sync, res['calendar_synchronization'])
        self.assertIsNotNone(c_sync['shareable_link'])

        client_email = ''
        patch('optscale_client.config_client.client.Client.google_calendar_service_key',
              return_value={'client_email': client_email}).start()
        code, res = self.client.organization_calendar_get(self.org_id)
        self.assertEqual(code, 200)
        self.assertIsNone(res.get('service_account'))
        self.assertDictEqual(c_sync, res['calendar_synchronization'])

        client_email = 'example@hystax.com'
        patch('optscale_client.config_client.client.Client.google_calendar_service_key',
              return_value={'client_email': client_email}).start()
        code, res = self.client.organization_calendar_get(self.org_id)
        self.assertEqual(code, 200)
        self.assertEqual(res.get('service_account'), client_email)
        self.assertDictEqual(c_sync, res['calendar_synchronization'])

    def test_delete(self):
        code, c_sync = self.client.calendar_synchronization_create(
            self.valid_calendar_sync_payload)
        self.assertEqual(code, 201)
        with patch('rest_api.rest_api_server.controllers.calendar_synchronization.'
                   'CalendarSynchronizationController.delete_calendar_events'):
            code, _ = self.client.calendar_synchronization_delete(c_sync['id'])
            self.assertEqual(code, 204)

    @patch('rest_api.google_calendar_client.client.GoogleCalendarClient.list_events')
    @patch('rest_api.google_calendar_client.client.GoogleCalendarClient.create_event')
    def test_delete_existing_bookings(self, p_create_event, p_list_event):
        patch('rest_api.rest_api_server.controllers.shareable_resource.'
              'ShareableBookingController.publish_task').start()
        resource_id = self._create_resource()['id']
        schedule_book = {
            'resource_id': resource_id,
            'acquired_by_id': self.employee['id'],
        }
        patch(
            'rest_api.rest_api_server.handlers.v2.shareable_resources.'
            'ShareableBookingBaseAsyncHandler.check_booking_permission',
            side_effect=self.booking_check_side_effect).start()
        code, booking = self.client.shareable_book_create(
            self.org_id, schedule_book)
        self.assertEqual(code, 201)

        event = {'id': '123456'}
        p_create_event.return_value = event
        code, c_sync = self.client.calendar_synchronization_create(
            self.valid_calendar_sync_payload)
        self.assertEqual(code, 201)

        p_list_event.return_value = [event]
        with patch('rest_api.google_calendar_client.client.GoogleCalendarClient.'
                   'delete_event') as p_delete_event:
            code, _ = self.client.calendar_synchronization_delete(c_sync['id'])
            self.assertEqual(code, 204)
            p_delete_event.assert_called_once_with(
                c_sync['calendar_id'], event['id'])

    def test_delete_nonexisting(self):
        code, _ = self.client.calendar_synchronization_delete(str(uuid.uuid4()))
        self.assertEqual(code, 404)

    def test_delete_deleted_org(self):
        patch('rest_api.rest_api_server.controllers.employee.'
              'EmployeeController.delete').start()
        code, c_sync = self.client.calendar_synchronization_create(
            self.valid_calendar_sync_payload)
        self.assertEqual(code, 201)
        code, _ = self.client.organization_delete(self.org_id)
        code, _ = self.client.calendar_synchronization_delete(c_sync['id'])
        self.assertEqual(code, 404)

    def test_patch_deleted(self):
        code, c_sync = self.client.calendar_synchronization_create(
            self.valid_calendar_sync_payload)
        self.assertEqual(code, 201)
        with patch('rest_api.rest_api_server.controllers.calendar_synchronization.'
                   'CalendarSynchronizationController.delete_calendar_events'):
            code, _ = self.client.calendar_synchronization_delete(c_sync['id'])
            self.assertEqual(code, 204)

        code, res = self.client.calendar_synchronization_update(
            c_sync['id'], {'last_completed': 123})
        self.assertEqual(code, 404)
        self.assertEqual(res['error']['error_code'], 'OE0002')

    def test_patch(self):
        code, c_sync = self.client.calendar_synchronization_create(
            self.valid_calendar_sync_payload)
        self.assertEqual(code, 201)

        code, res = self.client.calendar_synchronization_update(
            c_sync['id'], {'last_completed': 123})
        self.assertEqual(code, 200)
        self.assertEqual(res['last_completed'], 123)
        self.assertIsNotNone(res['shareable_link'])

    def test_patch_immutable(self):
        code, c_sync = self.client.calendar_synchronization_create(
            self.valid_calendar_sync_payload)
        self.assertEqual(code, 201)

        code, res = self.client.calendar_synchronization_update(
            c_sync['id'], {'organization_id': str(uuid.uuid4())})
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0211')

    def test_patch_unexpected(self):
        code, c_sync = self.client.calendar_synchronization_create(
            self.valid_calendar_sync_payload)
        self.assertEqual(code, 201)

        code, res = self.client.calendar_synchronization_update(
            c_sync['id'], {'not_organization_id': str(uuid.uuid4())})
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0212')

    def test_create(self):
        code, c_sync = self.client.calendar_synchronization_create(
            self.valid_calendar_sync_payload)
        self.assertEqual(code, 201)
        self.assertIsNotNone(c_sync, None)
        self.assertIsNotNone(c_sync['shareable_link'])

    def test_create_availability_check(self):
        self.p_availability_check.stop()
        event_id = 123
        with patch('rest_api.google_calendar_client.client.GoogleCalendarClient.'
                   'create_event', return_value={'id': event_id}) as p_create_event:
            with patch('rest_api.google_calendar_client.client.GoogleCalendarClient.'
                       'delete_event') as p_delete_event:
                code, c_sync = self.client.calendar_synchronization_create(
                    self.valid_calendar_sync_payload)
                self.assertEqual(code, 201)
                p_create_event.assert_called()
                p_delete_event.assert_called_once_with(
                    c_sync['calendar_id'], event_id)

    def test_create_availability_check_negative(self):
        self.p_availability_check.stop()
        with patch('rest_api.google_calendar_client.client.GoogleCalendarClient.'
                   'create_event', side_effect=CalendarException('')
                   ):
            code, res = self.client.calendar_synchronization_create(
                self.valid_calendar_sync_payload)
            self.assertEqual(code, 424)
            self.assertEqual(res['error']['error_code'], 'OE0493')

    @freeze_time('2020-04-15')
    def test_create_existing_bookings(self):
        patch('rest_api.rest_api_server.controllers.shareable_resource.'
              'ShareableBookingController.publish_task').start()
        resource_id = self._create_resource()['id']
        schedule_book = {
            'resource_id': resource_id,
            'acquired_by_id': self.employee['id'],
        }

        patch(
            'rest_api.rest_api_server.handlers.v2.shareable_resources.'
            'ShareableBookingBaseAsyncHandler.check_booking_permission',
            side_effect=self.booking_check_side_effect).start()
        code, booking = self.client.shareable_book_create(
            self.org_id, schedule_book)
        self.assertEqual(code, 201)

        event = {'id': '123'}
        p_create_event = patch(
            'rest_api.google_calendar_client.client.GoogleCalendarClient.create_event',
            return_value=event
        ).start()
        code, c_sync = self.client.calendar_synchronization_create(
            self.valid_calendar_sync_payload)
        self.assertEqual(code, 201)
        expected_call = {
            'calendar_id': c_sync['calendar_id'],
            'summary': 'resource is acquired by %s' % self.employee['name'],
            'end': datetime(2020, 4, 15).replace(
                hour=23, minute=59, second=0, microsecond=0) + timedelta(days=365),
            'start': datetime(2020, 4, 15),
            'description': ANY,
            'private_properties': None
        }
        p_create_event.assert_called_once_with(**expected_call)
        code, booking = self.client.shareable_book_get(booking['id'])
        self.assertEqual(code, 200)
        self.assertEqual(booking['event_id'], event['id'])

    def test_create_disabled_calendars(self):
        patch('optscale_client.config_client.client.Client.google_calendar_service_enabled',
              return_value=False).start()
        code, res = self.client.calendar_synchronization_create(
            self.valid_calendar_sync_payload)
        self.assertEqual(code, 424)
        self.assertEqual(res['error']['error_code'], 'OE0485')

    def test_create_duplicate(self):
        code, _ = self.client.calendar_synchronization_create(
            self.valid_calendar_sync_payload)
        self.assertEqual(code, 201)
        code, res = self.client.calendar_synchronization_create(
            self.valid_calendar_sync_payload)
        self.assertEqual(code, 409)
        self.assertEqual(res['error']['error_code'], 'OE0487')

    def test_create_multiple(self):
        code, _ = self.client.calendar_synchronization_create(
            self.valid_calendar_sync_payload)
        self.assertEqual(code, 201)
        self.valid_calendar_sync_payload['calendar_id'] = str(uuid.uuid4())
        code, res = self.client.calendar_synchronization_create(
            self.valid_calendar_sync_payload)
        self.assertEqual(code, 409)
        self.assertEqual(res['error']['error_code'], 'OE0487')

    def test_create_deleted_org(self):
        patch('rest_api.rest_api_server.controllers.employee.'
              'EmployeeController.delete').start()
        code, _ = self.client.organization_delete(self.org_id)
        self.assertEqual(code, 204)
        code, res = self.client.calendar_synchronization_create(
            self.valid_calendar_sync_payload)
        self.assertEqual(code, 404)
        self.assertEqual(res['error']['error_code'], 'OE0002')

    def test_create_unexpected(self):
        self.valid_calendar_sync_payload['calendar_year'] = 123
        code, res = self.client.calendar_synchronization_create(
            self.valid_calendar_sync_payload)
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0212')

    def test_create_immutable(self):
        self.valid_calendar_sync_payload['deleted_at'] = 123
        code, res = self.client.calendar_synchronization_create(
            self.valid_calendar_sync_payload)
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0211')

    def test_delete_not_existing_calendar_and_events(self):
        patch('rest_api.rest_api_server.controllers.shareable_resource.'
              'ShareableBookingController.publish_task').start()
        resource_id = self._create_resource()['id']
        schedule_book = {
            'resource_id': resource_id,
            'acquired_by_id': self.employee['id'],
        }
        patch(
            'rest_api.rest_api_server.handlers.v2.shareable_resources.'
            'ShareableBookingBaseAsyncHandler.check_booking_permission',
            side_effect=self.booking_check_side_effect).start()
        code, booking = self.client.shareable_book_create(
            self.org_id, schedule_book)
        self.assertEqual(code, 201)

        patch('rest_api.google_calendar_client.client.GoogleCalendarClient.create_event',
              return_value={'id': '123'}).start()
        p_publish_activity = patch(
            'rest_api.rest_api_server.controllers.base.BaseController.'
            'publish_activities_task'
        ).start()
        code, c_sync = self.client.calendar_synchronization_create(
            self.valid_calendar_sync_payload)
        self.assertEqual(code, 201)
        activity_param_tuples = self.get_publish_activity_tuple(
            self.org_id, c_sync['id'], 'calendar_synchronization',
            'calendar_connected', {
                'calendar_id': c_sync['calendar_id']
            })
        p_publish_activity.assert_called_once_with(
            *activity_param_tuples, add_token=True
        )

        with patch('rest_api.google_calendar_client.client.GoogleCalendarClient.'
                   'delete_event',
                   side_effect=CalendarException('Calendar not found')):
            code, _ = self.client.calendar_synchronization_delete(c_sync['id'])
            self.assertEqual(code, 204)
        self.assertEqual(p_publish_activity.call_count, 3)
        activity_warning_param_tuples = self.get_publish_activity_tuple(
            self.org_id, c_sync['id'], 'calendar_synchronization',
            'calendar_warning', {
                'calendar_id': c_sync['calendar_id'],
                'reason': 'Calendar not found',
                'level': 'WARNING'
            })
        activity_disconnected_param_tuples = self.get_publish_activity_tuple(
            self.org_id, c_sync['id'], 'calendar_synchronization',
            'calendar_disconnected', {
                'calendar_id': c_sync['calendar_id']
            })
        p_publish_activity.assert_has_calls([
            call(*activity_warning_param_tuples, add_token=True),
            call(*activity_disconnected_param_tuples, add_token=True)])
