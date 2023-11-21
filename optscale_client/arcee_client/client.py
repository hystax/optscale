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
        return "/arcee/%s/%s" % (self._api_version, sub_url)

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
    def applications_url(id=None):
        url = 'applications'
        if id is not None:
            url = '%s/%s' % (url, id)
        return url

    @staticmethod
    def goals_url(id=None):
        url = 'goals'
        if id is not None:
            url = '%s/%s' % (url, id)
        return url

    @staticmethod
    def run_url(id):
        url = 'run'
        if id is not None:
            url = '%s/%s' % (url, id)
        return url

    @staticmethod
    def executor_url(id_):
        return "%s/%s" % ("executors", id_)

    @staticmethod
    def runs_url():
        return 'runs'

    @staticmethod
    def tokens_url(id=None):
        url = 'tokens'
        if id is not None:
            url = '%s/%s' % (url, id)
        return url

    @staticmethod
    def executors_url():
        return "run/executors"

    def goals_get(self):
        """
        Get goals
        :return:
        """
        return self.get(self.goals_url())

    def goals_create(self, key, target_value, tendency, name, func):
        """
        Creates goal
        """
        b = {
            "key": key,
            "target_value": target_value,
            "tendency": tendency,
            "name": name,
            "func": func
        }
        return self.post(self.goals_url(), b)

    def goals_update(self, goal_id, target_value=None, tendency=None, name=None, func=None):
        b = dict()
        if target_value is not None:
            b.update({
                "target_value": target_value,
            })
        if tendency is not None:
            b.update({
                "tendency": tendency,
            })
        if name is not None:
            b.update({
                "name": name,
            })
        if func is not None:
            b.update({
                "func": func,
            })
        return self.patch(self.goals_url(goal_id), b)

    def goal_get(self, goal_id):
        """
        Gets goal by id
        :param goal_id:
        :return:
        """
        return self.get(self.goals_url(goal_id))

    def goal_delete(self, goal_id):
        """
        Deketes goal by goal_id
        :param goal_id:
        :return:
        """
        return self.delete(self.goals_url(goal_id))

    def applications_get(self):
        return self.get(self.applications_url())

    def applications_bulk_get(self, application_ids, include_deleted=False):
        url = f'{self.applications_url()}/bulk'
        url += self.query_url(
            application_id=application_ids,
            include_deleted=include_deleted
        )
        return self.get(url)

    def application_get(self, id: str):
        return self.get(self.applications_url(id))

    def application_create(self, application_key, owner_id, name=None, goals=None):
        """
        Creates application
        :param application_key:
        :param owner_id:
        :param name:
        :param goals:
        :return:
        """
        b = {
            'key': application_key,
            'owner_id': owner_id,
            'name': name,
            'goals': goals
        }
        return self.post(self.applications_url(), b)

    def run_update(
            self,
            id_,
            runset_id=None,
            hyperparameters=None,
            state=None,
            reason=None,
            runset_name=None,
            finish=False,
    ):
        """
        Updates run. This method used with bulldozer worker
        """
        b = dict()
        if runset_id is not None:
            b.update({
                "runset_id": runset_id,
            })
        if hyperparameters is not None:
            b.update({
                "hyperparameters": hyperparameters,
            })
        if state is not None:
            b.update({
                "state": state,
            })
        if reason is not None:
            b.update({
                "reason": reason,
            })

        if runset_name is not None:
            b.update({
                "runset_name": runset_name,
            })
        if finish:
            b.update({
                "finish": finish,
            })
        return self.patch(self.run_url(id_), b)

    def application_update(self, application_id, owner_id=None, name=None, goals=None):
        """
        Updates application
        :param application_id:
        :param owner_id:
        :param name:
        :param goals: list(goal_id):
        :return:
        """
        b = dict()
        if owner_id is not None:
            b.update({
                "owner_id": owner_id
            })
        if name is not None:
            b.update({
                "name": name
            })
        if goals is not None:
            b.update({
                "goals": goals
            })
        return self.patch(self.applications_url(application_id), b)

    def application_delete(self, id):
        """

        :param id:
        :return:
        """
        return self.delete(self.applications_url(id))

    def applications_runs_get(self, application_id):
        """
        Gets application runs
        :param application_id:
        :return:
        """
        return self.get("%s/run" % self.applications_url(application_id))

    def runs_bulk_get(self, runset_ids=None):
        """
        Gets runs by runset ids
        :param runset_ids: list (runset_id: str)
        :return:
        """
        url = self.runs_url()
        if runset_ids:
            url += self.query_url(runset_id=runset_ids)
        return self.get(url)

    def run_milestones_get(self, run_id):
        """
        Gets milestones
        :param run_id:
        :return:
        """
        return self.get("%s/milestones" % self.run_url(run_id))

    def run_logs_get(self, run_id):
        """
        Gets logs
        :param run_id:
        :return:
        """
        return self.get("%s/logs" % self.run_url(run_id))

    def run_get(self, run_id):
        """
        Gets logs
        :param run_id:
        :return:
        """
        return self.get(self.run_url(run_id))

    def executors_get(self, applications_ids=None, run_ids=None):
        """
        Gets executors
        :param applications_ids: list (application_id: str)
        :param run_ids: list(run_id: str)
        :return:
        """
        if applications_ids is None:
            applications_ids = []
        if run_ids is None:
            run_ids = []
        url = self.executors_url() + self.query_url(
            run_id=run_ids,
            application_id=applications_ids,
        )
        return self.get(url)

    def imports_get(self, app_id):
        """
        Gets Imports for application
        :param app_id:
        :return:
        """
        return self.get("%s/imports" % self.applications_url(app_id))

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

    def stages_get(self, run_id):
        """
        Gets stages
        :param run_id:
        :return:
        """
        return self.get("%s/stages" % self.run_url(run_id))

    def proc_data_get(self, run_id):
        """
        Gets Proc data
        :param run_id:
        :return:
        """
        return self.get("%s/proc" % self.run_url(run_id))

    def runs_by_executor(self, executor_id, applications_ids=None):
        """
        Gets runs by executor id
        """
        if applications_ids is None:
            applications_ids = []
        url = "%s/%s" % (self.executor_url(executor_id), "runs") + self.query_url(
            application_id=applications_ids,
        )
        return self.get(url)
