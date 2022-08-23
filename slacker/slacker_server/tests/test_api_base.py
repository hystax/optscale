import os
import time
from unittest.mock import patch
from slacker_client.client import (
    Client as SlackerClient, FetchMethodHttpProvider)

import tornado.testing

from slacker_server.models.models import User
from config_client.client import Client as ConfigClient
from slacker_server.models.db_base import BaseDB
from slacker_server.models.db_factory import DBFactory, DBType
from slacker_server.server import make_slack_app, make_tornado_app
from slacker_server.utils import gen_id


class TestApiBase(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return make_tornado_app(self.app, self.db, self.config_cl)

    def setUp(self):
        os.environ['ASYNC_TEST_TIMEOUT'] = '20'

        self.db = DBFactory(DBType.Test, None).db
        self.config_cl = ConfigClient(host='127.0.0.1', port=80)
        self.app = make_slack_app(self.db.engine, self.config_cl)

        self.cluster_secret = gen_id()
        patch('slacker_server.tests.test_api_base.ConfigClient.cluster_secret',
              return_value=self.cluster_secret).start()
        patch('slacker_server.tests.test_api_base.ConfigClient.public_ip',
              ).start()
        patch('slacker_server.slack_client.SlackClient.chat_post').start()
        http_provider = FetchMethodHttpProvider(self.fetch, rethrow=False)
        self.client = SlackerClient(http_provider=http_provider)
        self.client.token = 'token'
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

    def initialize_user(
            self, secret=None, slack_team_id=None, slack_channel_id=None):
        session = self.init_db_session()
        if not secret:
            secret = gen_id()
        if not slack_channel_id:
            slack_channel_id = gen_id()
        if not slack_team_id:
            slack_team_id = gen_id()
        user = User(slack_user_id=gen_id(),
                    slack_team_id=slack_team_id,
                    secret=secret,
                    slack_channel_id=slack_channel_id)
        session.add(user)
        session.commit()
        return user
