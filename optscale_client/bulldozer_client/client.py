import decimal
import json
import logging
import os
from abc import ABCMeta
from urllib.parse import urlencode

import requests
from typing import (
    Iterable,
    Union,
)
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
    def __init__(self, token='', secret='', ip=None):
        self._token = token
        self._secret = secret
        self._ip = ip

    @property
    def headers(self):
        headers = {'Content-type': 'application/json'}
        if self._token:
            headers.update({'x-api-key': str(self._token)})
        if self._secret:
            headers.update({'Secret': str(self._secret)})
        if self._ip:
            headers.update({'X-Forwarded-For': self._ip})
        return headers

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
    def ip(self):
        return self._ip


class RequestsHttpProvider(AbstractHttpProvider):
    def __init__(self, url, token='', secret='', verify=True,
                 ip=None):
        self.url = url
        self.verify = verify
        self.session = requests.session()
        acura_cert = os.environ.get('ACURA_CERT')
        if acura_cert is not None:
            if not os.path.exists(ACURA_CERT_PATH):
                with open(ACURA_CERT_PATH, 'w') as f_crt:
                    f_crt.write(acura_cert)
            self.session.verify = ACURA_CERT_PATH
        super().__init__(token, secret, ip)

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
    def __init__(self, fetch_method, rethrow=True, token='', secret='', ip=None):
        self.fetch = fetch_method
        self._rethrow = rethrow
        super().__init__(token, secret, ip)

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


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)


