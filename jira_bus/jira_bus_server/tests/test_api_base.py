import json
import os
from os import path
from random import randint
from unittest.mock import patch, Mock

import time
import tornado.testing
from config_client.client import Client as ConfigClient

from jira_bus_client.client import (
    Client as JiraBusClient, FetchMethodHttpProvider)
from jira_bus_server.models.db_base import BaseDB
from jira_bus_server.models.db_factory import DBFactory, DBType
from jira_bus_server.server import make_app
from jira_bus_server.utils import gen_id


class TestApiBase(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return make_app(DBType.Test, '127.0.0.1', 80)

    def setUp(self):
        os.environ['ASYNC_TEST_TIMEOUT'] = '20'
        os.environ['BASE_HANDLER_LOG_ERRORS_WITH_NEWLINES'] = '1'

        self.db = DBFactory(DBType.Test, None).db
        self.config_cl = ConfigClient(host='127.0.0.1', port=80)

        self.cluster_secret = gen_id()
        patch('jira_bus_server.tests.test_api_base.ConfigClient.cluster_secret',
              return_value=self.cluster_secret).start()
        patch('jira_bus_server.tests.test_api_base.ConfigClient.public_ip',
              ).start()
        self.auth_user_id = gen_id()
        self.auth_cl_mock = Mock()
        self.rest_cl_mock = Mock()
        self.atlassian_cl_mock = Mock()
        patch('jira_bus_server.controllers.base.BaseController.'
              '_get_rest_client',
              return_value=self.rest_cl_mock).start()
        patch('jira_bus_server.controllers.base.BaseController.'
              '_get_auth_client',
              return_value=self.auth_cl_mock).start()
        patch('jira_bus_server.controllers.base.BaseController.'
              '_get_atlassian_client',
              return_value=self.atlassian_cl_mock).start()
        valid_until = int(time.time()) + 24 * 3600
        patch('jira_bus_server.handlers.v2.base.BaseHandler.'
              '_get_meta_by_token',
              return_value={'user_id': self.auth_user_id,
                            'valid_until': valid_until}).start()
        patch('jira_bus_server.controllers.base.BaseController.'
              '_get_auth_token_by_auth_user_id',
              return_value='totally-not-a-fake-token').start()
        self.p_optscale_permission = patch(
            'jira_bus_server.handlers.v2.base.BaseHandler.'
            'check_optscale_permission')
        self.m_optscale_permission = self.p_optscale_permission.start()

        self.organization_id = gen_id()
        self.client_key = gen_id()
        self.account_id = gen_id()
        self.project_key = 'OSB'
        self.issue_number = randint(1, 999999)
        self.issue_key = '{}-{}'.format(self.project_key, self.issue_number)
        self.installed_payload = {
            'key': 'ac.ci.d9fe0782-2201-11ec-83bf-0a0027000019',
            'clientKey': self.client_key,
            'publicKey': 'FAKE_KEY',
            'sharedSecret': 'FAKE_KEY',
            'serverVersion': '100178',
            'pluginsVersion': '1001.0.0-SNAPSHOT',
            'baseUrl': 'https://example.com',
            'productType': 'jira',
            'description': 'Atlassian JIRA at https://team-1630308317828.atlassian.net ',
            'eventType': 'installed'
        }

        super().setUp()

    def tearDown(self):
        DBFactory.clean_type(DBType.Test)
        patch.stopall()
        if os.path.exists('db.sqlite'):
            os.remove('db.sqlite')
        super().tearDown()

    def init_db_session(self):
        return BaseDB.session(self.db.engine)()

    def _make_controller(self, controller_class):
        session = BaseDB.session(self.db.engine)()
        return controller_class(session, None, self.db.engine)

    def verify_error_code(self, resp, code):
        self.assertTrue('error' in resp, 'No error in response')
        self.assertTrue('error_code' in resp['error'],
                        'No error code in error')
        self.assertEqual(code, resp['error']['error_code'],
                         msg='Unexpected error code')

    def get_client(self, include_token=False, include_secret=False,
                   include_client_key=False, include_account_id=False,
                   include_issue_key=False):
        http_provider = FetchMethodHttpProvider(self.fetch, rethrow=False)
        client = JiraBusClient(http_provider=http_provider)
        if include_token:
            client.token = 'token'
        if (include_secret or include_client_key or include_account_id or
                include_issue_key):
            # Secret is required when test headers are used
            client.secret = self.cluster_secret
        if include_client_key:
            client.extra_headers['Hx-Test-Client-Key'] = self.client_key
        if include_account_id:
            client.extra_headers['Hx-Test-Account-Id'] = self.account_id
        if include_issue_key:
            client.extra_headers['Hx-Test-Issue-Key'] = self.issue_key
        return client

    def get_response_mock(self, file_name):
        base_path = path.dirname(__file__)
        file_name_ext = file_name + '.json'
        with open(path.join(base_path, 'response_mocks', file_name_ext)) as f:
            return json.load(f)
