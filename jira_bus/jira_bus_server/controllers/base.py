import functools
import inspect
import json
import logging

import requests
from auth_client.client_v2 import Client as AuthClient
from optscale_exceptions.common_exc import (
    WrongArgumentsException, ForbiddenException, NotFoundException,
    ConflictException, FailedDependency, TimeoutException)
from optscale_exceptions.http_exc import OptHTTPError
from requests.exceptions import RequestException, HTTPError
from rest_api_client.client_v2 import Client as RestClient
from tornado.ioloop import IOLoop

from jira_bus_server.atlassian_client.client import AtlassianClient
from jira_bus_server.atlassian_client.exceptions import (
    AtlassianClientException)
from jira_bus_server.constants import APP_KEY
from jira_bus_server.exceptions import Err
from jira_bus_server.models.models import (AppInstallation, UserAssignment,
                                           OrganizationAssignment)
from jira_bus_server.utils import tp_executor

LOG = logging.getLogger(__name__)


class BaseController:
    def __init__(self, db_session, config=None, engine=None):
        super().__init__()
        self._session = db_session
        self._config = config
        self._db = None
        self._engine = engine

    @property
    def engine(self):
        return self._engine

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, val):
        self._session = val

    @property
    def _cluster_secret(self):
        return self._config.cluster_secret()

    def _get_rest_client(self, token=None, secret=None) -> RestClient:
        return RestClient(url=self._config.restapi_url(),
                          token=token, secret=secret)

    def _get_auth_client(self, token=None, secret=None) -> AuthClient:
        return AuthClient(url=self._config.auth_url(),
                          token=token, secret=secret)

    @staticmethod
    def _get_atlassian_client(app_installation):
        base_url = json.loads(app_installation.extra_payload)['baseUrl']
        return AtlassianClient(
            APP_KEY, base_url, app_installation.shared_secret)

    def _get_model(self, model, **filter_kwargs):
        if not filter_kwargs:
            raise ValueError('No filter kwargs provided')
        return (self.session
                .query(model)
                .filter(model.deleted.is_(False))
                .filter_by(**filter_kwargs)
                .one_or_none())

    def _get_app_installation_by_client_key(
            self, client_key, raise_not_found=True) -> AppInstallation:
        app_installation = self._get_model(
            AppInstallation, client_key=client_key)
        if not app_installation and raise_not_found:
            raise NotFoundException(Err.OJ0014, [client_key])
        return app_installation

    def _get_user_assignment_by_account_id(
            self, account_id, raise_not_found=True) -> UserAssignment:
        user_assignment = self._get_model(
            UserAssignment, jira_account_id=account_id)
        if not user_assignment and raise_not_found:
            raise NotFoundException(Err.OJ0008, ['user', account_id])
        return user_assignment

    def _get_user_assignment_by_secret(
            self, secret, raise_invalid=True) -> UserAssignment:
        user_assignment = self.session.query(UserAssignment).filter(
            UserAssignment.secret == secret,
            UserAssignment.deleted.is_(False),
        ).one_or_none()
        if not user_assignment and raise_invalid:
            raise WrongArgumentsException(Err.OJ0011, ['secret'])
        return user_assignment

    def _get_org_assignment_by_org_id(
            self, organization_id,
            raise_not_found=True) -> OrganizationAssignment:
        org_assignment = self.session.query(OrganizationAssignment).filter(
            OrganizationAssignment.organization_id == organization_id,
            OrganizationAssignment.deleted.is_(False),
        ).one_or_none()
        if not org_assignment and raise_not_found:
            raise NotFoundException(Err.OJ0008, [
                'organization_id', organization_id])
        return org_assignment

    def _get_org_assignment_by_client_key(
            self, client_key, raise_not_found=True) -> OrganizationAssignment:
        org_assignment = (
            self.session
                .query(OrganizationAssignment)
                .join(OrganizationAssignment.app_installation)
                .filter(AppInstallation.client_key == client_key,
                        AppInstallation.deleted.is_(False),
                        OrganizationAssignment.deleted.is_(False))
                .one_or_none()
        )
        if not org_assignment and raise_not_found:
            raise NotFoundException(Err.OJ0019, [client_key])
        return org_assignment

    @staticmethod
    def _parse_issue_key(issue_key):
        issue_key_parts = issue_key.rsplit('-', 1)
        try:
            project_key = issue_key_parts[0]
            issue_number = int(issue_key_parts[1])
        except (IndexError, ValueError):
            LOG.error('Could not parse issue key: %s', issue_key)
            raise WrongArgumentsException(Err.OJ0011, ['issue_key'])
        return project_key, issue_number

    def _get_issue_info(self, app_installation, issue_key):
        project_key, issue_number = self._parse_issue_key(issue_key)

        extra_payload = json.loads(app_installation.extra_payload)
        # Jira docs say to use displayUrl if it's present for user-facing links
        base_url = extra_payload.get('displayUrl') or extra_payload['baseUrl']
        issue_link = '{}/browse/{}'.format(base_url, issue_key)

        atlassian_client = self._get_atlassian_client(app_installation)
        issue_details = atlassian_client.issue(issue_key).get(
            fields='status', expand='transitions')
        available_statuses = sorted({
            x['to']['name'] for x in issue_details['transitions']})
        current_status = issue_details['fields']['status']['name']
        return {
            'issue_key': issue_key,
            'project_key': project_key,
            'issue_number': issue_number,
            'issue_link': issue_link,
            'available_statuses': available_statuses,
            'current_status': current_status,
        }

    @staticmethod
    def get_atlassian_public_key(key_id):
        key_url = f'https://connect-install-keys.atlassian.com/{key_id}'
        try:
            response = requests.get(key_url, timeout=60)
        except RequestException as exc:
            raise FailedDependency(Err.OJ0015, [str(exc)])
        return response.text

    def get_atlassian_shared_secret(self, client_key):
        app_installation = self._get_app_installation_by_client_key(client_key)
        return app_installation.shared_secret

    def _get_auth_token_by_auth_user_id(self, auth_user_id):
        auth_client = self._get_auth_client(secret=self._cluster_secret)
        _, token_info = auth_client.token_get_user_id(auth_user_id)
        return token_info['token']

    def get_auth_token(self, account_id):
        user_assignment = self._get_user_assignment_by_account_id(account_id)
        if not user_assignment.auth_user_id:
            raise FailedDependency(Err.OJ0021, [account_id])
        return self._get_auth_token_by_auth_user_id(
            user_assignment.auth_user_id)


