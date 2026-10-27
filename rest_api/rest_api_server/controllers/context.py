import logging

from rest_api.rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api.rest_api_server.controllers.base import (
    BaseHierarchicalController, MongoMixin)
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.models.models import (
    Organization, CloudAccount, Employee, Pool, ReportImport, PoolAlert,
    PoolPolicy, ResourceConstraint, Rule, ShareableBooking, Webhook,
    OrganizationConstraint, OrganizationBI, OrganizationGemini, PowerSchedule,
    EmployeeEmail, GeminiData)
from tools.optscale_exceptions.common_exc import (WrongArgumentsException,
                                                  NotFoundException)
from rest_api.rest_api_server.utils import tp_executor_context
from sqlalchemy import true
from rest_api.rest_api_server.controllers.organization import OrganizationController

LOG = logging.getLogger(__name__)


class ContextController(MongoMixin):
    def __init__(self, db_session, config=None, token=None, engine=None):
        super().__init__()
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

    def _get_input(self, **kwargs):
        type_name = kwargs.get("type")
        uuid = kwargs.get("uuid")
        if not type_name or not uuid:
            raise WrongArgumentsException(Err.OE0173, [])
        if isinstance(type_name, str):
            type_name = type_name.lower()
        if type_name not in ['organization', 'cloud_account', 'employee',
                             'pool', 'report_import', 'cloud_resource',
                             'pool_alert', 'pool_policy',
                             'resource_constraint', 'rule',
                             'shareable_booking', 'webhook',
                             'organization_constraint', 'organization_bi',
                             'organization_gemini', 'power_schedule',
                             'employee_email', 'gemini_data']:
            raise WrongArgumentsException(Err.OE0174, [type_name])
        return type_name, uuid

    def _get_item(self, type_name, uuid):
        type_name_map = {
            'organization': Organization.__name__,
            'cloud_account': CloudAccount.__name__,
            'employee': Employee.__name__,
            'pool': Pool.__name__,
            'report_import': ReportImport.__name__,
            'pool_alert': PoolAlert.__name__,
            'rule': Rule.__name__,
            'shareable_booking': ShareableBooking.__name__,
            'webhook': Webhook.__name__,
            'organization_constraint': OrganizationConstraint.__name__,
            'organization_bi': OrganizationBI.__name__,
            'organization_gemini': OrganizationGemini.__name__,
            'power_schedule': PowerSchedule.__name__,
            'employee_email': EmployeeEmail.__name__,
            'gemini_data': GeminiData.__name__,
        }

        def call_query(base):
            return base.filter_by(id=uuid, deleted_at=0).one_or_none()

        def call_pipeline(base):
            return base.find_one({"_id": uuid, "deleted_at": 0})

        query_map = {
            'organization': (self.session.query(Organization), call_query),
            'cloud_account': (self.session.query(CloudAccount), call_query),
            'employee': (self.session.query(Employee), call_query),
            'pool': (self.session.query(Pool), call_query),
            'report_import': (self.session.query(ReportImport), call_query),
            'pool_alert': (self.session.query(PoolAlert), call_query),
            'pool_policy': (self.session.query(PoolPolicy), call_query),
            'resource_constraint': (self.session.query(ResourceConstraint), call_query),
            'rule': (self.session.query(Rule), call_query),
            'cloud_resource': (self.resources_collection, call_pipeline),
            'shareable_booking': (self.session.query(ShareableBooking), call_query),
            'webhook': (self.session.query(Webhook), call_query),
            'organization_constraint': (self.session.query(OrganizationConstraint),
                                        call_query),
            'organization_bi': (self.session.query(OrganizationBI), call_query),
            'organization_gemini': (self.session.query(OrganizationGemini),
                                    call_query),
            'power_schedule': (self.session.query(PowerSchedule), call_query),
            'employee_email': (self.session.query(EmployeeEmail), call_query),
            'gemini_data': (self.session.query(GeminiData), call_query)
        }

        query_base, func = query_map.get(type_name)
        item = func(query_base)
        if not item:
            raise NotFoundException(Err.OE0002,
                                    [type_name_map.get(type_name), uuid])
        return item

    def context(self, **kwargs):
        type_name, uuid = self._get_input(**kwargs)
        result_map = {
            'organization': lambda x: {
                'organization': [x.id, ]
            },
            'pool': lambda x: {
                'organization': [x.organization_id, ],
                'pool': self.get_hierarchy(x),
            },
        }
        childs_map = {
            'cloud_account': lambda x: (
                'organization', x.organization
            ),
            'employee': lambda x: (
                'organization', x.organization
            ),
            'report_import': lambda x: (
                'organization', x.cloud_account.organization
            ),
            'cloud_resource': lambda x: (
                self.get_info_for_resource(x)
            ),
            'pool_alert': lambda x: (
                'pool', x.pool
            ),
            'pool_policy': lambda x: (
                'pool', x.pool
            ),
            'resource_constraint': lambda x: (
                self.get_info_for_resource(
                    self._get_item('cloud_resource', x.resource_id))
            ),
            'rule': lambda x: (
                'organization', x.organization
            ),
            'shareable_booking': lambda x: (
                self.get_info_for_resource(
                    self._get_item('cloud_resource', x.resource_id))
            ),
            'webhook': lambda x: (
                'organization', x.organization
            ),
            'organization_constraint': lambda x: (
                'organization', self._get_item('organization', x.organization_id)
            ),
            'organization_bi': lambda x: (
                'organization', self._get_item('organization', x.organization_id)
            ),
            'organization_gemini': lambda x: (
                'organization', self._get_item('organization', x.organization_id)
            ),
            'power_schedule': lambda x: (
                'organization', self._get_item('organization', x.organization_id)
            ),
            'employee_email': lambda x: (
                'employee',
                self._get_item('employee', x.employee_id)
            ),
            'gemini_data': lambda x: (
                'organization',
                self._get_item('organization',
                               x.organization_gemini.organization_id)
            )
        }
        item = self._get_item(type_name, uuid)
        source_type = type_name
        if type_name in childs_map:
            type_name, item = childs_map.get(type_name)(item)
        res = result_map.get(type_name)(item)
        deleted_object = self.check_deleted(res)
        if deleted_object:
            raise WrongArgumentsException(Err.OE0472, [
                source_type, uuid, deleted_object[0], deleted_object[1]])
        self.restrict_allowed_actions(res)
        return res

    def check_deleted(self, result_map):
        models = {
            'organization': Organization,
            'pool': Pool
        }
        for obj_type, model in models.items():
            ids = result_map.get(obj_type)
            if ids:
                deleted_objects = self.session.query(model.id).filter(
                    model.id.in_(ids),
                    model.deleted.is_(True)
                ).all()
                if deleted_objects:
                    return obj_type, deleted_objects[0][0]
        return None

    def _get_disabled_organizations(self, ids):
        return self.session.query(Organization.id).filter(
            Organization.id.in_(ids),
            Organization.deleted.is_(False),
            Organization.disabled.is_(true())
        ).all()

    def restrict_allowed_actions(self, result_map):
        # key: (get_restricted_objects, allowed_actions)
        models = {
            'organization': lambda x: (
                self._get_disabled_organizations(x),
                ['INFO_ORGANIZATION']
            )
        }
        for obj_type, expr_set in models.items():
            ids = result_map.get(obj_type)
            if not ids:
                continue
            objects, allowed_actions = expr_set(ids)
            result_map[obj_type] = [
                _id if _id not in [
                    r_id for (r_id,) in objects
                ] else {_id: allowed_actions} for _id in ids
            ]

    def get_hierarchy(self, item):
        model_type = item.__class__
        hierarchy_items = BaseHierarchicalController(
            self.session, self._config
        ).get_item_hierarchy('parent_id', item.parent_id, 'id', model_type)
        result = list(map(lambda x: x.id, hierarchy_items))
        result.append(item.id)
        return result

    def get_info_for_resource(self, resource):
        if not resource.get('pool_id'):
            type_name = 'organization'
            if resource.get('cloud_account_id'):
                query = self.session.query(Organization).join(
                    CloudAccount, CloudAccount.organization_id == Organization.id
                ).filter(
                    CloudAccount.id == resource['cloud_account_id'])
            else:
                query = self.session.query(Organization).filter(
                    Organization.id == resource['organization_id'])
        else:
            type_name = 'pool'
            query = self.session.query(Pool).filter(
                Pool.id == resource['pool_id'])
        return type_name, query.one_or_none()

    def on_finish(self):
        if self._mongo_client is not None:
            self._mongo_client.close()


class ContextAsyncController(BaseAsyncControllerWrapper):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.executor = tp_executor_context

    def _get_controller_class(self):
        return ContextController
