import os
import json
import requests
import datetime
import logging
from urllib.parse import urlencode
from abc import ABCMeta
from retrying import retry

LOG = logging.getLogger(__name__)
ACURA_CERT_PATH = '/acura.crt'


def retry_if_connection_error(exception):
    if isinstance(exception, requests.ConnectionError):
        return True
    if isinstance(exception, requests.HTTPError):
        if exception.response.status_code in (503,):
            return True
    return False


class AbstractHttpProvider(metaclass=ABCMeta):
    def __init__(self, token='', secret=''):
        self._token = token
        self._secret = secret

    @property
    def headers(self):
        return {'Authorization': str('Bearer ' + str(self._token)),
                'Secret': str(self._secret),
                'Content-type': 'application/json'}

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, value):
        self._token = value

    @property
    def secret(self):
        return self._secret

    @secret.setter
    def secret(self, value):
        self._secret = value


class RequestsHttpProvider(AbstractHttpProvider):
    def __init__(self, url, token='', secret='', verify=True):
        self.url = url
        self.verify = verify
        self.session = requests.session()
        acura_cert = os.environ.get('ACURA_CERT')
        if acura_cert is not None:
            if not os.path.exists(ACURA_CERT_PATH):
                with open(ACURA_CERT_PATH, 'w') as f_crt:
                    f_crt.write(acura_cert)
            self.session.verify = ACURA_CERT_PATH
        super().__init__(token, secret)

    @retry(stop_max_delay=10000, wait_fixed=1000,
           retry_on_exception=retry_if_connection_error)
    def request(self, path, method, data=None):
        full_url = self.url + path
        response = self.session.request(method, full_url, data=data,
                                        headers=self.headers, verify=self.verify)
        response.raise_for_status()
        response_body = None
        if response.status_code != requests.codes.no_content:
            response_body = json.loads(response.content.decode('utf-8'))
        return response.status_code, response_body

    def close(self):
        self.session.close()


class FetchMethodHttpProvider(AbstractHttpProvider):
    def __init__(self, fetch_method, rethrow=True, token='', secret=''):
        self.fetch = fetch_method
        self._rethrow = rethrow
        super().__init__(token, secret)

    def request(self, url, method, body=None):
        response = self.fetch(
            url, method=method, body=body, allow_nonstandard_methods=True,
            headers=self.headers
        )
        if self._rethrow:
            response.rethrow()
        try:
            decoded_response = json.loads(response.body.decode('utf-8'))
        except Exception as e:
            LOG.error("failed to decode response body %s", e)
            decoded_response = None
        return response.code, decoded_response

    def close(self):
        pass


class Client:
    def __init__(self, address="127.0.0.1", port="80", api_version="v1",
                 url=None, http_provider=None, token='', secret='', verify=True):
        if http_provider is None:
            if url is None:
                url = "http://%s:%s" % (address, port)
            http_provider = RequestsHttpProvider(url, token, secret, verify)
        self._http_provider = http_provider
        self._api_version = api_version

    def _url(self, sub_url):
        return "/report/%s/%s" % (self._api_version, sub_url)

    def _request(self, url, method, body=None):
        data = None
        if body is not None:
            data = json.dumps(body)
        return self._http_provider.request(self._url(url), method, data)

    def get(self, url, body=None):
        return self._request(url, "GET", body)

    def post(self, url, body):
        return self._request(url, "POST", body)

    def patch(self, url, body):
        return self._request(url, "PATCH", body)

    @property
    def token(self):
        return self._http_provider.token

    @token.setter
    def token(self, value):
        self._http_provider.token = value

    @property
    def secret(self):
        return self._http_provider.secret

    @secret.setter
    def secret(self, value):
        self._http_provider.secret = value

    @staticmethod
    def query_url(**query):
        query = {
            key: value for key, value in query.items() if value is not None
        }
        encoded_query = urlencode(query)
        return "?" + encoded_query

    @staticmethod
    def event_poll_url():
        url = '%s/%s' % (Client.event_url(), 'poll')
        return url

    def event_get(self, event_id):
        return self.get(self.event_url(event_id))

    def event_poll(self, limit=None, ack_only=False, last_id=None,
                   include_read=False, levels=list(), object_types=list()):
        body = {
            'limit': limit,
            'ack_only': ack_only,
            'last_id': last_id,
            'include_read': include_read,
            'levels': levels,
            'object_types': object_types
        }

        return self.get(self.event_poll_url(), body)

    def event_ack(self, event_id, resolution=''):
        body = {
            'resolution': resolution
        }
        return self.patch(self.event_url(event_id), body)

    def event_ack_all(self, timestamp=None, resolution=None):
        body = {
            'timestamp': timestamp,
            'resolution': resolution
        }
        return self.patch(self.event_url(), body)
