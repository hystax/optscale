import uuid

import mongomock
import tornado.testing
from unittest.mock import patch

from keeper.report_server.server import make_app

import optscale_client.report_client.client
import optscale_client.report_client.client_v2


class TestReportBase(tornado.testing.AsyncHTTPTestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._db_session = None

    def get_app(self):
        return make_app('127.0.0.1', 80,
                        mongo_client_class=mongomock.MongoClient)

    @patch('keeper.report_server.server.MongoClient')
    @patch('optscale_client.config_client.client.Client')
    @patch('keeper.report_server.controllers.message_publisher.Publisher')
    def setUp(self, p_rabbit, p_config, p_mongo):
        secret = str(uuid.uuid4())
        p_config.return_value.mongo_params.return_value = (
            'root', 'pass', 'localhost', 27017, 'keeper')
        p_config.return_value.rabbit_params.return_value = (
            'root', 'pass', 'localhost', 27017)
        p_config.return_value.cluster_secret.return_value = secret
        p_config.return_value.agent_secret.return_value = secret
        super().setUp()
        patch(
            'keeper.report_server.handlers.v1.base.Config').start()
        patch(
            'keeper.report_server.handlers.v1.base.AuthClient.authorize',
            lambda *args: (200, {'accepted'})).start()
        http_provider = optscale_client.report_client.client.FetchMethodHttpProvider(
            self.fetch, rethrow=False)
        self.client = optscale_client.report_client.client_v2.Client(
            http_provider=http_provider)
        self.client.token = 'token'
        self.client.secret = secret
        mongomock.patch(servers=(('localhost', 27017),))

    def tearDown(self):
        super().tearDown()
