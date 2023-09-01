import io
import json

import requests
import logging
from abc import ABCMeta
from urllib.parse import urlencode
from retrying import retry

DEFAULT_STOP_MAX_ATTEMPT_NUMBER = 10
DEFAULT_WAIT_FIXED = 100
DEFAULT_RETRY_ARGS = dict(
    stop_max_attempt_number=DEFAULT_STOP_MAX_ATTEMPT_NUMBER,
    wait_fixed=DEFAULT_WAIT_FIXED,
)

LOG = logging.getLogger(__name__)


def retry_if_connection_error(exception):
    if isinstance(exception, requests.ConnectionError):
        return True
    if isinstance(exception, requests.HTTPError):
        if exception.response.status_code in (503,):
            return True
    return False


class AbstractHttpProvider(metaclass=ABCMeta):
    def __init__(self, token="", secret="", extra_headers=None):
        self._token = token
        self._secret = secret
        self._extra_headers = extra_headers or {}

    @property
    def headers(self):
        return {
            "Authorization": str("Bearer " + str(self._token)),
            "Secret": str(self._secret),
            "Content-type": "application/json",
            **self._extra_headers,
        }

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

    @property
    def extra_headers(self):
        return self._extra_headers

    @extra_headers.setter
    def extra_headers(self, value):
        self._extra_headers = value


class RequestsHttpProvider(AbstractHttpProvider):
    def __init__(self, url, token="", secret="", extra_headers=None, verify=True):
        self.url = url
        self.verify = verify
        self.session = requests.session()
        super().__init__(token, secret, extra_headers)

    @retry(**DEFAULT_RETRY_ARGS, retry_on_exception=retry_if_connection_error)
    def request(self, path, method, data=None):
        full_url = self.url + path

        headers = self.headers
        if data and isinstance(data, io.IOBase):
            headers["Content-type"] = "application/octet-stream"
            data.seek(0, 2)
            headers["Content-length"] = str(data.tell())
            data.seek(0, 0)

        response = self.session.request(
            method, full_url, data=data, headers=headers, verify=self.verify
        )
        response.raise_for_status()
        response_body = None
        if response.status_code != requests.codes.no_content:
            if "application/json" in response.headers["Content-Type"]:
                response_body = json.loads(response.content.decode("utf-8"))
            if "text/plain" in response.headers["Content-Type"]:
                response_body = response.content.decode()
        return response.status_code, response_body

    def close(self):
        self.session.close()


