import datetime
import logging

from collections import defaultdict
from sqlalchemy import exists, and_
from sqlalchemy.exc import IntegrityError

from rest_api.rest_api_server.controllers.expense import (
    CloudFilteredPoolFormattedExpenseController,
    PoolFilteredPoolFormattedExpenseController,
    EmployeeFilteredPoolFormattedExpenseController,
    PoolFormattedExpenseController, ExpenseController,
    PoolExpensesExportFilteredPoolFormattedExpenseController)
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.models.enums import PoolPurposes
from rest_api.rest_api_server.models.models import (
    Pool, Organization, Employee, Checklist, CloudAccount, Rule,
    AssignmentRequest, PoolAlert, InviteAssignment, PoolPolicy,
    PoolExpensesExport, OrganizationConstraint, OrganizationLimitHit)
from rest_api.rest_api_server.controllers.base import (
    BaseController, MongoMixin, BaseHierarchicalController)
from rest_api.rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api.rest_api_server.controllers.organization_constraint import OrganizationConstraintController
from rest_api.rest_api_server.utils import (
    check_int_attribute, raise_does_not_exist_exception,
    raise_invalid_argument_exception, check_bool_attribute,
    BASE_POOL_EXPENSES_EXPORT_LINK_FORMAT as BASE_LINK_FORMAT)
from tools.optscale_exceptions.common_exc import (
    WrongArgumentsException, ForbiddenException, NotFoundException,
    ConflictException, FailedDependency)

LOG = logging.getLogger(__name__)


