import hashlib
import json
import logging
import os
import traceback
from json import JSONDecodeError
import requests
import time
import jwt
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, HTTPError
from atlassian_jwt.url_utils import hash_url
from jwt.exceptions import PyJWTError

from jira_bus.jira_bus_server.exceptions import Err
from jira_bus.jira_bus_server.models.db_base import BaseDB
from jira_bus.jira_bus_server.utils import ModelEncoder, tp_executor

from optscale_client.auth_client.client_v2 import Client as AuthClient
from tools.optscale_exceptions.http_exc import OptHTTPError

LOG = logging.getLogger(__name__)


class DefaultHandler(RequestHandler):
    def write_error(self, status_code, **kwargs):
        self.set_header("Content-Type", "application/json")
        self.set_status(404)
        self.finish(
            json.dumps(
                {
                    "error": {
                        "status_code": 404,
                        "error_code": Err.OJ0002.name,
                        "reason": self._reason,
                        "params": [],
                    }
                }
            )
        )


class BaseHandler(RequestHandler):
    def initialize(self, engine, config):
        self._engine = engine
        self._config = config
        self._controller = None
        self._session = None
        self.executor = tp_executor

    @property
    def token(self):
        auth_header = self.request.headers.get("Authorization")
        if not auth_header:
            return None
        return auth_header.split(maxsplit=1)[-1]

    def raise405(self):
        raise OptHTTPError(405, Err.OJ0003, [self.request.method])

    def head(self, *args, **kwargs):
        self.raise405()

    def get(self, *args, **kwargs):
        self.raise405()

    def post(self, *args, **kwargs):
        self.raise405()

    def delete(self, *args, **kwargs):
        self.raise405()

    def patch(self, *args, **kwargs):
        self.raise405()

    def put(self, *args, **kwargs):
        self.raise405()

    def options(self, *args, **kwargs):
        self.raise405()

    def _get_request(self):
        return self.request

    def session(self):
        if not self._session:
            self._session = BaseDB.session(self._engine)
        return self._session()

    def prepare(self):
        self.set_content_type()

    def set_content_type(self, content_type='application/json; charset="utf-8"'):
        self.set_header("Content-Type", content_type)

    def on_finish(self):
        self.session().close()

    @property
    def controller(self):
        if not self._controller:
            self._controller = self._get_controller_class()(
                self.session(), self._config, self._engine
            )
        return self._controller

    def _get_controller_class(self):
        raise NotImplementedError

    def write_error(self, status_code, **kwargs):
        exc = kwargs.get("exc_info")[1]
        res = {
            "error": {
                "status_code": status_code,
                "error_code": getattr(exc, "error_code", "U0%s" % status_code),
                "reason": self._reason,
                "params": getattr(exc, "params", []),
            }
        }
        self.set_content_type('application/json; charset="utf-8"')
        self.finish(json.dumps(res, cls=ModelEncoder))

    def _request_body(self):
        try:
            return json.loads(self.request.body.decode("utf-8"))
        except JSONDecodeError:
            raise OptHTTPError(400, Err.OJ0004, [])

    def _request_arguments(self):
        return self.request.arguments

    def log_exception(self, typ, value, tb):
        out_list = traceback.format_exception(typ, value, tb)
        if isinstance(value, HTTPError):
            if value.log_message:
                format = "%d %s: " + value.log_message + "\\n%s"
                args = (
                    [value.status_code, self._request_summary()] +
                    list(value.args) +
                    [repr("".join(out_list))]
                )
            else:
                format = "%d %s:\\n%s"
                args = [value.status_code, self._request_summary()] + [
                    repr("".join(out_list))
                ]
        else:
            format = "Uncaught exception %s\\n%r\\n %s"
            args = (self._request_summary(), self.request, repr("".join(out_list)))
        if os.environ.get("PYCHARM_DEBUG_HOST") or os.environ.get(
                "BASE_HANDLER_LOG_ERRORS_WITH_NEWLINES"
        ):
            # Log with real line breaks to simplify reading exceptions in debug
            LOG.warning((format % tuple(args)).replace("\\n", "\n"))
        else:
            LOG.warning(format, *args)

    def get_request_data(self):
        raise NotImplementedError

    def get_request_arguments(self):
        return self._request_arguments()

    @property
    def secret(self):
        return self.request.headers.get("Secret")

    def check_cluster_secret(self, **kwargs):
        cluster_secret = self._config.cluster_secret()
        return self._check_secret(cluster_secret, **kwargs)

    def _check_secret(self, secret, raises=True):
        if raises and not self.secret == secret:
            raise OptHTTPError(403, Err.OJ0005, [])
        else:
            return self.secret == secret

    def _check_permissions(self, action, type, resource_id, auth_token=None):
        client = AuthClient(url=self._config.auth_url())
        client.token = auth_token or self.token
        LOG.info("Given Auth token is %s:" % self.token)
        try:
            code, response = client.authorize(action, type, resource_id)
            LOG.info("Auth code %s, response: %s", code, response)
        except requests.exceptions.HTTPError as exc:
            if exc.response.status_code == 401:
                raise OptHTTPError(401, Err.OJ0012, [])
            if exc.response.status_code == 403:
                raise OptHTTPError(403, Err.OJ0018, [])
            if exc.response.status_code == 404:
                raise OptHTTPError(404, Err.OJ0008, [type, resource_id])
            raise

    def _get_token_meta(self, digests):
        """
        Get token meta such as user id from auth
        :return:
        """
        client = AuthClient(url=self._config.auth_url())
        client.token = self.token
        client.secret = self._config.cluster_secret()
        try:
            _, token_meta_dict = client.token_meta_get(digests)
        except requests.exceptions.HTTPError as exc:
            if exc.response.status_code == 401:
                raise OptHTTPError(401, Err.OJ0012, [])
            raise
        return token_meta_dict

    def _get_meta_by_token(self, token):
        user_digest = list(
            map(lambda x: hashlib.md5(x.encode("utf-8")).hexdigest(), [token])
        )[0]
        token_meta = self._get_token_meta([user_digest]).get(user_digest, {})
        return token_meta

    async def check_optscale_auth(self):
        try:
            token_meta = await IOLoop.current().run_in_executor(
                self.executor, self._get_meta_by_token, self.token
            )
        except AttributeError:
            raise OptHTTPError(401, Err.OJ0012, [])
        token_valid_until = token_meta.get("valid_until", 0)
        token_user_id = token_meta.get("user_id", "")

        if token_valid_until < time.time():
            raise OptHTTPError(401, Err.OJ0012, [])
        return token_user_id

    async def check_optscale_permission(
            self, action, type, resource_id, auth_token=None
    ):
        try:
            await IOLoop.current().run_in_executor(
                self.executor,
                self._check_permissions,
                action,
                type,
                resource_id,
                auth_token,
            )
        except AttributeError:
            raise OptHTTPError(401, Err.OJ0012, [])

    def _check_atlassian_qsh(self, qsh, context_qsh, method=None, url=None):
        if not url:
            url = self.request.uri
        if not method:
            method = self.request.method
        if context_qsh:
            computed_qsh = "context-qsh"
        else:
            computed_qsh = hash_url(http_method=method, url=url)
        if qsh != computed_qsh:
            LOG.error(
                "received qsh %s did not match computed qsh %s",
                qsh, computed_qsh
            )
            raise OptHTTPError(401, Err.OJ0012, [])

    def _get_token_data(self, jwt_token, require_account, require_issue):
        client_key = jwt_token["iss"]
        account_id = jwt_token.get("sub")
        issue_key = (
            jwt_token.get("context", {}).get("jira", {}).get("issue", {}).get("key")
        )
        if not account_id and require_account:
            raise OptHTTPError(401, Err.OJ0016, [])
        if not issue_key and require_issue:
            raise OptHTTPError(401, Err.OJ0022, [])
        return client_key, account_id, issue_key

    def _get_fake_token_data(self, require_account, require_issue):
        client_key = self.request.headers.get("Hx-Test-Client-Key")
        account_id = self.request.headers.get("Hx-Test-Account-Id")
        issue_key = self.request.headers.get("Hx-Test-Issue-Key")
        if client_key:
            self.check_cluster_secret()
            if not account_id and require_account:
                raise OptHTTPError(401, Err.OJ0016, [])
            if not issue_key and require_issue:
                raise OptHTTPError(401, Err.OJ0022, [])
            return client_key, account_id, issue_key

    async def check_atlassian_auth_asymmetric(
            self, context_qsh=False, require_account=False, require_issue=False
    ):
        """
        Check asymmetric atlassian auth token. Asymmetric tokens are used in
        app lifecycle callbacks. They are verified by atlassian public key that
        is fetched by a web request.

        :param context_qsh: Auth tokens from Jira usually include a query
            signature (qsh). But if a token is obtained through JavaScript
            (e.g. inside of our settings page), there will be `context-qsh`
            string instead of a proper signature. Set this param to True to
            validate against this string instead of proper qsh. Atlassian docs
            recommend validating for a single qsh type in a single API handler,
            that's why there is a parameter instead of validating for any of
            both qsh types.
        :param require_account: Some API calls may be executed without user.
            Set this param to to True to require user account ID to be present.
        :param require_issue: Some API calls may be executed in Jira issue
            context. Set this parameter to True to require Jira issue key to be
            present.
        :return: tuple: (client_key, account_id, issue_key).
            Client ID is Jira tenant ID (the entity where our app is
            installed). Account ID is current Jira user account ID, it can be
            None if operation is executed without user. Issue key is Jira issue
            key, can be None if operation is executed outside of issue context.
        """

        # Support fake credentials for our testing needs
        if fake_results := self._get_fake_token_data(require_account, require_issue):
            return fake_results

        try:
            key_id = jwt.get_unverified_header(self.token)["kid"]
            public_key = await self.controller.get_atlassian_public_key(key_id)
            jwt_token = jwt.decode(
                self.token,
                public_key,
                algorithms=["RS256"],
                # The `aud` claim matches URL of our app. But the app may be
                # accessible and installed through different URLs, so let's
                # make our life easier (though slightly less secure) and not
                # verify `aud` at all.
                options={"verify_aud": False},
            )
            self._check_atlassian_qsh(jwt_token["qsh"], context_qsh)
        except PyJWTError as exc:
            LOG.error("Asymmetric token verify error: %s", exc)
            raise OptHTTPError(401, Err.OJ0012, [])

        return self._get_token_data(jwt_token, require_account, require_issue)

    async def check_atlassian_auth(
            self, context_qsh=False, require_account=False, require_issue=False,
            token=None, method=None, url=None
    ):
        """
        Check ordinary atlassian auth token. These tokens are verified by a
        shared secret that is saved during our app installation.

        :param context_qsh: Auth tokens from Jira usually include a query
            signature (qsh). But if a token is obtained through JavaScript
            (e.g. inside of our settings page), there will be `context-qsh`
            string instead of a proper signature. Set this param to True to
            validate against this string instead of proper qsh. Atlassian docs
            recommend validating for a single qsh type in a single API handler,
            that's why there is a parameter instead of validating for any of
            both qsh types.
        :param require_account: Some API calls may be executed without user.
            Set this param to to True to require user account ID to be present.
        :param require_issue: Some API calls may be executed in Jira issue
            context. Set this parameter to True to require Jira issue key to be
            present.
        :param jwt: Atlassian JWT string. Provide it to validate external JWT.
        :param url: Request URL string for generating qsh to validate Atlassian
            JWT. Provide it to validate external JWT.
        :param method: Request method string for generating qsh to validate
            Atlassian JWT. Provide it to validate external JWT.
        :return: tuple: (client_key, account_id, issue_key).
            Client ID is Jira tenant ID (the entity where our app is
            installed). Account ID is current Jira user account ID, it can be
            None if operation is executed without user. Issue key is Jira issue
            key, can be None if operation is executed outside of issue context.
        """
        if not token:
            token = self.token

        # Support fake credentials for our testing needs
        if fake_results := self._get_fake_token_data(require_account, require_issue):
            return fake_results

        try:
            client_key = jwt.decode(token, options={"verify_signature": False})[
                "iss"
            ]
            shared_secret = await self.controller.get_atlassian_shared_secret(
                client_key
            )
            jwt_token = jwt.decode(token, shared_secret, algorithms=["HS256"])
            self._check_atlassian_qsh(jwt_token["qsh"], context_qsh,
                                      method=method, url=url)
        except PyJWTError as exc:
            LOG.error("Token verify error: %s", exc)
            raise OptHTTPError(401, Err.OJ0012, [])

        return self._get_token_data(jwt_token, require_account, require_issue)

    def get_arg(self, name, type, default=None, repeated=False):
        try:
            if repeated:
                result = [type(a) for a in self.get_arguments(name)]
                if not result and default:
                    result = default
                return result
            else:
                arg = self.get_argument(name, default=default)
                if arg:
                    if type == bool and isinstance(arg, str):
                        lowered = arg.lower()
                        if lowered not in ["true", "false"]:
                            raise ValueError("%s should be true or false" % arg)
                        return lowered == "true"
                    return type(arg)
                else:
                    return arg
        except (ValueError, TypeError):
            raise OptHTTPError(400, Err.OJ0011, [name])
