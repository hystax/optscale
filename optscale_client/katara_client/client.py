import json
import logging
import os
from abc import ABCMeta
from urllib.parse import urlencode

import requests
from retrying import retry

LOG = logging.getLogger(__name__)


def retry_if_connection_error(exception):
    if isinstance(exception, requests.ConnectionError):
        return True
    if isinstance(exception, requests.HTTPError):
        if exception.response.status_code in (503,):
            return True
    return False


class AbstractHttpProvider(metaclass=ABCMeta):
    def __init__(self, secret="", ip=None):
        self._secret = secret
        self._ip = ip

    @property
    def headers(self):
        headers = {"Secret": str(self._secret), "Content-type": "application/json"}
        if self._ip:
            headers.update({"X-Forwarded-For": self._ip})
        return headers

    @property
    def secret(self):
        return self._secret

    @secret.setter
    def secret(self, value):
        self._secret = value

    @property
    def ip(self):
        return self._ip


class RequestsHttpProvider(AbstractHttpProvider):
    def __init__(self, url, secret="", verify=True, ip=None):
        self.url = url
        self.verify = verify
        self.session = requests.session()
        super().__init__(secret, ip)

    @retry(
        stop_max_delay=10000,
        wait_fixed=1000,
        retry_on_exception=retry_if_connection_error,
    )
    def request(self, path, method, data=None):
        full_url = self.url + path
        response = self.session.request(
            method, full_url, data=data, headers=self.headers, verify=self.verify
        )
        response.raise_for_status()
        response_body = None
        if response.status_code != requests.codes.no_content:
            response_body = json.loads(response.content.decode("utf-8"))
        return response.status_code, response_body

    def close(self):
        self.session.close()


class FetchMethodHttpProvider(AbstractHttpProvider):
    def __init__(self, fetch_method, rethrow=True, secret="", ip=None):
        self.fetch = fetch_method
        self._rethrow = rethrow
        super().__init__(secret, ip)

    def request(self, url, method, body=None):
        response = self.fetch(
            url,
            method=method,
            body=body,
            allow_nonstandard_methods=True,
            headers=self.headers,
        )
        if self._rethrow:
            response.rethrow()
        try:
            decoded_response = json.loads(response.body.decode("utf-8"))
        except Exception as e:
            LOG.error("Failed to decode response body %s", e)
            decoded_response = None
        return response.code, decoded_response

    def close(self):
        pass


class Client:
    def __init__(
        self,
        address="127.0.0.1",
        port="80",
        api_version="v2",
        url=None,
        http_provider=None,
        secret="",
        verify=True,
        ip=None,
    ):
        if http_provider is None:
            if url is None:
                url = "http://%s:%s" % (address, port)
            http_provider = RequestsHttpProvider(url, secret, verify, ip)
        self._http_provider = http_provider
        self._api_version = api_version

    def _url(self, sub_url):
        return "/katara/%s/%s" % (self._api_version, sub_url)

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

    @property
    def secret(self):
        return self._http_provider.secret

    @secret.setter
    def secret(self, value):
        self._http_provider.secret = value

    @staticmethod
    def query_url(**query):
        query = {key: value for key, value in query.items() if value is not None}
        encoded_query = urlencode(query, doseq=True)
        return "?" + encoded_query

    @staticmethod
    def reports_url(id=None):
        url = "reports"
        if id is not None:
            url = "%s/%s" % (url, id)
        return url

    @staticmethod
    def schedules_url(id=None):
        url = "schedules"
        if id is not None:
            url = "%s/%s" % (url, id)
        return url

    @staticmethod
    def recipients_url(id=None):
        url = "recipients"
        if id is not None:
            url = "%s/%s" % (url, id)
        return url

    @staticmethod
    def tasks_url(id=None):
        url = "tasks"
        if id is not None:
            url = "%s/%s" % (url, id)
        return url

    def schedule_get(self, id):
        return self.get(self.schedules_url(id))

    def schedule_update(self, id, **params):
        return self.patch(self.schedules_url(id), params)

    def schedule_delete(self, id):
        return self.delete(self.schedules_url(id))

    def schedule_create(self, crontab, report_id, recipient_id):
        body = {
            "crontab": crontab,
            "report_id": report_id,
            "recipient_id": recipient_id,
        }
        return self.post(self.schedules_url(), body)

    def schedule_list(self, recipient_id, report_id=None):
        url = self.schedules_url() + self.query_url(
            recipient_id=recipient_id, report_id=report_id
        )
        return self.get(url)

    def task_get(self, id, expanded=False):
        url = self.tasks_url(id)
        url += self.query_url(expanded=expanded)
        return self.get(url)

    def task_update(self, id, **params):
        return self.patch(self.tasks_url(id), params)

    def tasks_create(self, tasks: list):
        body = {"tasks": tasks}
        return self.post(self.tasks_url(), body)

    def report_get(self, id):
        return self.get(self.reports_url(id))

    def report_list(self):
        return self.get(self.reports_url())

    def recipient_get(self, id):
        return self.get(self.recipients_url(id))

    def recipient_update(self, id, **params):
        return self.patch(self.recipients_url(id), params)

    def recipients_delete(
        self, recipient_ids: list = None, scope_ids: list = None, user_ids: list = None
    ):
        url = self.recipients_url() + self.query_url(
            recipient_ids=recipient_ids, scope_ids=scope_ids, user_ids=user_ids
        )
        return self.delete(url)

    def recipient_create(self, scope_id, role_purpose=None, user_id=None, meta=None):
        body = {
            "role_purpose": role_purpose,
            "scope_id": scope_id,
        }
        if user_id:
            body["user_id"] = user_id
        if meta:
            body["meta"] = meta
        return self.post(self.recipients_url(), body)

    def recipient_list(self, scope_id):
        url = self.recipients_url() + self.query_url(scope_id=scope_id)
        return self.get(url)
