import time
from unittest.mock import patch, Mock

from slacker.slacker_server.tests.test_api_base import TestApiBase
from slacker.slacker_server.utils import gen_id


class TestConnectAPI(TestApiBase):
    def setUp(self):
        super().setUp()
        self.user_id = gen_id()
        patch('slacker.slacker_server.controllers.base.BaseHandlerController.'
              'get_user_id', return_value=self.user_id).start()
        self.auth_cl_mock = Mock()
        self.rest_cl_mock = Mock()
        patch('slacker.slacker_server.controllers.base.BaseController.'
              'get_user_api_clients',
              return_value=(self.auth_cl_mock, self.rest_cl_mock)).start()
        valid_until = int(time.time()) + 24 * 3600
        patch('slacker.slacker_server.handlers.v2.base.'
              'BaseHandler.get_meta_by_token',
              return_value={'user_id': self.user_id,
                            'valid_until': valid_until}).start()

    def test_connect_secret_doesnt_exist(self):
        code, resp = self.client.connect_slack_user('fake')
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OS0011')

    def test_connect_without_secret(self):
        code, resp = self.client.post(self.client.connect_url(), {})
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OS0010')

    def test_connect_unexpected(self):
        code, resp = self.client.post(self.client.connect_url(),
                                      {'secret': 'test', 'message': 1})
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OS0007')

    def test_connect_successful(self):
        secret = gen_id()
        self.auth_cl_mock.user_update.return_value = (200, {'email': '1@1.com'})
        self.rest_cl_mock.organization_list.return_value = (
            200, {'organizations': [{'id': 'orgid', 'name': 'org'}]})
        self.initialize_user(secret)
        code, resp = self.client.connect_slack_user(secret)
        self.assertEqual(code, 201)

    def test_connect_already_connected(self):
        secret = gen_id()
        self.auth_cl_mock.user_update.return_value = (200, {'email': '1@1.com'})
        self.rest_cl_mock.organization_list.return_value = (
            200, {'organizations': [{'id': 'orgid', 'name': 'org'}]})
        self.initialize_user(secret)
        code, resp = self.client.connect_slack_user(secret)
        self.assertEqual(code, 201)

        code, resp = self.client.connect_slack_user(secret)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OS0013')

    def test_unathorized(self):
        secret = gen_id()
        valid_until = int(time.time()) - 1
        patch('slacker.slacker_server.handlers.v2.base.'
              'BaseHandler.get_meta_by_token',
              return_value={'user_id': self.user_id,
                            'valid_until': valid_until}).start()
        code, resp = self.client.post(self.client.connect_url(),
                                      {'secret': secret})
        self.assertEqual(code, 401)
        self.verify_error_code(resp, 'OS0018')
