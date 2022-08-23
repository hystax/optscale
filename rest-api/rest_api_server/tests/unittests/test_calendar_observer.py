import uuid
from datetime import datetime, timedelta
from freezegun import freeze_time
from unittest.mock import patch, ANY, PropertyMock
from optscale_exceptions.common_exc import FailedDependency

from rest_api_server.models.db_factory import DBType, DBFactory
from rest_api_server.models.db_base import BaseDB
from rest_api_server.tests.unittests.test_api_base import TestApiBase
from rest_api_server.exceptions import Err
from optscale_exceptions.http_exc import OptHTTPError

NEWLY_DISCOVERED_TIME = 300  # 5 min


class TestObserver(TestApiBase):
    def setUp(self, version='v2'):
        super().setUp(version)
        db = DBFactory(DBType.Test, None).db
        engine = db.engine
        self.session = BaseDB.session(engine)()
        _, self.org = self.client.organization_create(
            {'name': "partner_test"})

        self.org_id = self.org['id']
        self.pool_id = self.org['pool_id']
        user_id = self.gen_id()
        _, self.employee = self.client.employee_create(
            self.org_id, {'name': 'Eliot Alderson', 'auth_user_id': user_id})
        patch('rest_api_server.controllers.cloud_account.'
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
            auth_user_id=user_id)

        self.valid_calendar_sync_payload = {
            'organization_id': self.org_id,
            'calendar_id': str(uuid.uuid4().hex)
        }
        self.p_availability_check = patch(
            'rest_api_server.controllers.calendar_synchronization.'
            'CalendarSynchronizationController._check_calendar_availability')
        self.p_availability_check.start()
        patch('config_client.client.Client.google_calendar_service_enabled',
              return_value=True).start()
        patch('config_client.client.Client.google_calendar_service_key').start()

        self.auth_user = self.gen_id()
        self._mock_auth_user(self.auth_user)

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

    def test_observe_nonexisting_org(self):
        code, res = self.client.observe_calendar(str(uuid.uuid4()))
        self.assertEqual(code, 404)
        self.assertEqual(res['error']['error_code'], 'OE0002')

    def test_observe_deleted_org(self):
        patch('rest_api_server.controllers.employee.'
              'EmployeeController.delete').start()
        code, _ = self.client.organization_delete(self.org_id)
        self.assertEqual(code, 204)
        code, res = self.client.observe_calendar(self.org_id)
        self.assertEqual(code, 404)
        self.assertEqual(res['error']['error_code'], 'OE0002')

    def test_observe_calendarless_org(self):
        code, res = self.client.observe_calendar(self.org_id)
        self.assertEqual(code, 404)
        self.assertEqual(res['error']['error_code'], 'OE0486')

    def test_observe_empty(self):
        code, c_sync = self.client.calendar_synchronization_create(
            self.valid_calendar_sync_payload)
        self.assertEqual(code, 201)
        with patch(
                'google_calendar_client.client.GoogleCalendarClient.list_events',
                return_value=[]
        ):
            code, _ = self.client.observe_calendar(self.org_id)
            self.assertEqual(code, 204)

    @patch('rest_api_server.controllers.calendar_synchronization.'
           'CalendarSynchronizationController.public_ip',
           new_callable=PropertyMock)
    @patch('google_calendar_client.client.GoogleCalendarClient.update_event')
    @patch('google_calendar_client.client.GoogleCalendarClient.create_event')
    def test_observe_event_non_changed(self, p_create_event,
                                       p_patch_event, p_public_ip):
        patch('rest_api_server.controllers.shareable_resource.'
              'ShareableBookingController.publish_task').start()
        code, c_sync = self.client.calendar_synchronization_create(
            self.valid_calendar_sync_payload)
        self.assertEqual(code, 201)

        resource = self._create_resource()
        schedule_book = {
            'resource_id': resource['id'],
            'acquired_by_id': self.employee['id'],
        }
        patch(
            'rest_api_server.handlers.v2.shareable_resources.'
            'ShareableBookingBaseAsyncHandler.check_booking_permission',
            side_effect=self.booking_check_side_effect).start()
        dt = datetime(2021, 5, 1)
        public_ip = '1.2.3.4'
        event = {
            'id': '123',
            'calendar_id': c_sync['calendar_id'],
            'start': dt,
            'end': dt.replace(hour=23, minute=59, second=0,
                              microsecond=0) + timedelta(days=365),
            'summary': f"{resource.get('name')} is acquired by {self.employee['name']}",
            'status': 'confirmed',
            'description': f"https://{public_ip}/resources/{resource['id']}"
        }
        p_create_event.return_value = event
        with freeze_time(dt):
            code, booking = self.client.shareable_book_create(
                self.org_id, schedule_book)
            self.assertEqual(code, 201)

            p_public_ip.return_value = public_ip
            with patch(
                    'google_calendar_client.client.GoogleCalendarClient.list_events',
                    return_value=[event]
            ):
                code, _ = self.client.observe_calendar(self.org_id)
                self.assertEqual(code, 204)
                p_patch_event.assert_not_called()

    @patch('rest_api_server.controllers.calendar_synchronization.'
           'CalendarSynchronizationController.public_ip',
           new_callable=PropertyMock)
    @patch('google_calendar_client.client.GoogleCalendarClient.create_event')
    def test_observe_event_changed(self, p_create_event, p_public_ip):
        patch('rest_api_server.controllers.shareable_resource.'
              'ShareableBookingController.publish_task').start()
        code, c_sync = self.client.calendar_synchronization_create(
            self.valid_calendar_sync_payload)
        self.assertEqual(code, 201)

        resource = self._create_resource()
        schedule_book = {
            'resource_id': resource['id'],
            'acquired_by_id': self.employee['id'],
        }
        patch(
            'rest_api_server.handlers.v2.shareable_resources.'
            'ShareableBookingBaseAsyncHandler.check_booking_permission',
            side_effect=self.booking_check_side_effect).start()
        dt = datetime(2021, 1, 1)
        end_dt = dt.replace(
            hour=23, minute=59, second=0, microsecond=0) + timedelta(days=365)

        public_ip = '1.2.3.4'
        event = {
            'id': '123',
            'calendar_id': c_sync['calendar_id'],
            'start': dt,
            'end': end_dt,
            'summary': "Empire is acquired by Pickle Rick",
            'status': 'confirmed',
            'description': f"https://{public_ip}/resources/{resource['id']}"
        }
        p_create_event.return_value = event
        with freeze_time(dt):
            code, booking = self.client.shareable_book_create(
                self.org_id, schedule_book)
            self.assertEqual(code, 201)

            p_public_ip.return_value = public_ip
            with patch(
                    'google_calendar_client.client.GoogleCalendarClient.list_events',
                    return_value=[event]
            ) as p_list_event, patch(
                'google_calendar_client.client.GoogleCalendarClient.update_event'
            ) as p_patch_event:
                code, _ = self.client.observe_calendar(self.org_id)
                self.assertEqual(code, 204)
                p_patch_event.assert_called_once_with(
                    c_sync['calendar_id'], event['id'],
                    summary=f"{resource.get('name')} is acquired by {self.employee['name']}")
                p_list_event.assert_called_once_with(
                    c_sync['calendar_id'], ANY, ANY,
                    datetime.utcnow() - timedelta(days=28)
                )

            with patch(
                    'config_client.client.Client.google_calendar_service_key',
                    return_value={'client_email': 'example@hystax.com'}):
                code, res = self.client.organization_calendar_get(self.org_id)
                self.assertEqual(code, 200)
                c_sync = res['calendar_synchronization']
            with patch(
                'google_calendar_client.client.GoogleCalendarClient.update_event'
            ), patch(
                'google_calendar_client.client.GoogleCalendarClient.list_events',
                return_value=[event]
            ) as p_list_event:
                code, _ = self.client.observe_calendar(self.org_id)
                self.assertEqual(code, 204)
                p_list_event.assert_called_once_with(
                    c_sync['calendar_id'], ANY, ANY,
                    datetime.fromtimestamp(c_sync['last_completed'])
                )
            p_publish_activity = patch(
                'rest_api_server.controllers.base.BaseController.'
                'publish_activities_task'
            ).start()
            with patch('google_calendar_client.client.GoogleCalendarClient.list_events',
                       side_effect=FailedDependency(Err.OE0490, ['not found'])):
                code, _ = self.client.observe_calendar(self.org_id)
                self.assertEqual(code, 204)
                error = 'Unable to list calendar events: not found'
                activity_param_tuples = self.get_publish_activity_tuple(
                    self.org_id, c_sync['id'], 'calendar_synchronization',
                    'calendar_warning', {
                        'calendar_id': c_sync['calendar_id'],
                        'reason': error,
                        'is_observer': True,
                        'level': 'WARNING'
                    })
                p_publish_activity.assert_called_once_with(
                    *activity_param_tuples, add_token=True
                )
        # 365 - the end of endless booking event
        # 180 - days before the end of the endless booking event, when it will be updated
        # 100 < (365 - 180), there are no changes to the end of the event
        with freeze_time(dt + timedelta(days=100)), patch(
                'google_calendar_client.client.GoogleCalendarClient.list_events',
                return_value=[event]), patch(
            'google_calendar_client.client.GoogleCalendarClient.update_event'
        ) as p_patch_event:
            code, _ = self.client.observe_calendar(self.org_id)
            self.assertEqual(code, 204)
            p_patch_event.assert_called_once_with(
                c_sync['calendar_id'], event['id'],
                summary=f"{resource.get('name')} is acquired by {self.employee['name']}")
        # 200 > (365 - 180), there is a change in the end of the event
        end_dt += timedelta(days=200)
        with freeze_time(dt + timedelta(days=200)), patch(
                'google_calendar_client.client.GoogleCalendarClient.list_events',
                return_value=[event]), patch(
            'google_calendar_client.client.GoogleCalendarClient.update_event'
        ) as p_patch_event:
            code, _ = self.client.observe_calendar(self.org_id)
            self.assertEqual(code, 204)
            p_patch_event.assert_called_once_with(
                c_sync['calendar_id'], event['id'], end=end_dt,
                summary=f"{resource.get('name')} is acquired by {self.employee['name']}")
        # 200 + 365 - the end of the event has been updated by a previous observation
        # 400 + (365 - 180) > 200 + 365, updating the end of the event again
        event['end'] = end_dt
        end_dt += timedelta(days=200)
        with freeze_time(dt + timedelta(days=400)), patch(
                'google_calendar_client.client.GoogleCalendarClient.list_events',
                return_value=[event]), patch(
            'google_calendar_client.client.GoogleCalendarClient.update_event'
        ) as p_patch_event:
            code, _ = self.client.observe_calendar(self.org_id)
            self.assertEqual(code, 204)
            p_patch_event.assert_called_once_with(
                c_sync['calendar_id'], event['id'], end=end_dt,
                summary=f"{resource.get('name')} is acquired by {self.employee['name']}")

    @patch('rest_api_server.controllers.calendar_synchronization.'
           'CalendarSynchronizationController.public_ip', new_callable=PropertyMock)
    @patch('google_calendar_client.client.GoogleCalendarClient.update_event')
    @patch('google_calendar_client.client.GoogleCalendarClient.create_event')
    def test_observe_event_deleted(self, p_create_event,
                                   p_patch_event, p_public_ip):
        patch('rest_api_server.controllers.shareable_resource.'
              'ShareableBookingController.publish_task').start()
        code, c_sync = self.client.calendar_synchronization_create(
            self.valid_calendar_sync_payload)
        self.assertEqual(code, 201)

        resource = self._create_resource()
        schedule_book = {
            'resource_id': resource['id'],
            'acquired_by_id': self.employee['id'],
        }
        patch(
            'rest_api_server.handlers.v2.shareable_resources.'
            'ShareableBookingBaseAsyncHandler.check_booking_permission',
            side_effect=self.booking_check_side_effect).start()
        public_ip = '1.2.3.4'
        dt = datetime(2021, 5, 1)
        event = {
            'id': '123',
            'calendar_id': c_sync['calendar_id'],
            'start': dt,
            'end': datetime.max.replace(second=0, microsecond=0),
            'summary': f"{resource.get('name')} is acquired by {self.employee['name']}",
            'status': 'cancelled',
            'description': f"https://{public_ip}/resources/{resource['id']}"
        }
        p_create_event.return_value = event
        with freeze_time(dt):
            code, booking = self.client.shareable_book_create(
                self.org_id, schedule_book)
            self.assertEqual(code, 201)

            p_public_ip.return_value = public_ip
            with patch(
                    'google_calendar_client.client.GoogleCalendarClient.list_events',
                    return_value=[event]
            ) as p_list_event:
                code, _ = self.client.observe_calendar(self.org_id)
                self.assertEqual(code, 204)
                p_patch_event.assert_called_once_with(
                    c_sync['calendar_id'], event['id'], status='confirmed')
                p_list_event.assert_called_once_with(
                    c_sync['calendar_id'], ANY, ANY,
                    datetime.utcnow() - timedelta(days=28)
                )
        with freeze_time(dt + timedelta(days=1)):
            with patch('config_client.client.Client.google_calendar_service_key',
                       return_value={'client_email': 'example@hystax.com'}):
                code, res = self.client.organization_calendar_get(self.org_id)
                self.assertEqual(code, 200)
                c_sync = res['calendar_synchronization']
            with patch(
                    'google_calendar_client.client.GoogleCalendarClient.list_events',
                    return_value=[event]
            ) as p_list_event:
                code, _ = self.client.observe_calendar(self.org_id)
                self.assertEqual(code, 204)
                p_list_event.assert_called_once_with(
                    c_sync['calendar_id'], ANY, ANY,
                    datetime.fromtimestamp(c_sync['last_completed'])
                )

        with patch('google_calendar_client.client.GoogleCalendarClient.'
                   'delete_event') as p_delete_event:
            code, booking = self.client.shareable_book_delete(booking['id'])
            self.assertEqual(code, 204)

        permanently_deleted_event = {
            'id': '456',
            'calendar_id': c_sync['calendar_id'],
            'start': datetime(2000, 1, 1, 0, 0),
            'end': datetime(2000, 1, 2, 0, 0),
            'summary': f"{resource.get('name')} is acquired by {self.employee['name']}",
            'status': 'cancelled',
            'description': f"https://{public_ip}/resources/{resource['id']}"
        }
        p_create_event.return_value = permanently_deleted_event
        with freeze_time(dt):
            code, booking = self.client.shareable_book_create(
                self.org_id, schedule_book)
            self.assertEqual(code, 201)
            self.assertEqual(booking['event_id'], permanently_deleted_event['id'])

        event['id'] = '789'
        p_create_event.return_value = event
        p_public_ip.return_value = public_ip
        with patch(
                'google_calendar_client.client.GoogleCalendarClient.list_events',
                return_value=[permanently_deleted_event]):
            code, _ = self.client.observe_calendar(self.org_id)
            self.assertEqual(code, 204)
        code, booking = self.client.shareable_book_get(booking['id'])
        self.assertEqual(code, 200)
        self.assertEqual(booking['event_id'], event['id'])
