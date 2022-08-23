import io
import json
import inspect
import os
import time

import requests
import logging
from abc import ABCMeta
from urllib.parse import urlencode
from retrying import retry

DEFAULT_STOP_MAX_ATTEMPT_NUMBER = 10
DEFAULT_WAIT_FIXED = 100
DEFAULT_RETRY_ARGS = dict(
    stop_max_attempt_number=DEFAULT_STOP_MAX_ATTEMPT_NUMBER,
    wait_fixed=DEFAULT_WAIT_FIXED)

LOG = logging.getLogger(__name__)
ACURA_CERT_PATH = '/acura.crt'


def retry_if_connection_error(exception):
    if isinstance(exception, requests.ConnectionError):
        return True
    if isinstance(exception, requests.HTTPError):
        if exception.response.status_code in (503,):
            return True
    return False


def null_check(func):
    """
        Checks that expected args/kwargs are set. *args/**kwargs are ignored.
        Calls func if params are broken so original error was not nasked
    """
    def check(*args, **kwargs):
        spec = inspect.getfullargspec(func)
        res = {}
        if spec.defaults:
            res.update(dict(zip(reversed(spec.args), reversed(spec.defaults))))
        if spec.kwonlydefaults:
            res.update(spec.kwonlydefaults)

        all_args = dict(zip(spec.args, args))
        res.update(all_args)

        broken_call = False
        for k, v in kwargs.items():
            if k in all_args:
                # already set
                broken_call = True
            if k in spec.args or k in spec.kwonlyargs:
                # is in args/kwargs
                res[k] = v
        if len(res) != len(spec.args) + len(spec.kwonlyargs):
            # duplicates
            broken_call = True
        unset = list(filter(lambda x: res.get(x) is None, res.keys()))
        if unset and not broken_call:
            raise Exception("Should provide %s" % " or ".join(unset))
        return func(*args, **kwargs)

    return check


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

    @retry(**DEFAULT_RETRY_ARGS, retry_on_exception=retry_if_connection_error)
    def request(self, path, method, data=None):
        full_url = self.url + path

        headers = self.headers
        if data and isinstance(data, io.IOBase):
            headers['Content-type'] = 'application/octet-stream'
            data.seek(0, 2)
            headers['Content-length'] = str(data.tell())
            data.seek(0, 0)

        response = self.session.request(method, full_url, data=data,
                                        headers=headers, verify=self.verify)
        response.raise_for_status()
        response_body = None
        if response.status_code != requests.codes.no_content:
            if 'application/json' in response.headers['Content-Type']:
                response_body = json.loads(
                    response.content.decode('utf-8'))
            if ('text/plain' in response.headers['Content-Type'] or
                    'text/csv' in response.headers['Content-Type']):
                response_body = response.content.decode()
            if 'application/octet-stream' in response.headers['Content-Type']:
                response_body = response.content
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
            url, method=method, body=body, headers=self.headers,
            allow_nonstandard_methods=True)
        if self._rethrow:
            response.rethrow()
        response_body = None
        try:
            content_type = response.headers.get('Content-Type')
            if content_type:
                if 'application/json' in content_type:
                    response_body = json.loads(response.body.decode('utf-8'))
                elif ('text/plain' in content_type or
                      'text/csv' in content_type):
                    response_body = response.body.decode()
                elif 'application/octet-stream' in content_type:
                    response_body = response.body
        except Exception as e:
            LOG.error("failed to decode response body %s", e)
            response_body = None
        return response.code, response_body

    def close(self):
        pass


class Client:
    def __init__(self, address="127.0.0.1", port="80", api_version="v1",
                 url=None, http_provider=None, token='', secret='',
                 verify=True):
        if http_provider is None:
            if url is None:
                url = "http://%s:%s" % (address, port)
            http_provider = RequestsHttpProvider(
                url, token, secret, verify)
        self._http_provider = http_provider
        self._api_version = api_version

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

    def _url(self, sub_url):
        return "/restapi/%s/%s" % (self._api_version, sub_url)

    def _request(self, url, method, body=None):
        data = None
        if body is not None:
            data = json.dumps(body)
        return self._http_provider.request(self._url(url), method, data)

    def get(self, url, body=None):
        return self._request(url, "GET", body)

    def post(self, url, body):
        return self._request(url, "POST", body)

    def put(self, url, body):
        return self._request(url, "PUT", body)

    def patch(self, url, body):
        return self._request(url, "PATCH", body)

    def delete(self, url, body=None):
        return self._request(url, "DELETE", body)

    @staticmethod
    def context_url():
        url = 'context'
        return url

    @staticmethod
    def auth_hierarchy_url():
        url = 'auth_hierarchy'
        return url

    @staticmethod
    def resource_url():
        url = 'resources_info'
        return url

    @staticmethod
    def query_url(**query):
        query = {
            key: value for key, value in query.items() if value is not None
            }
        encoded_query = urlencode(query)
        return "?" + encoded_query

    def __del__(self):
        self._http_provider.close()

    def context_get(self, type, uuid):
        body = {
            "type": type,
            "uuid": uuid
        }
        return self.get(self.context_url(), body)

    def auth_hierarchy_get(self, type, scope_id):
        url = self.auth_hierarchy_url()
        url += self.query_url(
            type=type,
            scope_id=scope_id
        )
        return self.get(url)

    def resources_get(self, payload):
        body = {
            "payload": payload
        }
        return self.get(self.resource_url(), body)
