import json
import logging
import traceback
import tornado.web

from auth.auth_server.exceptions import Err
from auth.auth_server.models.db_base import BaseDB
from auth.auth_server.utils import ModelEncoder, run_task

from tools.optscale_exceptions.common_exc import (WrongArgumentsException,
                                                  UnauthorizedException)
from tools.optscale_exceptions.http_exc import OptHTTPError

LOG = logging.getLogger(__name__)


class DefaultHandler(tornado.web.RequestHandler):
    def write_error(self, status_code, **kwargs):
        self.set_header('Content-Type', 'application/json')
        self.set_status(404)
        self.finish(json.dumps({
            'error': {
                'status_code': 404,
                'error_code': Err.OA0053.name,
                'reason': self._reason,
                'params': [],
            }
        }))


class BaseHandler(tornado.web.RequestHandler):
    def initialize(self, engine, config):
        self._engine = engine
        self._config = config
        self._controller = None
        self._session = None
        self.set_content_type('application/json; charset="utf-8"')

    def raise405(self):
        raise OptHTTPError(405, Err.OA0052, [self.request.method])

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

    def on_finish(self):
        self.session().close()

    @property
    def controller(self):
        if not self._controller:
            self._controller = self._get_controller_class()(
                self.session(), self._config)
        return self._controller

    def _get_controller_class(self):
        raise NotImplementedError

    def write_error(self, status_code, **kwargs):
        exc = kwargs.get('exc_info')[1]
        res = {
            'error': {
                'status_code': status_code,
                'error_code': getattr(exc, 'error_code', f'U0{status_code}'),
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
        request_object = self._validate_request_body()
        if not request_object:
            raise OptHTTPError(400, Err.OA0050, [])
        return request_object

    def _validate_request_body(self):
        try:
            request_object = json.loads(self.request.body.decode('utf-8'))
            if not isinstance(request_object, dict):
                return None
        except (TypeError, json.JSONDecodeError):
            return None
        return request_object

    def log_exception(self, typ, value, tb):
        if isinstance(value, OptHTTPError):
            if value.log_message:
                format_ = "%d %s: " + value.log_message
                args = ([value.status_code, self._request_summary()] +
                        list(value.args))
                LOG.warning(format_, *args)
        else:
            out_list = traceback.format_exception(typ, value, tb)

            LOG.error("Uncaught exception %s\\n%r\\n %s",
                      self._request_summary(), self.request,
                      repr(''.join(out_list)))

    def get_request_data(self):
        raise NotImplementedError

    def get_ip_addr(self):
        return self.request.headers.get(
            'X-Forwarded-For', self.request.remote_ip).split(',')[0]


class BaseAuthHandler(BaseHandler):

    @property
    def token(self):
        auth_header = self.request.headers.get('Authorization')
        if not auth_header:
            return {'token': None}
        return {'token': auth_header[7:]}

    async def check_token(self):
        try:
            token = self.get_argument('access_token', None)
            if not token:
                auth_header = self.request.headers.get('Authorization', None)
                if not auth_header:
                    raise UnauthorizedException(Err.OA0062, [])
                token = auth_header[7:]
            await self.controller.check_token_valid(token)
        except UnauthorizedException as ex:
            raise OptHTTPError.from_opt_exception(401, ex)

    async def prepare(self):
        await self.check_token()


class BaseSecretHandler(BaseHandler):

    def initialize(self, engine, config):
        super().initialize(engine, config)
        self.cluster_secret = config.cluster_secret()

    @property
    def secret(self):
        return self.request.headers.get('Secret')

    def check_cluster_secret(self, **kwargs):
        return self._check_secret(self.cluster_secret, **kwargs)

    def _check_secret(self, secret, raises=True):
        if raises and not self.secret == secret:
            raise OptHTTPError(403, Err.OA0006, [])
        else:
            return self.secret == secret

    def prepare(self):
        if not self.secret:
            raise OptHTTPError(401, Err.OA0007, [])
        super().prepare()


class BaseAsyncCollectionHandler(BaseHandler):

    async def _validate_params(self, **kwargs):
        pass

    async def post(self, **url_params):
        data = self._request_body()
        try:
            await self._validate_params(**data)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        data.update(url_params)
        data.update({'ip': self.get_ip_addr()})
        res = await run_task(self.controller.create, **data)
        self.set_status(201)
        self.write(res.to_json())


class BaseAsyncAuthCollectionHandler(BaseAuthHandler):

    def _validate_params(self, **kwargs):
        pass

    async def post(self, **url_params):
        data = self._request_body()
        duplicates = list(filter(lambda x: x in url_params, data.keys()))
        if duplicates:
            unexpected_string = ', '.join(duplicates)
            raise OptHTTPError(400, Err.OA0022, [unexpected_string])
        data.update(url_params)
        # update data with auth token
        data.update(self.token)
        self._validate_params(**data)
        res = await run_task(self.controller.create, **data)
        self.set_status(201)
        self.write(res.to_json())


class BaseAsyncAuthItemHandler(BaseAuthHandler):

    def _validate_params(self, item, **kwargs):
        pass

    async def _get_item(self, item_id, **kwargs):
        item = await run_task(self.controller.get, item_id, **kwargs)
        type_name = self.controller.model_type.__name__
        if item is None:
            raise OptHTTPError(404, Err.OA0003, [type_name, item_id])
        return item

    @staticmethod
    def merge_resource_info(item, resource_info):
        return dict(list(item.to_dict().items()) + [
            ('scope_name', resource_info.get('name'))])

    async def put(self, **url_params):
        data = self._request_body()
        data.update(url_params)
        data.update(self.token)
        res = await run_task(self.controller.create, **data)
        self.set_status(201)
        self.write(res.to_json())

    async def get(self, item_id, **kwargs):
        kwargs.update(self.token)
        item = await self._get_item(item_id, **kwargs)
        self._validate_params(item, **kwargs)
        self.write(item.to_json())

    async def patch(self, item_id, **kwargs):
        data = self._request_body()
        kwargs.update(self.token)
        data.update(self.token)
        item = await self._get_item(item_id, **kwargs)
        self._validate_params(item, **kwargs)
        res = await run_task(self.controller.edit, item_id, **data)
        self.write(res.to_json())

    async def delete(self, item_id, **kwargs):
        item = await self._get_item(item_id)
        kwargs.update(self.token)
        self._validate_params(item, **kwargs)
        await run_task(self.controller.delete, item_id, **kwargs)
        self.set_status(204)
