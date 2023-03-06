import base64
import tornado.testing
import uuid

from requests.exceptions import HTTPError
from tornado.httpclient import HTTPRequest
from unittest.mock import patch

from tornado.httputil import HTTPHeaders

from diproxy.main import make_app, Urls


# noinspection PyMethodMayBeStatic
class ConfigClientMock:
    def __init__(self, *args, **kwargs):
        pass

    def thanos_remote_write_url(self):
        return 'http://thanos:12345/api/v1/write'

    def restapi_url(self):
        return 'http://restapi:70'

    def cluster_secret(self):
        return 'secret'


def get_basic_credentials(username, password):
    return base64.b64encode(f'{username}:{password}'.encode()).decode()


class TestDiproxy(tornado.testing.AsyncHTTPTestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._db_session = None

    def get_app(self):
        return self.io_loop.run_sync(lambda: make_app())

    def setUp(self):
        patch('diproxy.main.ConfigClient', ConfigClientMock).start()
        super().setUp()

    def _send_request(self, request: HTTPRequest):
        return self.io_loop.run_sync(
            lambda: self.http_client.fetch(request, raise_error=False),
            timeout=tornado.testing.get_async_test_timeout())

    def _send_write_request(self, headers, data=b''):
        request = HTTPRequest(
            method='POST',
            url=self.get_url(Urls.write),
            headers=headers or {},
            body=data,
        )
        return self._send_request(request)

    def test_no_ca_header(self):
        response = self._send_write_request(headers={})
        self.assertEqual(response.code, 400)

    @patch('diproxy.main.RestApiClient.cloud_account_get')
    def test_non_existing_ca(self, p_get_ca):
        headers = {
            'Cloud-Account-Id': str(uuid.uuid4())
        }
        p_get_ca.side_effect = HTTPError()
        response = self._send_write_request(headers=headers)
        self.assertEqual(response.code, 422)

    @patch('diproxy.main.RestApiClient.cloud_account_get')
    def test_unsupported_ca(self,  p_get_ca):
        ca_id = str(uuid.uuid4())
        headers = {'Cloud-Account-Id': ca_id}
        p_get_ca.return_value = 200, {
            'id': ca_id,
            'config': {}
        }
        response = self._send_write_request(headers=headers)
        self.assertEqual(response.code, 422)

    @patch('diproxy.main.RestApiClient.cloud_account_get')
    def test_unauthorized(self, p_get_ca):
        ca_id = str(uuid.uuid4())
        headers = {
            'Cloud-Account-Id': ca_id,
            'Authorization': 'Basic qwerty'
        }
        p_get_ca.return_value = 200, {
            'id': ca_id,
            'config': {'credentials': get_basic_credentials(
                'user', 'pass')}
        }
        response = self._send_write_request(headers=headers)
        self.assertEqual(response.code, 401)

    @patch('diproxy.main.RemoteWriteStorageClient.write')
    @patch('diproxy.main.RestApiClient.cloud_account_get')
    def test_write_exception(self, p_get_ca, p_write_storage):
        ca_id = str(uuid.uuid4())
        creds = get_basic_credentials('user', 'pass')
        headers = {
            'Cloud-Account-Id': ca_id,
            'Authorization': f'Basic {creds}'
        }
        p_get_ca.return_value = 200, {
            'id': ca_id,
            'config': {'credentials': creds}
        }
        p_write_storage.side_effect = Exception('Unexpected error')
        response = self._send_write_request(headers=headers)
        self.assertEqual(response.code, 503)

    @patch('diproxy.main.RemoteWriteStorageClient.write')
    @patch('diproxy.main.RestApiClient.cloud_account_get')
    def test_write(self, p_get_ca, p_write_storage):
        ca_id = str(uuid.uuid4())
        creds = get_basic_credentials('user', 'pass')
        headers = {
            'Cloud-Account-Id': ca_id,
            'Authorization': f'Basic {creds}'
        }
        p_get_ca.return_value = 200, {
            'id': ca_id,
            'config': {'credentials': creds}
        }

        storage_status_code = 418
        storage_data = b'111'
        storage_headers = HTTPHeaders(headers)
        p_write_storage.return_value = (storage_status_code,
                                        storage_data,
                                        storage_headers)
        response = self._send_write_request(headers=headers)
        self.assertEqual(response.code, storage_status_code)
        self.assertEqual(response.body, storage_data)
        for k, v in storage_headers.items():
            self.assertEqual(response.headers.get(k), v)

    def test_not_implemented(self):
        request = HTTPRequest(
            method='POST',
            url=self.get_url('/123'),
            headers={},
            body=b'',
        )
        response = self._send_request(request)
        self.assertEqual(response.code, 404)
        self.assertEqual(response.body, b'')
        self.assertTrue('Content-Type' not in response.headers)
