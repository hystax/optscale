import logging
from pymongo import UpdateMany
from rest_api_server.controllers.assignment import AssignmentController
from rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from optscale_exceptions.common_exc import (WrongArgumentsException,
                                            ForbiddenException)
from rest_api_server.exceptions import Err
from rest_api_server.utils import (check_string_attribute,
                                   raise_not_provided_exception,
                                   raise_does_not_exist_exception,
                                   check_list_attribute, check_int_attribute)

LOG = logging.getLogger(__name__)


class AssignmentBulkController(AssignmentController):

    @property
    def allowed_parameters(self):
        return ['resource_ids', 'pool_id', 'owner_id']

    def _validate_parameters(self, **values):
        for param in self.allowed_parameters:
            value = values.get(param)
            if param == 'resource_ids':
                check_list_attribute(param, value)
                for item in value:
                    check_string_attribute('id', item)
            elif value is not None:
                check_string_attribute(param, value)
        created_at = values.get('created_at')
        if created_at is not None:
            check_int_attribute('created_at', created_at)
        unexpected_params = [
            p for p in values.keys() if p not in
            self.allowed_parameters + ['created_at']]
        if unexpected_params:
            raise WrongArgumentsException(Err.OE0212, [unexpected_params])

    def validate_common_params(self, pool, current_employee, owner,
                               token=None):
        if self.validate_pool(pool, current_employee, owner,
                              token=token):
            if self.validate_owner(owner, pool, token=token):
                return
            else:
                raise ForbiddenException(Err.OE0379, [owner.name])
        else:
            raise ForbiddenException(Err.OE0380, [])

    def _prepare_assign_common_data(self, employee, **kwargs):
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
        if employee.organization_id != pool.organization_id:
            raise WrongArgumentsException(Err.OE0454, ['Pool', pool.id])
        if employee.organization_id != owner.organization_id:
            raise WrongArgumentsException(Err.OE0454, ['Owner', owner.id])
        return pool, owner

    def prepare_resources(self, current_employee, token, by_request=False,
                          **kwargs):
        succeeded = []
        failed = []
        resource_ids = kwargs.get('resource_ids')
        if not resource_ids:
            raise_not_provided_exception('resource_ids')
        resources = self.resource_ctrl.list(_id=resource_ids)
        valid_resources = {res['id']: res for res in resources}
        non_free_resources = []
        for res_id in resource_ids:
            if res_id not in valid_resources:
                failed.append({"id": res_id,
                               "message": "Resource %s not found" % res_id,
                               "code": Err.OE0002.name})
            else:
                resource = valid_resources[res_id]
                if resource.get('cluster_id'):
                    failed.append(
                        {"id": res_id,
                         "message": "Can't create assignment request for "
                                    "cluster dependent resource",
                         "code": Err.OE0464.name})
                elif resource.get('employee_id') == current_employee.id:
                    succeeded.append(resource)
                else:
                    non_free_resources.append(resource)
        if non_free_resources:
            result = self.check_resource_permissions(non_free_resources, token)
            allowed, denied = result
            succeeded.extend(allowed)
            for resource in denied:
                msg = ("Current user doesn't have enough permissions "
                       "for target resource")
                failed.append({
                    "id": resource['cloud_resource_id'],
                    "message": msg,
                    "code": Err.OE0381.name})
        return succeeded, failed

    def _bulk_create(self, assignments_bulk):
        if not assignments_bulk:
            return
        self.resources_collection.bulk_write([
            UpdateMany(
                filter={
                    '$or': [
                        {'_id': r['resource_id']},
                        {'cluster_id': r['resource_id']}
                    ],
                    'deleted_at': 0
                },
                update={'$set': {
                    'pool_id': r['pool_id'],
                    'employee_id': r['owner_id']
                }}
            ) for r in assignments_bulk
        ])

    def create_assignments_bulk(self, user_id, organization_id, token,
                                **kwargs):
        result = {"succeeded": [],
                  "failed": []}
        self._validate_parameters(**kwargs)
        employee = self.employee_ctrl.get_employee_by_user_and_organization(
            user_id, organization_id=organization_id)
        pool, owner = self._prepare_assign_common_data(employee, **kwargs)
        self.validate_common_params(pool, employee, owner, token)
        succeeded, failed = self.prepare_resources(employee, token, **kwargs)
        result["failed"] = failed
        assigned_resource_ids = []
        dependent_resource_ids = []
        assignments_bulk = []
        for resource in succeeded:
            assigned_resource_ids.append(resource['id'])
            assignments_bulk.append({
                'resource_id': resource['id'],
                'pool_id': pool.id,
                'owner_id': owner.id
            })
            dependent_resource_ids.extend(map(
                lambda r: r['id'], resource.get('sub_resources', [])))
        if not assignments_bulk:
            return result
        self._bulk_create(assignments_bulk)
        self.publish_bulk_assignment_activity(assignments_bulk)
        requests = self.invalidate_requests(assigned_resource_ids)
        self.session.bulk_save_objects(requests)
        self.session.commit()
        result["succeeded"] = [res['id'] for res in succeeded]
        return result


class AssignmentAsyncBulkController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return AssignmentBulkController
