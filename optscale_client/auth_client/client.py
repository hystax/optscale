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
            headers.update({'Authorization': str('Bearer ' + str(self._token))})
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
    def __init__(self, address="127.0.0.1", port="80", api_version="v1",
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
        return "/auth/%s/%s" % (self._api_version, sub_url)

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
    def user_url(id=None):
        url = 'users'
        if id is not None:
            url = '%s/%s' % (url, id)
        return url

    def role_url(self, id=None, assignable_to_user_id=None):
        url = 'roles'
        if id is not None:
            url = '%s/%s' % (url, id)
        if assignable_to_user_id is not None:
            url += self.query_url(assignable=assignable_to_user_id)
        return url

    @staticmethod
    def token_url():
        url = 'tokens'
        return url

    @staticmethod
    def type_url(id=None):
        url = 'types'
        if id is not None:
            url = '%s/%s' % (url, id)
        return url

    @staticmethod
    def authorization_url():
        url = 'authorize'
        return url

    @staticmethod
    def authorization_userlist_url():
        url = 'authorize_userlist'
        return url

    @staticmethod
    def scope_url():
        url = 'scopes'
        return url

    @staticmethod
    def allowed_action_url():
        url = 'allowed_actions'
        return url

    @staticmethod
    def assignment_url(user_id, id=None):
        url = 'assignments'
        if id is not None:
            url = '%s/%s' % (url, id)
        return '%s/%s' % (Client.user_url(user_id), url)

    @staticmethod
    def digests_url():
        url = 'digests'
        return url

    @staticmethod
    def action_resource_url():
        url = 'action_resources'
        return url

    def user_create(self, email, password, type_id, display_name,
                    is_active=True, id=None, scope_id=None):
        body = {
            "email": email,
            "password": password,
            "display_name": display_name,
            "type_id": type_id,
            "scope_id": scope_id,
            "is_active": is_active
        }
        if id is None:
            return self.post(self.user_url(), body)
        else:
            return self.put(self.user_url(id), body)

    def user_get(self, id):
        return self.get(self.user_url(id))

    def user_list(self):
        code, resp_body = self.get(self.user_url())
        return code, resp_body['users']

    def user_update(self, id, **params):
        return self.patch(self.user_url(id), params)

    def user_delete(self, id):
        return self.delete(self.user_url(id))

    def role_create(self, name, type_id, lvl_id, is_active=True,
                    id=None, scope_id=None, description=None, shared=False):

        body = {
            "name": name,
            "description": description,
            "type_id": type_id,
            "lvl_id": lvl_id,
            "scope_id": scope_id,
            "is_active": is_active,
            "shared": shared
        }
        if id is None:
            return self.post(self.role_url(), body)
        else:
            return self.put(self.role_url(id), body)

    def role_get(self, id):
        return self.get(self.role_url(id))

    def role_update(self, id, name=None, is_active=None, actions=None,
                    description=None, shared=None):
        body = {
            "name": name,
            "description": description,
            "is_active": is_active,
            "actions": actions,
            "shared": shared
        }
        return self.patch(self.role_url(id), body)

    def role_list(self, assignable_to_user_id=None):
        code, resp_body = self.get(self.role_url(
            assignable_to_user_id=assignable_to_user_id))
        return code, resp_body.get('roles')

    def role_delete(self, id):
        return self.delete(self.role_url(id))

    def token_get(self, email, password):
        body = {
            "email": email,
            "password": password
        }
        return self.post(self.token_url(), body)

    def token_get_user_id(self, user_id):
        body = {'user_id': user_id}
        return self.post(self.token_url(), body)

    def authorize(self, action, resource_type, uuid=None):
        body = {
            "action": action,
            "resource_type": resource_type,
            "uuid": uuid
        }
        return self.post(self.authorization_url(), body)

    def type_get(self, id):
        return self.get(self.type_url(id))

    def type_list(self):
        code, resp_body = self.get(self.type_url())
        return code, resp_body['types']

    def assignment_list(self, user_id):
        code, response = self.get(self.assignment_url(user_id=user_id))
        return (code, response['assignments']) if code == 200 else (code,
                                                                    response)

    def assignment_create(self, user_id, role_id, type_id, resource_id):
        body = {
            "role_id": role_id,
            "type_id": type_id,
            "resource_id": resource_id
        }
        return self.post(self.assignment_url(user_id), body)

    def assignment_delete(self, id, user_id):
        return self.delete(self.assignment_url(user_id, id))

    def assignment_get(self, id, user_id):
        return self.get(self.assignment_url(user_id, id))

    def _scope_get(self, action):
        url = self.scope_url()
        url += self.query_url(
            action=action
        )
        code, response = self.get(url)
        return (code, response['scopes']) if code == 200 else (code, response)

    def scope_user_create_get(self):
        return self._scope_get('create_user')

    def scope_role_create_get(self):
        return self._scope_get('create_role')

    def scope_user_assign_get(self, user_id, role_id):
        action = 'assign_user'
        url = self.scope_url()
        url += self.query_url(
            action=action,
            user_id=user_id,
            role_id=role_id,
        )
        code, response = self.get(url)
        return (code, response['scopes']) if code == 200 else (code, response)

    def allowed_action_get(self, payload):
        body = {
            "payload": payload
        }
        code, response = self.get(self.allowed_action_url(), body)
        return (code, response['allowed_actions']) if code == 200 else (
            code, response)

    def token_meta_get(self, digests):
        """
        :param digests: list of digests
        :return:
        """
        payload_dict = {
            'digests': digests
        }
        body = {
            "payload": json.dumps(payload_dict)
        }
        code, response = self.get(self.digests_url(), body)
        return code, response

    def action_resources_get(self, actions, assignable_only=True):
        """
        :param actions: list of actions
        :param assignable_only: bool (show only assignable)
        :return: dict {ACTION:[[scope_type, scope_id]...]...}
        """
        payload_dict = {
            'actions': actions,
            'assignable_only': assignable_only
        }
        body = {
            "payload": json.dumps(payload_dict)
        }
        code, response = self.get(self.action_resource_url(), body)
        return (code, response['action_resources']) if code == 200 else (
            code, response)

    def authorize_user_list(self, users, actions, scope_type, scope_id):
        body = {
            "users": users,
            "actions": actions,
            "scope_type": scope_type,
            "scope_id": scope_id
        }
        code, response = self.post(self.authorization_userlist_url(), body)
        return code, response
