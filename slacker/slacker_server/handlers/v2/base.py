import hashlib
import json
import logging
import time
import traceback
from json import JSONDecodeError

import requests
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, HTTPError

from optscale_client.auth_client.client_v2 import Client as AuthClient
from tools.optscale_exceptions.common_exc import UnauthorizedException
from tools.optscale_exceptions.http_exc import OptHTTPError

from slacker.slacker_server.exceptions import Err
from slacker.slacker_server.models.db_base import BaseDB
from slacker.slacker_server.utils import ModelEncoder, tp_executor

LOG = logging.getLogger(__name__)


class DefaultHandler(RequestHandler):
    def set_default_headers(self):
        self.set_header("Content-Type", "application/json; charset=UTF-8")

    def write_error(self, status_code, **kwargs):
        self.set_status(404)
        self.finish(
            json.dumps(
                {
                    "error": {
                        "status_code": 404,
                        "error_code": Err.OS0002.name,
                        "reason": self._reason,
                        "params": [],
                    }
                }
            )
        )


class BaseHandler(RequestHandler):
    def set_default_headers(self):
        self.set_header("Content-Type", "application/json; charset=UTF-8")

    def initialize(self, app, engine, config_cl):
        self.app = app
        self.engine = engine
        self.config_cl = config_cl
        self._controller = None
        self._session = None
        self.executor = tp_executor

    @property
    def token(self):
        auth_header = self.request.headers.get("Authorization")
        if not auth_header:
            return None
        return auth_header[7:]

    def raise405(self):
        raise OptHTTPError(405, Err.OS0003, [self.request.method])

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
            self._session = BaseDB.session(self.engine)
        return self._session()

    def prepare(self):
        try:
            if not self.token and not self.secret:
                raise UnauthorizedException(Err.OS0006, [])
            if self.request.method == "POST":
                self._validate_post_parameters()
        except UnauthorizedException as exc:
            self.set_status(401)
            self.finish({"error": str(exc)})

    def _validate_post_parameters(self):
        if not self.request.body:
            return
        body = self._request_body()
        if isinstance(body, dict):
            duplicated_params = list(
                filter(lambda x: x in self.path_kwargs, body.keys())
            )
            message = ", ".join(duplicated_params)
            if duplicated_params:
                raise OptHTTPError(400, Err.OS0012, [message])

    def on_finish(self):
        self.session().close()

    def write_json(self, response):
        self.write(json.dumps(response, cls=ModelEncoder))

    @property
    def controller(self):
        if not self._controller:
            self._controller = self._get_controller_class()(
                self.app, self.session(), self.config_cl, self.token, self.engine
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

        self.finish(json.dumps(res, cls=ModelEncoder))

    def _request_body(self):
        try:
            return json.loads(self.request.body.decode("utf-8"))
        except JSONDecodeError:
            raise OptHTTPError(400, Err.OS0004, [])

    def _request_arguments(self):
        return self.request.arguments

    def log_exception(self, typ, value, tb):
        out_list = traceback.format_exception(typ, value, tb)
        if isinstance(value, HTTPError):
            if value.log_message:
                format = "%d %s: " + value.log_message + "\\n%s"
                args = (
                    [value.status_code, self._request_summary()]
                    + list(value.args)
                    + [repr("".join(out_list))]
                )
            else:
                format = "%d %s:\\n%s"
                args = [value.status_code, self._request_summary()] + [
                    repr("".join(out_list))
                ]
            LOG.warning(format, *args)
        else:
            LOG.error(
                "Uncaught exception %s\\n%r\\n %s",
                self._request_summary(),
                self.request,
                repr("".join(out_list)),
            )

    def get_request_data(self):
        raise NotImplementedError

    def get_request_arguments(self):
        return self._request_arguments()

    @staticmethod
    def raise401():
        raise OptHTTPError(401, Err.OS0018, [])

    def get_token_meta(self, digests):
        """
        Get token meta such as user id from auth
        :return:
        """
        client = AuthClient(url=self.config_cl.auth_url())
        client.token = self.token
        client.secret = self.config_cl.cluster_secret()
        try:
            _, token_meta_dict = client.token_meta_get(digests)
        except requests.exceptions.HTTPError as exc:
            if exc.response.status_code == 401:
                self.raise401()
            raise
        return token_meta_dict

    def get_meta_by_token(self, token):
        user_digest = list(
            map(lambda x: hashlib.md5(x.encode("utf-8")).hexdigest(), [token])
        )[0]
        token_meta = self.get_token_meta([user_digest]).get(user_digest, {})
        return token_meta

    async def check_self_auth(self):
        try:
            token_meta = await IOLoop.current().run_in_executor(
                self.executor, self.get_meta_by_token, self.token
            )
        except AttributeError:
            self.raise401()
        token_valid_until = token_meta.get("valid_until", 0)
        token_user_id = token_meta.get("user_id", "")

        if token_valid_until < time.time():
            self.raise401()
        return token_user_id

    @property
    def secret(self):
        return self.request.headers.get("Secret")

    def check_cluster_secret(self, **kwargs):
        cluster_secret = self.config_cl.cluster_secret()
        return self._check_secret(cluster_secret, **kwargs)

    def _check_secret(self, secret, raises=True):
        if raises and not self.secret == secret:
            raise OptHTTPError(403, Err.OS0005, [])
        else:
            return self.secret == secret
