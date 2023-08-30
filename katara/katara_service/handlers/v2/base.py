import json
import logging
import traceback
import tornado.web

from katara.katara_service.exceptions import Err
from katara.katara_service.models.db_base import BaseDB
from katara.katara_service.utils import ModelEncoder

from tools.optscale_exceptions.common_exc import (
    ForbiddenException,
    WrongArgumentsException,
    NotFoundException,
    ConflictException,
    UnauthorizedException
)

from tools.optscale_exceptions.http_exc import OptHTTPError


LOG = logging.getLogger(__name__)


class DefaultHandler(tornado.web.RequestHandler):
    def write_error(self, status_code, **kwargs):
        self.set_header('Content-Type', 'application/json')
        self.set_status(404)
        self.finish(json.dumps({
            'error': {
                'status_code': 404,
                'error_code': Err.OKA0007.name,
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
        raise OptHTTPError(405, Err.OKA0008, [self.request.method])

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
        if self._session:
            self._session.close()

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
                'error_code': getattr(exc, 'error_code', 'U0%s' % status_code),
                'reason': self._reason,
                'params': getattr(exc, 'params', []),
            }
        }
        self.set_content_type('application/json; charset="utf-8"')
        self.finish(json.dumps(res, cls=ModelEncoder))

    def set_content_type(
            self, content_type='application/json; charset="utf-8"'):
        self.set_header('Content-Type', content_type)

    def _request_body(self):
        request_object = self._validate_request_body()
        if not request_object:
            raise OptHTTPError(400, Err.OKA0009, [])
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
                format = "%d %s: " + value.log_message
                args = ([value.status_code, self._request_summary()] +
                        list(value.args))
                LOG.warning(format, *args)
        else:
            out_list = traceback.format_exception(typ, value, tb)

            LOG.error("Uncaught exception %s\\n%r\\n %s",
                      self._request_summary(), self.request,
                      repr(''.join(out_list)))

    def get_arg(self, name, type, default=None, repeated=False):
        try:
            if repeated:
                return [type(a) for a in self.get_arguments(name)]
            else:
                arg = self.get_argument(name, default=default)
                if arg:
                    if type == bool:
                        lowered = arg.lower()
                        if lowered not in ['true', 'false']:
                            raise WrongArgumentsException(Err.OKA0026, [name])
                        return lowered == 'true'
                    return type(arg)
                else:
                    return arg
        except ValueError:
            raise WrongArgumentsException(Err.OKA0025, [name])

    def parse_url_params_into_payload(self, payload_map_params):
        data = {}
        payload = {}
        for k in self.request.arguments.keys():
            extract_target = data
            repeated = False
            param = k
            param_type = str
            if k in payload_map_params.keys():
                param, param_type, repeated = payload_map_params.get(k)
                extract_target = payload
            extract_target[param] = self.get_arg(
                k, param_type, repeated=repeated)
        data['payload'] = payload
        return data


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
            raise OptHTTPError(403, Err.OKA0010, [])
        else:
            return self.secret == secret

    def prepare(self):
        try:
            if not self.secret:
                raise UnauthorizedException(Err.OKA0011, [])
        except UnauthorizedException as exc:
            raise OptHTTPError.from_opt_exception(401, exc)
        self.check_cluster_secret()
        super().prepare()


class BaseAsyncCollectionHandler(BaseSecretHandler):

    def _validate_params(self, **kwargs):
        pass

    async def post(self, **url_params):
        data = self._request_body()
        duplicates = list(filter(lambda x: x in url_params.keys(),
                                 data.keys()))
        if duplicates:
            unexpected_string = ', '.join(duplicates)
            raise OptHTTPError(400, Err.OKA0012, [unexpected_string])
        data.update(url_params)
        self._validate_params(**data)
        try:
            item = await self.controller.create(**data)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)
        except ConflictException as ex:
            raise OptHTTPError.from_opt_exception(409, ex)
        except ForbiddenException as ex:
            raise OptHTTPError.from_opt_exception(403, ex)
        except UnauthorizedException as ex:
            raise OptHTTPError.from_opt_exception(401, ex)
        self.set_status(201)
        self.write(item.to_json())


class BaseAsyncItemHandler(BaseSecretHandler):

    def _validate_params(self, item, **kwargs):
        pass

    async def _get_item(self, item_id, **kwargs):
        try:
            item = await self.controller.get(item_id, **kwargs)
            if item is None:
                type_name = self.controller.model_type.__name__
                raise OptHTTPError(404, Err.OKA0013, [type_name, item_id])
            return item
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)
        except ForbiddenException as ex:
            raise OptHTTPError.from_opt_exception(403, ex)
        except NotImplementedError:
            raise OptHTTPError(405, Err.OKA0014, [])

    async def get(self, id):
        item = await self._get_item(id)
        self.write(item.to_json())

    async def patch(self, id, **kwargs):
        data = self._request_body()
        item = await self._get_item(id, **kwargs)
        self._validate_params(item, **kwargs)
        try:
            item = await self.controller.edit(id, **data)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        except NotFoundException as ex:
            raise OptHTTPError.from_opt_exception(404, ex)
        except ConflictException as ex:
            raise OptHTTPError.from_opt_exception(409, ex)
        except ForbiddenException as ex:
            raise OptHTTPError.from_opt_exception(403, ex)
        except UnauthorizedException as ex:
            raise OptHTTPError.from_opt_exception(401, ex)
        except NotImplementedError:
            raise OptHTTPError(405, Err.OKA0014, [])
        self.write(item.to_json())

    async def delete(self, id, **kwargs):
        item = await self._get_item(id)
        self._validate_params(item, **kwargs)
        try:
            await self.controller.delete(id, **kwargs)
        except ForbiddenException as ex:
            raise OptHTTPError.from_opt_exception(403, ex)
        except UnauthorizedException as ex:
            raise OptHTTPError.from_opt_exception(401, ex)
        self.set_status(204)
