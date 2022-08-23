import json
import uuid
from datetime import datetime
from unittest.mock import patch, ANY
from rest_api_server.tests.unittests.test_api_base import TestApiBase


class TestWebhooksApi(TestApiBase):

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
            self.organization_id, self.cloud_acc_dict,
            auth_user_id=self.auth_user)

        self.resource_id = self._create_resource()['id']
        self.valid_body = {
            'object_type': 'environment',
            'object_id': self.resource_id,
            'action': 'booking_acquire',
            'url': 'url',
        }

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

    def test_create_webhook(self):
        code, webhook = self.client.webhook_create(self.organization_id,
                                                   self.valid_body)
        self.assertEqual(code, 201)
        self.assertTrue(
            all(kv in webhook.items() for kv in self.valid_body.items()))
        self.assertTrue('active')
        self.assertIsNone(webhook['headers'])

    def test_create_invalid_params(self):
        code, resp = self.client.webhook_create(
            str(uuid.uuid4()), self.valid_body)
        self.assertEqual(code, 404)
        self.verify_error_code(resp, 'OE0002')
        for field, value, error in [
            ('object_type', 'some', 'OE0287'), ('action', 'some', 'OE0287'),
            ('url', 1, 'OE0214'), ('headers', 'some text', 'OE0219'),
            ('active', 'value', 'OE0226')
        ]:
            body = self.valid_body.copy()
            body[field] = value
            code, resp = self.client.webhook_create(self.organization_id, body)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, error)
        self.valid_body['organization_id'] = 'duplicate'
        code, resp = self.client.webhook_create(self.organization_id,
                                                self.valid_body)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0456')

    def test_create_header_active(self):
        body = {
            'object_type': 'environment',
            'object_id': self.resource_id,
            'action': 'booking_acquire',
            'url': 'url',
            'active': False,
            'headers': json.dumps({'token': 'valid'})
        }
        code, webhook = self.client.webhook_create(self.organization_id, body)
        self.assertEqual(code, 201)
        self.assertTrue(all(kv in webhook.items() for kv in body.items()))

    def test_create_invalid_object_id(self):
        self.valid_body['object_id'] = str(uuid.uuid4())
        resource_id = self._create_resource(is_shareable=False)['id']
        for r_id in [str(uuid.uuid4()), resource_id]:
            self.valid_body['object_id'] = r_id
            code, resp = self.client.webhook_create(self.organization_id,
                                                    self.valid_body)
            self.assertEqual(code, 404)
            self.verify_error_code(resp, 'OE0002')

    def test_create_unexpected_params(self):
        for k in ['deleted_at', 'id', 'another']:
            body = self.valid_body.copy()
            body[k] = 'value'
            code, resp = self.client.webhook_create(
                self.organization_id, body)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0212')

    def test_update_wrong_params(self):
        code, webhook = self.client.webhook_create(
            self.organization_id, self.valid_body)
        self.assertEqual(code, 201)
        for immutable in ['deleted_at', 'created_at', 'organization_id',
                          'object_type', 'object_id', 'action']:
            code, resp = self.client.webhook_update(
                webhook['id'], {immutable: 'value'})
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0211')

        code, resp = self.client.webhook_update(webhook['id'],
                                                {'unexpected': 'value'})
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0212')

    def test_create_not_provided(self):
        for req_param in ['object_type', 'object_id', 'action', 'url']:
            body = self.valid_body.copy()
            body.pop(req_param)
            code, resp = self.client.webhook_create(
                self.organization_id, body)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0216')

    def test_create_duplicate(self):
        code, _ = self.client.webhook_create(
            self.organization_id, self.valid_body)
        self.assertEqual(code, 201)
        code, resp = self.client.webhook_create(
            self.organization_id, self.valid_body)
        self.assertEqual(code, 409)
        self.verify_error_code(resp, 'OE0503')
        self.valid_body['action'] = 'booking_release'
        code, resp = self.client.webhook_create(
            self.organization_id, self.valid_body)
        self.assertEqual(code, 201)

    def test_get_webhook(self):
        code, hook = self.client.webhook_create(self.organization_id,
                                                self.valid_body)
        self.assertEqual(code, 201)
        code, resp = self.client.webhook_get(hook['id'])
        self.assertEqual(code, 200)
        self.assertTrue(
            all(kv in hook.items() for kv in self.valid_body.items()))

    def test_get_not_exist_webhook(self):
        code, resp = self.client.webhook_get(str(uuid.uuid4()))
        self.assertEqual(code, 404)
        self.verify_error_code(resp, 'OE0002')

    def test_update_webhook(self):
        code, hook = self.client.webhook_create(self.organization_id,
                                                self.valid_body)
        self.assertEqual(code, 201)
        params = {
            'active': False,
            'url': 'another',
            'headers': json.dumps({'some': 'header'})
        }
        code, resp = self.client.webhook_update(hook['id'], params)
        self.assertEqual(code, 200)
        self.assertTrue(
            all(kv in resp.items() for kv in params.items()))

    def test_update_webhook_wrong_parameters(self):
        code, hook = self.client.webhook_create(self.organization_id,
                                                self.valid_body)
        self.assertEqual(code, 201)
        valid_params = {
            'active': False,
            'url': 'another',
            'headers': json.dumps({'some': 'header'})
        }
        for field, value, error in [
            ('url', 1, 'OE0214'), ('headers', 'some text', 'OE0219'),
            ('active', 'value', 'OE0226')
        ]:
            params = valid_params.copy()
            params[field] = value
            code, resp = self.client.webhook_update(hook['id'], params)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, error)

    def test_update_not_exist_webhook(self):
        code, resp = self.client.webhook_update(
            str(uuid.uuid4()), {'active': False})
        self.assertEqual(code, 404)
        self.verify_error_code(resp, 'OE0002')

    def test_delete_webhook(self):
        code, hook = self.client.webhook_create(self.organization_id,
                                                self.valid_body)
        self.assertEqual(code, 201)
        code, resp = self.client.webhook_delete(hook['id'])
        self.assertEqual(code, 204)
        self.assertIsNone(resp)
        code, resp = self.client.webhook_delete(hook['id'])
        self.assertEqual(code, 404)
        self.verify_error_code(resp, 'OE0002')

    def test_list_webhooks(self):
        code, hook = self.client.webhook_create(self.organization_id,
                                                self.valid_body)
        self.assertEqual(code, 201)
        self.valid_body['action'] = 'booking_release'
        code, hook2 = self.client.webhook_create(self.organization_id,
                                                 self.valid_body)
        self.assertEqual(code, 201)

        resource_id = self._create_resource()['id']
        self.valid_body['object_id'] = resource_id
        self.valid_body['active'] = False
        code, hook3 = self.client.webhook_create(self.organization_id,
                                                 self.valid_body)
        self.assertEqual(code, 201)

        code, resp = self.client.webhook_list(self.organization_id)
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['webhooks']), 3)
        for webhook in resp['webhooks']:
            self.assertTrue(
                webhook['id'] in [hook['id'], hook2['id'], hook3['id']])

        code, resp = self.client.webhook_list(
            self.organization_id, {'active': False})
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['webhooks']), 1)
        self.assertEqual(resp['webhooks'][0]['id'], hook3['id'])

        code, resp = self.client.webhook_list(
            self.organization_id, {'object_type': 'environment'})
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['webhooks']), 3)

        code, resp = self.client.webhook_list(
            self.organization_id, {'object_id': hook2['object_id']})
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['webhooks']), 2)
        for webhook in resp['webhooks']:
            self.assertTrue(webhook['id'] in [hook['id'], hook2['id']])

        code, resp = self.client.webhook_list(
            self.organization_id, {'action': 'booking_release'})
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['webhooks']), 2)
        for webhook in resp['webhooks']:
            self.assertTrue(webhook['id'] in [hook2['id'], hook3['id']])

    def test_webhook_logs_empty(self):
        code, hook = self.client.webhook_create(self.organization_id,
                                                self.valid_body)
        self.assertEqual(code, 201)
        code, resp = self.client.webhook_logs_get(hook['id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['logs']), 0)

    def test_webhook_logs(self):
        code, hook = self.client.webhook_create(self.organization_id,
                                                self.valid_body)
        self.assertEqual(code, 201)
        self.valid_body['action'] = 'booking_release'
        code, hook2 = self.client.webhook_create(self.organization_id,
                                                 self.valid_body)
        self.assertEqual(code, 201)
        logs = [
            {
                'webhook_id': hook['id'],
                'execution_time': int(datetime(2021, 5, 5).timestamp())
            },
            {
                'webhook_id': hook['id'],
                'execution_time': int(datetime(2021, 5, 2).timestamp())
            },
            {
                'webhook_id': hook['id'],
                'execution_time': int(datetime(2021, 5, 6).timestamp())
            },
            {
                'webhook_id': hook2['id'],
                'execution_time': int(datetime(2021, 5, 2).timestamp())
            },
            {
                'webhook_id': hook2['id'],
                'execution_time': int(datetime(2021, 5, 1).timestamp())
            }
        ]
        self.mongo_client.restapi.webhook_logs.insert_many(logs)
        code, logs = self.client.webhook_logs_get(hook['id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(logs['logs']), 3)
        self.assertEqual(logs['logs'][0]['execution_time'],
                         int(datetime(2021, 5, 2).timestamp()))
        self.assertEqual(logs['logs'][1]['execution_time'],
                         int(datetime(2021, 5, 5).timestamp()))
        self.assertEqual(logs['logs'][2]['execution_time'],
                         int(datetime(2021, 5, 6).timestamp()))
        code, logs = self.client.webhook_logs_get(hook2['id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(logs['logs']), 2)

    def test_publish_hook_task(self):
        self._mock_auth_user(self.auth_user)
        patch(
            'rest_api_server.handlers.v2.shareable_resources.'
            'ShareableBookingBaseAsyncHandler.check_booking_permission',
            return_value={}
        ).start()
        resource_id = self._create_resource()['id']
        schedule_book = {
            'resource_id': resource_id,
            'acquired_by_id': self.employee['id'],
        }
        p_publish_task = patch(
            'rest_api_server.controllers.shareable_resource.'
            'ShareableBookingController.publish_task').start()
        code, book = self.client.shareable_book_create(self.organization_id,
                                                       schedule_book)
        self.assertEqual(code, 201)
        code, _ = self.client.shareable_book_release(
            book['id'], {'released_at': int(datetime.utcnow().timestamp())})
        self.assertEqual(code, 200)
        self.assertEqual(p_publish_task.call_count, 1)
        p_publish_task.assert_called_with({
            'organization_id': self.organization_id,
            'observe_time': ANY,
            'resource': ANY,
            'object_id': ANY
        })
