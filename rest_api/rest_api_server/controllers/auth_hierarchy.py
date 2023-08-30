import logging
import copy

from sqlalchemy import and_

from rest_api.rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.models.models import Organization, Pool
from tools.optscale_exceptions.common_exc import (
    WrongArgumentsException, NotFoundException)

LOG = logging.getLogger(__name__)


class AuthHierarchyController(object):
    model_map = {
        'organization': Organization,
        'pool': Pool
    }

    def __init__(self, db_session, config=None, token=None, engine=None):
        self.session = db_session
        self._config = config
        self._engine = engine
        self._db = None
        self.token = token

    @property
    def engine(self):
        return self._engine

    @engine.setter
    def engine(self, val):
        self._engine = val

    def _check_resource(self, type, scope_id):
        model = self.model_map.get(type)
        if model is None:
            raise WrongArgumentsException(Err.OE0216, ['model'])
        resource = self.session.query(model).filter(
            and_(model.id == scope_id,
                 model.deleted.is_(False))).one_or_none()
        if not resource:
            raise NotFoundException(Err.OE0002, [model.__name__, scope_id])

    def auth_hierarchy(self, type=None, scope_id=None):
        if not type:
            raise WrongArgumentsException(Err.OE0216, ['type'])
        if not scope_id and type != 'root':
            raise WrongArgumentsException(Err.OE0216, ['scope_id'])
        if type != 'root':
            self._check_resource(type, scope_id)

        result = dict()
        sql = self.session.query(Organization.id, Pool.id).outerjoin(
            Pool, and_(
                Pool.organization_id == Organization.id,
                Pool.deleted.is_(False))
        ).filter(Organization.deleted.is_(False))
        if type != 'root':
            sql = sql.filter(self.model_map.get(type).id == scope_id)
        queryset = sql.order_by(Organization.id, Pool.id).all()
        if result.get('organization') is None:
            result['organization'] = dict()
        for item in queryset:
            organization_id, pool_id = item
            if organization_id is not None and organization_id not in result['organization']:
                result['organization'][organization_id] = dict()
            if result['organization'][organization_id].get('pool') is None:
                result['organization'][organization_id]['pool'] = list()
            if pool_id is not None:
                result['organization'][organization_id]['pool'].append(pool_id)
        result_scope = {
            'root': lambda t: dict(root=dict(null=result)),
            'organization': lambda t: dict(organization=copy.deepcopy(result[t])),
            'pool': lambda t: dict(
                pool=copy.deepcopy(result['organization'][queryset[0][0]][t]))
        }
        return result_scope.get(type)(type)


class AuthHierarchyAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return AuthHierarchyController
