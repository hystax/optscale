import enum
from copy import deepcopy

from sqlalchemy import and_, or_
from sqlalchemy.orm import aliased

from rest_api.rest_api_server.controllers.pool import PoolController
from rest_api.rest_api_server.controllers.employee import EmployeeController
from rest_api.rest_api_server.controllers.organization_constraint import OrganizationConstraintController
from rest_api.rest_api_server.models.enums import AssignmentRequestStatuses

from rest_api.rest_api_server.models.models import (
    Organization, CloudAccount, AssignmentRequest, Employee, Pool, PoolPolicy,
    ResourceConstraint, ConstraintLimitHit)
from rest_api.rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api.rest_api_server.controllers.base import BaseController, MongoMixin


class ConfigurationRequiredTypes(enum.Enum):
    CLOUD_CONFIG = 'cloud_account_not_configured'
    ROOT_POOL = 'only_root_pool_exists'


class MyTasksController(BaseController, MongoMixin):
    def _get_model_type(self):
        return Organization

    def get_cloud_accounts(self, org_id):
        return self.session.query(CloudAccount).filter(
            CloudAccount.organization_id == org_id,
            CloudAccount.deleted.is_(False),
        ).all()

    def get_assignment_requests(self, employee_id, incoming_details=False,
                                outgoing_details=False):
        request_filters = (
            AssignmentRequest.deleted.is_(False),
            AssignmentRequest.status == AssignmentRequestStatuses.PENDING,
            or_(
                AssignmentRequest.approver_id == employee_id,
                AssignmentRequest.requester_id == employee_id
            )
        )

        if not incoming_details and not outgoing_details:
            requests = self.session.query(
                AssignmentRequest
            ).filter(*request_filters).all()

            if requests:
                incoming_count = len([r for r in requests
                                      if r.approver_id == employee_id])
                outgoing_count = len(requests) - incoming_count
            else:
                incoming_count, outgoing_count = 0, 0

            return {
                'incoming_assignment_requests': {'count': incoming_count},
                'outgoing_assignment_requests': {'count': outgoing_count},
            }
        else:
            approver = aliased(Employee, name='approver')
            requester = aliased(Employee, name='requested')
            response = self.session.query(
                AssignmentRequest,
                approver.name,
                requester.name,
                Pool.id,
                Pool.name,
                Pool.purpose,
            ).outerjoin(
                approver, approver.id == AssignmentRequest.approver_id
            ).outerjoin(
                requester, requester.id == AssignmentRequest.requester_id
            ).outerjoin(
                Pool, Pool.id == AssignmentRequest.source_pool_id
            ).filter(*request_filters).order_by(
                AssignmentRequest.created_at
            ).all()
            resource_ids = [r[0].resource_id for r in response]
            resources_map = {
                r['_id']: r for r in self.resources_collection.find(
                    {'_id': {'$in': resource_ids}, 'deleted_at': 0,
                     'cluster_id': {'$exists': False}})
            }

            incoming = []
            outgoing = []
            for request_info in response:
                (request, approver_name, requester_name, pool_id, pool_name,
                 pool_purpose) = request_info
                resource = resources_map.get(request.resource_id)
                if not resource:
                    continue
                task = {
                    'assignment_request_id': request.id,
                    'resource_id': request.resource_id,
                    'source_pool_id': request.source_pool_id,
                    'message': request.message,
                    'resource_type': resource['resource_type'],
                    'source_pool_purpose': pool_purpose,
                    'source_pool_name': pool_name,
                    'resource_name': resource.get('name'),
                    'cloud_resource_id': resource['cloud_resource_id'],
                }
                if resource.get('cluster_type_id'):
                    task['cluster_type_id'] = resource['cluster_type_id']

                if request.approver_id == employee_id:
                    task['requester_id'] = request.requester_id
                    task['requester_name'] = requester_name
                    incoming.append(task)
                else:
                    task['approver_id'] = request.approver_id
                    task['approver_name'] = approver_name
                    outgoing.append(task)

            result = {
                'incoming_assignment_requests': {'count': len(incoming)},
                'outgoing_assignment_requests': {'count': len(outgoing)},
            }
            if incoming_details:
                result['incoming_assignment_requests']['tasks'] = incoming
            if outgoing_details:
                result['outgoing_assignment_requests']['tasks'] = outgoing
            return result

    def get_exceeded_pools_and_forecasts(
            self, root_pool_id, pool_details=False, forecast_details=False):
        b_ctrl = PoolController(self.session, self._config, self.token)
        pool_limit_costs = b_ctrl.get_pool_hierarchy_costs(
            root_pool_id)

        exceeded_pools = []
        exceeded_forecasts = []
        for pool_info in pool_limit_costs.values():
            if pool_info['cost'] > pool_info['limit']:
                exceeded_pools.append(pool_info)
            elif pool_info['forecast'] > pool_info['limit']:
                exceeded_forecasts.append(pool_info)

        if pool_details or forecast_details:
            pool_ids = [b['id'] for b in exceeded_pools + exceeded_forecasts]
            pool_names = self.get_pool_details(pool_ids)

            def formatted_pool(pool):
                return {
                    'pool_id': pool['id'],
                    'pool_name': pool_names.get(pool['id']),
                    'pool_purpose': pool['purpose'],
                    'limit': pool['limit'],
                    'total_expenses': pool['cost'],
                    'forecast': pool['forecast'],
                }

            exceeded_forecasts = [formatted_pool(b)
                                  for b in exceeded_forecasts]
            exceeded_pools = [formatted_pool(b) for b in exceeded_pools]

        result = {
            'exceeded_pools': {'count': len(exceeded_pools)},
            'exceeded_pool_forecasts': {'count': len(exceeded_forecasts)}
        }
        if pool_details:
            result['exceeded_pools']['tasks'] = exceeded_pools
        if forecast_details:
            result['exceeded_pool_forecasts']['tasks'] = exceeded_forecasts
        return result

    def get_constraints_tasks(self, employee, organization,
                              violated_details=False, differ_details=False):
        pool_ctrl = PoolController(self.session, self._config,
                                   self.token)
        permission_pool_map = pool_ctrl.get_all_available_pools_by_permissions(
            employee.auth_user_id, organization.id, self.token
        )
        managed_pools = permission_pool_map['MANAGE_RESOURCES']
        pools = permission_pool_map['MANAGE_OWN_RESOURCES']
        managed_pool_ids = [pool.id for pool in managed_pools]
        pool_ids = [pool.id for pool in pools]
        pool_map = {x.id: x for x in pools + managed_pools}
        constraints_map, policy_map, resource_hit_map = dict(), dict(), dict()
        for model, dest_map, group_key in [(ResourceConstraint, constraints_map, 'resource_id'),
                                           (PoolPolicy, policy_map, 'pool_id')]:
            for constraint in self.session.query(model).filter(and_(
                    model.organization_id == organization.id,
                    model.deleted.is_(False)
            )).all():
                map_constraints = dest_map.get(getattr(constraint, group_key))
                if map_constraints is None:
                    map_constraints = {}
                    dest_map[getattr(constraint, group_key)] = map_constraints
                map_constraints[getattr(constraint, 'type').value] = constraint
        for hit in self.session.query(ConstraintLimitHit).filter(and_(
                ConstraintLimitHit.organization_id == organization.id,
                ConstraintLimitHit.deleted.is_(False)
        )).all():
            resource_hits = resource_hit_map.get(hit.resource_id)
            if resource_hits is None:
                resource_hits = {}
                resource_hit_map[hit.resource_id] = resource_hits
            existing_hit = resource_hits.get(hit.type.value)
            if existing_hit is None or existing_hit.time < hit.time:
                resource_hits[hit.type.value] = hit

        resource_to_find = set(
            resource_hit_map.keys() | constraints_map.keys())
        resource_filter = {
            '_id': {'$in': list(resource_to_find)},
            'deleted_at': 0,
            'active': True
        }
        if organization.pool_id not in managed_pool_ids:
            resource_filter['$or'] = [
                {'pool_id': {'$in': managed_pool_ids}},
                {'$and': [
                    {'employee_id': employee.id},
                    {'pool_id': {'$in': pool_ids}}
                ]}
            ]
        resource_map = {
            r['_id']: r for r in self.resources_collection.find(resource_filter)
        }

        pool_names = self.get_pool_details(pool_ids)
        differ_constraint_results = []
        employees = EmployeeController(
            self.session, self._config, self.token).list(organization.id)
        employees_map = {e['id']: e for e in employees}
        for resource_id, type_constraint_map in constraints_map.items():
            resource = resource_map.get(resource_id)
            if not resource:
                continue
            resource_pool_id = resource.get('pool_id')
            if not resource_pool_id:
                continue
            type_policy_map = policy_map.get(resource_pool_id)
            if not type_policy_map:
                continue
            for constraint_type, constraint in type_constraint_map.items():
                policy = type_policy_map.get(constraint_type)
                if not policy:
                    continue
                policy_limit = policy.limit
                if constraint_type == 'ttl':
                    policy_limit = policy_limit * 3600 + resource.get(
                        'first_seen', resource.get('created_at'))
                if constraint.limit == policy_limit:
                    continue
                diff_constraint = constraint.to_dict()
                pool_policy_dict = policy.to_dict()
                pool_policy_dict['limit'] = policy_limit
                pool_name = pool_names.get(resource_pool_id)
                pool_policy_dict['pool_name'] = pool_name
                diff_constraint['resource_name'] = resource.get('name')
                diff_constraint['pool_purpose'] = pool_map.get(
                    resource_pool_id).purpose if pool_map.get(
                    resource_pool_id) else None
                diff_constraint[
                    'cloud_resource_id'] = resource['cloud_resource_id']
                diff_constraint['resource_type'] = resource['resource_type']
                diff_constraint['policy'] = pool_policy_dict
                diff_constraint['owner_id'] = employees_map.get(
                    resource.get('employee_id'), {}).get('id')
                diff_constraint['owner_name'] = employees_map.get(
                    resource.get('employee_id'), {}).get('name')
                diff_constraint['pool_id'] = resource_pool_id
                diff_constraint['pool_name'] = pool_name
                differ_constraint_results.append(diff_constraint)
        differ_tasks = {'count': len(differ_constraint_results)}
        if differ_details:
            differ_tasks.update({'tasks': differ_constraint_results})

        violated_constraints = []
        for resource_id, hits in resource_hit_map.items():
            resource = resource_map.get(resource_id)
            if not resource:
                continue
            for constraint_type, limit_hit in hits.items():
                pool_id = limit_hit.pool_id
                limit_hit_dict = limit_hit.to_dict()
                limit_hit_dict['resource_name'] = resource.get('name')
                resource_pool_id = resource.get('pool_id')
                limit_hit_dict['pool_id'] = resource_pool_id
                limit_hit_dict['pool_name'] = pool_names.get(resource_pool_id)
                limit_hit_dict['pool_purpose'] = pool_map.get(
                    resource_pool_id).purpose if pool_map.get(
                    resource_pool_id) else None
                limit_hit_dict[
                    'cloud_resource_id'] = resource['cloud_resource_id']
                limit_hit_dict['resource_type'] = resource['resource_type']
                limit_hit_dict['owner_id'] = employees_map.get(
                    resource.get('employee_id'), {}).get('id')
                limit_hit_dict['owner_name'] = employees_map.get(
                    resource.get('employee_id'), {}).get('name')
                constraint = constraints_map.get(
                    resource_id, {}).get(constraint_type)
                limit_val = limit_hit.ttl_value or limit_hit.expense_value
                if pool_id and constraint:
                    continue
                elif constraint and constraint.limit and constraint.limit <= limit_val:
                    violated_constraints.append(limit_hit_dict)
                elif not constraint and pool_id:
                    policy = policy_map.get(pool_id, {}).get(constraint_type)
                    if policy and policy.active and policy.limit and policy.limit <= limit_val:
                        violated_constraints.append(limit_hit_dict)
        violated_tasks = {'count': len(violated_constraints)}
        if violated_details:
            violated_tasks.update({'tasks': violated_constraints})

        return {
            'violated_constraints': violated_tasks,
            'differ_constraints': differ_tasks
        }

    def get_org_constraints_tasks(self, organization_id, details=True):
        tasks = []
        count = 0
        constr_ctrl = OrganizationConstraintController(
            self.session, self._config, self.token)
        constraints = constr_ctrl.list(organization_id=organization_id)
        for c in constraints:
            hits = constr_ctrl.get_constraint_limit_hits([c.id])
            if hits:
                count += 1
                if details:
                    c_dict = c.to_dict()
                    last_hit = max(hits, key=lambda x: x.created_at)
                    task = last_hit.to_dict()
                    for f in ['name', 'type', 'last_run', 'definition',
                              'filters']:
                        task[f] = c_dict[f]
                    tasks.append(task)
        result = {'violated_organization_constraints': {'count': count}}
        if details:
            result['violated_organization_constraints']['tasks'] = tasks
        return result

    def get_tasks(self, user_id, org, types):

        employee_ctrl = EmployeeController(
            self.session, self._config, self.token)
        employee = employee_ctrl.get_employee_by_user_and_organization(
            user_id, organization_id=org.id)

        result = {}

        incoming_details = 'incoming_assignment_requests' in types
        outgoing_details = 'outgoing_assignment_requests' in types
        result.update(self.get_assignment_requests(
            employee.id,
            incoming_details=incoming_details,
            outgoing_details=outgoing_details,
        ))

        pool_details = 'exceeded_pools' in types
        forecast_details = 'exceeded_pool_forecasts' in types
        result.update(self.get_exceeded_pools_and_forecasts(
            org.pool_id, pool_details, forecast_details))

        violated_details = 'violated_constraints' in types
        differ_details = 'differ_constraints' in types
        result.update(self.get_constraints_tasks(
            employee, org, violated_details=violated_details,
            differ_details=differ_details))

        org_constraints_details = 'violated_organization_constraints' in types
        result.update(self.get_org_constraints_tasks(
            org.id, details=org_constraints_details))

        for k, v in deepcopy(result).items():
            if not v['count']:
                del result[k]

        return result

    def get_pool_details(self, pool_ids):
        response = self.session.query(
            Pool.id,
            Pool.name
        ).filter(
            Pool.id.in_(pool_ids)
        ).all()
        pool_names = {pool_id: pool_name
                      for pool_id, pool_name in response}
        return pool_names


class MyTasksAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return MyTasksController
