import json

import requests
import logging
from abc import ABCMeta
from retrying import retry

DEFAULT_STOP_MAX_ATTEMPT_NUMBER = 10
DEFAULT_WAIT_FIXED = 100
DEFAULT_RETRY_ARGS = dict(
    stop_max_attempt_number=DEFAULT_STOP_MAX_ATTEMPT_NUMBER,
    wait_fixed=DEFAULT_WAIT_FIXED)

LOG = logging.getLogger(__name__)


def retry_if_connection_error(exception):
    if isinstance(exception, requests.ConnectionError):
        return True
    if isinstance(exception, requests.HTTPError):
        if exception.response.status_code in (503,):
            return True
    return False


class AbstractHttpProvider(metaclass=ABCMeta):

    def __init__(self, token='', secret=''):
        self.token = token
        self.secret = secret

    @property
    def headers(self):
        return {'Authorization': str('Bearer ' + str(self.token)),
                'Secret': str(self.secret),
                'Content-type': 'application/json'}


class RequestsHttpProvider(AbstractHttpProvider):
    def __init__(self, url, verify=True, token='', secret=''):
        self.url = url
        self.verify = verify
        self.session = requests.session()
        super().__init__(token=token, secret=secret)

    @retry(**DEFAULT_RETRY_ARGS, retry_on_exception=retry_if_connection_error)
    def request(self, path, method, data=None):
        full_url = self.url + path
        response = self.session.request(
            method, full_url, data=data, headers=self.headers,
            verify=self.verify)
        response.raise_for_status()
        response_body = None
        if response.status_code != requests.codes.no_content:
            if 'application/json' in response.headers['Content-Type']:
                response_body = json.loads(
                    response.content.decode('utf-8'))
            if 'text/plain' in response.headers['Content-Type']:
                response_body = response.content.decode()
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
            if 'application/json' in response.headers['Content-Type']:
                response_body = json.loads(response.body.decode('utf-8'))
            if 'text/plain' in response.headers['Content-Type']:
                response_body = response.body.decode()
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
                url, verify, token=token, secret=secret)
        self._http_provider = http_provider
        self._api_version = api_version

    def _url(self, sub_url):
        return "/herald/%s/%s" % (self._api_version, sub_url)

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

    def delete(self, url):
        return self._request(url, "DELETE")

    @staticmethod
    def user_notification_url(id):
        url = "users/%s/notifications" % id
        return url

    @staticmethod
    def notification_url(id):
        url = "notifications/%s" % id
        return url

    def user_notification_list(self, user_id):
        code, resp_body = self.get(self.user_notification_url(user_id))
        return code, resp_body.get('notifications')

    def notification_get(self, id):
        return self.get(self.notification_url(id))

    def notification_create(self, user_id, name, filter, reactions=None):
        body = {
            "name": name,
            "filter": filter,
            "reactions": reactions
        }
        return self.post(self.user_notification_url(user_id), body)

    def notification_update(self, id, **params):
        return self.patch(self.notification_url(id), params)

    def notification_delete(self, id):
        return self.delete(self.notification_url(id))
