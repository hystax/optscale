import json
from urllib.parse import urlencode
from optscale_client.auth_client.client import Client as Client_v1


class Client(Client_v1):
    def __init__(self, address="127.0.0.1", port="80", api_version="v2",
                 url=None, http_provider=None, token='', secret='',
                 verify=True, ip=None):
        super().__init__(address=address, port=port, api_version=api_version,
                         url=url, http_provider=http_provider, token=token,
                         secret=secret, verify=verify, ip=ip)

    def get(self, url, body=None):
        if body:
            url = url + self.query_url(**body)
        return self._request(url, "GET")

    @staticmethod
    def my_assignment_url():
        return 'assignments'

    @staticmethod
    def assignment_register_url(user_id):
        return '%s/assignment_register' % Client.user_url(user_id)

    @staticmethod
    def purposed_roles_url():
        return 'purposed_roles'

    @staticmethod
    def user_existence_url():
        return 'user_existence'

    @staticmethod
    def user_roles_url():
        url = 'user_roles'
        return url

    @staticmethod
    def action_resource_url(user_id=None):
        url = 'action_resources'
        if user_id:
            url = '%s/%s' % (Client.user_url(user_id), url)
        return url

    @staticmethod
    def verification_codes_url():
        url = 'verification_codes'
        return url

    @staticmethod
    def query_url(**query):
        query = {
            key: value for key, value in query.items() if value is not None
        }
        encoded_query = urlencode(query, doseq=True)
        return "?" + encoded_query

    def allowed_action_get(self, payload: list):
        params = {}
        for k, v in payload:
            if params.get(k):
                params[k].append(v)
                continue
            params[k] = [v]
        url = self.allowed_action_url() + self.query_url(**params)
        code, response = self.get(url)
        return (code, response['allowed_actions']) if code == 200 else (
            code, response)

    def action_resources_get(self, actions, assignable_only=True,
                             user_id=None):
        """
        :param actions: list of actions
        :param assignable_only: bool (show only assignable)
        :param user_id: string (required cluster secret)
        :return: dict {ACTION:[[scope_type, scope_id]...]...}
        """
        url = self.action_resource_url(user_id) + self.query_url(
            action=actions, assignable_only=assignable_only)
        code, response = self.get(url)
        return (code, response['action_resources']) if code == 200 else (
            code, response)

    def token_meta_get(self, digests: list):
        """
        :param digests: list of digests
        :return:
        """
        url = self.digests_url() + self.query_url(digest=digests)
        code, response = self.get(url)
        return code, response

    def user_create(self, email, password, display_name, is_active=True,
                    id=None):
        body = {
            "email": email,
            "password": password,
            "display_name": display_name,
            "is_active": is_active
        }
        if id is None:
            return self.post(self.user_url(), body)
        else:
            return self.put(self.user_url(id), body)

    def my_assignment_list(self):
        code, response = self.get(self.my_assignment_url())
        return (code, response['assignments']
                ) if code == 200 else (code, response)

    def get_purposed_role(self, purpose):
        url = self.purposed_roles_url() + self.query_url(purpose=purpose)
        code, response = self.get(url)
        return code, response

    def assignment_register(self, user_id, role_id, type_id, resource_id):
        body = {
            "role_id": role_id,
            "type_id": type_id,
            "resource_id": resource_id
        }
        return self.post(self.assignment_register_url(user_id), body)

    def user_exists(self, email, user_info=False):
        url = self.user_existence_url() + self.query_url(email=email,
                                                         user_info=user_info)
        return self.get(url)

    def user_list(self, user_ids=None):
        url = self.user_url()
        if user_ids:
            url += self.query_url(user_id=user_ids)
        code, resp_body = self.get(url)
        return code, resp_body['users']

    def user_roles_get(
            self, user_ids: list = None, role_purposes: list = None,
            scope_ids: list = None):
        """
        :param user_ids: list of user ids
        :param role_purposes: list of user ids
        :param scope_ids: list of user ids
        :return:
        """
        url = self.user_roles_url() + self.query_url(
            user_ids=user_ids, role_purposes=role_purposes,
            scope_ids=scope_ids)
        code, response = self.get(url)
        return code, response

    def bulk_action_resource_url(self):
        return 'bulk_action_resources'

    def bulk_action_resources_get(self, user_ids, actions, assignable_only=True):
        url = self.bulk_action_resource_url() + self.query_url(
            user_id=user_ids,
            action=actions,
            assignable_only=assignable_only
        )
        return self.get(url)

    def signin_url(self):
        return 'signin'

    def signin(self, provider, token):
        body = {
            "provider": provider,
            "token": token,
        }
        return self.post(self.signin_url(), body)

    def verification_code_create(self, email, code):
        body = {
            "email": email,
            "code": code,
        }
        return self.post(self.verification_codes_url(), body)
