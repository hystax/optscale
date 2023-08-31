import tornado.testing
from unittest.mock import patch
from metroculus.metroculus_api.server import make_app
import optscale_client.metroculus_client.client as MetroculusClient


class TestBase(tornado.testing.AsyncHTTPTestCase):

    def get_app(self):
        return make_app('127.0.0.1', 80, wait=False)

    def setUp(self):
        super().setUp()
        patch('optscale_client.config_client.client.Client.cluster_secret',
              return_value='secret').start()
        http_provider = MetroculusClient.FetchMethodHttpProvider(
            self.fetch, rethrow=False, secret='secret')
        self.client = MetroculusClient.Client(http_provider=http_provider)

    def verify_error_code(self, resp, code):
        self.assertTrue('error' in resp, 'No error in response')
        self.assertTrue('error_code' in resp['error'],
                        'No error code in error')
        self.assertEqual(code, resp['error']['error_code'],
                         msg='Unexpected error code')

    def tearDown(self):
        patch.stopall()