class Client:
    def __init__(self, address="127.0.0.1", port="80", api_version="v2",
                 url=None, http_provider=None, token='', secret='', verify=True, ip=None):
        if http_provider is None:
            if url is None:
                url = "http://%s:%s" % (address, port)
            http_provider = RequestsHttpProvider(url, token, secret, verify, ip)
        self._http_provider = http_provider
        self._api_version = api_version

    def _url(self, sub_url):
        return "/bulldozer/%s/%s" % (self._api_version, sub_url)

    def _request(self, url, method, body=None):
        data = None
        if body is not None:
            data = json.dumps(body, cls=Encoder)
        return self._http_provider.request(self._url(url), method, data)

    def get(self, url, body=None):
        return self._request(url, "GET", body)

    def post(self, url, body):
        return self._request(url, "POST", body)

    def patch(self, url, body):
        return self._request(url, "PATCH", body)

    def delete(self, url):
        return self._request(url, "DELETE")

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
        encoded_query = urlencode(query, doseq=True)
        return "?" + encoded_query

    @staticmethod
    def tokens_url(id=None):
        url = 'tokens'
        if id is not None:
            url = '%s/%s' % (url, id)
        return url

    @staticmethod
    def templates_url(id=None):
        url = 'templates'
        if id is not None:
            url = '%s/%s' % (url, id)
        return url

    def runsets_url(self, template_id):
        return '%s/%s/runsets' % (self.templates_url(), template_id)

    @staticmethod
    def runset_url(id_):
        return 'runsets/%s' % id_

    @staticmethod
    def runners_url(id=None):
        url = 'runners'
        if id is not None:
            url = '%s/%s' % (url, id)
        return url

    def token_create(self, token: str):
        """
        Creates token
        :param token:
        :return:
        """
        b = {
            'token': token,
        }
        return self.post(self.tokens_url(), b)

    def token_delete(self, id: str):
        """
        :param id: id or token
        :return:
        """
        return self.delete(self.tokens_url(id))

    def token_get(self, id: str):
        """
        :param id: id or token
        :return:
        """
        return self.get(self.tokens_url(id))

    def template_create(
            self,
            name: str,
            application_ids: Iterable[str],
            cloud_account_ids: Iterable[str],
            region_ids: Iterable[str],
            instance_types: Iterable[str],
            budget: decimal.Decimal,
            name_prefix: str,
            tags: dict,
            hyperparameters: dict
    ):
        b = {
            "name": name,
            "application_ids": application_ids,
            "cloud_account_ids": cloud_account_ids,
            "region_ids": region_ids,
            "instance_types": instance_types,
            "budget": budget,
            "name_prefix": name_prefix,
            "tags": tags,
            "hyperparameters": hyperparameters,
        }
        return self.post(self.templates_url(), b)

    def template_update(
            self,
            id_: str,
            name: Union[str, None] = None,
            application_ids: Union[Iterable[str], None] = None,
            cloud_account_ids: Union[Iterable[str], None] = None,
            region_ids: Union[Iterable[str], None] = None,
            instance_types: Union[Iterable[str], None] = None,
            budget: Union[decimal.Decimal, None] = None,
            name_prefix: Union[str, None] = None,
            tags: Union[dict, None] = None,
            hyperparameters: Union[dict, None] = None
    ):
        b = dict()
        if name is not None:
            b.update({"name": name})
        if application_ids is not None:
            b.update({"application_ids": application_ids})
        if cloud_account_ids is not None:
            b.update({"cloud_account_ids": cloud_account_ids})
        if region_ids is not None:
            b.update({"region_ids": region_ids})
        if instance_types is not None:
            b.update({"instance_types": instance_types})
        if budget is not None:
            b.update({"budget": budget})
        if name_prefix is not None:
            b.update({"name_prefix": name_prefix})
        if tags is not None:
            b.update({"tags": tags})
        if hyperparameters is not None:
            b.update({"hyperparameters": hyperparameters})
        return self.patch(self.templates_url(id_), b)

    def templates_list(self):
        return self.get(self.templates_url())

    def template_delete(self, id_: str):
        return self.delete(self.templates_url(id_))

    def template_get(self, id_: str):
        return self.get(self.templates_url(id_))

    def runset_create(
            self,
            template_id: str,
            application_id: str,
            cloud_account_id: str,
            region_id: str,
            instance_type: str,
            name_prefix: str,
            owner_id: str,
            hyperparameters: dict,
            tags: dict,
            destroy_conditions: dict,
            commands: str,
            spot_settings: Union[dict, None] = None,
            open_ingress: bool = False,
    ):
        b = {
            "application_id": application_id,
            "cloud_account_id": cloud_account_id,
            "region_id": region_id,
            "instance_type": instance_type,
            "owner_id": owner_id,
            "name_prefix": name_prefix,
            "tags": tags,
            "hyperparameters": hyperparameters,
            "destroy_conditions": destroy_conditions,
            "commands": commands,
            "spot_settings": spot_settings,
            "open_ingress": open_ingress,
        }
        return self.post(self.runsets_url(template_id), b)

    def runset_update(self, runset_id, state: int, runner_id=None):
        b = {
            "state": state,
            "runner_id": runner_id,
        }
        return self.patch(self.runset_url(runset_id), b)

    def runset_list(self, template_id):
        return self.get(self.runsets_url(template_id))

    def runset_get(self, id_):
        return self.get(self.runset_url(id_))

    def runners_list(self, runset_id):
        url = "%s/%s" % (self.runset_url(runset_id), "runners")
        return self.get(url)

    def runners_bulk_get(self, runset_ids: Iterable[str]):
        """
        Gets runners list by runset ids
        :return:
        """
        if runset_ids is None:
            runset_ids = list()
        url = self.runners_url() + self.query_url(
            runset_id=runset_ids
        )
        return self.get(url)

    def update_runner(
        self,
        runner_id: str,
        state: Union[int, None] = None,
        return_code: Union[int, None] = None,
        reason: [str, None] = None,
        instance_id: Union[str, None] = None,
        name: Union[str, None] = None,
        ip_addr: Union[str, None] = None,
        destroyed_at: Union[int, None] = None,
        started_at: Union[int, None] = None,
        run_id: Union[str, None] = None,
    ):
        b = dict()
        if state is not None:
            b.update({"state": state})
        if return_code is not None:
            b.update({"return_code": return_code})
        if reason is not None:
            b.update({"reason": reason})
        if instance_id is not None:
            b.update({"instance_id": instance_id})
        if name is not None:
            b.update({"name": name})
        if ip_addr is not None:
            b.update({"ip_addr": ip_addr})
        if destroyed_at is not None:
            b.update({"destroyed_at": destroyed_at})
        if started_at is not None:
            b.update({"started_at": started_at})
        if run_id is not None:
            b.update({"run_id": run_id})
        return self.patch(self.runners_url(runner_id), b)

    def get_runner(self, runner_id):
        return self.get(self.runners_url(runner_id))
