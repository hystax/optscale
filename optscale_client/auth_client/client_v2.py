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
    def user_options_url(user_id, option_name=None):
        url = '%s/options' % Client.user_url(user_id)
        if option_name is not None:
            url = '%s/%s' % (url, option_name)
        return url

    @staticmethod
    def login_options_url():
        url = 'login_options'
        return url

    @staticmethod
    def auth_policies_url(policy_id=None):
        url = 'auth_policies'
        if policy_id is not None:
            url = '%s/%s' % (url, policy_id)
        return url

    @staticmethod
    def mfa_methods_url(user_id, method_id=None):
        url = '%s/mfa_methods' % Client.user_url(user_id)
        if method_id is not None:
            url = '%s/%s' % (url, method_id)
        return url

    @staticmethod
    def mfa_method_confirm_url(user_id, method_id):
        return '%s/confirm' % Client.mfa_methods_url(user_id, method_id)

    @staticmethod
    def login_challenge_codes_url():
        return 'login_challenge_codes'

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
                    id=None, verified=False):
        body = {
            "email": email,
            "password": password,
            "display_name": display_name,
            "is_active": is_active,
            "verified": verified
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

    def user_options_list(self, user_id, with_values=False):
        url = self.user_options_url(user_id) + self.query_url(
            with_values=with_values)
        return self.get(url)

    def user_options_get(self, user_id, option_name):
        url = self.user_options_url(user_id, option_name)
        return self.get(url)

    def user_options_update(self, user_id, option_name, value):
        url = self.user_options_url(user_id, option_name)
        return self.patch(url, value)

    def user_options_create(self, user_id, option_name, value):
        return self.user_options_update(user_id, option_name, value)

    def user_options_delete(self, user_id, option_name):
        url = self.user_options_url(user_id, option_name)
        return self.delete(url)

    # --- MFA (two-step login, methods, policies) ---
    # Credentials: TOKEN is the user's token (self.token), SECRET the cluster
    # secret (self.secret), CHALLENGE a login challenge id passed in the body
    # (the browser has no token yet). Every method returns (code, response).

    def login_options(self, email):
        """
        Step 1 of the sign-in: how the user can authenticate (password,
        identity providers). Credential: none.
        """
        return self.post(self.login_options_url(), {'email': email})

    def token_get_by_challenge(self, challenge_id, code, method_id=None):
        """
        Completes an `mfa_required` login challenge (a 202 of token_get)
        with a TOTP or e-mail code: 201 with the token. Credential:
        CHALLENGE. method_id: the method the code belongs to; without it
        the default method is tried (then every TOTP method).
        """
        body = {'challenge_id': challenge_id, 'code': code}
        if method_id is not None:
            body['method_id'] = method_id
        return self.post(self.token_url(), body)

    def login_challenge_code_send(self, challenge_id, method_id=None):
        """
        Sends (again) the e-mail code of an `mfa_required` login challenge:
        204. One code per minute per user (403 OA0072 meanwhile).
        Credential: CHALLENGE. method_id: the confirmed e-mail method of
        the user, optional as a user has a single one.
        """
        body = {'challenge_id': challenge_id}
        if method_id is not None:
            body['method_id'] = method_id
        return self.post(self.login_challenge_codes_url(), body)

    def mfa_methods_get(self, user_id):
        """
        MFA status of a user: status (disabled / configured / enforced)
        and the confirmed methods. Credential: TOKEN of the user or SECRET.
        """
        return self.get(self.mfa_methods_url(user_id))

    def mfa_method_create(self, user_id, type_, label=None,
                          challenge_id=None):
        """
        Starts the enrollment of a method: 201 with the pending method
        (plus secret and otpauth_uri for totp). type_: totp or email.
        label: required for totp. Credential: TOKEN of the user, SECRET or
        CHALLENGE (an `enrollment_required` login challenge of the user).
        """
        body = {'type': type_}
        if label is not None:
            body['label'] = label
        if challenge_id is not None:
            body['challenge_id'] = challenge_id
        return self.post(self.mfa_methods_url(user_id), body)

    def mfa_method_confirm(self, user_id, method_id, code,
                           challenge_id=None):
        """
        Confirms a pending method with a code of the device / mailbox:
        200 with the method, or 201 with {method, token} in challenge mode.
        Credential: TOKEN of the user, SECRET or CHALLENGE.
        """
        body = {'code': code}
        if challenge_id is not None:
            body['challenge_id'] = challenge_id
        return self.post(self.mfa_method_confirm_url(user_id, method_id),
                         body)

    def mfa_method_update(self, user_id, method_id, **params):
        """
        Updates a confirmed method: label and / or is_default (true only,
        it replaces the current default). Credential: TOKEN of the user or
        SECRET.
        """
        return self.patch(self.mfa_methods_url(user_id, method_id), params)

    def mfa_method_delete(self, user_id, method_id):
        """
        Removes a method: 204. The last one cannot be removed while an
        organization enforces MFA (403 OA0091). Credential: TOKEN of the
        user or SECRET.
        """
        return self.delete(self.mfa_methods_url(user_id, method_id))

    def mfa_methods_reset(self, user_id):
        """
        Resets the MFA of a user (lost device): every method removed, the
        user's tokens deleted, 204. Credential: SECRET or TOKEN of an
        organization manager of the user.
        """
        return self.delete(self.mfa_methods_url(user_id))

    def auth_policy_list(self, scope_type, scope_id):
        """
        Active authentication policies of a scope (organization).
        Credential: TOKEN (INFO_ORGANIZATION) or SECRET.
        """
        url = self.auth_policies_url() + self.query_url(
            scope_type=scope_type, scope_id=scope_id)
        code, response = self.get(url)
        return (code, response['auth_policies']) if code == 200 else (
            code, response)

    def auth_policy_create(self, scope_type, scope_id, purpose):
        """
        Creates a policy, e.g. purpose `mfa` to enforce MFA for the users
        of an organization: 201. Credential: TOKEN (EDIT_PARTNER) or
        SECRET.
        """
        body = {
            'scope_type': scope_type,
            'scope_id': scope_id,
            'purpose': purpose,
        }
        return self.post(self.auth_policies_url(), body)

    def auth_policy_delete(self, policy_id):
        """
        Deletes a policy: 204. Credential: TOKEN (EDIT_PARTNER) or SECRET.
        """
        return self.delete(self.auth_policies_url(policy_id))
