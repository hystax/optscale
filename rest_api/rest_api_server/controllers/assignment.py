import logging
from datetime import datetime

from requests import HTTPError
from sqlalchemy.sql import and_
from collections import defaultdict
from rest_api.rest_api_server.controllers.base import BaseController, MongoMixin
from rest_api.rest_api_server.controllers.pool import PoolController
from rest_api.rest_api_server.controllers.cloud_resource import CloudResourceController
from rest_api.rest_api_server.controllers.employee import EmployeeController
from rest_api.rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from tools.optscale_exceptions.common_exc import (
    WrongArgumentsException, ForbiddenException, NotFoundException,
    FailedDependency)
from rest_api.rest_api_server.controllers.organization import OrganizationController
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.models.enums import AssignmentRequestStatuses
from rest_api.rest_api_server.models.models import (
    CloudAccount, Pool, Employee, AssignmentRequest)
from rest_api.rest_api_server.utils import (
    check_string_attribute, raise_not_provided_exception,
    raise_does_not_exist_exception, check_int_attribute)

LOG = logging.getLogger(__name__)


class AssignmentController(BaseController, MongoMixin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._employee_ctrl = None
        self._resource_ctrl = None
        self._pool_ctrl = None
        self._organization_ctrl = None

    @property
    def pool_ctrl(self):
        if not self._pool_ctrl:
            self._pool_ctrl = PoolController(
                self.session, self._config, self.token
            )
        return self._pool_ctrl

    @property
    def employee_ctrl(self):
        if not self._employee_ctrl:
            self._employee_ctrl = EmployeeController(
                self.session, self._config, self.token
            )
        return self._employee_ctrl

    @property
    def resource_ctrl(self):
        if not self._resource_ctrl:
            self._resource_ctrl = CloudResourceController(
                self.session, self._config, self.token
            )
        return self._resource_ctrl

    @property
    def organization_ctrl(self):
        if not self._organization_ctrl:
            self._organization_ctrl = OrganizationController(
                self.session, self._config, self.token
            )
        return self._organization_ctrl

    @staticmethod
    def _validate_parameters(**params):
        allowed_parameters = ['resource_id', 'pool_id', 'owner_id']
        for param in allowed_parameters:
            value = params.get(param)
            if value is not None:
                check_string_attribute(param, value)
        created_at = params.get('created_at')
        if created_at is not None:
            check_int_attribute('created_at', created_at)
        allowed_parameters.append('created_at')
        unexpected_params = [
            p for p in params.keys() if p not in allowed_parameters]
        if unexpected_params:
            raise WrongArgumentsException(Err.OE0212, [unexpected_params])

    def get_active_requests(self, res_ids):
        res = self.session.query(
            AssignmentRequest
        ).filter(
            and_(
                AssignmentRequest.resource_id.in_(res_ids),
                AssignmentRequest.deleted.is_(False)
            )
        ).all()
        return {request.resource_id: request for request in res}

    def invalidate_requests(self, res_ids):
        now_ts = int(datetime.utcnow().timestamp())
        resource_request_map = self.get_active_requests(res_ids)
        requests = list(resource_request_map.values())
        for request in requests:
            request.status = AssignmentRequestStatuses.CANCELED
            request.deleted_at = now_ts
            # TODO add notifications if current user not a requester
        return requests

    def _prepare_assign_data(self, employee, **kwargs):
        resource_id = kwargs.get('resource_id')
        if not resource_id:
            raise_not_provided_exception('resource_id')
        resource = None
        try:
            resource = self.resource_ctrl.get(resource_id)
        except NotFoundException:
            raise_does_not_exist_exception('resource_id', resource_id)
        if resource.get('cluster_id'):
            raise FailedDependency(Err.OE0464, [resource_id])
        owner_id = kwargs.get('owner_id')
        if owner_id:
            owner = self.employee_ctrl.get(owner_id)
            if not owner:
                raise_does_not_exist_exception('owner_id', owner_id)
        else:
            owner = employee
        pool_id = kwargs.get('pool_id')
        if not pool_id:
            raise_not_provided_exception('pool_id')
        pool = self.pool_ctrl.get(pool_id)
        if not pool:
            raise_does_not_exist_exception('pool_id', pool_id)
        return resource, pool, owner

    def get_assignments(self, user_id, organization_id):
        employee = self.employee_ctrl.get_employee_by_user_and_organization(
            user_id, organization_id=organization_id)
        return self.list(employee_id=employee.id)

    def validate_resource(self, resource, current_employee, token):
        if resource.get('employee_id') == current_employee.id:
            # the resource is mine
            return True
        else:
            # resource is not mine
            # check that we can manage this resource
            return self._authorize_action_for_pool(
                action="MANAGE_RESOURCES",
                pool_id=resource.get('pool_id'),
                token=token)

    def _authorize_another_user(self, action, pool_id, user_id):
        code, response = self.auth_client.authorize_user_list(
            users=[user_id], actions=[action],
            scope_type="pool", scope_id=pool_id)
        if code != 200:
            return False
        else:
            return action in response[user_id]

    def _authorize_user_list(self, action, pool_id, users):
        authorized, restricted = [], []
        code, response = self.auth_client.authorize_user_list(
            users=users, actions=[action],
            scope_type="pool", scope_id=pool_id)
        if code == 200:
            for user_id in users:
                if action in response[user_id]:
                    authorized.append(user_id)
                else:
                    restricted.append(user_id)
        return authorized, restricted

    def _authorize_current_user(self, action, pool_id):
        try:
            code, _ = self.auth_client.authorize(
                action=action, resource_type="pool", uuid=pool_id)
        except HTTPError as ex:
            return False
        return True

    def _authorize_action_for_pool(self, action, pool_id, token=None,
                                   user_id=None):
        if token:
            self.auth_client.token = token
        if user_id:
            return self._authorize_another_user(action, pool_id, user_id)
        else:
            return self._authorize_current_user(action, pool_id)

    def validate_pool(self, pool, current_employee, owner, token=None):
        if owner.id == current_employee.id:
            action = "MANAGE_OWN_RESOURCES"
        else:
            action = "MANAGE_RESOURCES"
        return self._authorize_action_for_pool(action=action,
                                               pool_id=pool.id,
                                               token=token)

    def validate_owner(self, owner, pool, token=None):
        action = "MANAGE_OWN_RESOURCES"
        return self._authorize_action_for_pool(
            action=action, pool_id=pool.id, user_id=owner.auth_user_id,
            token=token)

    def validate_assignment(self, resource, pool, current_employee, owner,
                            token=None, by_request=False):
        if by_request or self.validate_resource(resource, current_employee,
                                                token=token):
            if self.validate_pool(pool, current_employee, owner,
                                  token=token):
                if self.validate_owner(owner, pool, token=token):
                    return
                else:
                    raise ForbiddenException(Err.OE0379, [owner.name])
            else:
                raise ForbiddenException(Err.OE0380, [])
        else:
            raise ForbiddenException(Err.OE0381,
                                     [resource['cloud_resource_id']])

    def create_assignment(self, user_id, organization_id, token,
                          by_request=False, **kwargs):
        self._validate_parameters(**kwargs)
        employee = self.employee_ctrl.get_employee_by_user_and_organization(
            user_id, organization_id=organization_id)
        assign_data = self._prepare_assign_data(employee, **kwargs)
        resource, pool, owner = assign_data
        self.validate_assignment(resource, pool, employee, owner,
                                 token=token, by_request=by_request)
        if not by_request:
            requests = self.invalidate_requests([resource['id']])
            if requests:
                self.session.bulk_save_objects(requests)
                self.session.commit()
        assignment_info = dict(
            resource_id=resource['id'],
            pool_id=pool.id,
            owner_id=owner.id,
        )
        assignment = self.create(**assignment_info)
        self.publish_bulk_assignment_activity([assignment_info])
        return assignment

    def create(self, **kwargs):
        for k in ['resource_id', 'pool_id', 'owner_id']:
            if k not in kwargs:
                raise WrongArgumentsException(Err.OE0216, [k])
        upd = self.resources_collection.update_many(
            filter={
                '$or': [
                    {'_id': kwargs['resource_id']},
                    {'cluster_id': kwargs['resource_id']}
                ],
                'deleted_at': 0
            },
            update={'$set': {
                'pool_id': kwargs['pool_id'],
                'employee_id': kwargs['owner_id']
            }}
        )
        if not upd.matched_count:
            raise NotFoundException(
                Err.OE0002, ['Resource', kwargs['resource_id']])
        return kwargs

    def list(self, **kwargs):
        filters = [{k: v} for k, v in kwargs.items()]
        filters.append({'cluster_id': {'$exists': False}})
        pipeline = [
            {
                '$match': {
                    '$and': filters
                }
            },
            {
                '$project': {
                    'pool_id': '$pool_id',
                    'resource_id': '$_id',
                    'owner_id': '$employee_id',
                    '_id': 0,
                }
            }
        ]
        assignments = self.resources_collection.aggregate(pipeline)
        return list(assignments)

    def check_resource_permissions(self, resources, token):
        cache = {}
        manageable_resources = []
        restricted_resources = []
        for resource in resources:
            pool_id = resource.get('pool_id')
            if pool_id in cache:
                result = cache[pool_id]
            else:
                result = self._authorize_action_for_pool(
                        "MANAGE_RESOURCES",
                        pool_id,
                        token=token)
                cache[pool_id] = result
            if result:
                manageable_resources.append(resource)
            else:
                restricted_resources.append(resource)
        return manageable_resources, restricted_resources

    def split_resources(self, user_id, organization_id, token, resource_ids):
        employee = self.employee_ctrl.get_employee_by_user_and_organization(
            user_id, organization_id=organization_id)

        cloud_accs = self.session.query(CloudAccount).filter(
            and_(
                CloudAccount.organization_id == organization_id,
                CloudAccount.deleted.is_(False)
            )).all()
        cloud_acc_details_map = {ca.id: ca for ca in cloud_accs}
        resources = self.resource_ctrl.list(
            _id=resource_ids,
            cloud_account_id=list(cloud_acc_details_map.keys()),
            organization_id=organization_id, include_subresources=False)

        employee_ids = set()
        pool_ids = set()
        for rss in resources:
            employee_id = rss.get('employee_id')
            if employee_id:
                employee_ids.add(employee_id)
            pool_id = rss.get('pool_id')
            if pool_id:
                pool_ids.add(pool_id)

        owner_details_map = {}
        if employee_ids:
            employees = self.session.query(Employee).filter(
                and_(
                    Employee.deleted.is_(False),
                    Employee.id.in_(list(employee_ids))
                )).all()
            for emp in employees:
                owner_details_map[emp.id] = emp

        pool_details_map = self.get_pools_details_map(pool_ids)

        user_own_resources = []
        manageable_resources = []
        restricted_resources = []
        others = []
        for resource in resources:
            if resource.get('employee_id') == employee.id:
                user_own_resources.append(resource)
            else:
                others.append(resource)
        if others:
            result = self.check_resource_permissions(others, token)
            manageable, restricted = result
            manageable_resources = manageable
            restricted_resources = restricted
        res_ids = [resource['id'] for resource in
                   user_own_resources + manageable_resources]
        resource_request_map = self.get_active_requests(res_ids)
        return {
            "owned": self.add_resource_info(
                user_own_resources, pool_details_map,
                owner_details_map, cloud_acc_details_map, resource_request_map),
            "managed": self.add_resource_info(
                manageable_resources, pool_details_map,
                owner_details_map, cloud_acc_details_map, resource_request_map),
            "restricted": self.add_resource_info(
                restricted_resources, pool_details_map,
                owner_details_map, cloud_acc_details_map, resource_request_map)
        }

    @staticmethod
    def add_resource_info(resources, pool_details_map, owner_map, cc_map,
                          res_req_map):
        result = []
        for res in resources:
            base = res
            if res.get('pool_id'):
                pool = pool_details_map[res['pool_id']]
                base['pool_name'] = pool['name']
                base['pool_purpose'] = pool['purpose']
            else:
                base['pool_name'] = None
                base['pool_purpose'] = None
            if res.get('cloud_account_id'):
                base['cloud_account_name'] = cc_map[
                    res['cloud_account_id']].name
                base['cloud_type'] = cc_map[
                    res['cloud_account_id']].type.value
            else:
                base['cloud_account_name'] = None
                base['cloud_type'] = None
            if res.get('employee_id'):
                base['owner_name'] = owner_map[res['employee_id']].name
            else:
                base['owner_name'] = None
            base['resource_id'] = base.pop('id')
            base.pop('deleted_at')
            base['has_active_transfer'] = base['resource_id'] in res_req_map
            result.append(base)
        return result

    def get_pools_details_map(self, pool_ids):
        result = self.session.query(
            Pool.id, Pool.name, Pool.purpose
        ).filter(
            Pool.deleted.is_(False),
            Pool.id.in_(pool_ids)
        ).all()
        pool_details_map = {}
        for pool_id, pool_name, pool_purpose in result:
            pool_details_map[pool_id] = {
                'name': pool_name,
                'purpose': pool_purpose,
            }
        return pool_details_map

    def get_employees_by_permission_in_pool(
            self, user_id, pool_id, exclude_myself=False):
        pool = self.session.query(
            Pool
        ).filter(
            Pool.deleted.is_(False),
            Pool.id == pool_id
        ).scalar()
        if not pool:
            raise NotFoundException(
                Err.OE0002, [Pool.__name__, pool_id])
        org = pool.organization
        cur_employee = self.employee_ctrl.get_employee_by_user_and_organization(
            user_id, organization_id=org.id)
        employees = self.employee_ctrl._list(org.id)
        user_ids = [employee.auth_user_id for employee in employees]
        authorized, _ = self._authorize_user_list('MANAGE_OWN_RESOURCES',
                                                  pool.id,
                                                  user_ids)
        result = filter(lambda x: x.auth_user_id in authorized, employees)
        if exclude_myself:
            result = filter(lambda x: x.id != cur_employee.id, result)
        return result

    def get_assignment_targets_info(self, budet_ids, owner_ids):
        pools = self.session.query(Pool).filter(
            Pool.id.in_(budet_ids)
        ).all()
        employees = self.session.query(Employee).filter(
            Employee.id.in_(owner_ids)
        ).all()
        return {
            'pools': {b.id: b for b in pools},
            'employees': {e.id: e for e in employees}
        }

    def publish_bulk_assignment_activity(self, assignments_bulk):
        assignments_map = defaultdict(int)
        pool_ids, employee_ids = set(), set()
        for a in assignments_bulk:
            k = (a['pool_id'], a['owner_id'])
            pool_ids.add(a['pool_id'])
            employee_ids.add(a['owner_id'])
            assignments_map[k] += 1
        targets_info = self.get_assignment_targets_info(
            pool_ids, employee_ids)

        for k, res_cnt in assignments_map.items():
            pool_id, employee_id = k
            pool = targets_info['pools'].get(pool_id)
            owner = targets_info['employees'].get(employee_id)
            meta = dict(
                total_count=res_cnt,
                employee_name=owner.name,
                employee_id=owner.id,
                object_name=pool.name
            )
            self.publish_activities_task(
                pool.organization_id, pool.id, 'pool', 'resource_assigned',
                meta, 'pool.resource_assigned', add_token=True)


class AssignmentAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return AssignmentController