class FetchMethodHttpProvider(AbstractHttpProvider):
    def __init__(
        self, fetch_method, rethrow=True, token="", secret="", extra_headers=None
    ):
        self.fetch = fetch_method
        self._rethrow = rethrow
        super().__init__(token, secret, extra_headers)

    def request(self, url, method, body=None):
        response = self.fetch(
            url,
            method=method,
            body=body,
            headers=self.headers,
            allow_nonstandard_methods=True,
        )
        if self._rethrow:
            response.rethrow()
        response_body = None
        try:
            content_type = response.headers.get("Content-Type")
            if content_type:
                if "application/json" in content_type:
                    response_body = json.loads(response.body.decode("utf-8"))
                elif "text/plain" in content_type:
                    response_body = response.body.decode()
        except Exception as e:
            LOG.error("failed to decode response body %s", e)
            response_body = None
        return response.code, response_body

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
        token="",
        secret="",
        extra_headers=None,
        verify=True,
    ):
        if http_provider is None:
            if url is None:
                url = "http://%s:%s" % (address, port)
            http_provider = RequestsHttpProvider(
                url, token, secret, extra_headers, verify
            )
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

    @property
    def extra_headers(self):
        return self._http_provider.extra_headers

    @extra_headers.setter
    def extra_headers(self, value):
        self._http_provider.extra_headers = value

    def _url(self, sub_url):
        return "/jira_bus/%s/%s" % (self._api_version, sub_url)

    def _request(self, url, method, body=None):
        data = None
        if body is not None:
            data = json.dumps(body)
        return self._http_provider.request(self._url(url), method, data)

    def get(self, url, body=None):
        if body:
            url = url + self.query_url(**body)
        return self._request(url, "GET")

    def post(self, url, body):
        return self._request(url, "POST", body)

    def put(self, url, body):
        return self._request(url, "PUT", body)

    def patch(self, url, body):
        return self._request(url, "PATCH", body)

    def delete(self, url):
        return self._request(url, "DELETE")

    @staticmethod
    def query_url(**query):
        query = {key: value for key, value in query.items() if value is not None}
        encoded_query = urlencode(query, doseq=True)
        return "?" + encoded_query

    def __del__(self):
        self._http_provider.close()

    def app_descriptor_url(self):
        return "app_descriptor"

    def installed_url(self):
        return "installed"

    def user_assignment_url(self):
        return "user_assignment"

    def organization_assignment_url(self):
        return "organization_assignment"

    def issue_info_url(self):
        return "issue_info"

    def organization_url(self):
        return "organization"

    def issue_updated_url(self):
        return "issue_updated"

    def issue_deleted_url(self):
        return "issue_deleted"

    def shareable_resource_url(self):
        return "shareable_resource"

    def issue_attachment_collection_url(self, resource_id):
        return "shareable_resource/{}/issue_attachment".format(resource_id)

    def issue_attachment_item_url(self, attachment_id):
        return "issue_attachment/{}".format(attachment_id)

    def shareable_book_collection_url(self, resource_id):
        return "shareable_resource/{}/shareable_book".format(resource_id)

    def shareable_book_item_url(self, booking_id):
        return "shareable_book/{}".format(booking_id)

    def organization_status_url(self, organization_id):
        return "organization/{}/status".format(organization_id)

    def app_descriptor(self, base_host=None):
        url = self.app_descriptor_url() + self.query_url(base_host=base_host)
        return self.get(url)

    def installed(self, payload):
        return self.post(self.installed_url(), payload)

    def user_assignment_get(self):
        return self.get(self.user_assignment_url())

    def user_assignment_create(self):
        return self.post(self.user_assignment_url(), None)

    def assign_auth_user(self, secret):
        return self.patch(self.user_assignment_url(), {"secret": secret})

    def user_assignment_delete(self):
        return self.delete(self.user_assignment_url())

    def organization_assignment_get(self, details=False):
        return self.get(
            self.organization_assignment_url() + self.query_url(details=details)
        )

    def organization_assignment_create(self, organization_id):
        return self.post(
            self.organization_assignment_url(), {"organization_id": organization_id}
        )

    def organization_assignment_delete(self):
        return self.delete(self.organization_assignment_url())

    def issue_info_get(self):
        return self.get(self.issue_info_url())

    def organization_list(self):
        return self.get(self.organization_url())

    def issue_updated(self, payload):
        return self.post(self.issue_updated_url(), payload)

    def issue_deleted(self, payload):
        return self.post(self.issue_deleted_url(), payload)

    def shareable_resource_list(self, current_issue=False):
        return self.get(
            self.shareable_resource_url() + self.query_url(current_issue=current_issue)
        )

    def issue_attachment_create(self, resource_id, data):
        return self.post(self.issue_attachment_collection_url(resource_id), data)

    def issue_attachment_update(self, attachment_id, data):
        return self.patch(self.issue_attachment_item_url(attachment_id), data)

    def issue_attachment_delete(self, attachment_id):
        return self.delete(self.issue_attachment_item_url(attachment_id))

    def shareable_book_create(self, resource_id, data):
        return self.post(self.shareable_book_collection_url(resource_id), data)

    def shareable_book_release(self, booking_id):
        return self.patch(self.shareable_book_item_url(booking_id), {})

    def shareable_book_delete(self, booking_id):
        return self.delete(self.shareable_book_item_url(booking_id))

    def organization_status_get(self, organization_id):
        return self.get(self.organization_status_url(organization_id))
