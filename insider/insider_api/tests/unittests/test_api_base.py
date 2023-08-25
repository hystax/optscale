import mongomock
import tornado.testing
from unittest.mock import patch, PropertyMock
import optscale_client.insider_client.client as insider_client
from insider.insider_api.server import make_app


class TestBase(tornado.testing.AsyncHTTPTestCase):

    def get_app(self):
        return make_app('127.0.0.1', 80, wait=False)

    def setUp(self):
        super().setUp()
        patch('optscale_client.config_client.client.Client.cluster_secret',
              return_value='secret').start()
        patch('optscale_client.config_client.client.Client.restapi_url').start()
        self.mongo_client = mongomock.MongoClient()
        patch('insider.insider_api.controllers.base.BaseController.mongo_client',
              new_callable=PropertyMock, return_value=self.mongo_client
              ).start()
        http_provider = insider_client.FetchMethodHttpProvider(
            self.fetch, rethrow=False, secret='secret')
        self.client = insider_client.Client(http_provider=http_provider)

    def verify_error_code(self, resp, code):
        self.assertTrue('error' in resp, 'No error in response')
        self.assertTrue('error_code' in resp['error'],
                        'No error code in error')
        self.assertEqual(code, resp['error']['error_code'],
                         msg='Unexpected error code')

    def tearDown(self):
        patch.stopall()
