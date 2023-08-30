import uuid
from datetime import datetime
from freezegun import freeze_time
from pymongo import UpdateOne
from unittest.mock import patch, ANY

from rest_api.rest_api_server.models.db_factory import DBFactory, DBType
from rest_api.rest_api_server.models.db_base import BaseDB
from rest_api.rest_api_server.models.models import Checklist
from rest_api.rest_api_server.tests.unittests.test_api_base import TestApiBase
from rest_api.rest_api_server.utils import encoded_tags

DEFAULT_CACHE_TIME = 900


class TestCloudResourceApi(TestApiBase):

    def setUp(self, version='v2'):
        super().setUp(version)
        patch('rest_api.rest_api_server.controllers.cloud_account.'
              'CloudAccountController._configure_report').start()
        _, self.org = self.client.organization_create({'name': "organization"})
        self.client.pool_update(self.org['pool_id'], {'limit': 100})
        self.org_id = self.org['id']
        self.auth_user_1 = self.gen_id()
        _, self.employee_1 = self.client.employee_create(
            self.org['id'], {'name': 'employee_1',
                             'auth_user_id': self.auth_user_1})
        self.update_default_owner_for_pool(self.org['pool_id'],
                                           self.employee_1['id'])
        aws_cloud_acc = {
            'name': 'my cloud_acc',
            'type': 'aws_cnr',
            'config': {
                'access_key_id': 'key',
                'secret_access_key': 'secret',
                'config_scheme': 'create_report'
            }
        }
        _, self.cloud_acc = self.create_cloud_account(
            self.org_id, aws_cloud_acc, auth_user_id=self.auth_user_1)
        self.cloud_acc_id = self.cloud_acc['id']
        self.valid_resource = {
            'cloud_resource_id': 'res_id',
            'name': 'resource',
            'resource_type': 'test_type',
            'region': 'test_region',
            'tags': {
                'key': 'value'
            }
        }
        user_roles = [{
            "user_id": self.auth_user_1,
            "role_purpose": 'optscale_manager'
        }]
        self.p_get_roles_info = patch(
            'rest_api.rest_api_server.handlers.v1.base.BaseAuthHandler.get_roles_info',
            return_value=user_roles).start()

    def extend_expenses(self, expenses):
        self.expenses.extend(expenses)
        resource_ids = list(map(lambda x: x['resource_id'], expenses))
        self.update_resource_info_by_expenses(resource_ids)

    def _add_calendar(self):
        patch('rest_api.rest_api_server.controllers.calendar_synchronization.'
              'CalendarSynchronizationController._check_calendar_availability').start()
        patch('optscale_client.config_client.client.Client.google_calendar_service_enabled',
              return_value=True).start()
        patch('optscale_client.config_client.client.Client.google_calendar_service_key').start()
        patch('rest_api.google_calendar_client.client.GoogleCalendarClient.create_event',
              return_value={'id': 'abcd'}).start()
        valid_calendar_sync_payload = {
            'organization_id': self.org_id,
            'calendar_id': str(uuid.uuid4().hex)
        }
        code, c_sync = self.client.calendar_synchronization_create(
            valid_calendar_sync_payload)
        self.assertEqual(code, 201)
        return c_sync

    def test_resource_values(self):
        code, resource = self.cloud_resource_create(
            self.cloud_acc_id, {
                'cloud_resource_id': 'res_id',
                'resource_type': 'test',
            })
        self.assertIsNotNone(resource['id'])
        mongo_resource = next(self.resources_collection.aggregate([
            {'$match': {'_id': resource['id']}}
        ]))
        self.assertEqual(mongo_resource['_id'], resource['id'])
        for req_field in [
            'cloud_resource_id', 'cloud_account_id', 'resource_type',
            'deleted_at', 'created_at', 'first_seen', 'last_seen',
            'employee_id', 'pool_id',
        ]:
            self.assertEqual(mongo_resource[req_field], resource[req_field])
        for opt_field in ['name', 'region', 'meta']:
            self.assertTrue(opt_field in resource)
            self.assertFalse(opt_field in mongo_resource)
            default_values = {
                'meta': {'cloud_console_link': None}, 'tags': {}
            }
            self.assertEqual(
                resource[opt_field], default_values.get(opt_field))

    def test_create_resource(self):
        code, resource = self.cloud_resource_create(self.cloud_acc_id,
                                                    self.valid_resource)
        self.assertEqual(code, 201)
        for k, v in self.valid_resource.items():
            self.assertEqual(resource[k], v)

    def test_create_missing_required(self):
        params = self.valid_resource.copy()
        del params['resource_type']
        code, ret = self.cloud_resource_create(self.cloud_acc_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(ret['error']['reason'],
                         'resource_type is not provided')

    def test_create_unexpected(self):
        params = self.valid_resource.copy()
        params['dot'] = '1'
        code, ret = self.cloud_resource_create(self.cloud_acc_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(ret['error']['reason'],
                         "Unexpected parameters: ['dot']")

    def test_create_wrong_format(self):
        params = self.valid_resource.copy()
        params['resource_type'] = 1
        code, ret = self.cloud_resource_create(self.cloud_acc_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(ret['error']['reason'],
                         'resource_type should be a string')

    def test_patch(self):
        code, resource = self.cloud_resource_create(self.cloud_acc_id,
                                                    self.valid_resource)
        self.assertEqual(code, 201)
        resource.pop('assignment_history', None)

        params = {'name': 'test'}
        code, ret = self.client.cloud_resource_update(resource['id'], params)
        self.assertEqual(code, 200)
        resource.update(params)
        self.assertDictEqual(ret, resource)

        params = {'env_properties': {'field': 'value'}}
        code, ret = self.client.cloud_resource_update(resource['id'], params)
        self.assertEqual(code, 400)
        self.assertEqual(ret['error']['error_code'], 'OE0480')

    def test_patch_env_property_activities_task(self):
        patch('rest_api.rest_api_server.controllers.base.'
              'BaseController.publish_activities_task').start()
        env_alert = {
            'based': 'env_change',
            'pool_id': self.org['pool_id'],
            'contacts': [{'slack_channel_id': 'superchannel',
                          'slack_team_id': 'superteam'}],
            'threshold': 0
        }
        code, pool_alert = self.client.alert_create(self.org_id, env_alert)
        self.assertEqual(code, 201)
        code, resource = self.cloud_resource_create(self.cloud_acc_id,
                                                    self.valid_resource)
        self.assertEqual(code, 201)
        self.resources_collection.update_one(
            filter={'_id': resource['id']},
            update={'$set': {'shareable': True}}
        )

        p_disp_task = patch('rest_api.rest_api_server.controllers.base.'
                            'BaseController.publish_activities_task').start()
        params = {'env_properties': {'field': 'value'}}
        resource['shareable'] = True
        code, ret = self.client.cloud_resource_update(resource['id'], params)
        self.assertEqual(code, 200)
        meta = {
                'alert_id': pool_alert['id'],
                'env_properties': ANY
        }
        p_disp_task.assert_called_once_with(
            self.org_id, resource['id'], 'resource', 'env_property_updated',
            meta, 'alert.violation.env_change')

    def test_patch_env_property_activities_task_with_employee_contact(self):
        patch('rest_api.rest_api_server.controllers.base.'
              'BaseController.publish_activities_task').start()
        env_alert = {
            'based': 'env_change',
            'pool_id': self.org['pool_id'],
            'contacts': [{'employee_id': self.employee_1['id']}],
            'threshold': 0
        }
        code, pool_alert = self.client.alert_create(self.org_id, env_alert)
        self.assertEqual(code, 201)
        code, resource = self.cloud_resource_create(self.cloud_acc_id,
                                                    self.valid_resource)
        self.assertEqual(code, 201)
        self.resources_collection.update_one(
            filter={'_id': resource['id']},
            update={'$set': {'shareable': True}}
        )

        p_disp_task = patch('rest_api.rest_api_server.controllers.base.'
                            'BaseController.publish_activities_task').start()
        params = {'env_properties': {'field': 'value'}}
        resource['shareable'] = True
        code, ret = self.client.cloud_resource_update(resource['id'], params)
        self.assertEqual(code, 200)
        meta = {
                'alert_id': pool_alert['id'],
                'env_properties': ANY
        }
        p_disp_task.assert_called_once_with(
            self.org_id, resource['id'], 'resource', 'env_property_updated',
            meta, 'alert.violation.env_change')

    def test_patch_pool_id(self):
        code, resource = self.cloud_resource_create(self.cloud_acc_id,
                                                    self.valid_resource)
        self.assertEqual(code, 201)

        params = {'pool_id': self.org['pool_id']}
        code, res = self.client.cloud_resource_update(resource['id'], params)
        self.assertEqual(code, 200)
        self.assertEqual(res['pool_id'], self.org['pool_id'])

        params = {'pool_id': 'fake'}
        code, res = self.client.cloud_resource_update(resource['id'], params)
        self.assertEqual(code, 400)
        self.verify_error_code(res, 'OE0002')

        code, pool_deleted = self.client.pool_create(
            self.org['id'], {'name': 'pool_deleted', 'limit': 5,
                             'parent_id': self.org['pool_id']})
        code, _ = self.client.pool_delete(pool_deleted['id'])
        self.assertEqual(code, 204)
        params = {'pool_id': pool_deleted['id']}
        code, res = self.client.cloud_resource_update(resource['id'], params)
        self.assertEqual(code, 400)
        self.verify_error_code(res, 'OE0002')

    def test_patch_employee_id(self):
        code, resource = self.cloud_resource_create(self.cloud_acc_id,
                                                    self.valid_resource)
        self.assertEqual(code, 201)

        params = {'employee_id': self.employee_1['id']}
        code, res = self.client.cloud_resource_update(resource['id'], params)
        self.assertEqual(code, 200)
        self.assertEqual(res['employee_id'], self.employee_1['id'])

        params = {'employee_id': 'fake'}
        code, res = self.client.cloud_resource_update(resource['id'], params)
        self.assertEqual(code, 400)
        self.verify_error_code(res, 'OE0002')

        auth_user = self.gen_id()
        code, employee_deleted = self.client.employee_create(
            self.org['id'], {'name': 'employee_deleted',
                             'auth_user_id': auth_user})
        patch('rest_api.rest_api_server.controllers.employee.EmployeeController.'
              'get_org_manager_user', return_value=auth_user).start()
        code, _ = self.client.employee_delete(employee_deleted['id'])
        self.assertEqual(code, 204)
        params = {'employee_id': employee_deleted['id']}
        code, res = self.client.cloud_resource_update(resource['id'], params)
        self.assertEqual(code, 400)
        self.verify_error_code(res, 'OE0002')

    def test_patch_shareable(self):
        code, resource = self.cloud_resource_create(self.cloud_acc_id,
                                                    self.valid_resource)
        self.assertEqual(code, 201)

        params = {'shareable': False}
        code, resp = self.client.cloud_resource_update(resource['id'], params)
        self.assertEqual(code, 200)
        self.assertEqual(resp['shareable'], False)

        params = {'shareable': True}
        code, resp = self.client.cloud_resource_update(resource['id'], params)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0479')

        params = {'shareable': 'no'}
        code, resp = self.client.cloud_resource_update(resource['id'], params)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0226')

    def test_patch_environment(self):
        env_resource = {
            'name': 'resource',
            'resource_type': 'some_env_type',
            'tags': {}
        }
        code, resource = self.environment_resource_create(
            self.org_id, env_resource)
        self.assertEqual(code, 201)
        self.assertTrue(resource['shareable'])
        self.assertTrue(resource['is_environment'])

        params = {'shareable': False}
        code, response = self.client.cloud_resource_update(resource['id'], params)
        self.assertEqual(code, 400)
        self.verify_error_code(response, 'OE0488')

        params = {'env_properties': {'field': 'value'}}
        code, response = self.client.cloud_resource_update(resource['id'], params)
        self.assertEqual(code, 200)
        history_len = self.property_history_collection.count()
        self.assertEqual(history_len, 1)

    def test_properties_with_dots(self):
        env_resource = {
            'name': 'resource',
            'resource_type': 'some_env_type',
            'tags': {}
        }
        code, resource = self.environment_resource_create(
            self.org_id, env_resource)
        self.assertEqual(code, 201)
        self.assertTrue(resource['shareable'])
        self.assertTrue(resource['is_environment'])

        params = {'env_properties': {'field.1': 'value'}}
        code, response = self.client.cloud_resource_update(resource['id'], params)
        self.assertEqual(code, 200)
        history_len = self.property_history_collection.count()
        self.assertEqual(history_len, 1)

    def test_patch_shareable_with_bookings(self):
        patch('rest_api.rest_api_server.controllers.shareable_resource.'
              'ShareableBookingController.publish_task').start()
        self._mock_auth_user(self.auth_user_1)
        res = self.valid_resource.copy()
        res['resource_type'] = 'Instance'
        code, resource = self.cloud_resource_create(self.cloud_acc_id, res)
        self.assertEqual(code, 201)
        seen_time = int(datetime.utcnow().timestamp() - 5)
        self.resources_collection.bulk_write([UpdateOne(
            filter={'_id': resource['id']},
            update={'$set': {'last_seen': seen_time, 'active': True}})])
        code, data = self.client.resources_bulk_share(self.org_id,
                                                      [resource['id']])
        self.assertEqual(code, 201)
        schedule_book = {
            'resource_id': resource['id'],
            'acquired_by_id': self.employee_1['id'],
        }
        code, book = self.client.shareable_book_create(self.org_id,
                                                       schedule_book)
        self.assertEqual(code, 201)
        calendar = self._add_calendar()

        params = {'shareable': False}
        with patch('rest_api.rest_api_server.controllers.calendar_synchronization.'
                   'CalendarSynchronizationController.delete_calendar_event_by_id'
                   ) as p_delete_event:
            code, resp = self.client.cloud_resource_update(resource['id'], params)
            self.assertEqual(code, 200)
            self.assertEqual(resp['shareable'], False)
            p_delete_event.assert_called_once_with(
                ANY, 'abcd')
        code, data = self.client.shareable_book_get(book['id'])
        self.assertEqual(code, 404)

        code, resp = self.client.cloud_resource_get(resource['id'], True)
        self.assertEqual(code, 200)
        self.assertIsNone(resp['details']['env_properties_collector_link'])

    def test_delete(self):
        code, resource = self.cloud_resource_create(self.cloud_acc_id,
                                                    self.valid_resource)
        self.assertEqual(code, 201)
        resource.pop('assignment_history', None)

        code, get_cloud_acc = self.client.cloud_resource_get(resource['id'])
        self.assertEqual(code, 200)
        self.assertDictEqual(get_cloud_acc, resource)

        code, _ = self.client.cloud_resource_delete(resource['id'])
        self.assertEqual(code, 204)

        code, _ = self.client.cloud_resource_get(resource['id'])
        self.assertEqual(code, 404)

    def test_list(self):
        code, resource = self.cloud_resource_create(self.cloud_acc_id,
                                                    self.valid_resource)
        self.assertEqual(code, 201)

        code, resource_list = self.client.cloud_resource_list(self.cloud_acc_id)
        self.assertEqual(code, 200)
        self.assertEqual(len(resource_list['resources']), 1)

        valid_resource_2 = self.valid_resource
        valid_resource_2['cloud_resource_id'] = 'res_id2'
        code, resource2 = self.cloud_resource_create(self.cloud_acc_id,
                                                     self.valid_resource)
        self.assertEqual(code, 201)

        new_cloud_acc = {
            'name': 'my new cloud_acc',
            'type': 'aws_cnr',
            'config': {
                'access_key_id': 'key',
                'secret_access_key': 'secret',
                'config_scheme': 'create_report'
            }
        }
        code, cloud_acc2 = self.create_cloud_account(self.org_id,
                                                     new_cloud_acc)
        self.assertEqual(code, 201)
        code, resource2 = self.cloud_resource_create(cloud_acc2['id'],
                                                     self.valid_resource)
        self.assertEqual(code, 201)

        code, resource_list = self.client.cloud_resource_list(self.cloud_acc_id)
        self.assertEqual(code, 200)
        self.assertEqual(len(resource_list['resources']), 2)

        code, resource_list = self.client.cloud_resource_list(
            cloud_acc2['id'],
            cloud_resource_id=self.valid_resource['cloud_resource_id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(resource_list['resources']), 1)

        code, _ = self.client.cloud_resource_list('bad_ca_id')
        self.assertEqual(code, 404)

    def test_create_resource_with_invalid_employee_and_pool(self):
        params = {
            'cloud_resource_id': 'res_id',
            'name': 'resource',
            'resource_type': 'test',
            'employee_id': str(uuid.uuid4()),
            'pool_id': str(uuid.uuid4())
        }
        code, resource = self.cloud_resource_create(
            self.cloud_acc_id, params, set_allowed=False)
        self.assertEqual(code, 201)
        # assigned to (root pool - root pool default owner)
        self.assertEqual(resource.get('employee_id'), self.employee_1['id'])
        self.assertEqual(resource.get('pool_id'), self.org['pool_id'])

    def test_create_resource_with_employee_and_pool(self):
        # valid pool, valid employee
        code, employee = self.client.employee_create(self.org_id,
                                                     {'name': 'John Smith'})
        params = {
            'cloud_resource_id': str(uuid.uuid4()),
            'name': 'resource',
            'resource_type': 'test',
            'employee_id': employee['id'],
            'pool_id': self.org['pool_id']
        }
        code, resource = self.cloud_resource_create(
            self.cloud_acc_id, params)
        self.assertEqual(code, 201)
        self.assertEqual(resource['employee_id'], employee['id'])
        self.assertEqual(resource['pool_id'], self.org['pool_id'])

        _, sub1 = self.client.pool_create(self.org_id, {
            'name': "sub1", 'parent_id': self.org['pool_id'],
            'limit': 50})
        _, sub2 = self.client.pool_create(self.org_id, {
            'name': "sub2", 'parent_id': sub1['id']})
        params = {
            'cloud_resource_id': str(uuid.uuid4()),
            'name': 'resource',
            'resource_type': 'test',
            'employee_id': employee['id'],
            'pool_id': sub2['id']
        }
        code, resource = self.cloud_resource_create(
            self.cloud_acc_id, params)
        self.assertEqual(code, 201)
        self.assertEqual(resource['employee_id'], employee['id'])
        self.assertEqual(resource['pool_id'], sub2['id'])

        _, sub3 = self.client.pool_create(self.org_id, {
            'name': "sub3", 'parent_id': sub1['id'], 'limit': 10})

        params = {
            'cloud_resource_id': str(uuid.uuid4()),
            'name': 'resource',
            'resource_type': 'test',
            'employee_id': employee['id'],
            'pool_id': sub3['id']
        }
        code, resource = self.cloud_resource_create(
            self.cloud_acc_id, params)
        self.assertEqual(resource['employee_id'], employee['id'])
        self.assertEqual(resource['pool_id'], sub3['id'])

        # valid employee, another org pool
        _, new_org = self.client.organization_create({'name': "new org"})
        params = {
            'cloud_resource_id': str(uuid.uuid4()),
            'name': 'resource',
            'resource_type': 'test',
            'employee_id': employee['id'],
            'pool_id': new_org['pool_id']
        }
        code, resource = self.cloud_resource_create(
            self.cloud_acc_id, params, set_allowed=False)
        self.assertEqual(code, 201)
        # assigned to (root pool - root pool default owner)
        self.assertEqual(resource.get('employee_id'), self.employee_1['id'])
        self.assertEqual(resource.get('pool_id'), self.org['pool_id'])

    def test_create_without_name(self):
        params = self.valid_resource.copy()
        del params['name']
        code, ret = self.cloud_resource_create(self.cloud_acc_id, params)
        self.assertEqual(code, 201)
        self.assertIsNone(ret.get('name'))

    def test_create_preinstalled(self):
        params = self.valid_resource.copy()
        params['resource_type'] = 'Instance'
        params['meta'] = {'preinstalled': 'NA'}
        code, res = self.cloud_resource_create(self.cloud_acc_id, params)
        self.assertEqual(code, 201)
        self.assertEqual(res['meta']['preinstalled'],
                         params['meta']['preinstalled'])
        self.assertIsNone(res.get('preinstalled'))

    def test_create_field_from_meta(self):
        params = self.valid_resource.copy()
        params['resource_type'] = 'Snapshot Chain'
        params['meta'] = {'size': 123}
        code, res = self.cloud_resource_create(self.cloud_acc_id, params)
        self.assertEqual(code, 201)
        self.assertEqual(res['meta']['size'],
                         params['meta']['size'])
        self.assertIsNone(res.get('size'))

    def test_cloud_resource_id_range(self):
        params = {
            'name': 'resource',
            'resource_type': 'test'
        }
        for x in [0, 513]:
            params['cloud_resource_id'] = ''.join('1' for i in range(x))
            code, resource = self.cloud_resource_create(
                self.cloud_acc_id, params)
            self.assertEqual(code, 400)
            self.verify_error_code(resource, 'OE0215')
        for x in [1, 512]:
            params['cloud_resource_id'] = ''.join('1' for i in range(x))
            code, resource = self.cloud_resource_create(
                self.cloud_acc_id, params)
            self.assertEqual(code, 201)

    def add_cached_resource(self, resource_ids, valid_until=None, active=True):
        last_seen = int(datetime.utcnow().timestamp())
        if valid_until:
            active = valid_until > last_seen
            last_seen = valid_until - DEFAULT_CACHE_TIME
        self.resources_collection.update_many(
            filter={
                '_id': {'$in': resource_ids}
            },
            update={'$set': {'last_seen': last_seen, 'active': active}}
        )

    def add_recommendations(self, resource_id, modules, timestamp=None,
                            last_check=None, checklist=True):
        if not timestamp:
            timestamp = int(datetime.utcnow().timestamp())

        recommendations = {
            'modules': modules,
            'run_timestamp': timestamp
        }
        db = DBFactory(DBType.Test, None).db
        engine = db.engine
        session = BaseDB.session(engine)()
        if not last_check:
            last_check = timestamp
        if checklist:
            record = Checklist(
                organization_id=self.org_id,
                last_run=last_check,
                last_completed=last_check
            )
            session.add(record)
            session.commit()
        self.resources_collection.update_one(
            filter={
                '_id': resource_id
            },
            update={'$set': {'recommendations': recommendations}}
        )

    def test_get_cloud_resource(self):
        code, employee = self.client.employee_create(self.org_id,
                                                     {'name': 'John Smith'})
        resource_dict = {
            'cloud_resource_id': str(uuid.uuid4()),
            'name': 'resource',
            'resource_type': 'instance',
            'employee_id': employee['id'],
            'pool_id': self.org['pool_id'],
            'region': 'us-east',
            'service_name': 'service'
        }
        with freeze_time(datetime(2020, 2, 14)):
            _, resource = self.cloud_resource_create(
                self.cloud_acc_id, resource_dict)
            code, response = self.client.cloud_resource_get(resource['id'])
            self.assertEqual(code, 200)
            code, response = self.client.cloud_resource_get(
                resource['id'], details=True)
            self.assertEqual(code, 200)
            self.assertEqual(
                resource['created_at'], response['details']['last_seen'])
            for k, v in resource_dict.items():
                self.assertEqual(response[k], v)
        with freeze_time(datetime(2020, 2, 28)):
            expenses = [
                {
                    'cost': 650,
                    'date': datetime(2020, 1, 14),
                    'cloud_account_id': self.cloud_acc_id,
                    'resource_id': resource['id'],
                    'sign': 1
                },
                {
                    'cost': 300, 'date': datetime(2020, 2, 15),
                    'cloud_account_id': self.cloud_acc_id,
                    'resource_id': resource['id'],
                    'sign': 1
                },
                {
                    'cost': 50,
                    'date': datetime(2020, 2, 16),
                    'cloud_account_id': self.cloud_acc_id,
                    'resource_id': resource['id'],
                    'sign': 1
                },
                {
                    'cost': 150,
                    'date': datetime(2020, 2, 16),
                    'cloud_account_id': self.cloud_acc_id,
                    'resource_id': 'res_3_id',
                    'sign': 1
                }
            ]
            self.extend_expenses(expenses)

            code, response = self.client.cloud_resource_get(
                resource['id'], details=True)
            self.assertEqual(code, 200)
            for k, v in resource_dict.items():
                self.assertEqual(response[k], v)
            details = response.get('details')
            self.assertIsNotNone(details)
            self.assertEqual(details['cost'], 350)
            self.assertEqual(details['cloud_type'], self.cloud_acc['type'])
            self.assertEqual(datetime.fromtimestamp(details['last_seen']),
                             datetime(2020, 2, 16))
            self.assertEqual(details['forecast'], 350)
            self.assertEqual(datetime.fromtimestamp(details['first_seen']),
                             datetime(2020, 1, 14))
            self.assertEqual(details['region'], 'us-east')
            self.assertEqual(details['owner_name'], employee['name'])
            self.assertEqual(details['cloud_name'], self.cloud_acc['name'])
            self.assertEqual(details['service_name'], 'service')
            self.assertEqual(details['total_cost'], 1000)
            self.assertEqual(details['pool_name'], self.org['name'])
            self.assertEqual(details['pool_purpose'], 'business_unit')

            self.add_cached_resource(
                [resource['id'], 'res_3_id'], datetime.utcnow().timestamp() + 500)
            self.add_cached_resource(
                [resource['id'], 'res_3_id'], datetime.utcnow().timestamp() + 1000)
            code, response = self.client.cloud_resource_get(
                resource['id'], details=True)
        details = response.get('details')
        # we updated last seen in 100 (1000 - 900(default cache)) seconds
        self.assertEqual(datetime.fromtimestamp(details['last_seen']),
                         datetime(2020, 2, 28, 0, 1, 40))
        code, response = self.client.cloud_resource_get(
            resource['id'], details=True)
        self.assertEqual(code, 200)
        self.assertTrue(isinstance(response['created_at'], int))
        for k, v in resource_dict.items():
            self.assertEqual(response[k], v)
        details = response.get('details')
        self.assertEqual(details['cost'], 0)
        self.assertEqual(details['cloud_type'], self.cloud_acc['type'])
        self.assertEqual(details['forecast'], 0)
        self.assertEqual(details['region'], 'us-east')
        self.assertEqual(details['owner_name'], employee['name'])
        self.assertEqual(details['cloud_name'], self.cloud_acc['name'])
        self.assertEqual(details['service_name'], 'service')
        self.assertEqual(details['total_cost'], 1000)
        self.assertEqual(details['pool_name'], self.org['name'])
        self.assertEqual(details['pool_purpose'], 'business_unit')

    def test_get_environment_resource(self):
        code, employee = self.client.employee_create(
            self.org_id, {'name': 'John Smith'})
        resource_dict = {
            'name': 'resource',
            'resource_type': 'instance',
            'employee_id': employee['id'],
            'pool_id': self.org['pool_id']
        }
        with freeze_time(datetime(2020, 2, 14)):
            _, resource = self.environment_resource_create(
                self.org_id, resource_dict, set_allowed=True)
            code, _ = self.client.cloud_resource_get(resource['id'])
            self.assertEqual(code, 200)
            code, response = self.client.cloud_resource_get(
                resource['id'], details=True)
            self.assertEqual(code, 200)
            self.assertEqual(
                resource['created_at'], response['details']['last_seen'])
            for k, v in resource_dict.items():
                self.assertEqual(response[k], v)
        with freeze_time(datetime(2020, 2, 28)):
            expenses = [
                {
                    'cost': 650,
                    'date': datetime(2020, 1, 14),
                    'cloud_account_id': resource['cloud_account_id'],
                    'resource_id': resource['id'],
                    'sign': 1
                },
                {
                    'cost': 300, 'date': datetime(2020, 2, 15),
                    'cloud_account_id': resource['cloud_account_id'],
                    'resource_id': resource['id'],
                    'sign': 1
                },
                {
                    'cost': 50,
                    'date': datetime(2020, 2, 16),
                    'cloud_account_id': resource['cloud_account_id'],
                    'resource_id': resource['id'],
                    'sign': 1
                },
                {
                    'cost': 150,
                    'date': datetime(2020, 2, 16),
                    'cloud_account_id': self.cloud_acc_id,
                    'resource_id': 'res_3_id',
                    'sign': 1
                }
            ]
            self.extend_expenses(expenses)
            self.add_cached_resource(
                [resource['id'], 'res_3_id'],
                datetime.utcnow().timestamp() + 1000)

            code, response = self.client.cloud_resource_get(
                resource['id'], details=True)
            self.assertEqual(code, 200)
            for k, v in resource_dict.items():
                self.assertEqual(response[k], v)
            details = response.get('details')
            self.assertIsNotNone(details)
            self.assertEqual(details['cost'], 350)
            self.assertEqual(details['cloud_type'], 'environment')
            self.assertEqual(datetime.fromtimestamp(details['last_seen']),
                             datetime(2020, 2, 28, 0, 1, 40))
            self.assertEqual(details['forecast'], 394.44)
            self.assertEqual(datetime.fromtimestamp(details['first_seen']),
                             datetime(2020, 1, 14))
            self.assertEqual(details['region'], None)
            self.assertEqual(details['owner_name'], employee['name'])
            self.assertEqual(details['cloud_name'], 'Environment')
            self.assertEqual(details['service_name'], None)
            self.assertEqual(details['total_cost'], 1000)
            self.assertEqual(details['pool_name'], self.org['name'])
            self.assertEqual(details['pool_purpose'], 'business_unit')

        code, response = self.client.cloud_resource_get(
            resource['id'], details=True)
        self.assertEqual(code, 200)
        self.assertTrue(isinstance(response['created_at'], int))
        for k, v in resource_dict.items():
            self.assertEqual(response[k], v)
        details = response.get('details')
        self.assertEqual(details['cost'], 0)
        self.assertEqual(details['cloud_type'], 'environment')
        self.assertEqual(details['forecast'], 0)
        self.assertEqual(details['region'], None)
        self.assertEqual(details['owner_name'], employee['name'])
        self.assertEqual(details['cloud_name'], 'Environment')
        self.assertEqual(details['service_name'], None)
        self.assertEqual(details['total_cost'], 1000)
        self.assertEqual(details['pool_name'], self.org['name'])
        self.assertEqual(details['pool_purpose'], 'business_unit')

    def test_get_cloud_resource_with_bookings(self):
        patch('rest_api.rest_api_server.controllers.shareable_resource.'
              'ShareableBookingController.publish_task').start()
        patch('rest_api.rest_api_server.controllers.shareable_resource.'
              'ShareableBookingController.check_employee_permission').start()
        user_id = self.gen_id()
        _, employee = self.client.employee_create(
            self.org_id, {'name': 'empl1', 'auth_user_id': user_id})
        self._mock_auth_user(user_id)
        resource_dict = {
            'cloud_resource_id': str(uuid.uuid4()),
            'name': 'res1',
            'resource_type': 'Instance',
            'tags': {'tk': 'tv'}
        }
        _, resource = self.cloud_resource_create(
            self.cloud_acc_id, resource_dict)
        self._make_resources_active([resource['id']])
        code, data = self.client.resources_bulk_share(self.org_id,
                                                      [resource['id']])
        self.assertEqual(code, 201)

        code, data = self.client.cloud_resource_get(resource['id'],
                                                    details=True)
        self.assertEqual(code, 200)
        self.assertEqual(data['details']['shareable_bookings'], [])
        self.assertIn(resource['id'],
                      data['details']['env_properties_collector_link'])

        now_ts = int(datetime.utcnow().timestamp())
        schedule_book = {
            'resource_id': resource['id'],
            'acquired_by_id': employee['id'],
            'acquired_since': now_ts,
            'released_at': 0,
        }
        code, data = self.client.shareable_book_create(self.org_id,
                                                       schedule_book)
        self.assertEqual(code, 201)

        code, data = self.client.cloud_resource_get(resource['id'],
                                                    details=True)
        self.assertEqual(code, 200)
        self.assertEqual(len(data['details']['shareable_bookings']), 1)
        self.assertEqual(data['details']['shareable_bookings'][0][
                             'acquired_by']['id'],  employee['id'])

    def test_get_cloud_resource_details_without_expenses(self):
        user_id = self.gen_id()
        _, employee = self.client.employee_create(
            self.org_id, {'name': 'empl1', 'auth_user_id': user_id})
        self._mock_auth_user(user_id)
        resource_dict = {
            'cloud_resource_id': str(uuid.uuid4()),
            'name': 'res1',
            'resource_type': 'res_test',
            'pool_id': self.org['pool_id'],
            'employee_id': employee['id']
        }
        now = datetime.utcnow()
        with freeze_time(now):
            _, resource = self.cloud_resource_create(
                self.cloud_acc_id, resource_dict)
            self.add_cached_resource([resource['id']])
            code, response = self.client.cloud_resource_get(
                resource['id'], details=True)
        self.assertEqual(code, 200)
        for k, v in resource_dict.items():
            self.assertEqual(response[k], v)
        details = response.get('details')
        self.assertEqual(details['cost'], 0)
        self.assertEqual(details['cloud_type'], self.cloud_acc['type'])
        self.assertEqual(details['cloud_name'], self.cloud_acc['name'])
        self.assertEqual(len(details['constraints']), 0)
        self.assertEqual(len(details['policies']), 0)
        for dt in ['last_seen', 'first_seen']:
            self.assertTrue(details[dt] in [
                int(now.timestamp()),
                int(now.replace(hour=0, minute=0, second=0, microsecond=0
                                ).timestamp())
            ])
        for zero_field in ['cost', 'forecast', 'total_cost']:
            self.assertEqual(details[zero_field], 0)
        self.assertEqual(details['pool_name'], self.org['name'])
        self.assertEqual(details['pool_purpose'], 'business_unit')
        self.assertEqual(details['owner_name'], employee['name'])
        self.client.pool_policy_create(
            self.org['pool_id'], {
                'limit': 150,
                'type': 'ttl'
            }
        )
        self.client.resource_constraint_create(
            resource['id'], {
                'limit': 200,
                'type': 'total_expense_limit'
            }
        )
        code, response = self.client.cloud_resource_get(
            resource['id'], details=True)
        self.assertEqual(code, 200)
        details = response.get('details')
        self.assertEqual(len(details['constraints']), 1)
        self.assertIsNotNone(details['constraints']['total_expense_limit'])
        self.assertEqual(len(details['policies']), 1)
        self.assertIsNotNone(details['policies']['ttl'])

    def test_resource_details_cluster(self):
        user_id = self.gen_id()
        _, employee = self.client.employee_create(
            self.org_id, {'name': 'empl1', 'auth_user_id': user_id})
        self._mock_auth_user(user_id)
        code, c_type = self.client.cluster_type_create(
            self.org_id, {'name': 'c_type', 'tag_key': 'tk'})
        self.assertEqual(code, 201)

        resource_dict = {
            'cloud_resource_id': str(uuid.uuid4()),
            'name': 'res1',
            'resource_type': 'res_test',
            'tags': {'tk': 'tv'}
        }
        _, resource = self.cloud_resource_create(
            self.cloud_acc_id, resource_dict)
        self.assertIsNotNone(resource.get('cluster_id'))
        code, response = self.client.cloud_resource_get(
            resource['cluster_id'], details=True)
        self.assertEqual(code, 200)
        self.assertEqual(response['cluster_type_id'], c_type['id'])
        self.assertTrue(len(response.get('sub_resources', [])), 1)
        for k, v in response['sub_resources'][0].items():
            if not isinstance(v, dict) and not isinstance(v, list):
                self.assertEqual(resource[k], v, k)
        self.assertIsNotNone(response['sub_resources'][0].get('details'))
        self.assertIsNotNone(response.get('details'))
        for k in ['cloud_type', 'cloud_name', 'service_name', 'region']:
            self.assertIsNone(response.get('details', {}).get(k))

        with freeze_time(datetime(2020, 2, 28)):
            expenses = [
                {
                    'cost': 650,
                    'date': datetime(2020, 1, 14),
                    'cloud_account_id': self.cloud_acc_id,
                    'resource_id': resource['id'],
                    'sign': 1
                },
                {
                    'cost': 650,
                    'date': datetime(2020, 2, 24),
                    'cloud_account_id': self.cloud_acc_id,
                    'resource_id': resource['id'],
                    'sign': 1
                },
                {
                    'cost': 150,
                    'date': datetime(2020, 2, 16),
                    'cloud_account_id': self.cloud_acc_id,
                    'resource_id': 'res_3_id',
                    'sign': 1
                }
            ]
            self.extend_expenses(expenses)

            self._make_resources_active([resource['cluster_id']])
            self._make_resources_active([resource['id']])
            code, response = self.client.cloud_resource_get(
                resource['cluster_id'], details=True)
            self.assertEqual(code, 200)
            self.assertIsNotNone(response.get('details'))
            self.assertEqual(response.get('details').get('total_cost'), 1300)
            self.assertEqual(response.get('details').get('cost'), 650)
            self.assertTrue(response.get(
                'details').get('forecast') > response.get(
                'details').get('cost'))
            self.assertTrue(response.get('sub_resources', [])[0].get(
                'details').get('forecast') > response.get(
                'details').get('cost'))

        self.add_recommendations(resource['id'], [
            {'name': 'module1', 'saving': 10},
            {'name': 'module2', 'saving': 20},
        ])
        resource_dict['cloud_resource_id'] = str(uuid.uuid4())
        resource_dict['name'] = 'res2'
        _, resource2 = self.cloud_resource_create(
            self.cloud_acc_id, resource_dict)
        self.assertIsNotNone(resource2.get('cluster_id'))
        self.add_recommendations(resource2['id'], [
            {'name': 'module1', 'saving': 10},
        ], checklist=False)
        code, response = self.client.cloud_resource_get(
            resource['cluster_id'], details=True)
        self.assertEqual(code, 200)
        self.assertIsNotNone(response.get('recommendations'))
        self.assertEqual(len(response.get('recommendations').get('modules')), 3)

        code, response = self.client.cloud_resource_get(
            resource['id'], details=True)
        self.assertEqual(code, 200)

        resource_dict = {
            'cloud_resource_hash': str(uuid.uuid4()),
            'name': 'res1',
            'resource_type': 'res_test',
            'tags': {'tk': 'tv'}
        }
        _, resource = self.cloud_resource_create(
            self.cloud_acc_id, resource_dict)
        self.assertIsNotNone(resource.get('cluster_id'))
        code, response = self.client.cloud_resource_get(
            resource['cluster_id'], details=True)
        self.assertEqual(code, 200)
        self.assertEqual(response['cluster_type_id'], c_type['id'])
        self.assertTrue(len(response.get('sub_resources', [])), 2)

    def test_resource_details_deleted_constraints(self):
        user_id = self.gen_id()
        _, employee = self.client.employee_create(
            self.org_id, {'name': 'empl1', 'auth_user_id': user_id})
        self._mock_auth_user(user_id)
        resource_dict = {
            'cloud_resource_id': str(uuid.uuid4()),
            'name': 'res1',
            'resource_type': 'res_test',
            'pool_id': self.org['pool_id'],
            'employee_id': employee['id']
        }
        _, resource = self.cloud_resource_create(
            self.cloud_acc_id, resource_dict)
        self.add_cached_resource([resource['id']])
        now = int(datetime.utcnow().timestamp())
        self.client.pool_policy_create(
            self.org['pool_id'], {
                'limit': 150,
                'type': 'ttl'
            }
        )
        self.client.resource_constraint_create(
            resource['id'], {
                'limit': 200,
                'type': 'total_expense_limit'
            }
        )
        code, response = self.client.cloud_resource_get(
            resource['id'], details=True)
        self.assertEqual(code, 200)
        details = response.get('details')
        self.assertEqual(len(details['constraints']), 1)
        self.assertIsNotNone(details['constraints']['total_expense_limit'])
        self.assertEqual(len(details['policies']), 1)
        self.assertIsNotNone(details['policies']['ttl'])
        limit = details['policies']['ttl']['limit']
        self.assertTrue(limit > now)
        self.assertTrue(isinstance(limit, int))
        constraint_id = details['constraints']['total_expense_limit']['id']
        policy_id = details['policies']['ttl']['id']

        self.client.resource_constraint_delete(constraint_id)
        self.client.pool_policy_delete(policy_id)
        code, response = self.client.cloud_resource_get(
            resource['id'], details=True)
        self.assertEqual(code, 200)
        details = response.get('details')
        self.assertEqual(len(details['constraints']), 0)
        self.assertEqual(len(details['policies']), 0)

    def test_resource_active_several_caches(self):
        user_id = self.gen_id()
        _, employee = self.client.employee_create(
            self.org_id, {'name': 'empl1', 'auth_user_id': user_id})
        self._mock_auth_user(user_id)
        resource_dict = {
            'cloud_resource_id': str(uuid.uuid4()),
            'name': 'res1',
            'resource_type': 'instance',
            'pool_id': self.org['pool_id'],
            'employee_id': employee['id']
        }
        _, resource = self.cloud_resource_create(
            self.cloud_acc_id, resource_dict)

        cache_map = [
            (resource['id'], int(datetime.utcnow().timestamp()) + 1000),
            (str(uuid.uuid4()), int(datetime.utcnow().timestamp()) + 2000),
        ]
        for res_id, valid_until in cache_map:
            self.add_cached_resource([res_id], valid_until)
        code, response = self.client.cloud_resource_get(
            resource['id'], details=True)
        self.assertEqual(code, 200)
        self.assertTrue(response['details']['active'])

    def test_tags_with_dot(self):
        self.valid_resource['tags'] = {
            'origin.id': 'some_id',
            'origin.name': 'some_name'
        }
        code, resource = self.cloud_resource_create(self.cloud_acc_id,
                                                    self.valid_resource)
        self.assertEqual(code, 201)
        mongo_resource = next(self.resources_collection.find(
            {'_id': resource['id']}))
        decoded_tags = encoded_tags(mongo_resource['tags'], decode=True)
        self.assertEqual(decoded_tags, resource['tags'])

    def test_resource_no_recommendations(self):
        code, resource = self.cloud_resource_create(self.cloud_acc_id,
                                                    self.valid_resource)
        self.assertEqual(code, 201)
        self.assertIsNotNone(resource['recommendations'])
        self.assertEqual(len(resource['recommendations']), 0)

    def test_resource_recommendations_not_active(self):
        code, resource = self.cloud_resource_create(self.cloud_acc_id,
                                                    self.valid_resource)
        self.add_recommendations(resource['id'], [
            {'name': 'module1', 'saving': 10},
            {'name': 'module2', 'saving': 20},
        ])
        self.add_cached_resource([resource['id']], active=False)
        code, resource = self.client.cloud_resource_get(resource['id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(resource['recommendations']), 2)

    def test_resource_recommendations(self):
        code, resource = self.cloud_resource_create(self.cloud_acc_id,
                                                    self.valid_resource)
        self.add_cached_resource([resource['id']])
        self.add_recommendations(resource['id'], [
            {'name': 'module1', 'saving': 10},
            {'name': 'module2', 'saving': 20},
        ])
        code, resource = self.client.cloud_resource_get(resource['id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(resource['recommendations']['modules']), 2)

    def test_resource_recommendations_old_checklist(self):
        code, resource = self.cloud_resource_create(self.cloud_acc_id,
                                                    self.valid_resource)
        self.add_cached_resource([resource['id']])
        last_check = int(datetime.utcnow().timestamp())
        timstamp = last_check - 1
        self.add_recommendations(resource['id'], [
            {'name': 'module1', 'saving': 10},
            {'name': 'module2', 'saving': 20},
        ], timestamp=timstamp, last_check=last_check)
        code, resource = self.client.cloud_resource_get(resource['id'])
        self.assertEqual(code, 200)
        self.assertIsNone(resource['recommendations'].get('modules'))

    def test_resource_forecast_not_active(self):
        code, resource = self.cloud_resource_create(self.cloud_acc_id,
                                                    self.valid_resource)
        with freeze_time(datetime(2020, 4, 11)):
            expenses = [
                {
                    'cost': 10,
                    'date': datetime(2020, 4, 1),
                    'cloud_account_id': self.cloud_acc_id,
                    'resource_id': resource['id'],
                    'sign': 1
                }
            ]
            self.extend_expenses(expenses)
            self._make_resources_active([resource['id']])
            code, data = self.client.cloud_resource_get(
                resource['id'], details=True)
            self.assertEqual(code, 200)
            self.assertEqual(data['details']['forecast'], 30)
            self._make_resources_inactive([resource['id']])
            code, data = self.client.cloud_resource_get(
                resource['id'], details=True)
            self.assertEqual(code, 200)
            self.assertEqual(data['details']['forecast'], 10)

    def test_create_meta_field_not_in_meta(self):
        params = self.valid_resource.copy()
        params['resource_type'] = 'Snapshot'
        vol_id = 'vol_id'
        params['volume_id'] = vol_id
        code, res = self.cloud_resource_create(self.cloud_acc_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0212')

    def test_get_detail_traffic_info(self):
        resource_dict = {
            'cloud_resource_id': str(uuid.uuid4()),
            'resource_type': 'test_type',
        }
        _, resource = self.cloud_resource_create(
            self.cloud_acc_id, resource_dict)
        expenses = [
            {
                'cost': 650,
                'date': datetime(2020, 1, 14),
                'cloud_account_id': self.cloud_acc_id,
                'resource_id': resource['id'],
                'sign': 1
            }
        ]
        self.extend_expenses(expenses)
        self.traffic_expenses = [
            {
                'cloud_account_id': self.cloud_acc['id'],
                'resource_id': resource['cloud_resource_id'],
                'date': int(datetime.utcnow().timestamp()),
                'type': 1,
                'from': 'region_1',
                'to': 'External',
                'usage': 10,
                'cost': 20,
                'sign': 1
            },
            {
                'cloud_account_id': self.cloud_acc['id'],
                'resource_id': resource['cloud_resource_id'],
                'date': int(datetime.utcnow().timestamp()),
                'type': 1,
                'from': 'region_2',
                'to': 'External',
                'usage': 10,
                'cost': 20,
                'sign': 1
            }
        ]
        code, response = self.client.cloud_resource_get(
            resource['id'], details=True)
        self.assertEqual(code, 200)
        self.assertEqual(response['details']['total_traffic_expenses'], 40)
        self.assertEqual(response['details']['total_traffic_usage'], 20)

    def test_get_cluster_detail_traffic_info(self):
        code, c_type = self.client.cluster_type_create(
            self.org_id, {'name': 'c_type', 'tag_key': 'tk'})
        self.assertEqual(code, 201)

        resource_dict = {
            'cloud_resource_id': str(uuid.uuid4()),
            'name': 'res1',
            'resource_type': 'res_test',
            'tags': {'tk': 'tv'}
        }
        _, resource = self.cloud_resource_create(
            self.cloud_acc_id, resource_dict)
        self.traffic_expenses = [
            {
                'cloud_account_id': self.cloud_acc['id'],
                'resource_id': resource['cloud_resource_id'],
                'date': int(datetime.utcnow().timestamp()),
                'type': 1,
                'from': 'region_1',
                'to': 'External',
                'usage': 10,
                'cost': 20,
                'sign': 1
            }
        ]
        self.assertIsNotNone(resource.get('cluster_id'))
        for k in [resource['cluster_id'], resource['id']]:
            code, response = self.client.cloud_resource_get(
                k, details=True)
            self.assertEqual(code, 200)
            self.assertEqual(response['details']['total_traffic_expenses'], 20)
            self.assertEqual(response['details']['total_traffic_usage'], 10)