class PoolController(BaseController, MongoMixin):
    def _get_model_type(self):
        return Pool

    def _authorize_action_for_user(self, action, pool_id, user_id):
        self.auth_client.token = self.token
        code, response = self.auth_client.authorize_user_list(
            users=[user_id], actions=[action],
            scope_type="pool", scope_id=pool_id)
        if code != 200:
            return False
        else:
            return action in response[user_id]

    def validate_owner(self, owner, pool_id):
        action = "MANAGE_OWN_RESOURCES"
        return self._authorize_action_for_user(
            action=action, pool_id=pool_id, user_id=owner.auth_user_id)

    def _get_employee(self, empl_id):
        employee = self.session.query(
            Employee
        ).filter(
            Employee.deleted.is_(False),
            Employee.id == empl_id
        ).scalar()
        return employee

    def _define_current_empl(self, org_id):
        try:
            user_id = self.get_user_id()
            query = self.session.query(Employee).filter(
                Employee.organization_id == org_id,
                Employee.auth_user_id == user_id,
                Employee.deleted.is_(False))
            curr_empl = query.scalar()
        except Exception as exc:
            curr_empl = None
        return curr_empl

    def get_org_by_id(self, org_id):
        org = self.session.query(
            Organization
        ).filter(
            Organization.id == org_id,
            Organization.deleted.is_(False)
        ).one_or_none()
        return org

    def _validate(self, item, is_new=True, **kwargs):
        query = self.session.query(exists().where(
            and_(*(item.get_uniqueness_filter(is_new)))))
        pool_exist = query.scalar()
        if pool_exist:
            raise ConflictException(Err.OE0149, [Pool.__name__, item.name])

        parent_id = kwargs.get('parent_id')
        if parent_id:
            parent = self.get(parent_id, organization_id=item.organization_id)
            if not parent:
                raise_does_not_exist_exception(Pool.__name__, [parent_id])

        limit = kwargs.get('limit', 0 if item.limit is None else item.limit)
        deleted_at = kwargs.get(
            'deleted_at', 0 if is_new else item.deleted_at)
        if not deleted_at:
            if is_new is False:
                parent_id = item.parent_id if not parent_id else parent_id
                self.check_child_pool_sum(parent_id=parent_id,
                                          pool_value=limit, pool_id=item.id)
                for field_name in ['purpose', 'name']:
                    value = kwargs.get(field_name)
                    if not item.parent_id and value is not None:
                        raise WrongArgumentsException(
                            Err.OE0449, [field_name, 'root pool'])
            else:
                self.check_child_pool_sum(parent_id=parent_id, pool_value=limit)

        default_owner_id = kwargs.get('default_owner_id')
        if default_owner_id:
            owner = self._get_employee(default_owner_id)
            if not owner:
                raise_does_not_exist_exception(Employee.__name__,
                                               default_owner_id)
            if not is_new and not self.validate_owner(owner, item.id):
                raise ForbiddenException(Err.OE0379, [owner.name])

    def create(self, auto_extension=False, **kwargs):
        if not kwargs.get('purpose'):
            parent_id = kwargs.get('parent_id')
            kwargs['purpose'] = PoolPurposes.BUDGET if (
                parent_id) else PoolPurposes.BUSINESS_UNIT
        if not kwargs.get('default_owner_id'):
            org_id = kwargs.get('organization_id')
            curr_empl = self._define_current_empl(org_id)
            kwargs['default_owner_id'] = curr_empl.id if curr_empl else None

        self.check_create_restrictions(**kwargs)
        pool = self.model_type(**kwargs)
        if auto_extension:
            user_id = self.get_user_id()
            self.extend_parent_pools(user_id, pool, pool.limit, is_new=True)
        self._validate(pool, True, **kwargs)
        self.session.add(pool)

        LOG.info("Creating %s with parameters %s",
                 self.model_type.__name__, kwargs)
        try:
            self.session.commit()
        except IntegrityError as ex:
            self.session.rollback()
            raise WrongArgumentsException(Err.OE0003, [str(ex)])

        if pool.parent_id:
            meta = {
                'object_name': pool.name
            }
            self.publish_activities_task(
                pool.organization_id, pool.id, 'pool',
                'pool_created', meta, 'pool.pool_created', add_token=True)
        return pool

    def edit(self, item_id, auto_extension=False, **kwargs):
        check_bool_attribute('auto_extension', auto_extension)
        if auto_extension:
            user_id = kwargs.pop('user_id')
            new_limit = kwargs.get('limit')
            check_int_attribute('limit', new_limit)
            pool = self.get(item_id)
            self.extend_parent_pools(user_id, pool, new_limit)
        result = super().edit(item_id, **kwargs)
        meta = {
            'object_name': result.name,
            'params': ', '.join(['%s: %s' % (k, v) for k, v in kwargs.items()])
        }
        self.publish_activities_task(
            result.organization_id, result.id, 'pool',
            'pool_updated', meta, 'pool.pool_updated', add_token=True)
        return result

    def extend_parent_pools(self, user_id, pool, limit, is_new=False):
        organization_id = pool.organization_id
        permission_pool_map = self.get_all_available_pools_by_permissions(
            user_id, pool.organization_id, self.token,
            permissions=['MANAGE_POOLS']
        )
        managed_pool_ids = set(map(
            lambda x: x.id, permission_pool_map.get('MANAGE_POOLS', [])))
        org_pools = self.get_org_pools(organization_id)
        if is_new:
            org_pools.append(pool)
        children_pools_map = defaultdict(list)
        for p in org_pools:
            parent_id = p.parent_id
            if parent_id:
                children_pools_map[parent_id].append(p)
        pools_map = {p.id: p for p in org_pools}
        parent_id = pool.parent_id
        parent_sums = {pool.id: limit}
        while parent_id:
            parent_pool = pools_map[parent_id]
            pool_limit = 0
            for child in children_pools_map[parent_id]:
                new_limit = parent_sums.get(child.id) or child.limit
                pool_limit += new_limit
            if pool_limit > parent_pool.limit:
                if parent_id not in managed_pool_ids:
                    raise ForbiddenException(
                        Err.OE0471, [parent_pool.name, parent_id])
                parent_sums.update({parent_id: pool_limit})
            parent_id = parent_pool.parent_id
        for pool_id, new_limit in parent_sums.items():
            pools_map[pool_id].limit = new_limit

    def delete(self, item_id, allow_root_deletion=False):
        item = self.get(item_id)
        if not item:
            raise NotFoundException(Err.OE0002, [Pool.__name__, item_id])
        if item.parent_id is None and not allow_root_deletion:
            raise WrongArgumentsException(Err.OE0447, [])
        not_deleted_children_exists = self.session.query(exists().where(and_(
            self.model_type.deleted.is_(False),
            self.model_type.parent_id == item.id))
        ).scalar()
        if not_deleted_children_exists and not allow_root_deletion:
            raise FailedDependency(Err.OE0411, [Pool.__name__, item.name])
        if item.parent_id:
            parent_pool = self.get(item.parent_id)
            self.reassign_cleanup(item.id)
            invalid_owners, new_owner = self.get_reassigned_owners(item)
            _, resources_moved = self.reassign_resources(
                item.id, parent_pool.id, invalid_owners, new_owner)
            rules_redirected = self.redirect_assignment_rules(
                item.id, parent_pool.id, invalid_owners, new_owner)
            meta = {
                'object_name': item.name,
                'res_count': resources_moved,
                'new_pool_name': parent_pool.name,
                'rules_cnt': rules_redirected
            }
            self.publish_activities_task(
                item.organization_id, item.id, 'pool',
                'pool_deleted', meta, 'pool.pool_deleted', add_token=True)
            self.delete_exports_for_pool(item_id)
        OrganizationConstraintController(
            self.session, self._config, self.token).delete_constraints_with_hits(
            item.organization_id, filters={'pool_id': item_id})
        return super().delete(item_id)

    def delete_exports_for_pool(self, item_id):
        export = self.session.query(PoolExpensesExport).filter(
            PoolExpensesExport.pool_id == item_id,
            PoolExpensesExport.deleted.is_(False)
        ).one_or_none()
        if export:
            now_ts = int(datetime.datetime.utcnow().timestamp())
            export.deleted_at = now_ts
            self.session.add(export)
            self.session.commit()

    def get_reassigned_owners(self, pool):
        employees = self.session.query(Employee).filter(
            Employee.organization_id == pool.organization_id).all()
        employee_ids = []
        employee_auth_user_map = {}
        for e in employees:
            employee_ids.append(e.id)
            if not e.deleted:
                employee_auth_user_map[e.id] = e.auth_user_id
        user_action_pool_map = self.get_bulk_allowed_action_pools_map(
            list(employee_auth_user_map.values()),
            ['MANAGE_RESOURCES', 'MANAGE_OWN_RESOURCES'])
        invalid_owners = []
        for employee_id in employee_ids:
            auth_user_id = employee_auth_user_map.get(employee_id)
            actions = user_action_pool_map.get(auth_user_id)
            if not auth_user_id or not actions:
                invalid_owners.append(employee_id)
                continue
            allowed_pools = set()
            for pools in actions.values():
                allowed_pools.update(pools)
            if pool.parent_id not in allowed_pools:
                invalid_owners.append(employee_id)
        parent_default_owner_id = None
        if invalid_owners:
            parent = self.get(pool.parent_id)
            parent_default_owner_id = parent.default_owner_id
            if not parent_default_owner_id:
                resources_with_invalid_owner = self.resources_collection.find({
                    'pool_id': pool.id,
                    'employee_id': {'$in': invalid_owners}
                }).limit(1)
                for _ in resources_with_invalid_owner:
                    raise FailedDependency(Err.OE0459, [parent.id])
        return invalid_owners, parent_default_owner_id

    def reassign_resources(self, old_pool_id, new_pool_id, old_owner_ids,
                           new_owner_id):
        owners_changed, resources_moved = 0, 0
        if old_owner_ids:
            reassign_result = self.resources_collection.update_many(
                filter={
                    'pool_id': old_pool_id,
                    'employee_id': {'$in': old_owner_ids},
                },
                update={'$set': {'employee_id': new_owner_id}}
            )
            owners_changed = reassign_result.modified_count
        change_pool_result = self.resources_collection.update_many(
            filter={'pool_id': old_pool_id},
            update={'$set': {
                'pool_id': new_pool_id
            }}
        )
        resources_moved = change_pool_result.modified_count
        return owners_changed, resources_moved

    def get_organization_pools(self, org_id):
        pools = self.session.query(
            Pool
        ).filter(
            Pool.organization_id == org_id,
            Pool.deleted.is_(False)
        ).all()
        return list(map(lambda x: x.to_dict(), pools))

    def redirect_assignment_rules(self, old_pool_id, new_pool_id,
                                  old_owner_ids, new_owner_id):
        if old_owner_ids:
            rules = self.session.query(Rule).filter(and_(
                Rule.pool_id == old_pool_id,
                Rule.owner_id.in_(old_owner_ids),
                Rule.deleted.is_(False)
            )).all()
            for rule in rules:
                rule.owner_id = new_owner_id
        rules = self.session.query(Rule).filter(and_(
            Rule.pool_id == old_pool_id,
            Rule.deleted.is_(False)
        )).all()
        for rule in rules:
            rule.pool_id = new_pool_id
        self.session.commit()
        return len(rules)

    def reassign_cleanup(self, pool_id):
        for model, pool_field in [
            (AssignmentRequest, AssignmentRequest.source_pool_id),
            (PoolAlert, PoolAlert.pool_id),
            (InviteAssignment, InviteAssignment.scope_id)
        ]:
            objects = self.session.query(model).filter(
                and_(
                    pool_field == pool_id,
                    model.deleted.is_(False)
                )
            )
            for obj in objects:
                obj.deleted_at = int(datetime.datetime.utcnow().timestamp())
        self.session.commit()

    def get_sub_pools(self, pool_id, show_details=False):
        pools = BaseHierarchicalController(
            self.session, self._config, self.token
        ).get_item_hierarchy('id', pool_id, 'parent_id', Pool)
        sub_pools = []
        for pool in pools:
            pool_dict = pool.to_dict()
            if show_details:
                pool_dict.update({
                    'policies': [policy.to_dict() for policy in pool.policies
                                 if not policy.deleted]
                })
            sub_pools.append(pool_dict)
        return sub_pools

    def get_details(self, pool_dict, forecast=False, show_children=False,
                    show_details=False):
        root_pool_id = pool_dict['id']
        children = self.get_sub_pools(root_pool_id, show_details)
        pool_list = [pool_dict] + children
        pool_ids = [pool['id'] for pool in pool_list]
        if not show_children:
            children = []
            pool_list = [pool_dict]
        if show_details:
            pool_limit_costs = self.get_pool_hierarchy_costs(
                root_pool_id, forecast)
            for pool in pool_list:
                pool['cost'] = pool_limit_costs[pool['id']]['cost']
                pool['forecast'] = pool_limit_costs[pool['id']]['forecast']
                exports = self.get_pool_exports([pool['id']])
                if exports:
                    pool['expenses_export_link'] = BASE_LINK_FORMAT.format(
                        self._config.public_ip(), exports[0].id)
            saving, cnt = self.get_pool_savings(
                pool_dict['organization_id'], pool_ids)
            pool_dict.update({
                'saving': saving,
                'total_recommendations': cnt
            })
        return children, pool_dict

    def get_organization_forecast(self, cost, month_cost, organization_id):
        cloud_accounts = self.session.query(CloudAccount).filter(
            CloudAccount.organization_id == organization_id,
            CloudAccount.deleted.is_(False),
        ).all()
        cloud_acc_ids = list(map(lambda x: x.id, cloud_accounts))
        if cloud_acc_ids:
            exp_ctrl = ExpenseController(self._config)
            first_expenses = exp_ctrl.get_first_expenses_for_forecast(
                'cloud_account_id', cloud_acc_ids)
            return exp_ctrl.get_monthly_forecast(
                cost, month_cost,
                min(first_expenses.values()) if first_expenses else None)
        else:
            return 0

    def get_savings(self, organization_id, filter_field, filter_ids, group_field):
        last_completed = self.session.query(
            Checklist.last_completed
        ).filter(and_(
            Checklist.deleted.is_(False),
            Checklist.organization_id == organization_id,
        )).scalar()
        pipeline = [
            {
                '$match': {
                    '$and': [
                        {filter_field: {'$in': filter_ids}},
                        {'recommendations.run_timestamp': {
                            '$gte': last_completed}}
                    ]
                }
            },
            {
                '$unwind': '$recommendations.modules'
            },
            {
                '$group': {
                    '_id': '$%s' % group_field,
                    'saving': {
                        '$sum': '$recommendations.modules.saving'
                    },
                    'count': {'$sum': 1}
                }
            }
        ]
        res = list(self.resources_collection.aggregate(pipeline))
        saving, cnt = 0, 0
        if res:
            saving = sum([r.get('saving', 0) for r in res])
            cnt = sum([r.get('count', 0) for r in res])
        return saving, cnt

    def get_pool_savings(self, organization_id, pool_ids):
        return self.get_savings(organization_id, 'pool_id',
                                pool_ids, 'pool_id')

    def get_pool_hierarchy_costs(self, root_pool_id, forecast=True):
        pool_objects = BaseHierarchicalController(
            self.session, self._config, self.token
        ).get_item_hierarchy('id', root_pool_id, 'parent_id', Pool,
                             include_item=True)

        pool_map = {}
        for pool in pool_objects:
            pool_map[pool.id] = pool.to_dict()
            pool_map[pool.id]['children'] = [b.id for b in pool_objects
                                             if b.parent_id == pool.id]

        month_expenses = self.get_pool_expenses(
            list(pool_map.keys()), forecast=forecast)

        def calculate_costs(pool_id):
            self_cost = month_expenses.get(pool_id, {}).get('cost', 0)
            self_forecast = month_expenses.get(pool_id, {}).get('forecast', 0)
            children_costs = list(calculate_costs(b_id) for b_id in pool_map[
                pool_id]['children'])
            children_cost = sum(x[0] for x in children_costs)
            children_forecast = sum(x[1] for x in children_costs)
            pool_map[pool_id]['cost'] = self_cost + children_cost
            pool_map[pool_id]['forecast'] = self_forecast + children_forecast
            return pool_map[pool_id]['cost'], pool_map[pool_id]['forecast']

        calculate_costs(root_pool_id)
        return pool_map

    def get_pool_expenses(self, pool_ids, period_day=None, end_date=None,
                          forecast=True):
        expense_ctrl = ExpenseController(self._config)
        today = datetime.datetime.utcnow()
        month_start = today.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0)
        if not end_date:
            end_date = today
        if not period_day:
            period_day = month_start
        last_month_start = (month_start - datetime.timedelta(days=1)).replace(
            day=1)
        if forecast:
            start_date = min(last_month_start, period_day)
        else:
            start_date = period_day

        expenses = expense_ctrl.get_expenses_for_pools(
            start_date, end_date, pool_ids)

        first_expenses = {}
        result = {}
        for expense in expenses:
            date = expense['_id']['date']
            pool_id = expense['_id']['pool_id']
            if not result.get(pool_id):
                result[pool_id] = {'cost': 0, 'month_cost': 0,
                                   'forecast_cost': 0}
            if date >= period_day:
                result[pool_id]['cost'] += expense['cost']
            if date >= last_month_start:
                result[pool_id]['forecast_cost'] += expense['cost']
            if date >= month_start:
                result[pool_id]['month_cost'] += expense['cost']
            if pool_id not in first_expenses or first_expenses[pool_id] > date:
                first_expenses[pool_id] = date
        if forecast:
            for pool_id, expense in result.items():
                expense['forecast'] = expense_ctrl.get_monthly_forecast(
                    expense['forecast_cost'], expense['month_cost'],
                    first_expenses.get(pool_id))
        return result

    def check_child_pool_sum(self, pool_value, parent_id=None, pool_id=None):
        if parent_id or pool_id:
            check_int_attribute('limit', pool_value)
            root_pool_id = parent_id if parent_id else pool_id
            pool_objects = BaseHierarchicalController(
                self.session, self._config, self.token
            ).get_item_hierarchy('id', root_pool_id, 'parent_id', Pool,
                                 include_item=True)
            if pool_objects:
                stats_map = {}
                for pool_object in pool_objects:
                    stats_map[pool_object.id] = {}
                    stats_map[pool_object.id]['limit'] = pool_object.limit
                    stats_map[pool_object.id]['children_total_sum'] = sum(
                        b.limit for b in pool_objects
                        if b.parent_id == pool_object.id and b.id != pool_id)
                default_stats = {'limit': 0, 'children_total_sum': 0}
                if parent_id:
                    parent_stats = stats_map.get(parent_id, default_stats)
                    children_sum = parent_stats['children_total_sum'] + pool_value
                    if children_sum > parent_stats['limit']:
                        raise WrongArgumentsException(Err.OE0407, [])

                if pool_id:
                    pool_stats = stats_map.get(pool_id, default_stats)
                    if pool_stats['children_total_sum'] > pool_value:
                        raise WrongArgumentsException(
                            Err.OE0414, [pool_value, pool_id])

    @staticmethod
    def _get_full_path(pool, full_map_of_pools):
        result = None

        curr = full_map_of_pools[pool.id]
        if curr['parent_id'] is None:
            return pool.name
        while curr['parent_id'] is not None:
            if result:
                result = "%s->%s" % (curr['name'], result)
            else:
                result = curr['name']
            curr = full_map_of_pools[curr['parent_id']]
        return result

    @staticmethod
    def filter_pools_by_assignments(source_pools, target_ids):
        result_ids = set()
        for _ in range(len(source_pools)):
            modified = False
            for pool in source_pools:
                if pool.id in result_ids:
                    continue
                elif pool.parent_id in result_ids or (
                        pool.id in target_ids) or (
                        pool.parent_id in target_ids):
                    result_ids.add(pool.id)
                    modified = True
            if not modified:
                break
        return [pool for pool in source_pools
                if pool.id in result_ids]

    def _get_employee_by_user_and_organization(self, user_id,
                                               organization_id):
        employees = self.session.query(
            Employee
        ).filter(
            Employee.organization_id == organization_id,
            Employee.deleted.is_(False),
            Employee.auth_user_id == user_id
        ).all()
        employees_count = len(employees)
        if employees_count == 0:
            raise ForbiddenException(Err.OE0378, [])
        else:
            return employees[0]

    def get_org_pools(self, organization_id):
        pools = self.session.query(
            Pool
        ).filter(
            Pool.deleted.is_(False),
            Pool.organization_id == organization_id
        ).all()
        if not pools:
            raise NotFoundException(
                Err.OE0002, [Organization.__name__, organization_id])
        return pools

    def get_all_available_pools_by_permissions(
            self, user_id, org_id, token, pools=None, permissions=None):
        if permissions is None:
            permissions = ["MANAGE_OWN_RESOURCES", "MANAGE_RESOURCES"]
        if pools is None:
            pools = self.get_org_pools(org_id)
        organization = pools[0].organization
        action_pool_map = self.get_actions_assignment_map(
            organization, token,
            actions=permissions,
            user_id=user_id)
        result = {}
        for permission in permissions:
            result[permission] = self.filter_pools_by_assignments(
                pools, action_pool_map[permission])
        return result

    def get_pool_policies(self, pool_ids):
        return self.session.query(PoolPolicy).filter(
            and_(
                PoolPolicy.pool_id.in_(pool_ids),
                PoolPolicy.deleted.is_(False),
            )).all()

    def get_pool_exports(self, pool_ids):
        return self.session.query(PoolExpensesExport).filter(
            and_(
                PoolExpensesExport.pool_id.in_(pool_ids),
                PoolExpensesExport.deleted.is_(False),
            )).all()

    def get_export_link(self, pool_id):
        exports = self.get_pool_exports([pool_id])
        if exports:
            return BASE_LINK_FORMAT.format(
                self._config.public_ip(), exports[0].id)
        else:
            return None

    def get_all_available_pools(self, user_id, organization_id, token,
                                permissions, condition):
        pools = self.get_org_pools(organization_id)
        self._get_employee_by_user_and_organization(
            user_id, organization_id=organization_id)
        full_pool_map = {pool.id: pool.to_dict() for pool in pools}
        permission_pool_map = self.get_all_available_pools_by_permissions(
            user_id, organization_id, token, pools, permissions
        )
        pool_policies = self.get_pool_policies(
            list(full_pool_map.keys()))
        pool_policies_map = {}
        for pool_policy in pool_policies:
            if not pool_policies_map.get(pool_policy.pool_id):
                pool_policies_map[pool_policy.pool_id] = []
            pool_policies_map[pool_policy.pool_id].append(
                pool_policy)

        exports = self.get_pool_exports(
            list(full_pool_map.keys()))
        pool_links_map = {}
        for export in exports:
            if not pool_links_map.get(export.pool_id):
                pool_links_map[export.pool_id] = BASE_LINK_FORMAT.format(
                    self._config.public_ip(), export.id)

        def get_pool_info(pool):
            default_owner_id = pool.default_owner_id
            default_owner_name = None
            if default_owner_id:
                default_owner_name = pool.default_owner.name
            res = {
                'id': pool.id,
                'name': pool.name,
                'limit': pool.limit,
                'pool_purpose': pool.purpose,
                'organization_id': pool.organization_id,
                'parent_id': pool.parent_id,
                'full_name': self._get_full_path(pool, full_pool_map),
                'default_owner_id': default_owner_id,
                'default_owner_name': default_owner_name,
                'policies': [bp.to_dict() for bp in pool_policies_map.get(
                    pool.id, [])]
            }
            if pool_links_map.get(pool.id):
                res['expenses_export_link'] = pool_links_map[pool.id]
            return res

        result = []
        if condition is None or condition == 'or':
            result_pool_map = {}
            for p_pools in permission_pool_map.values():
                for pool in p_pools:
                    result_pool_map[pool.id] = get_pool_info(pool)
            result = list(result_pool_map.values())
        elif condition == 'and':
            result_pool_ids = None
            all_pool_map = dict()
            for p_pools in permission_pool_map.values():
                all_pool_map.update({b.id: b for b in p_pools})
                matched_pool_ids = {b.id for b in p_pools}
                if result_pool_ids is None:
                    result_pool_ids = matched_pool_ids
                else:
                    result_pool_ids = result_pool_ids.intersection(
                        matched_pool_ids)
            result = [get_pool_info(all_pool_map[b_id])
                      for b_id in result_pool_ids]
        else:
            raise_invalid_argument_exception('condition')

        return result

    def get_expenses(self, pool, start_date, end_date, filter_by=None):
        controller_map = {
            'cloud': CloudFilteredPoolFormattedExpenseController,
            'pool': PoolFilteredPoolFormattedExpenseController,
            'employee': EmployeeFilteredPoolFormattedExpenseController,
            'pool_expenses_export': PoolExpensesExportFilteredPoolFormattedExpenseController,
        }

        controller = controller_map.get(
            filter_by, PoolFormattedExpenseController
        )(self.session, self._config)

        return controller.get_formatted_expenses(pool, start_date, end_date)

    def get_overview_savings(self, organization_id):
        last_completed = self.session.query(
            Checklist.last_completed
        ).filter(and_(
            Checklist.deleted.is_(False),
            Checklist.organization_id == organization_id,
        )).scalar()
        if not last_completed:
            return 0

        pipeline = [
            {'$match': {
                '$and': [
                    {'organization_id': organization_id},
                    {'created_at': last_completed}
                ]
            }},
            {'$unwind': '$data'},
            {'$group': {
                '_id': {'organization_id': '$organization_id',
                        'is_dismissed': '$data.is_dismissed'},
                'saving': {'$sum': '$data.saving'},
            }}
        ]
        for saving in self.checklists_collection.aggregate(pipeline):
            if not saving.get('_id', {}).get('is_dismissed', False):
                return saving.get('saving', 0)
        return 0

    def get_overview(self, organization, details=False):
        overview_base = self.session.query(
            Organization, CloudAccount, Pool, PoolPolicy
        ).outerjoin(CloudAccount, and_(
            CloudAccount.organization_id == Organization.id,
            CloudAccount.deleted.is_(False)
        )).join(Pool, and_(
            Pool.organization_id == Organization.id,
            Pool.deleted.is_(False),
            Pool.parent_id.is_(None)
        )).outerjoin(PoolPolicy, and_(
            PoolPolicy.pool_id == Pool.id,
            PoolPolicy.deleted.is_(False)
        )).filter(and_(
            Organization.id == organization.id
        )).all()
        root_pool, pool_policies, cloud_account_ids = None, set(), set()
        for _, cloud_account, pool, pool_policy in overview_base:
            if pool_policy:
                pool_policies.add(pool_policy)
            if cloud_account:
                cloud_account_ids.add(cloud_account.id)
            if pool and not root_pool:
                root_pool = pool
        if not root_pool:
            raise NotFoundException(
                Err.OE0002, [Pool.__name__, organization.pool_id])

        overview = root_pool.to_dict()
        if details:
            children, overview = self.get_details(
                overview, forecast=True, show_children=True, show_details=True)
            overview.pop('total_recommendations', None)
            overview['children'] = children
            overview.update({
                'policies': [policy.to_dict() for policy in pool_policies]
            })

            now = datetime.datetime.utcnow()
            pool_ids = [overview['id']] + [b['id'] for b in children]
            overview['saving'], _ = self.get_pool_savings(organization.id,
                                                          pool_ids)
            end_date = now.replace(day=1, hour=0, minute=0, second=0,
                                   microsecond=0) - datetime.timedelta(days=1)
            prev_month_expenses = self.get_pool_expenses(
                pool_ids, forecast=False, period_day=end_date.replace(day=1),
                end_date=end_date)
            overview['last_month_cost'] = 0
            for e in prev_month_expenses.values():
                overview['last_month_cost'] += e.get('cost', 0)
        return overview


class PoolAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return PoolController
