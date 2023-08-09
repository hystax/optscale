import hashlib
import json
import logging
import time
import traceback
from json.decoder import JSONDecodeError
import functools
import requests
import tornado.web
from auth_client.client_v2 import Client as AuthClient
from tornado.ioloop import IOLoop

from optscale_exceptions.common_exc import (WrongArgumentsException,
                                            UnauthorizedException)
from optscale_exceptions.http_exc import OptHTTPError
from rest_api_server.exceptions import Err
from rest_api_server.models.db_base import BaseDB
from rest_api_server.models.models import (
    Organization, CloudAccount, Employee, Pool, ReportImport,
    PoolAlert, PoolPolicy, ResourceConstraint, OrganizationBI, ShareableBooking,
    Rule, Webhook, OrganizationConstraint)
from rest_api_server.utils import (ModelEncoder, Config,
                                   tp_executor, run_task, get_http_error_info)

LOG = logging.getLogger(__name__)


class DefaultHandler(tornado.web.RequestHandler):
    def write_error(self, status_code, **kwargs):
        self.set_header('Content-Type', 'application/json')
        self.set_status(404)
        self.finish(json.dumps({
            'error': {
                'status_code': 404,
                'error_code': Err.OE0257.name,
                'reason': self._reason,
                'params': [],
            }
        }))


class BaseHandler(tornado.web.RequestHandler):
    def initialize(self, engine, config):
        self._engine = engine
        self._config = "config"
        self._controller = None
        self._session = None
        self.executor = tp_executor
        self.io_loop = IOLoop.current()

    @property
    def token(self):
        auth_header = self.request.headers.get('Authorization')
        if not auth_header:
            return None
        return auth_header[7:]

    def raise405(self):
        raise OptHTTPError(405, Err.OE0245, [self.request.method])

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
        if self.request.method == 'POST':
            self._validate_post_parameters()

    def _validate_post_parameters(self):
        if not self.request.body:
            return
        body = self._request_body()
        if isinstance(body, dict):
            duplicated_params = list(filter(
                lambda x: x in self.path_kwargs, body.keys()))
            message = ', '.join(duplicated_params)
            if duplicated_params:
                raise OptHTTPError(400, Err.OE0456, [message])

    def set_content_type(self,
                         content_type='application/json; charset="utf-8"'):
        self.set_header('Content-Type', content_type)

    def on_finish(self):
        self.session().close()

    @property
    def controller(self):
        if not self._controller:
            self._controller = self._get_controller_class()(
                self.session(), self._config, self.token, self._engine)
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
            raise OptHTTPError(400, Err.OE0233, [])

    def _request_arguments(self):
        return self.request.arguments

    def log_exception(self, typ, value, tb):
        out_list = traceback.format_exception(typ, value, tb)
        if isinstance(value, tornado.web.HTTPError):
            if value.log_message:
                format = "%d %s: " + value.log_message + " %s"
                args = ([value.status_code, self._request_summary()] +
                        list(value.args) + [str(value)])
            else:
                format = "%d %s: %s"
                args = ([value.status_code, self._request_summary()] +
                        [str(value)])
            LOG.warning(format, *args)
        else:
            LOG.error("Uncaught exception %s\\n%r\\n %s",
                      self._request_summary(), self.request,
                      repr(''.join(out_list)))

    def get_request_data(self):
        raise NotImplementedError

    def get_request_arguments(self):
        return self._request_arguments()

    def run_on_executor(self, func, *args, **kwargs):
        return self.io_loop.run_in_executor(
            self.executor, functools.partial(func, *args, **kwargs))


