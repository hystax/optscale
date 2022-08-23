import logging
from datetime import datetime, time, timedelta
from collections import defaultdict

from sqlalchemy.sql import and_
from rest_api_server.exceptions import Err
from optscale_exceptions.common_exc import (
    ConflictException, NotFoundException, WrongArgumentsException,
    FailedDependency)
from rest_api_server.models.enums import ConstraintTypes
from rest_api_server.models.models import (
    ResourceConstraint, CloudAccount, Organization, Pool, Employee)
from rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api_server.controllers.base import MongoMixin
from rest_api_server.controllers.constraint_base import ConstraintBaseController
from rest_api_server.controllers.cloud_resource import CloudResourceController
from rest_api_server.utils import check_int_attribute

LOG = logging.getLogger(__name__)


class ResourceConstraintController(ConstraintBaseController, MongoMixin):
    def _get_model_type(self):
        return ResourceConstraint

    def get_relation_field(self):
        return 'resource_id'

    def get_model_name(self):
        return 'Resource'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cloud_resource_ctrl = None

    @property
    def cloud_resource_ctrl(self):
        if self._cloud_resource_ctrl is None:
            self._cloud_resource_ctrl = CloudResourceController(
                self.session, self._config, self.token)
        return self._cloud_resource_ctrl

    def get_resource_owner(self, resource_id):
        auth_user_id = self.cloud_resource_ctrl.get_owner(resource_id)
        return auth_user_id

    def create(self, **kwargs):
        constraint = super().create(**kwargs)
        self.publish_constraint_activity(constraint, 'constraint_created')
        return constraint

    def delete(self, item_id):
        constraint = super().delete(item_id)
        self.publish_constraint_activity(constraint, 'constraint_deleted')
        return constraint

    def edit(self, item_id, **kwargs):
        constraint_dict = self.get(item_id).to_dict()
        updates = {
            k: v for k, v in kwargs.items()
            if constraint_dict.get(k) != kwargs[k]
        }
        constraint = super().edit(item_id, **kwargs)
        if updates:
            evt_args = dict(
                params=', '.join(
                    ['%s: %s' % (k, v) for k, v in updates.items()])
            )
            self.publish_constraint_activity(constraint, 'constraint_updated',
                                             evt_args)
        return constraint

    def publish_constraint_activity(self, constraint, action, updates=None):
        resource = next(self.resources_collection.find(
            {'_id': constraint.resource_id}).limit(1))
        if resource.get('cluster_type_id'):
            organization_id = resource['organization_id']
        else:
            organization_id = self.session.query(
                CloudAccount.organization_id
            ).filter(
                CloudAccount.id == resource['cloud_account_id']
            ).scalar()
        meta = {
            'object_name': resource.get('name'),
            'constraint_type': constraint.type.value
        }
        if updates:
            meta.update(updates)
        self.publish_activities_task(
            organization_id, resource['_id'], 'resource', action, meta,
            'resource.{action}'.format(action=action), add_token=True)

    def raise409(self, constraint_type, field_id):
        raise ConflictException(Err.OE0441, [constraint_type, field_id])

    def handle_ttl_hit(self, resource_data, constraint, now):
        if now > constraint.limit:
            return constraint.limit, now

    def check_limit(self, constraint_type, limit):
        check_int_attribute('limit', limit)
        if constraint_type == ConstraintTypes.TTL and limit != 0:
            if limit - int(datetime.utcnow().timestamp()) < 0:
                raise WrongArgumentsException(Err.OE0461, [])

    def get_entity(self, item_id):
        try:
            resource = self.cloud_resource_ctrl.get(item_id)
        except NotFoundException:
            return None

        if not resource.get('active', False):
            raise FailedDependency(Err.OE0443, [item_id])
        if resource.get('cluster_id'):
            raise FailedDependency(Err.OE0464, [item_id])
        return resource

    def get_organization_id_from_entity(self, resource):
        if resource.get('cluster_type_id'):
            return resource['organization_id']

        cloud_account_id = resource['cloud_account_id']
        cloud_account = self.session.query(CloudAccount).filter(and_(
            CloudAccount.deleted.is_(False),
            CloudAccount.id == cloud_account_id,
        )).one_or_none()
        if cloud_account is None:
            raise NotFoundException(
                Err.OE0002, [self.get_model_name(), resource['id']])
        return cloud_account.organization_id

    def get_by_ids(self, org_id, resource_ids):
        constraint_types = self.supported_constraint_types(org_id)
        return self.session.query(ResourceConstraint).filter(
            and_(
                ResourceConstraint.resource_id.in_(resource_ids),
                ResourceConstraint.deleted.is_(False),
                ResourceConstraint.limit > 0,
                ResourceConstraint.type.in_(constraint_types)
            )).all()

    def handle_resource(self, resource_data, constraint, now):
        res = super().handle_resource(resource_data, constraint, now)
        if res:
            res.pop('pool_id', None)
        return res

    def get_violations(self, org_id, resource_data_map, now):
        constraints = self.get_by_ids(org_id, list(resource_data_map.keys()))

        res = {}
        for constraint in constraints:
            resource_data = resource_data_map.get(constraint.resource_id)
            if not resource_data:
                continue
            violation = self.handle_resource(resource_data, constraint, now)
            if violation:
                res[(resource_data['resource_id'], constraint.type)] = violation
        return res


class ResourceConstraintOrganizationController(ResourceConstraintController):
    def get_relation_field(self):
        return 'organization_id'

    def get_entity(self, item_id):
        return self.session.query(Organization).filter(and_(
            Organization.id == item_id,
            Organization.deleted.is_(False)
        )).one_or_none()

    def get_resources(self, resource_ids, organization_id):
        cloud_account_ids = self.session.query(CloudAccount.id).filter(and_(
            CloudAccount.deleted.is_(False),
            CloudAccount.organization_id == organization_id
        )).all()
        cloud_account_ids = [ca[0] for ca in cloud_account_ids]
        resources = self.cloud_resource_ctrl.list(
            _id=resource_ids, organization_id=organization_id,
            cloud_account_id=cloud_account_ids, include_subresources=False)
        pool_ids, employee_ids = set(), set()
        for resource in resources:
            pool_ids.add(resource['pool_id'])
            employee_ids.add(resource['employee_id'])
        pool_map = {pool.id: pool
                    for pool in self._get_entities(Pool, list(pool_ids))}
        employee_map = {employee.id: employee
                        for employee in self._get_entities(Employee,
                                                           list(employee_ids))}
        resources_info_result = []
        resource_info_fields = ['id', 'cloud_resource_id', 'name',
                                'employee_id', 'active', 'constraint_violated']
        for resource in resources:
            pool = pool_map.get(resource.get('pool_id'))
            employee = employee_map.get(resource.get('employee_id'))
            resource_info = {'owner': {
                'id': employee.id,
                'name': employee.name
            }, 'pool': {
                'id': pool.id,
                'name': pool.name,
                'purpose': pool.purpose.value
            }}
            for field in resource_info_fields:
                if field in resource:
                    resource_info[field] = resource[field]
            resources_info_result.append(resource_info)
        return resources_info_result


class ResourceConstraintAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return ResourceConstraintController


class ResourceConstraintOrganizationAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return ResourceConstraintOrganizationController
