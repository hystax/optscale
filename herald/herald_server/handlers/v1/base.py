import functools
import hashlib
import json
from json.decoder import JSONDecodeError
import logging
import traceback
import time
import requests

import tornado.web
from tornado.ioloop import IOLoop

from herald_server.exceptions import Err
from herald_server.models.db_base import BaseDB
from herald_server.utils import ModelEncoder, Config, tp_executor

from auth_client.client_v2 import Client as AuthClient
from optscale_exceptions.http_exc import OptHTTPError
from optscale_exceptions.common_exc import UnauthorizedException


LOG = logging.getLogger(__name__)


class DefaultHandler(tornado.web.RequestHandler):
    def write_error(self, status_code, **kwargs):
        self.set_header('Content-Type', 'application/json')
        self.set_status(404)
        self.finish(json.dumps({
            'error': {
                'status_code': 404,
                'error_code': 'G0029',
                'reason': self._reason,
                'params': [],
            }
        }))


class BaseHandler(tornado.web.RequestHandler):
    def initialize(self, engine, config, rabbit_client):
        self._engine = engine
        self._config = config
        self.rabbit_client = rabbit_client
        self._controller = None
        self._session = None
        self.executor = tp_executor
        self.io_loop = IOLoop.current()

    def raise405(self):
        raise OptHTTPError(
            405, Err.G0008, [self.request.method])

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

    def head(self, *args, **kwargs):
        raise self.raise405()

    def _get_request(self):
        return self.request

    def session(self):
        if not self._session:
            self._session = BaseDB.session(self._engine)
        return self._session()

    def prepare(self):
        self.set_content_type()

    def set_content_type(self,
                         content_type='application/json; charset="utf-8"'):
        self.set_header('Content-Type', content_type)

    def on_finish(self):
        self.session().close()

    @property
    def controller(self):
        if not self._controller:
            self._controller = self._get_controller_class()(
                self.session(), self._config, self.rabbit_client)
        return self._controller

    def _get_controller_class(self):
        raise NotImplementedError

    def write_error(self, status_code, **kwargs):
        exc = kwargs.get('exc_info')[1]
        res = {
            'error': {
                'status_code': status_code,
                'error_code': getattr(exc, 'error_code', 'U0%s' % status_code),
                'reason': self._reason,
                'params': getattr(exc, 'params', []),
            }
        }
        self.set_content_type('application/json; charset="utf-8"')
        self.finish(json.dumps(res, cls=ModelEncoder))

    def _request_body(self):
        try:
            return json.loads(self.request.body.decode('utf-8'))
        except JSONDecodeError:
            raise OptHTTPError(
                400, Err.G0007, [])

    def log_exception(self, typ, value, tb):
        if isinstance(value, tornado.web.HTTPError):
            if value.log_message:
                format = "%d %s: " + value.log_message
                args = ([value.status_code, self._request_summary()] +
                        list(value.args))
                LOG.warning(format, *args)
        else:
            out_list = traceback.format_exception(typ, value, tb)

            LOG.error("Uncaught exception %s\\n%r\\n %s",
                      self._request_summary(), self.request,
                      repr(''.join(out_list)))


class BaseAuthHandler(BaseHandler):

    def initialize(self, engine, config, rabbit_client):
        super().initialize(engine, config, rabbit_client)
        self.cluster_secret = config.cluster_secret()

    @property
    def token(self):
        auth_header = self.request.headers.get('Authorization')
        if not auth_header:
            return None
        return auth_header[7:]

    @property
    def secret(self):
        return self.request.headers.get('Secret')

    def get_awaitable(self, meth, *args, **kwargs):
        return self.io_loop.run_in_executor(
            self.executor, functools.partial(meth, *args, **kwargs))

    async def check_permissions(self, action, type, resource_id):
        await self.get_awaitable(self._check_permissions, action, type, resource_id)

    def _check_permissions(self, action, type, resource_id):
        client = AuthClient(url=Config().auth_url)
        client.token = self.token
        LOG.info('Given Auth token is %s:' % self.token)
        try:
            code, response = client.authorize(action, type, resource_id)
            LOG.info('Auth code %s, response: %s', code, response)
        except requests.exceptions.HTTPError as exc:
            if exc.response.status_code == 403:
                raise OptHTTPError(403, Err.G0003, [])
            if exc.response.status_code == 400:
                raise OptHTTPError(400, Err.G0028, [str(exc)])
            if exc.response.status_code == 401:
                raise OptHTTPError(401, Err.G0004, [])
            if exc.response.status_code == 404:
                raise OptHTTPError(404, Err.G0002, [resource_id])
            raise

    def check_cluster_secret(self, **kwargs):
        return self._check_secret(self.cluster_secret, **kwargs)

    def _check_secret(self, secret, raises=True):
        if raises and not self.secret == secret:
            raise OptHTTPError(403, Err.G0006, [])
        else:
            return self.secret == secret

    def prepare(self):
        super().prepare()
        if not self.token and not self.secret:
            raise OptHTTPError(401, Err.G0005, [])

    def get_token_meta(self, digests):
        """
        Get token meta such as user id from auth
        :return:
        """
        client = AuthClient(url=Config().auth_url)
        client.token = self.token
        client.secret = self._config.cluster_secret()
        try:
            _, token_meta_dict = client.token_meta_get(digests)
        except requests.exceptions.HTTPError as exc:
            if exc.response.status_code == 401:
                raise UnauthorizedException(Err.G0004, [])
            raise
        return token_meta_dict

    def get_meta_by_token(self, token):
        user_digest = list(map(
            lambda x: hashlib.md5(x.encode('utf-8')).hexdigest(), [token]))[0]
        token_meta = self.get_token_meta([user_digest]).get(user_digest, {})
        return token_meta

    def check_self_auth(self, user_id):
        token_meta = self.get_meta_by_token(self.token)
        token_valid_until = token_meta.get('valid_until', 0)
        token_user_id = token_meta.get('user_id', '')
        token_expired = token_valid_until < time.time()
        if token_expired or token_user_id != user_id:
            raise OptHTTPError(403, Err.G0003, [])
