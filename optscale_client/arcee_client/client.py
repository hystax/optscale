import json
import logging
from abc import ABCMeta
from typing import Optional, List
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
                                        headers=self.headers,
                                        verify=self.verify)
        response.raise_for_status()
        response_body = None
        if response.status_code != requests.codes.no_content:
            response_body = json.loads(response.content.decode('utf-8'))
        return response.status_code, response_body

    def close(self):
        self.session.close()


class FetchMethodHttpProvider(AbstractHttpProvider):
    def __init__(self, fetch_method, rethrow=True, token='', secret='',
                 ip=None):
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
                 url=None, http_provider=None, token='', secret='',
                 verify=True, ip=None):
        if http_provider is None:
            if url is None:
                url = "http://%s:%s" % (address, port)
            http_provider = RequestsHttpProvider(url, token, secret, verify,
                                                 ip)
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
    def tasks_url(id=None):
        url = 'tasks'
        if id is not None:
            url = '%s/%s' % (url, id)
        return url

    @staticmethod
    def metrics_url(id=None):
        url = 'metrics'
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

    @staticmethod
    def leaderboards_url(task_id):
        return '%s/leaderboards' % Client.tasks_url(task_id)

    @staticmethod
    def datasets_url(id_=None):
        url = 'datasets'
        if id_ is not None:
            url = '%s/%s' % (url, id_)
        return url

    @staticmethod
    def leaderboard_url(id_=None):
        url = "leaderboards"
        if id_ is not None:
            url = '%s/%s' % (url, id_)
        return url

    @staticmethod
    def leaderboard_datasets_url(id_=None):
        url = "leaderboard_datasets"
        if id_ is not None:
            url = '%s/%s' % (url, id_)
        return url

    @staticmethod
    def labels_url():
        return 'labels'

    @staticmethod
    def console_url(run_id):
        return '%s/console' % Client.run_url(run_id)

    @staticmethod
    def consoles_url(run_id):
        return '%s/consoles' % Client.run_url(run_id)

    @staticmethod
    def models_url(model_id=None):
        url = 'models'
        if model_id:
            url = '%s/%s' % (url, model_id)
        return url

    @staticmethod
    def run_model_version_url(run_id, model_id):
        return 'runs/%s/models/%s/version' % (run_id, model_id)

    def model_versions_url(self, task_id):
        return '%s/model_versions' % (self.tasks_url(task_id))

    def metrics_get(self):
        """
        Get metrics
        :return:
        """
        return self.get(self.metrics_url())

    def metrics_create(self, key, target_value, tendency, name, func):
        """
        Creates metric
        """
        b = {
            "key": key,
            "target_value": target_value,
            "tendency": tendency,
            "name": name,
            "func": func
        }
        return self.post(self.metrics_url(), b)

    def metrics_update(self, metric_id, target_value=None, tendency=None,
                       name=None, func=None):
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
        return self.patch(self.metrics_url(metric_id), b)

    def metric_get(self, metric_id):
        """
        Gets metric by id
        :param metric_id:
        :return:
        """
        return self.get(self.metrics_url(metric_id))

    def metric_delete(self, metric_id):
        """
        Deketes metric by metric_id
        :param metric_id:
        :return:
        """
        return self.delete(self.metrics_url(metric_id))

    def tasks_get(self):
        return self.get(self.tasks_url())

    def tasks_bulk_get(self, task_ids, include_deleted=False):
        url = f'{self.tasks_url()}/bulk'
        url += self.query_url(
            task_id=task_ids,
            include_deleted=include_deleted
        )
        return self.get(url)

    def task_get(self, id: str):
        return self.get(self.tasks_url(id))

    def task_create(self, task_key, owner_id, name=None, metrics=None,
                    description=None):
        """
        Creates task
        :param task_key:
        :param owner_id:
        :param name:
        :param metrics:
        :param description:
        :return:
        """
        b = {
            'key': task_key,
            'owner_id': owner_id,
            'name': name,
            'metrics': metrics,
            'description': description,
        }
        return self.post(self.tasks_url(), b)

    def run_update(
            self,
            id_,
            runset_id=None,
            hyperparameters=None,
            state=None,
            reason=None,
            runset_name=None,
            dataset_ids=None,
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
        if dataset_ids is not None:
            b.update({
                "dataset_ids": dataset_ids,
            })
        if finish:
            b.update({
                "finish": finish,
            })
        return self.patch(self.run_url(id_), b)

    def task_update(
            self, task_id, owner_id=None, name=None, metrics=None, **params
    ):
        """
        Updates task
        :param task_id:
        :param owner_id:
        :param name:
        :param metrics: list(metric_id):
        :param params: task optional parameters like *description*
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
        if metrics is not None:
            b.update({
                "metrics": metrics
            })
        b.update(params)
        return self.patch(self.tasks_url(task_id), b)

    def task_delete(self, id):
        """

        :param id:
        :return:
        """
        return self.delete(self.tasks_url(id))

    def tasks_runs_get(self, task_id):
        """
        Gets task runs
        :param task_id:
        :return:
        """
        return self.get("%s/run" % self.tasks_url(task_id))

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

    def run_delete(self, run_id):
        """
        Deletes run by run_id
        :param run_id:
        :return:
        """
        return self.delete(self.run_url(run_id))

    def executors_get(self, tasks_ids=None, run_ids=None):
        """
        Gets executors
        :param tasks_ids: list (task_id: str)
        :param run_ids: list(run_id: str)
        :return:
        """
        if tasks_ids is None:
            tasks_ids = []
        if run_ids is None:
            run_ids = []
        url = self.executors_url() + self.query_url(
            run_id=run_ids,
            task_id=tasks_ids,
        )
        return self.get(url)

    def imports_get(self, app_id):
        """
        Gets Imports for task
        :param app_id:
        :return:
        """
        return self.get("%s/imports" % self.tasks_url(app_id))

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

    def executors_breakdown_get(self):
        return self.get("executors/breakdown")

    def runs_by_executor(self, executor_id, tasks_ids=None):
        """
        Gets runs by executor id
        """
        if tasks_ids is None:
            tasks_ids = []
        url = "%s/%s" % (self.executor_url(executor_id), "runs") + self.query_url(
            task_id=tasks_ids,
        )
        return self.get(url)

    def leaderboards_create(self, task_id, primary_metric, grouping_tags,
                            other_metrics=None, filters=None, group_by_hp=True):
        """
        Creates leaderboard
        """
        leaderboard = {
            "primary_metric": primary_metric,
            "other_metrics": other_metrics or [],
            "filters": filters or [],
            "grouping_tags": grouping_tags,
            "group_by_hp": group_by_hp,
        }
        return self.post(self.leaderboards_url(task_id), leaderboard)

    def leaderboard_update(self, task_id, primary_metric=None,
                           grouping_tags=None,
                           other_metrics=None, filters=None, group_by_hp=None):
        leaderboard = dict()
        for key, param in {
            'primary_metric': primary_metric,
            'grouping_tags': grouping_tags,
            'other_metrics': other_metrics,
            'filters': filters,
            'group_by_hp': group_by_hp
        }.items():
            if param is not None:
                leaderboard.update({
                    key: param
                })
        if filters is not None:
            leaderboard.update({
                "filters": filters,
            })
        return self.patch(self.leaderboards_url(task_id), leaderboard)

    def leaderboard_get(self, task_id):
        """
        Gets leaderboard by task_id
        :param leaderboard_id:
        :return:
        """
        return self.get(self.leaderboards_url(task_id))

    def leaderboard_delete(self, task_id):
        """
        Deletes leaderboard by task_id
        :param task_id:
        :return:
        """
        return self.delete(self.leaderboards_url(task_id))

    def leaderboard_details_get(self, task_id):
        """
        Gets leaderboard details by id
        :param task_id:
        :return:
        """
        url = self.leaderboards_url(task_id) + '/details'
        return self.get(url)

    def dataset_create(
            self,
            path: str,
            labels: List[str] = None,
            name: Optional[str] = None,
            description: Optional[str] = None,
            timespan_from: Optional[int] = None,
            timespan_to: Optional[int] = None,
    ):
        b = {
            "path": path,
            "name": name,
            "description": description,
            "labels": labels or [],
            "timespan_from": timespan_from,
            "timespan_to": timespan_to,
        }
        return self.post(self.datasets_url(), b)

    def dataset_update(self, id_: str, **params):
        '''
        Update Dataset object

        :param id_:
        :param params: dataset optional parameters like *labels*, *name*,
            *description*, *timespan_from*, *timespan_to*
        :return:
        '''
        return self.patch(self.datasets_url(id_), params)

    def dataset_list(self, include_deleted=False):
        url = self.datasets_url()
        url += self.query_url(
            include_deleted=include_deleted
        )
        return self.get(url)

    def dataset_delete(self, id_: str):
        return self.delete(self.datasets_url(id_))

    def dataset_get(self, id_: str):
        return self.get(self.datasets_url(id_))

    def labels_list(self):
        return self.get(self.labels_url())

    def console_create(self, run_id: str, output: str, error: str):
        data = {
            "output": output,
            "error": error,
        }
        return self.post(self.consoles_url(run_id), data)

    def console_get(self, run_id: str):
        return self.get(self.console_url(run_id))

    def leaderboard_dataset_create(self, leaderboard_id: str, name: str,
                                   dataset_ids: list):
        b = {
            "name": name,
            "dataset_ids": dataset_ids
        }
        return self.post("%s/%s" % (self.leaderboard_url(leaderboard_id),
                                    self.leaderboard_datasets_url()), b)

    def leaderboard_dataset_update(self, leaderboard_dataset_id: str,
                                   name: str=None, dataset_ids: list=None):
        b = {}
        if name is not None:
            b['name'] = name
        if dataset_ids is not None:
            b['dataset_ids'] = dataset_ids
        return self.patch(
            self.leaderboard_datasets_url(leaderboard_dataset_id), b)

    def leaderboard_datasets_get(self, leaderboard_id: str,
                                 include_deleted=False):
        url = "%s/%s" % (self.leaderboard_url(leaderboard_id),
                         self.leaderboard_datasets_url())
        url += self.query_url(
            include_deleted=include_deleted
        )
        return self.get(url)

    def leaderboard_dataset_get(self, leaderboard_dataset_id: str):
        return self.get(self.leaderboard_datasets_url(leaderboard_dataset_id))

    def leaderboard_dataset_delete(self, leaderboard_dataset_id: str):
        return self.delete(self.leaderboard_datasets_url(
            leaderboard_dataset_id))

    def leaderboard_dataset_details(self, leaderboard_dataset_id: str):
        return self.get("%s/details" % self.leaderboard_datasets_url(
            leaderboard_dataset_id))

    def leaderboard_generate(self, leaderboard_dataset_id: str):
        return self.get("%s/generate" % self.leaderboard_datasets_url(
            leaderboard_dataset_id))

    def runs_bulk_get_by_ids(self, task_id: str, run_ids: list):
        url = "%s/%s" % (self.tasks_url(task_id), 'runs/bulk')
        url += self.query_url(
            run_id=run_ids,
        )
        return self.get(url)

    def model_create(
            self,
            key: str,
            name: str = None,
            description: str = None,
            tags: dict = None):
        body = {
            "key": key
        }
        if name is not None:
            body['name'] = name
        if description is not None:
            body['description'] = description
        if tags is not None:
            body['tags'] = tags
        return self.post(self.models_url(), body)

    def model_update(self, model_id: str, **params):
        return self.patch(self.models_url(model_id), params)

    def models_get(self):
        return self.get(self.models_url())

    def model_get(self, model_id: str):
        return self.get(self.models_url(model_id))

    def model_delete(self, model_id: str):
        return self.delete(self.models_url(model_id))

    def model_version_create(
            self,
            run_id: str,
            model_id: str,
            version: str = None,
            path: str = None,
            aliases: list = None,
            tags: dict = None):
        body = {}
        if version is not None:
            body['version'] = version
        if path is not None:
            body['path'] = path
        if aliases is not None:
            body['aliases'] = aliases
        if tags is not None:
            body['tags'] = tags
        return self.post(self.run_model_version_url(run_id, model_id), body)

    def model_version_update(self, run_id: str, model_id: str, **params):
        return self.patch(
            self.run_model_version_url(run_id, model_id), params)

    def model_version_delete(self, run_id: str, model_id: str):
        return self.delete(self.run_model_version_url(run_id, model_id))

    def model_versions_by_task(self, task_id: str):
        return self.get(self.model_versions_url(task_id))