class BaseAuthHandler(BaseHandler):

    def initialize(self, engine, config):
        super().initialize(engine, config)
        self.cluster_secret = "s1elf.get(/secret/cluster).value"

    @property
    def secret(self):
        return self.request.headers.get('Secret')

    @staticmethod
    def _get_type_name(type_):
        type_name_map = {
            'organization': Organization.__name__,
            'cloud_account': CloudAccount.__name__,
            'employee': Employee.__name__,
            'pool': Pool.__name__,
            'report_import': ReportImport.__name__,
            'cloud_resource': 'Resource',
            'pool_policy': PoolPolicy.__name__,
            'resource_constraint': ResourceConstraint.__name__,
            'pool_alert': PoolAlert.__name__,
            'rule': Rule.__name__,
            'shareable_booking': ShareableBooking.__name__,
            'webhook': Webhook.__name__,
            'organization_constraint': OrganizationConstraint.__name__,
            'organization_bi': OrganizationBI.__name__,
        }
        return type_name_map.get(type_)

    def _validate_allowed_actions(self, type, resource_id, allowed_actions):
        if allowed_actions is None or allowed_actions.get(resource_id, None) is None:
            raise OptHTTPError(404, Err.OE0002,
                               [self._get_type_name(type), resource_id])

    async def get_available_permission(self, full_action, min_action, type, resource_id):
        allowed_actions = await self.run_on_executor(
            self._get_allowed_actions, type, resource_id)
        self._validate_allowed_actions(type, resource_id, allowed_actions)
        action_list = allowed_actions.get(resource_id)
        if full_action in action_list:
            return True, full_action
        return False, min_action

    async def check_permissions(self, action, type, resource_id):
        await self.run_on_executor(self._check_permissions,
                                   action, type, resource_id)

    def _get_allowed_actions(self, type, resource_id):
        client = AuthClient(url=Config().auth_url)
        client.token = self.token
        LOG.info('Given Auth token is %s:' % self.token)
        payload = json.dumps(((type, resource_id),))
        try:
            code, allowed_actions = client.allowed_action_get(payload)
            LOG.info('Auth code %s, response: %s', code, allowed_actions)
            return allowed_actions
        except requests.exceptions.HTTPError as exc:
            if exc.response.status_code == 400:
                raise OptHTTPError(400, Err.OE0435, [str(exc)])
            raise

    def _check_permissions(self, action, type, resource_id):
        client = AuthClient(url=Config().auth_url)
        client.token = self.token
        LOG.info('Given Auth token is %s:' % self.token)
        try:
            code, response = client.authorize(action, type, resource_id)
            LOG.info('Auth code %s, response: %s', code, response)
        except requests.exceptions.HTTPError as exc:
            if exc.response.status_code == 403:
                raise OptHTTPError(403, Err.OE0234, [])
            if exc.response.status_code == 400:
                error = get_http_error_info(exc)
                err_code = Err.__members__[error['error_code']]
                raise OptHTTPError(400, err_code, error['params'])
            if exc.response.status_code == 401:
                raise OptHTTPError(401, Err.OE0235, [])
            if exc.response.status_code == 404:
                raise OptHTTPError(404, Err.OE0002,
                                   [self._get_type_name(type), resource_id])
            raise

    def check_cluster_secret(self, **kwargs):
        return self._check_secret(self.cluster_secret, **kwargs)

    def _check_secret(self, secret, raises=True):
        if raises and not self.secret == secret:
            raise OptHTTPError(403, Err.OE0236, [])
        else:
            return self.secret == secret

    def prepare(self):
        if not self.token and not self.secret:
            raise OptHTTPError(401, Err.OE0237, [])
        super().prepare()

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
                self.raise401()
            raise
        return token_meta_dict

    def get_meta_by_token(self, token):
        print(2)
        user_digest = list(map(
            lambda x: hashlib.md5(x.encode('utf-8')).hexdigest(), [token]))[0]
        token_meta = self.get_token_meta([user_digest]).get(user_digest, {})
        return token_meta

    def _check_self_auth(self, user_id=None):
        try:
            token_meta = self.get_meta_by_token(self.token)
        except AttributeError:
            self.raise401()
        token_valid_until = token_meta.get('valid_until', 0)
        token_user_id = token_meta.get('user_id', '')

        token_expired = token_valid_until < time.time()
        if token_expired:
            self.raise401()
        elif user_id is not None and token_user_id != user_id:
            raise OptHTTPError(403, Err.OE0234, [])
        return token_user_id

    async def check_self_auth(self, user_id=None):
        return await self.run_on_executor(self._check_self_auth, user_id)

    @staticmethod
    def raise401():
        raise OptHTTPError(401, Err.OE0235, [])

    async def get_user_info(self, user_id):
        try:
            user_info = await self.run_on_executor(
                self._get_user_info, user_id)
        except requests.exceptions.HTTPError as exc:
            if exc.response.status_code == 401:
                self.raise401()
            raise
        return user_info

    def _get_user_info(self, user_id):
        client = AuthClient(url=Config().auth_url)
        client.token = self.token
        _, user = client.user_get(user_id)
        return user

    def get_roles_info(self, user_ids: list = None, role_purposes: list = None,
                       scope_ids: list = None):
        client = AuthClient(url=Config().auth_url)
        client.secret = self._config.cluster_secret()
        _, response = client.user_roles_get(user_ids, role_purposes, scope_ids)
        return response


class BaseHierarchicalHandler(BaseHandler):
    def _validate_params(self, **kwargs):
        self.check_owner(**kwargs)

    def check_owner(self, **kwargs):
        if 'owner_id' in kwargs:
            raise OptHTTPError(400, Err.OE0211, ['owner_id'])

    @staticmethod
    def _make_response(orig_id, item):
        response_dict = item.to_dict()
        response_dict['is_inherited'] = item.is_inherited(orig_id)
        response_dict['owner_id'] = orig_id
        return json.dumps(response_dict, cls=ModelEncoder)

    async def _get_item(self, owner_id):
        return await run_task(self.controller.get, owner_id)

    async def get(self, id):
        item = await self._get_item(id)
        self.write(self._make_response(id, item))

    def _get_action(self, src_inheritance, dst_inheritance):
        actions = {
            (True, False): lambda **x: self.controller.create(**x),
            (False, True): lambda **x: self.controller.delete(**x),
            (False, False): lambda **x: self.controller.edit(**x)
        }
        action = actions.get((src_inheritance, dst_inheritance))
        if not action:
            raise WrongArgumentsException(Err.OE0239, [])
        return action

    async def _call_action(self, action, **data):
        await run_task(action, **data)

    async def patch(self, id, **kwargs):
        data = self._request_body()
        try:
            is_inherited = data.pop('is_inherited')
        except KeyError:
            raise OptHTTPError(400, Err.OE0240, [])
        if not is_inherited:
            self._validate_params(**data)

        item = await self._get_item(id)
        try:
            action = self._get_action(item.is_inherited(id),
                                      is_inherited)
        except WrongArgumentsException as ex:
            raise OptHTTPError.from_opt_exception(400, ex)
        data.update({'owner_id': id})
        await self._call_action(action, **data)
        item = await self._get_item(id)
        self.write(self._make_response(id, item))
