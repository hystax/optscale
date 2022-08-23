import json
import logging
import traceback
import tornado.web
from tornado import gen
import requests
from tornado.ioloop import IOLoop
from tornado.concurrent import return_future, run_on_executor
from optscale_exceptions.common_exc import (WrongArgumentsException,
                                            ForbiddenException,
                                            UnauthorizedException)
from optscale_exceptions.http_exc import OptHTTPError

from report_server.exceptions import Err
from report_server.utils import ModelEncoder
from report_server.utils import tp_executor, Config
from auth_client.client_v2 import Client as AuthClient
from json.decoder import JSONDecodeError

LOG = logging.getLogger(__name__)


class DefaultHandler(tornado.web.RequestHandler):
    def write_error(self, status_code, **kwargs):
        self.set_header('Content-Type', 'application/json')
        self.set_status(404)
        self.finish(json.dumps({
            'error': {
                'status_code': 404,
                'error_code': Err.OK0023.name,
                'reason': self._reason,
                'params': [],
            }
        }))


class BaseHandler(tornado.web.RequestHandler):
    def initialize(self, mongo_client, config, rabbit_client):
        self.mongo_client = mongo_client
        self._config = config
        self.rabbit_client = rabbit_client
        self._controller = None
        self.executor = tp_executor
        self.io_loop = IOLoop.current()

    def raise405(self):
        raise OptHTTPError(405, Err.OK0022, [self.request.method])

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

    def on_finish(self):
        pass

    @property
    def controller(self):
        if not self._controller:
            self._controller = self._get_controller_class()(
                self.mongo_client, self._config,
                self.rabbit_client)
        return self._controller

    def _validate_params(self, **kwargs):
        pass

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

    def set_content_type(self,
                         content_type='application/json; charset="utf-8"'):
        self.set_header('Content-Type', content_type)

    def _request_body(self):
        try:
            return json.loads(self.request.body.decode('utf-8'))
        except (JSONDecodeError, TypeError):
            raise OptHTTPError(400, Err.OK0038, [])

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

    def initialize(self, mongo_client, config, rabbit_client):
        super().initialize(mongo_client, config, rabbit_client)
        self.cluster_secret = config.cluster_secret()
        self.agent_secret = config.agent_secret()

    @property
    def token(self):
        auth_header = self.request.headers.get('Authorization')
        if not auth_header:
            return None
        return auth_header[7:]

    @property
    def secret(self):
        return self.request.headers.get('Secret')

    def prepare(self):
        try:
            if not self.token and not self.secret:
                raise UnauthorizedException(
                    Err.OK0005, [])
        except UnauthorizedException as exc:
            self.set_status(401)
            self.finish({'error': str(exc)})
        super().prepare()

    @gen.coroutine
    def check_permissions(self, action, type, resource_id):
        yield gen.Task(self._check_permissions, action, type, resource_id)

    @run_on_executor
    @return_future
    def _check_permissions(self, action, type, resource_id, callback=None):
        client = AuthClient(url=Config().auth_url)
        client.token = self.token
        LOG.info('Given Auth token is %s:' % self.token)
        try:
            code, response = client.authorize(action, type, resource_id)
            LOG.info('Auth code %s, response: %s', code, response)
        except requests.exceptions.HTTPError as exc:
            if exc.response.status_code == 403:
                raise OptHTTPError(403, Err.OK0002, [])
            if exc.response.status_code == 401:
                raise OptHTTPError(401, Err.OK0003, [])
            if exc.response.status_code == 404:
                raise OptHTTPError(404, Err.OK0004,
                                   ["business unit", resource_id])
            raise
        callback(None)

    def check_cluster_secret(self, **kwargs):
        return self._check_secret(self.cluster_secret, **kwargs)

    def check_agent_secret(self, **kwargs):
        return self._check_secret(self.agent_secret, **kwargs)

    def _check_secret(self, secret, raises=True):
        if raises:
            if not self.secret == secret:
                raise OptHTTPError(403, Err.OK0006, [])
        return self.secret == secret

    def get_request_data(self):
        return self._request_body()


class BaseReportHandler(BaseAuthHandler):
    def validate_payload(self, payload_dict):
        customers = payload_dict.get('customers')
        if (not customers or not isinstance(customers,
                                            list) or not len(customers) > 0):
            raise OptHTTPError(400, Err.OK0009, [])
        for customer_id in customers:
            yield self.check_permissions('INFO_CUSTOMER', 'customer',
                                         customer_id)

    @gen.coroutine
    def get(self):
        try:
            data = self.get_request_data()
        except ValueError:
            raise OptHTTPError(400, Err.OK0026, [])
        payload = data.get('payload')
        if payload is None:
            raise OptHTTPError(400, Err.OK0025, [])
        try:
            payload_dict = json.loads(payload)
            if not isinstance(payload_dict, dict):
                raise OptHTTPError(400, Err.OK0007, [])
        except ValueError:
            raise OptHTTPError(400, Err.OK0008, [])

        try:
            self.validate_payload(payload_dict)
            res = yield gen.Task(self.controller.get, **payload_dict)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        self.write(json.dumps(res.result(), cls=ModelEncoder))


class BaseReceiveHandler(BaseAuthHandler):
    @gen.coroutine
    def post(self, **url_params):
        data = self._request_body()
        data.update(url_params)
        self._validate_params(**data)
        try:
            res = yield gen.Task(self.controller.submit, **data)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        except ForbiddenException as ex:
            raise OptHTTPError.from_opt_exception(403, ex)
        except UnauthorizedException as ex:
            raise OptHTTPError.from_opt_exception(401, ex)
        self.set_status(201)
        self.write(json.dumps(res.result()))
