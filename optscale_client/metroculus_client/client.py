import json
import logging
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
    def __init__(self, secret=''):
        self._secret = secret

    @property
    def headers(self):
        return {
            'Secret': str(self._secret),
            'Content-type': 'application/json'
        }

    @property
    def secret(self):
        return self._secret

    @secret.setter
    def secret(self, value):
        self._secret = value


class RequestsHttpProvider(AbstractHttpProvider):
    def __init__(self, url, secret='', verify=True):
        self.url = url
        self.verify = verify
        self.session = requests.session()
        super().__init__(secret)

    @retry(stop_max_delay=10000, wait_fixed=1000,
           retry_on_exception=retry_if_connection_error)
    def request(self, path, method, data=None):
        full_url = self.url + path
        response = self.session.request(
            method, full_url, data=data,
            headers=self.headers, verify=self.verify)
        response.raise_for_status()
        response_body = None
        if response.status_code != requests.codes.no_content:
            response_body = json.loads(response.content.decode('utf-8'))
        return response.status_code, response_body

    def close(self):
        self.session.close()


class FetchMethodHttpProvider(AbstractHttpProvider):
    def __init__(self, fetch_method, rethrow=True, secret=''):
        self.fetch = fetch_method
        self._rethrow = rethrow
        super().__init__(secret)

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
            LOG.error("Failed to decode response body %s", e)
            decoded_response = None
        return response.code, decoded_response

    def close(self):
        pass


class Client:
    def __init__(self, address="127.0.0.1", port="80", api_version="v2",
                 url=None, http_provider=None, secret='',
                 verify=True):
        if http_provider is None:
            if url is None:
                url = "http://%s:%s" % (address, port)
            http_provider = RequestsHttpProvider(url, secret, verify)
        self._http_provider = http_provider
        self._api_version = api_version

    @property
    def secret(self):
        return self._http_provider.secret

    @secret.setter
    def secret(self, value):
        self._http_provider.secret = value

    def _url(self, sub_url):
        return "/metroculus/%s/%s" % (self._api_version, sub_url)

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
    def query_url(**query):
        query = {
            key: value for key, value in query.items() if value is not None
        }
        encoded_query = urlencode(query, doseq=True)
        return "?" + encoded_query

    @staticmethod
    def aggregated_metrics_url():
        return 'agr_metrics'

    @staticmethod
    def activity_breakdown_url():
        return 'activity_breakdown'

    @staticmethod
    def metrics_url():
        return 'metrics'

    @staticmethod
    def k8s_metrics_url():
        return 'k8s_metrics'

    def get_activity_breakdown(self, cloud_account_id, resource_ids, start_date,
                               end_date, meter_name=None):
        body = {
            'cloud_account_id': cloud_account_id,
            'resource_id': resource_ids,
            'start_date': start_date,
            'end_date': end_date
        }
        if meter_name:
            body.update({'meter_name': meter_name})
        url = self.activity_breakdown_url() + self.query_url(**body)
        return self.get(url)

    def get_aggregated_metrics(self, cloud_account_id, resource_ids, start_date,
                               end_date, meter_name=None):
        body = {
            'cloud_account_id': cloud_account_id,
            'resource_id': resource_ids,
            'start_date': start_date,
            'end_date': end_date
        }
        if meter_name:
            body.update({'meter_name': meter_name})
        url = self.aggregated_metrics_url() + self.query_url(**body)
        return self.get(url)

    def get_metrics(self, cloud_account_id, resource_id, start_date,
                    end_date, interval=900):
        body = {
            'cloud_account_id': cloud_account_id,
            'resource_id': resource_id,
            'start_date': start_date,
            'end_date': end_date,
            'interval': interval
        }
        url = self.metrics_url() + self.query_url(**body)
        return self.get(url)

    def get_k8s_metrics(self, cloud_account_id, start_date, end_date):
        body = {
            'cloud_account_id': cloud_account_id,
            'start_date': start_date,
            'end_date': end_date,
        }
        url = self.k8s_metrics_url() + self.query_url(**body)
        return self.get(url)