class BaseAsyncControllerWrapper(object):
    """
    Used to wrap sync controller methods to return futures
    """

    def __init__(self, db_session, config=None, engine=None):
        self._session = db_session
        self._config = config
        self._db = None
        self._engine = engine
        self._controller = None
        self.executor = tp_executor

    @property
    def controller(self):
        if not self._controller:
            self._controller = self._get_controller_class()(
                self._session, self._config, self.engine)
        return self._controller

    @property
    def engine(self):
        return self._engine

    def _get_controller_class(self):
        raise NotImplementedError

    @staticmethod
    def _is_module_in_trace(module_names):
        frames = inspect.trace()
        for frame_info in frames:
            cur_module = inspect.getmodule(frame_info[0])
            cur_module_name = cur_module.__name__
            for module_name in module_names:
                if (cur_module_name == module_name or
                        cur_module_name.startswith(module_name + '.')):
                    return True
        return False

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
        except AtlassianClientException as exc:
            raise OptHTTPError(424, Err.OJ0023, [str(exc)])
        except HTTPError as exc:
            # Super ugly error handling for RestAPI and Auth client errors
            # TODO: this can be made better
            handled_modules = ['auth_client', 'rest_api_client']
            if self._is_module_in_trace(handled_modules):
                error_dict = exc.response.json().get('error', {})
                raise OptHTTPError(exc.response.status_code, Err.OJ0020,
                                   [error_dict.get('reason')])
            raise

    def __getattr__(self, name):
        def _missing(*args, **kwargs):
            return self.get_future(name, *args, **kwargs)

        return _missing


class BaseAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return BaseController
