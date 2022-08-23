import functools
import hashlib
import json
import logging
from copy import deepcopy

from auth_client.client_v2 import Client as AuthClient
from rest_api_client.client_v2 import Client as RestClient
from optscale_exceptions.http_exc import OptHTTPError
from optscale_exceptions.common_exc import (
    WrongArgumentsException, ForbiddenException, NotFoundException,
    ConflictException, FailedDependency, TimeoutException)
from tornado.ioloop import IOLoop

from slacker_server.models.db_base import BaseDB
from slacker_server.utils import tp_executor

LOG = logging.getLogger(__name__)


class BaseController:
    def __init__(self, engine, config_cl):
        self.engine = engine
        self.config_cl = config_cl
        self._session = None
        self._auth_client = None
        self._rest_client = None

    @property
    def session(self):
        if not self._session:
            self._session = BaseDB.session(self.engine)()
        return self._session

    @property
    def auth_client(self):
        if not self._auth_client:
            self._auth_client = AuthClient(
                url=self.config_cl.auth_url(),
                secret=self.config_cl.cluster_secret())
        return self._auth_client

    @property
    def rest_client(self):
        if not self._rest_client:
            self._rest_client = RestClient(
                url=self.config_cl.restapi_url(),
                secret=self.config_cl.cluster_secret())
        return self._rest_client

    def get_user_api_clients(self, user_id=None, token=None):
        if user_id and token is None:
            _, token_info = self.auth_client.token_get_user_id(user_id)
            token = token_info['token']
        auth_cl = deepcopy(self.auth_client)
        auth_cl.token = token
        auth_cl.secret = None
        rest_cl = deepcopy(self.rest_client)
        rest_cl.token = token
        rest_cl.secret = None
        return auth_cl, rest_cl

    def total_expense_limit_enabled(self, org_id):
        _, features = self.rest_client.organization_option_get(
            org_id, 'features')
        try:
            value = json.loads(features.get('value', {}))
            return bool(value.get('total_expense_limit_enabled'))
        except Exception as exc:
            LOG.warning('Invalid features option value for org %s: %s',
                        org_id, str(exc))
            return False


class BaseHandlerController(BaseController):
    def __init__(self, app, db_session, config_cl=None, token=None,
                 engine=None):
        super().__init__(engine, config_cl)
        self.app = app
        self._session = db_session
        self.config_cl = config_cl
        self._engine = engine
        self.token = token

    def get_user_id(self):
        user_digest = hashlib.md5(self.token.encode('utf-8')).hexdigest()
        _, token_meta = self.auth_client.token_meta_get([user_digest])
        return token_meta.get(user_digest, {}).get('user_id')


class BaseAsyncControllerWrapper(object):
    """
    Used to wrap sync controller methods to return futures
    """

    def __init__(self, app, db_session, config_cl=None, token=None, engine=None):
        self.session = db_session
        self.config_cl = config_cl
        self._controller = None
        self.engine = engine
        self.executor = tp_executor
        self.token = token
        self.app = app

    @property
    def controller(self):
        if not self._controller:
            self._controller = self._get_controller_class()(
                self.app, self.session, self.config_cl, self.token, self.engine)
        return self._controller

    def _get_controller_class(self):
        raise NotImplementedError

    async def get_future(self, meth_name, *args, **kwargs):
        method = getattr(self.controller, meth_name)
        try:
            return await IOLoop.current().run_in_executor(
                self.executor, functools.partial(method, *args, **kwargs))
        except WrongArgumentsException as exc:
            raise OptHTTPError.from_opt_exception(400, exc)
        except ForbiddenException as exc:
            raise OptHTTPError.from_opt_exception(403, exc)
        except NotFoundException as exc:
            raise OptHTTPError.from_opt_exception(404, exc)
        except ConflictException as exc:
            raise OptHTTPError.from_opt_exception(409, exc)
        except FailedDependency as exc:
            raise OptHTTPError.from_opt_exception(424, exc)
        except TimeoutException as exc:
            raise OptHTTPError.from_opt_exception(503, exc)

    def __getattr__(self, name):
        def _missing(*args, **kwargs):
            return self.get_future(name, *args, **kwargs)
        return _missing
