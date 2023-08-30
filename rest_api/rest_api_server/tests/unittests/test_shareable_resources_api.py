from datetime import datetime, timedelta
import uuid
import json
from unittest.mock import patch, ANY, call
from freezegun import freeze_time

from rest_api.google_calendar_client.client import CalendarException
from rest_api.rest_api_server.tests.unittests.test_api_base import TestApiBase
from tools.optscale_exceptions.http_exc import OptHTTPError
from rest_api.rest_api_server.exceptions import Err

DAY_SECONDS = 24 * 60 * 60


class TestShareableResourcesApi(TestApiBase):
    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.organization = self.client.organization_create({
            'name': 'test organization'})
        self.organization_id = self.organization['id']
        self.auth_user = self.gen_id()
        _, self.employee = self.client.employee_create(
            self.organization['id'], {'name': 'employee',
                                      'auth_user_id': self.auth_user})
        _, self.pool = self.client.pool_create(self.organization_id, {
            'name': 'sub', 'parent_id': self.organization['pool_id']
        })
        self.pool_id = self.pool['id']
        self.org_pool_id = self.organization['pool_id']
        self.org_pool_purpose = 'business_unit'
        self.update_default_owner_for_pool(self.org_pool_id,
                                           self.employee['id'])
        self.auth_user_2 = self.gen_id()
        _, self.employee_2 = self.client.employee_create(
            self.organization['id'], {'name': 'employee_2',
                                      'auth_user_id': self.auth_user_2})
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
        self._mock_auth_user(self.auth_user)
        self.user = {
            'id': self.auth_user,
            'display_name': 'default',
            'email': 'email@email.com',
        }
        patch('rest_api.rest_api_server.handlers.v1.base.BaseAuthHandler._get_user_info',
              return_value=self.user).start()
        code, self.cloud_acc = self.create_cloud_account(
            self.organization_id, self.cloud_acc_dict,
            auth_user_id=self.auth_user)
        user_roles = [{
            "user_id": self.auth_user,
            "role_purpose": 'optscale_manager'
        }]
        self.p_get_roles_info = patch(
            'rest_api.rest_api_server.handlers.v1.base.BaseAuthHandler.get_roles_info',
            return_value=user_roles).start()
        patch('rest_api.rest_api_server.controllers.calendar_synchronization.'
              'CalendarSynchronizationController.'
              '_check_calendar_availability').start()
        patch('rest_api.rest_api_server.controllers.shareable_resource.'
              'ShareableBookingController.publish_task').start()
        self.p_validate_employee = patch(
            'rest_api.rest_api_server.controllers.shareable_resource.'
            'ShareableBookingController.check_employee_permission')
        self.p_validate_employee.start()

    def _create_resource(self, employee_id=None, pool_id=None,
                         is_shareable=True, resource_type='Instance',
                         tags=None):
        if not employee_id:
            employee_id = self.employee['id']
        if not pool_id:
            pool_id = self.pool_id
        resource = {
            'cloud_resource_id': str(uuid.uuid4()),
            'name': 'resource',
            'resource_type': resource_type,
            'employee_id': employee_id,
            'region': 'us-west-1',
            'pool_id': pool_id
        }
        if tags:
            resource['tags'] = tags
        code, created_res = self.cloud_resource_create(self.cloud_acc['id'],
                                                       resource)
        if is_shareable:
            resource_id = created_res['id']
            self.resources_collection.update_one(
                filter={
                    '_id': resource_id
                },
                update={'$set': {
                    'shareable': True}}
            )
            created_res['shareable'] = True
        return created_res

    def test_create_shareable(self):
        resource_id = self._create_resource()['id']
        schedule_book = {
            'resource_id': resource_id,
            'acquired_by_id': self.employee_2['id'],
        }
        p_create_event = patch(
            'rest_api.google_calendar_client.client.GoogleCalendarClient.create_event'
        ).start()
        code, resp = self.client.shareable_book_create(
            self.organization_id, schedule_book)
        self.assertEqual(code, 201)
        self.assertEqual(
            resp.get("acquired_by"),
            {"id": self.employee_2["id"], "name": self.employee_2["name"]},
        )
        p_create_event.assert_not_called()

    def test_not_existing_org(self):
        resource_id = self._create_resource()['id']
        schedule_book = {
            'resource_id': resource_id,
            'acquired_by_id': self.employee_2['id'],
        }
        code, response = self.client.shareable_book_create(str(uuid.uuid4()),
                                                           schedule_book)
        self.assertEqual(code, 404)
        self.assertEqual(response['error']['error_code'], 'OE0002')

    def test_not_existing_employee(self):
        resource_id = self._create_resource()['id']
        schedule_book = {
            'resource_id': resource_id,
            'acquired_by_id': str(uuid.uuid4()),
        }
        code, response = self.client.shareable_book_create(self.organization_id,
                                                           schedule_book)
        self.assertEqual(code, 404)
        self.assertEqual(response['error']['error_code'], 'OE0002')

    def test_unexpected_params(self):
        resource_id = self._create_resource()['id']
        now = int(datetime.utcnow().timestamp())
        since = now - DAY_SECONDS
        schedule_book = {
            'resource_id': resource_id,
            'acquired_by_id': self.employee_2['id'],
            'acquired_since': since,
            'released_at': now,
            'test': 'test'
        }
        code, response = self.client.shareable_book_create(self.organization_id,
                                                           schedule_book)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0212')

    def test_invalid_int_param(self):
        resource_id = self._create_resource()['id']
        now = int(datetime.utcnow().timestamp())
        schedule_book = {
            'resource_id': resource_id,
            'acquired_by_id': self.employee_2['id'],
            'acquired_since': 'invalid int',
            'released_at': now,
        }
        code, response = self.client.shareable_book_create(self.organization_id,
                                                           schedule_book)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0223')

    def test_not_existing_resource(self):
        schedule_book = {
            'resource_id': str(uuid.uuid4()),
            'acquired_by_id': self.employee_2['id'],
        }
        code, response = self.client.shareable_book_create(self.organization_id,
                                                           schedule_book)
        self.assertEqual(code, 404)
        self.assertEqual(response['error']['error_code'], 'OE0002')

    def test_invalid_resource_type(self):
        resource_id = self._create_resource(resource_type='Volume')['id']
        schedule_book = {
            'resource_id': resource_id,
            'acquired_by_id': self.employee_2['id'],
        }
        code, response = self.client.shareable_book_create(self.organization_id,
                                                           schedule_book)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0384')

    def test_create_env_booking(self):
        env_resource = {
            'name': 'resource',
            'resource_type': 'some_env_type',
            'tags': {}
        }
        code, resource = self.environment_resource_create(
            self.organization_id, env_resource)
        self.assertEqual(code, 201)

        now = int(datetime.utcnow().timestamp())
        since = now + DAY_SECONDS
        schedule_book = {
            'resource_id': resource['id'],
            'acquired_by_id': self.employee_2['id'],
            'acquired_since': since
        }
        self._mock_auth_user(self.auth_user)
        code, book = self.client.shareable_book_create(self.organization_id,
                                                       schedule_book)
        self.assertEqual(code, 201)

    def test_not_shareable_resource(self):
        resource_id = self._create_resource(is_shareable=False)['id']
        schedule_book = {
            'resource_id': resource_id,
            'acquired_by_id': self.employee_2['id'],
        }
        code, response = self.client.shareable_book_create(self.organization_id,
                                                           schedule_book)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0480')

    def test_not_shareable_cluster(self):
        code, cluster_type = self.client.cluster_type_create(
            self.organization_id, {'name': 'cluster', 'tag_key': 'type'})
        self.assertEqual(code, 201)

        code, res = self.client.cluster_types_apply(self.organization_id)
        self.assertEqual(code, 201)
        resource = self._create_resource(is_shareable=False,
                                         tags={'type': 'val'})
        resource_id = resource['id']
        code, res = self.client.cluster_types_apply(self.organization_id)
        self.assertEqual(code, 201)

        schedule_book = {
            'resource_id': resource_id,
            'acquired_by_id': self.employee_2['id'],
        }
        code, response = self.client.shareable_book_create(self.organization_id,
                                                           schedule_book)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0480')

    def test_make_cloud_resource_clustered(self):
        shareable_resource_1 = self._create_resource(tags={'type': 'val'})
        shareable_resource_1_id = shareable_resource_1['id']
        self.assertEqual(shareable_resource_1['shareable'], True)
        now = int(datetime.utcnow().timestamp())
        since = now + DAY_SECONDS
        released_at = since + DAY_SECONDS
        schedule_book = {
            'resource_id': shareable_resource_1_id,
            'acquired_by_id': self.employee_2['id'],
            'acquired_since': since,
            'released_at': released_at,
        }
        code, book_1 = self.client.shareable_book_create(self.organization_id,
                                                         schedule_book)
        self.assertEqual(code, 201)
        code, response = self.client.shareable_book_get(book_1['id'])
        self.assertEqual(code, 200)
        self.assertEqual(response['id'], book_1['id'])
        schedule_book['acquired_since'] = released_at + 1
        schedule_book['released_at'] = released_at + DAY_SECONDS
        code, book_2 = self.client.shareable_book_create(self.organization_id,
                                                         schedule_book)
        self.assertEqual(code, 201)
        code, response = self.client.shareable_book_get(book_2['id'])
        self.assertEqual(code, 200)
        self.assertEqual(response['id'], book_2['id'])
        code, response = self.client.shareable_resources_list(
            self.organization_id)
        self.assertEqual(code, 200)
        data = response['data']
        result = {res['id']: res for res in data}
        result_res = result.get(shareable_resource_1_id)
        self.assertEqual(result_res.get('shareable'), True)
        self.assertEqual(len(result_res.get('shareable_bookings')), 2)
        code, c_type = self.client.cluster_type_create(
            self.organization_id, {'name': 'cluster', 'tag_key': 'type'})
        self.assertEqual(code, 201)
        code, res = self.client.cluster_types_apply(self.organization_id)
        self.assertEqual(code, 201)
        code, res = self.client.cluster_types_apply(self.organization_id)
        self.assertEqual(code, 201)
        self.assertEqual(res['processed_resources'], 1)

        code, already_not_shareable_resource = self.client.cloud_resource_get(
            shareable_resource_1['id'], details=True)
        self.assertEqual(code, 200)
        self.assertEqual(already_not_shareable_resource['shareable'], False)

        code, cluster = self.client.cloud_resource_get(
            already_not_shareable_resource['cluster_id'], details=True)
        self.assertEqual(code, 200)
        self.assertEqual(cluster['cluster_type_id'], c_type['id'])
        self.assertEqual(len(cluster.get('sub_resources', [])), 1)
        sub_resource = cluster.get('sub_resources')[0]
        self.assertEqual(sub_resource['id'], shareable_resource_1_id)
        self.assertEqual(sub_resource['shareable'], False)

        code, response = self.client.shareable_book_get(book_1['id'])
        self.assertEqual(code, 404)

        code, response = self.client.shareable_book_get(book_2['id'])
        self.assertEqual(code, 404)

    def test_invalid_dates(self):
        resource_id = self._create_resource()['id']
        now = int(datetime.utcnow().timestamp())
        since = now + DAY_SECONDS
        schedule_book = {
            'resource_id': resource_id,
            'acquired_by_id': self.employee_2['id'],
            'acquired_since': since,
            'released_at': now,
        }
        code, response = self.client.shareable_book_create(self.organization_id,
                                                           schedule_book)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0446')

    def test_resource_belong_to_another_org(self):
        _, organization_2 = self.client.organization_create({
            'name': 'another test organization'})
        organization_2_id = organization_2['id']
        auth_user = self.gen_id()
        _, employee = self.client.employee_create(
            organization_2_id, {'name': 'employee_new',
                                'auth_user_id': auth_user})
        resource_id = self._create_resource(employee_id=employee['id'])['id']
        schedule_book = {
            'resource_id': resource_id,
            'acquired_by_id': employee['id'],
        }
        code, response = self.client.shareable_book_create(organization_2_id,
                                                           schedule_book)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0454')

    def test_cluster_not_shareable(self):
        code, cluster_type = self.client.cluster_type_create(
            self.organization_id, {'name': 'cluster', 'tag_key': 'type'})
        self.assertEqual(code, 201)
        code, res = self.client.cluster_types_apply(self.organization_id)
        self.assertEqual(code, 201)
        self._create_resource(is_shareable=False,
                              tags={'type': 'val'})
        code, res = self.client.cluster_types_apply(self.organization_id)
        self.assertEqual(code, 201)

        code, res = self.client.cluster_types_apply(self.organization_id)
        self.assertEqual(code, 201)
        cluster = list(
            self.resources_collection.find({'cluster_type_id': cluster_type[
                'id']}))[0]
        self.resources_collection.update_one(
            filter={
                '_id': cluster['_id']
            },
            update={'$set': {
                'employee_id': self.employee['id']
            }}
        )
        schedule_book = {
            'resource_id': cluster['_id'],
            'acquired_by_id': self.employee['id'],
        }
        code, response = self.client.shareable_book_create(self.organization_id,
                                                           schedule_book)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0480')

    def test_cluster_created(self):
        code, cluster_type = self.client.cluster_type_create(
            self.organization_id, {'name': 'cluster', 'tag_key': 'type'})
        self.assertEqual(code, 201)
        code, res = self.client.cluster_types_apply(self.organization_id)
        self.assertEqual(code, 201)
        self._create_resource(is_shareable=False,
                              tags={'type': 'val'})
        code, res = self.client.cluster_types_apply(self.organization_id)
        self.assertEqual(code, 201)

        code, res = self.client.cluster_types_apply(self.organization_id)
        self.assertEqual(code, 201)
        cluster = list(
            self.resources_collection.find({'cluster_type_id': cluster_type[
                'id']}))[0]
        self.resources_collection.update_one(
            filter={
                '_id': cluster['_id']
            },
            update={'$set': {
                'shareable': True,
                'employee_id': self.employee['id']
            }}
        )
        schedule_book = {
            'resource_id': cluster['_id'],
            'acquired_by_id': self.employee['id'],
        }
        code, response = self.client.shareable_book_create(self.organization_id,
                                                           schedule_book)
        self.assertEqual(code, 201)

        code, response = self.client.shareable_resources_list(
            self.organization_id)
        self.assertEqual(code, 200)
        returned_cluster = response['data'][0]
        self.assertIsNone(returned_cluster.get('cloud_account_name'))
        self.assertIsNone(returned_cluster.get('cloud_account_type'))
        self.assertEqual(returned_cluster.get('pool_name'),
                         self.organization['name'])
        self.assertEqual(returned_cluster.get('pool_purpose'),
                         self.org_pool_purpose)

    def test_create_duplicated_bookings(self):
        resource_id = self._create_resource()['id']
        now = int(datetime.utcnow().timestamp())
        released_at = now - DAY_SECONDS
        since = released_at - DAY_SECONDS
        schedule_book = {
            'resource_id': resource_id,
            'acquired_by_id': self.employee_2['id'],
            'acquired_since': since,
            'released_at': released_at,
        }
        code, response = self.client.shareable_book_create(
            self.organization_id, schedule_book)
        self.assertEqual(code, 201)
        code, response = self.client.shareable_book_create(
            self.organization_id, schedule_book)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0482')

    def test_date_invalid_slot_create(self):
        resource_id = self._create_resource()['id']
        now = int(datetime.utcnow().timestamp())
        released_at = now - DAY_SECONDS
        since = released_at - DAY_SECONDS
        schedule_book = {
            'resource_id': resource_id,
            'acquired_by_id': self.employee_2['id'],
            'acquired_since': since,
            'released_at': released_at,
        }
        code, response = self.client.shareable_book_create(self.organization_id,
                                                           schedule_book)
        self.assertEqual(code, 201)

        schedule_book['acquired_since'] = now - int(1.5 * DAY_SECONDS)
        code, response = self.client.shareable_book_create(self.organization_id,
                                                           schedule_book)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0482')

        schedule_book['acquired_since'] = now - int(3 * DAY_SECONDS)
        schedule_book['released_at'] = None
        code, response = self.client.shareable_book_create(self.organization_id,
                                                           schedule_book)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0482')

        schedule_book['acquired_since'] = now - int(3 * DAY_SECONDS)
        schedule_book['released_at'] = now - int(1.5 * DAY_SECONDS)
        code, response = self.client.shareable_book_create(self.organization_id,
                                                           schedule_book)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0482')

        schedule_book['acquired_since'] = now - int(3 * DAY_SECONDS)
        schedule_book['released_at'] = released_at
        code, response = self.client.shareable_book_create(self.organization_id,
                                                           schedule_book)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0482')

        schedule_book['acquired_since'] = now - int(3 * DAY_SECONDS)
        schedule_book['released_at'] = now
        code, response = self.client.shareable_book_create(self.organization_id,
                                                           schedule_book)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0482')

        schedule_book['acquired_since'] = now - int(3 * DAY_SECONDS)
        schedule_book['released_at'] = now - int(2 * DAY_SECONDS)
        code, response = self.client.shareable_book_create(self.organization_id,
                                                           schedule_book)
        self.assertEqual(code, 201)

    def test_patch_shareable(self):
        resource = self._create_resource()
        resource_id = resource['id']
        now = int(datetime.utcnow().timestamp())
        until = now + 2 * DAY_SECONDS
        schedule_book = {
            'resource_id': resource_id,
            'acquired_by_id': self.employee_2['id'],
            'acquired_since': now - DAY_SECONDS,
            'released_at': until,
        }
        code, book = self.client.shareable_book_create(self.organization_id,
                                                       schedule_book)
        self.assertEqual(code, 201)
        p_activities_publish = patch(
            'rest_api.rest_api_server.controllers.base.'
            'BaseController.publish_activities_task').start()
        released_at = now + DAY_SECONDS
        code, response = self.client.shareable_book_release(
            book['id'], {'released_at': released_at})

        self.assertEqual(code, 200)
        p_activities_publish.assert_has_calls([
            call(
                response['organization_id'], resource['id'], 'resource',
                'shareable_resource_changed', {
                    'object_name': resource['name']
                }, 'resource.shareable_resource_changed', add_token=True)])

        p_activities_publish = patch(
            'rest_api.rest_api_server.controllers.base.'
            'BaseController.publish_activities_task').start()
        p_update_event = patch(
            'rest_api.google_calendar_client.client.GoogleCalendarClient.update_event'
        ).start()
        code, response = self.client.shareable_book_release(
            book['id'], {'released_at': now - 1})
        self.assertEqual(code, 200)
        p_update_event.assert_not_called()
        p_activities_publish.assert_has_calls([
            call(
                response['organization_id'], resource['id'], 'resource',
                'shareable_booking_released', {
                    'object_name': resource['name']
                }, 'resource.shareable_booking_released', add_token=True)])

    def test_patch_None_released_at(self):
        resource = self._create_resource()
        resource_id = resource['id']
        now = int(datetime.utcnow().timestamp())
        until = now + DAY_SECONDS
        schedule_book = {
            'resource_id': resource_id,
            'acquired_by_id': self.employee_2['id'],
            'acquired_since': now,
            'released_at': until,
        }
        code, book_1 = self.client.shareable_book_create(self.organization_id,
                                                         schedule_book)
        self.assertEqual(code, 201)
        code, response = self.client.shareable_book_release(
            book_1['id'], {'released_at': None})

        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0216')

        code, response = self.client.shareable_book_release(
            book_1['id'], {'test': now})

        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0216')

        code, response = self.client.shareable_book_release(
            book_1['id'], {'released_at': until + 1, 'test': now})

        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0212')

    def test_patch_invalid_scope_period(self):
        resource = self._create_resource()
        resource_id = resource['id']
        now = int(datetime.utcnow().timestamp())
        since = now + DAY_SECONDS
        until = since + DAY_SECONDS
        schedule_book = {
            'resource_id': resource_id,
            'acquired_by_id': self.employee_2['id'],
            'acquired_since': since,
            'released_at': until,
        }
        code, book_1 = self.client.shareable_book_create(self.organization_id,
                                                         schedule_book)
        self.assertEqual(code, 201)
        schedule_book['acquired_since'] = now
        schedule_book['released_at'] = since - 1
        code, book_2 = self.client.shareable_book_create(self.organization_id,
                                                         schedule_book)
        self.assertEqual(code, 201)
        code, response = self.client.shareable_book_release(
            book_2['id'], {'released_at': since + 1})

        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0482')

    def test_release_not_shareable(self):
        resource = self._create_resource()
        resource_id = resource['id']
        schedule_book = {
            'resource_id': resource_id,
            'acquired_by_id': self.employee_2['id'],
        }
        code, book_1 = self.client.shareable_book_create(self.organization_id,
                                                         schedule_book)
        self.resources_collection.update_one(
            filter={
                '_id': resource_id
            },
            update={'$set': {
                'shareable': False}}
        )
        code, response = self.client.shareable_book_release(
            book_1['id'], {
                'released_at': int(datetime.utcnow().timestamp()) + 10})
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0480')

    def test_shareable_resource_list(self):
        now = int(datetime.utcnow().timestamp())
        old_since = now - DAY_SECONDS
        old_until = now - 1
        since = now + DAY_SECONDS
        until = since + DAY_SECONDS
        org_id = self.organization_id
        expected_resources = {}
        for i in range(0, 10):
            resource = self._create_resource()
            schedule_book = {
                'resource_id': resource['id'],
                'acquired_by_id': self.employee['id'],
            }
            books = []
            for j in range(0, 2):
                book_since = since if j == 1 else old_since
                book_until = until if j == 1 else old_until
                schedule_book['acquired_since'] = book_since
                schedule_book['released_at'] = book_until
                code, book = self.client.shareable_book_create(org_id,
                                                               schedule_book)
                acquired_by_id = book.pop('acquired_by').get('id')
                book['acquired_by'] = {'id': acquired_by_id,
                                       'name': self.employee['name']}
                self.assertEqual(code, 201)
                if now < book_until:
                    books.append(book)
            resource['cloud_account_name'] = self.cloud_acc_dict['name']
            resource['cloud_account_type'] = self.cloud_acc_dict['type']
            resource['pool_name'] = self.pool['name']
            resource['pool_purpose'] = self.pool['purpose']
            resource['shareable_bookings'] = books
            expected_resources[resource['id']] = resource
        code, response = self.client.shareable_resources_list(org_id)
        self.assertEqual(code, 200)
        data = response['data']
        result = {res['id']: res for res in data}
        self.assertDictEqual(result, expected_resources)

    def test_get_booking(self):
        resource = self._create_resource()
        now = int(datetime.utcnow().timestamp())
        resource_id = resource['id']
        schedule_book = {
            'resource_id': resource_id,
            'acquired_by_id': self.employee_2['id'],
            'acquired_since': now,
            'released_at': now + 1
        }
        code, book = self.client.shareable_book_create(self.organization_id,
                                                       schedule_book)
        self.assertEqual(code, 201)
        code, data = self.client.shareable_book_get(book['id'])
        self.assertEqual(code, 200)
        for k, v in schedule_book.items():
            self.assertEqual(data[k], v)

    def test_get_not_existing_booking(self):
        code, data = self.client.shareable_book_get('123')
        self.assertEqual(code, 404)
        self.assertEqual(data['error']['error_code'], 'OE0002')

        code, data = self.client.shareable_book_get(None)
        self.assertEqual(code, 404)
        self.assertEqual(data['error']['error_code'], 'OE0002')

    def test_get_deleted_booking_event(self):
        resource = self._create_resource()
        now = int(datetime.utcnow().timestamp())
        resource_id = resource['id']
        schedule_book = {
            'resource_id': resource_id,
            'acquired_by_id': self.employee_2['id'],
            'acquired_since': now,
            'released_at': now + 1
        }
        code, book = self.client.shareable_book_create(self.organization_id,
                                                       schedule_book)
        self.assertEqual(code, 201)
        p_activities_publish = patch(
            'rest_api.rest_api_server.controllers.base.'
            'BaseController.publish_activities_task').start()
        code, _ = self.client.shareable_book_delete(book['id'])
        self.assertEqual(code, 204)
        args = (resource['name'], resource['id'], 'John')
        p_activities_publish.assert_has_calls([
            call(self.organization_id, resource['id'], 'resource',
                 'shareable_resource_deleted', ANY,
                 'resource.shareable_resource_deleted', add_token=True)])

        code, data = self.client.shareable_book_get(book['id'])
        self.assertEqual(code, 404)
        self.assertEqual(data['error']['error_code'], 'OE0002')

    def test_delete_booking_from_invalid_period(self):
        resource = self._create_resource(employee_id=self.employee_2['id'])
        now = int(datetime.utcnow().timestamp())
        resource_id = resource['id']
        schedule_book = {
            'resource_id': resource_id,
            'acquired_by_id': self.employee['id'],
            'acquired_since': now - 10,
            'released_at': now + DAY_SECONDS
        }
        code, active_book = self.client.shareable_book_create(
            self.organization_id, schedule_book)
        self.assertEqual(code, 201)

        schedule_book['acquired_since'] = now - 2 * DAY_SECONDS
        schedule_book['released_at'] = now - DAY_SECONDS + 100
        code, past_book = self.client.shareable_book_create(
            self.organization_id, schedule_book)
        self.assertEqual(code, 201)

        schedule_book['acquired_since'] = now + DAY_SECONDS + 100
        schedule_book['released_at'] = now + 2 * DAY_SECONDS
        code, future_book = self.client.shareable_book_create(
            self.organization_id, schedule_book)
        self.assertEqual(code, 201)

        def side_eff(action, *args, **kwargs):
            if action == 'MANAGE_RESOURCES':
                raise OptHTTPError(403, Err.OE0234, [])
            else:
                return {}
        patch(
            'rest_api.rest_api_server.handlers.v1.base.'
            'BaseAuthHandler.check_permissions',
            side_effect=side_eff).start()

        # try to delete active booking for resource owner
        code, data = self.client.shareable_book_delete(active_book['id'])
        self.assertEqual(code, 403)
        self.assertEqual(data['error']['error_code'], 'OE0484')

        # try to delete past booking for resource owner
        code, data = self.client.shareable_book_delete(past_book['id'])
        self.assertEqual(code, 403)
        self.assertEqual(data['error']['error_code'], 'OE0484')

        # try to delete future booking for resource owner
        code, _ = self.client.shareable_book_delete(future_book['id'])
        self.assertEqual(code, 204)

    def test_delete_booking_by_org_manager(self):
        resource = self._create_resource()
        now = int(datetime.utcnow().timestamp())
        resource_id = resource['id']
        schedule_book = {
            'resource_id': resource_id,
            'acquired_by_id': self.employee_2['id'],
            'acquired_since': now - 10,
            'released_at': now + DAY_SECONDS
        }
        code, active_book = self.client.shareable_book_create(
            self.organization_id, schedule_book)
        self.assertEqual(code, 201)

        schedule_book['acquired_since'] = now - 2 * DAY_SECONDS
        schedule_book['released_at'] = now - DAY_SECONDS + 100
        code, past_book = self.client.shareable_book_create(
            self.organization_id, schedule_book)
        self.assertEqual(code, 201)

        schedule_book['acquired_since'] = now + DAY_SECONDS + 100
        schedule_book['released_at'] = now + 2 * DAY_SECONDS
        code, future_book = self.client.shareable_book_create(
            self.organization_id, schedule_book)
        self.assertEqual(code, 201)

        # try to delete active booking for organization manager
        code, _ = self.client.shareable_book_delete(active_book['id'])
        self.assertEqual(code, 204)

        # try to delete past booking for organization manager
        code, _ = self.client.shareable_book_delete(past_book['id'])
        self.assertEqual(code, 204)

        # try to delete future booking for organization manager
        code, _ = self.client.shareable_book_delete(future_book['id'])
        self.assertEqual(code, 204)

    def test_create_booking_in_past(self):
        resource = self._create_resource()
        now = int(datetime.utcnow().timestamp())
        since = now - DAY_SECONDS
        resource_id = resource['id']
        schedule_book = {
            'resource_id': resource_id,
            'acquired_by_id': self.employee_2['id'],
            'acquired_since': since,
            'released_at': now + DAY_SECONDS
        }
        self.p_get_roles_info.stop()
        user_roles = [{
            "user_id": self.auth_user,
            "role_purpose": 'optscale_engineer'
        }]
        self.p_get_roles_info = patch(
            'rest_api.rest_api_server.handlers.v1.base.BaseAuthHandler.get_roles_info',
            return_value=user_roles).start()
        code, data = self.client.shareable_book_create(
            self.organization_id, schedule_book)
        self.assertEqual(code, 403)
        self.assertEqual(data['error']['error_code'], 'OE0495')

    def test_calendar_events(self):
        calendar_sync_payload = {
            'organization_id': self.organization_id,
            'calendar_id': str(uuid.uuid4().hex)
        }
        patch('optscale_client.config_client.client.Client.google_calendar_service_enabled',
              return_value=True).start()
        patch('optscale_client.config_client.client.Client.google_calendar_service_key'
              ).start()
        code, c_sync = self.client.calendar_synchronization_create(
            calendar_sync_payload)
        self.assertEqual(code, 201)

        resource_id = self._create_resource()['id']
        schedule_book = {
            'resource_id': resource_id,
            'acquired_by_id': self.employee_2['id'],
        }
        self._mock_auth_user(self.auth_user)
        event = {'id': '123456'}
        p_create_event = patch(
            'rest_api.google_calendar_client.client.GoogleCalendarClient.create_event',
            return_value=event).start()
        dt = datetime(2021, 5, 1)
        with freeze_time(dt):
            code, booking = self.client.shareable_book_create(
                self.organization_id,  schedule_book)
        self.assertEqual(code, 201)
        expected_call = {
            'calendar_id': c_sync['calendar_id'],
            'summary': 'resource is acquired by %s' % self.employee_2['name'],
            'end': dt.replace(hour=23, minute=59, second=0,
                              microsecond=0) + timedelta(days=365),
            'start': dt,
            'description': ANY
        }
        p_create_event.assert_called_once_with(**expected_call)

        patch(
            'rest_api.google_calendar_client.client.GoogleCalendarClient.list_events',
            return_value=[event]
        ).start()
        p_update_event = patch(
            'rest_api.google_calendar_client.client.GoogleCalendarClient.update_event'
        ).start()
        dt = int(datetime.utcnow().timestamp()) + 1000
        code, response = self.client.shareable_book_release(
            booking['id'], {'released_at': dt})
        self.assertEqual(code, 200)
        p_update_event.assert_called_once_with(
            c_sync['calendar_id'], event['id'], end=datetime.fromtimestamp(dt))

        p_delete_event = patch(
            'rest_api.google_calendar_client.client.GoogleCalendarClient.delete_event'
        ).start()
        dt = datetime(2021, 5, 1)
        with freeze_time(dt):
            code, response = self.client.shareable_book_delete(booking['id'])
        self.assertEqual(code, 204)
        p_delete_event.assert_called_once_with(
            c_sync['calendar_id'], event['id'])

    def test_calendar_events_negative(self):
        calendar_sync_payload = {
            'organization_id': self.organization_id,
            'calendar_id': str(uuid.uuid4().hex)
        }
        patch('optscale_client.config_client.client.Client.google_calendar_service_enabled',
              return_value=True).start()
        patch('optscale_client.config_client.client.Client.google_calendar_service_key'
              ).start()
        code, c_sync = self.client.calendar_synchronization_create(
            calendar_sync_payload)
        self.assertEqual(code, 201)

        resource_id = self._create_resource()['id']
        schedule_book = {
            'resource_id': resource_id,
            'acquired_by_id': self.employee_2['id'],
        }
        self._mock_auth_user(self.auth_user)
        patch(
            'rest_api.google_calendar_client.client.GoogleCalendarClient.create_event',
            side_effect=CalendarException('')
        ).start()
        dt = datetime(2021, 5, 1)
        with freeze_time(dt):
            code, res = self.client.shareable_book_create(
                self.organization_id,  schedule_book)
        self.assertEqual(code, 424)
        self.assertEqual(res['error']['error_code'], 'OE0489')

        event = {'id': '123456'}
        patch('rest_api.google_calendar_client.client.GoogleCalendarClient.create_event',
              return_value=event).start()
        dt = datetime(2021, 5, 1)
        with freeze_time(dt):
            code, booking = self.client.shareable_book_create(
                self.organization_id, schedule_book)
        self.assertEqual(code, 201)

        dt = int(datetime.utcnow().timestamp()) + 1000
        patch(
            'rest_api.google_calendar_client.client.GoogleCalendarClient.list_events',
            return_value=[event]
        ).start()
        patch(
            'rest_api.google_calendar_client.client.GoogleCalendarClient.update_event',
            side_effect=CalendarException('')
        ).start()
        code, res = self.client.shareable_book_release(
            booking['id'], {'released_at': dt})
        self.assertEqual(code, 424)
        self.assertEqual(res['error']['error_code'], 'OE0491')

    def test_calendar_events_delete_no_permissions(self):
        calendar_sync_payload = {
            'organization_id': self.organization_id,
            'calendar_id': str(uuid.uuid4().hex)
        }
        patch('optscale_client.config_client.client.Client.google_calendar_service_enabled',
              return_value=True).start()
        patch('optscale_client.config_client.client.Client.google_calendar_service_key'
              ).start()
        code, c_sync = self.client.calendar_synchronization_create(
            calendar_sync_payload)
        self.assertEqual(code, 201)

        resource_id = self._create_resource()['id']
        schedule_book = {
            'resource_id': resource_id,
            'acquired_by_id': self.employee_2['id'],
        }
        self._mock_auth_user(self.auth_user)
        patch('rest_api.google_calendar_client.client.GoogleCalendarClient.create_event',
              return_value={'id': 'efgh'}).start()
        dt = datetime(2021, 5, 1)
        with freeze_time(dt):
            code, booking = self.client.shareable_book_create(
                self.organization_id, schedule_book)
        self.assertEqual(code, 201)

        event = {'id': '123456'}
        patch(
            'rest_api.google_calendar_client.client.GoogleCalendarClient.list_events',
            return_value=[event]
        ).start()
        patch(
            'rest_api.google_calendar_client.client.GoogleCalendarClient.delete_event',
            side_effect=CalendarException('')
        ).start()
        dt = datetime(2021, 5, 1)
        with freeze_time(dt):
            code, res = self.client.shareable_book_delete(booking['id'])
        self.assertEqual(code, 204)

    def test_get_bookings_for_resource(self):
        # resource without bookings
        resource = self._create_resource()
        code, response = self.client.resource_bookings_get(resource['id'])
        self.assertEqual(code, 200)
        self.assertEqual(response['bookings'], [])

        # only future and current bookings are returned
        now = int(datetime.utcnow().timestamp())
        now_until = now + DAY_SECONDS - 1
        old_since = now - DAY_SECONDS
        old_until = now - 1
        future_since = now_until + 1
        schedule_book = {
                'resource_id': resource['id'],
                'acquired_by_id': self.employee['id'],
        }
        acquired_time = [(old_since, old_until), (now, now_until),
                         (future_since, 0)]
        for since, released_at in acquired_time:
            schedule_book['acquired_since'] = since
            schedule_book['released_at'] = released_at
            code, booking = self.client.shareable_book_create(
                self.organization_id, schedule_book)
            self.assertEqual(code, 201)
        code, response = self.client.resource_bookings_get(resource['id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(response['bookings']), 2)
        for booking in response['bookings']:
            self.assertIn((booking['acquired_since'], booking['released_at']),
                          acquired_time)

    def test_get_bookings_not_existing_resource(self):
        code, response = self.client.resource_bookings_get('iamresource')
        self.assertEqual(code, 404)
        self.assertEqual(response['error']['error_code'], 'OE0002')

    def test_bookings_list_for_organization(self):
        resource = self._create_resource()
        code, response = self.client.resource_bookings_get(resource['id'])
        self.assertEqual(code, 200)
        self.assertEqual(response['bookings'], [])

        now = int(datetime.utcnow().timestamp())
        now_until = now + DAY_SECONDS - 1
        old_since = now - DAY_SECONDS
        old_until = now - 1
        future_since = now_until + 1
        schedule_book = {
            'resource_id': resource['id'],
            'acquired_by_id': self.employee['id'],
        }
        acquired_time = [(old_since, old_until), (now, now_until),
                         (future_since, 0)]
        for since, released_at in acquired_time:
            schedule_book['acquired_since'] = since
            schedule_book['released_at'] = released_at
            code, booking = self.client.shareable_book_create(
                self.organization_id, schedule_book)
            self.assertEqual(code, 201)

        # changed bookings for last hour
        start_date = now - 3600
        code, resp = self.client.shareable_book_list(
            self.organization_id, start_date=start_date, end_date=now)
        self.assertEqual(code, 200)
        bookings = resp['data']
        self.assertEqual(len(bookings), 2)
        self.assertEqual(bookings[0]['released_at'], old_until)
        self.assertEqual(bookings[1]['acquired_since'], now)

    def test_patch_current_booking(self):
        resource = self._create_resource()
        resource_id = resource['id']
        now = int(datetime.utcnow().timestamp())
        since = now - DAY_SECONDS
        until = now - 100
        schedule_book = {
            'resource_id': resource_id,
            'acquired_by_id': self.employee_2['id'],
            'acquired_since': since,
            'released_at': until,
        }
        code, book_1 = self.client.shareable_book_create(self.organization_id,
                                                         schedule_book)
        self.assertEqual(code, 201)

        def side_eff(action, *args, **kwargs):
            if action == 'MANAGE_RESOURCES':
                raise OptHTTPError(403, Err.OE0234, [])
            else:
                return {}
        patch(
            'rest_api.rest_api_server.handlers.v1.base.'
            'BaseAuthHandler.check_permissions',
            side_effect=side_eff).start()

        code, response = self.client.shareable_book_release(
            book_1['id'], {'released_at': now - 1})

        self.assertEqual(code, 403)
        self.assertEqual(response['error']['error_code'], 'OE0234')

        schedule_book_2 = {
            'resource_id': resource_id,
            'acquired_by_id': self.employee['id'],
            'acquired_since': until + 1,
            'released_at': 0,
        }
        code, book_2 = self.client.shareable_book_create(self.organization_id,
                                                         schedule_book_2)
        self.assertEqual(code, 201)

        code, response = self.client.shareable_book_release(
            book_2['id'], {'released_at': now + 100})

        self.assertEqual(code, 403)
        self.assertEqual(response['error']['error_code'], 'OE0498')

        code, response = self.client.shareable_book_release(
            book_2['id'], {'released_at': now - 1})

        self.assertEqual(code, 200)

    def test_book_employee_permissions(self):
        patch('rest_api.rest_api_server.controllers.shareable_resource.'
              'ShareableBookingController.auth_client').start()
        resource_id = self._create_resource()['id']
        schedule_book = {
            'resource_id': resource_id,
            'acquired_by_id': self.employee_2['id'],
        }
        self.p_validate_employee.stop()
        patch(
            'rest_api.rest_api_server.controllers.shareable_resource.'
            'ShareableBookingController.auth_client.authorize_user_list',
            return_value=(200, {self.auth_user_2: []})).start()
        code, resp = self.client.shareable_book_create(self.organization_id,
                                                       schedule_book)
        self.assertEqual(code, 403)
        self.verify_error_code(resp, 'OE0505')

        patch(
            'rest_api.rest_api_server.controllers.shareable_resource.'
            'ShareableBookingController.auth_client.authorize_user_list',
            return_value=(200, {
                self.auth_user_2: ['BOOK_ENVIRONMENTS'],
            })).start()
        code, resp = self.client.shareable_book_create(self.organization_id,
                                                       schedule_book)
        self.assertEqual(code, 201)

    def test_book_with_ssh_key_id(self):
        resource_id = self._create_resource()['id']
        resource_id_2 = self._create_resource()['id']
        code, ssh_key1 = self.client.ssh_key_create(
            self.employee['id'], {'name': 'k1', 'key': 'ssh AAAAC3Nz ubuntu'})
        self.assertEqual(code, 201)
        code, ssh_key2 = self.client.ssh_key_create(
            self.employee['id'], {'name': 'k1', 'key': 'ssh AAAAC3Nk ubuntu'})
        self.assertEqual(code, 201)

        schedule_book = {
            'resource_id': resource_id,
            'acquired_by_id': self.employee['id'],
            'ssh_key_id': ssh_key2['id']
        }
        code, resp = self.client.shareable_book_create(self.organization_id,
                                                       schedule_book)
        self.assertEqual(code, 201)
        self.assertEqual(json.loads(resp['ssh_key']), ssh_key2)

        schedule_book = {
            'resource_id': resource_id_2,
            'acquired_by_id': self.employee['id'],
            'ssh_key_id': ssh_key1['id']
        }
        code, resp = self.client.shareable_book_create(self.organization_id,
                                                       schedule_book)
        self.assertEqual(code, 201)
        self.assertEqual(json.loads(resp['ssh_key']), ssh_key1)

    def test_book_with_wrong_ssh_key_id(self):
        resource_id = self._create_resource()['id']
        self._mock_auth_user(self.auth_user_2)
        code, ssh_key1 = self.client.ssh_key_create(
            self.employee_2['id'], {'name': 'k1', 'key': 'ssh AAAAC3Nz ubuntu'})
        self.assertEqual(code, 201)
        self._mock_auth_user(self.auth_user)

        schedule_book = {
            'resource_id': resource_id,
            'acquired_by_id': self.employee['id'],
            'ssh_key_id': ssh_key1['id']
        }
        code, resp = self.client.shareable_book_create(self.organization_id,
                                                       schedule_book)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0510')

        schedule_book['ssh_key_id'] = str(uuid.uuid4())
        code, resp = self.client.shareable_book_create(self.organization_id,
                                                       schedule_book)
        self.assertEqual(code, 404)
        self.verify_error_code(resp, 'OE0002')

    def test_book_for_another_employee(self):
        resource_id = self._create_resource()['id']
        code, ssh_key1 = self.client.ssh_key_create(
            self.employee['id'],  {'name': 'k1', 'key': 'ssh AAAAC3Nz ubuntu'})
        self.assertEqual(code, 201)
        self._mock_auth_user(self.auth_user_2)
        code, ssh_key2 = self.client.ssh_key_create(
            self.employee_2['id'], {'name': 'k1', 'key': 'ssh AAAAC3Nt ubuntu'})
        self.assertEqual(code, 201)
        code, ssh_key3 = self.client.ssh_key_create(
            self.employee_2['id'],  {'name': 'k1', 'key': 'ssh AAAAC3Nk ubuntu'})
        self.assertEqual(code, 201)
        self._mock_auth_user(self.auth_user)

        schedule_book = {
            'resource_id': resource_id,
            'acquired_by_id': self.employee_2['id'],
            'ssh_key_id': ssh_key1['id']
        }
        code, resp = self.client.shareable_book_create(self.organization_id,
                                                       schedule_book)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0510')

        schedule_book['ssh_key_id'] = ssh_key3['id']
        code, resp = self.client.shareable_book_create(self.organization_id,
                                                       schedule_book)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0511')

        schedule_book['ssh_key_id'] = ssh_key2['id']
        code, resp = self.client.shareable_book_create(self.organization_id,
                                                       schedule_book)
        self.assertEqual(code, 201)

    def test_book_ssh_only(self):
        code, resource = self.environment_resource_create(
            self.organization_id, {
                'name': 'resource',
                'resource_type': 'some_env_type',
                'tags': {},
            })
        self.assertEqual(code, 201)
        code, _ = self.client.environment_resource_update(
            resource['id'], {'ssh_only': True})
        self.assertEqual(code, 200)
        schedule_book = {
            'resource_id': resource['id'],
            'acquired_by_id': self.employee['id'],
        }
        code, resp = self.client.shareable_book_create(self.organization_id,
                                                       schedule_book)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0216')

        code, ssh_key1 = self.client.ssh_key_create(
            self.employee['id'], {'name': 'k1', 'key': 'ssh AAAAC3Nz ubuntu'})
        self.assertEqual(code, 201)
        schedule_book['ssh_key_id'] = ssh_key1['id']
        code, resp = self.client.shareable_book_create(self.organization_id,
                                                       schedule_book)
        self.assertEqual(code, 201)

    def test_get_shareable_resource_details(self):
        resource_id = self._create_resource()['id']
        code, detailed_resource = self.client.environment_resource_get(
            resource_id, details=True)
        self.assertEqual(code, 200)
        not_shareable_res_id = self._create_resource(is_shareable=False)['id']
        code, detailed_resource = self.client.environment_resource_get(
            not_shareable_res_id, details=True)
        self.assertEqual(code, 404)

    def test_autorelease(self):
        for autorelease in [True, False]:
            resource = self._create_resource(employee_id=self.employee['id'])
            now = int(datetime.utcnow().timestamp())
            resource_id = resource['id']
            schedule_book = {
                'resource_id': resource_id,
                'acquired_by_id': self.employee['id'],
                'acquired_since': now - 10,
                'released_at': 0,
                'jira_auto_release': autorelease
            }
            code, active_book = self.client.shareable_book_create(
                self.organization_id, schedule_book)
            self.assertEqual(code, 201)

            attachment_params = {
                'shareable_booking_id': active_book['id'], 'issue_number': 123,
                'auto_detach_status': 'Done', 'client_key': 'test_client',
                'project_key': 'test_project', 'issue_link': 'test_link',
                'status': 'Done',
            }
            code, attachment = self.client.jira_issue_attachment_create(
                self.organization_id, attachment_params)
            self.assertEqual(code, 201)

            code, _ = self.client.jira_issue_attachment_update(
                attachment['id'], {'status': 'another'})
            self.assertEqual(code, 200)

            code, resp = self.client.shareable_book_get(active_book['id'])
            self.assertEqual(code, 200)
            self.assertEqual(resp['id'], active_book['id'])
            self.assertEqual(len(resp['jira_issue_attachments']), 1)
            self.assertEqual(resp['jira_issue_attachments'][0]['id'],
                             attachment['id'])
            self.assertEqual(resp['released_at'], 0)

            code, _ = self.client.jira_issue_attachment_update(
                attachment['id'], {'status': 'Done'})
            self.assertEqual(code, 200)

            code, resp = self.client.shareable_book_get(active_book['id'])
            self.assertEqual(code, 200)
            self.assertEqual(resp['id'], active_book['id'])
            self.assertEqual(len(resp['jira_issue_attachments']), 0)
            self.assertTrue(bool(resp['released_at']) == autorelease)
