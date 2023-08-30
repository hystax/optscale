import json
import logging
from copy import copy

from pymongo import UpdateOne, UpdateMany
from sqlalchemy import and_

from tools.optscale_exceptions.common_exc import NotFoundException
from rest_api.rest_api_server.controllers.base import (
    BaseController, BaseHierarchicalController, MongoMixin)
from rest_api.rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api.rest_api_server.controllers.employee import EmployeeController
from rest_api.rest_api_server.controllers.pool import PoolController
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.models.enums import ConditionTypes
from rest_api.rest_api_server.models.models import Pool, CloudAccount, Rule, Employee
from rest_api.rest_api_server.utils import encoded_tags


CHUNK_SIZE = 500
LOG = logging.getLogger(__name__)


class RuleWrapper:
    def __init__(self, rule):
        self.rule = rule
        self.pool_id = rule.pool_id
        self.pool = rule.pool
        self.owner_id = rule.owner_id
        self.owner = rule.owner
        self.converted_conditions = []
        for cond in rule.conditions:
            if not cond.deleted:
                self.converted_conditions.append(
                    CONDITIONS_MAP.get(cond.type)(cond))

    def validate(self):
        # implement rule validation
        # target pair validation
        # different condition combinations
        pass

    def match(self, res_info):
        for condition in self.converted_conditions:
            if not condition.match(res_info):
                return False
        return True


class BaseCondition:
    def __init__(self, condition):
        self.condition = condition
        self.meta = condition.meta_info
        self.target_attribute_name = None
        self.formatted_meta = None

    def match(self, res_info):
        raise NotImplementedError

    def get_sql_filter(self):
        raise NotImplementedError


class NameBasedCondition(BaseCondition):
    def __init__(self, condition):
        super().__init__(condition)
        self.target_attribute_names = ['name', 'cloud_resource_id']
        self.formatted_meta = self.meta.lower()

    def match(self, res_info):
        for n in self.target_attribute_names:
            name = res_info.get(n)
            if name and self.check_condition(name.lower()):
                return True
        return False

    def check_condition(self, name):
        raise NotImplementedError


class NameIsCondition(NameBasedCondition):
    def check_condition(self, name):
        return name == self.formatted_meta


class NameStartsWithCondition(NameBasedCondition):
    def check_condition(self, name):
        return name.startswith(self.formatted_meta)


class NameEndsWithCondition(NameBasedCondition):
    def check_condition(self, name):
        return name.endswith(self.formatted_meta)


class NameContainsCondition(NameBasedCondition):
    def check_condition(self, name):
        return self.formatted_meta in name


class TagIsCondition(BaseCondition):
    def __init__(self, condition):
        super().__init__(condition)
        self.target_attribute_name = 'tags'
        self.formatted_meta = TagIsCondition.convert_meta(self.meta)

    @staticmethod
    def convert_meta(value):
        value = json.loads(value)
        return {value.get("key"): value.get("value")}

    def match(self, res_info):
        tags = res_info.get(self.target_attribute_name)
        if tags:
            return self.formatted_meta.items() <= tags.items()
        return False


class TagExistsCondition(BaseCondition):
    def __init__(self, condition):
        super().__init__(condition)
        self.target_attribute_name = 'tags'

    def match(self, res_info):
        tags = res_info.get(self.target_attribute_name)
        if tags:
            return self.meta in tags.keys()
        return False


class TagValueStartsWith(TagIsCondition):
    def match(self, res_info):
        tags = res_info.get(self.target_attribute_name)
        if tags:
            matched = True
            for name, value in self.formatted_meta.items():
                matched &= tags.get(name, '').startswith(value)
            return matched
        return False


class ResourceTypeIsCondition(BaseCondition):
    def __init__(self, condition):
        super().__init__(condition)
        self.target_attribute_name = 'resource_type'
        self.formatted_meta = self.meta

    def match(self, res_info):
        res_type = res_info.get(self.target_attribute_name)
        if res_type:
            return res_type == self.formatted_meta
        return False


class CloudIsCondition(BaseCondition):
    def __init__(self, condition):
        super().__init__(condition)
        self.target_attribute_name = 'cloud_account_id'
        self.formatted_meta = self.meta

    def match(self, res_info):
        cc_id = res_info.get(self.target_attribute_name)
        if cc_id:
            return cc_id == self.formatted_meta
        return False


class RegionIsCondition(BaseCondition):
    def __init__(self, condition):
        super().__init__(condition)
        self.target_attribute_name = 'region'
        self.formatted_meta = self.meta

    def match(self, res_info):
        region = res_info.get(self.target_attribute_name)
        if region:
            return region == self.formatted_meta
        return False


CONDITIONS_MAP = {
    ConditionTypes.NAME_IS: NameIsCondition,
    ConditionTypes.NAME_STARTS_WITH: NameStartsWithCondition,
    ConditionTypes.NAME_ENDS_WITH: NameEndsWithCondition,
    ConditionTypes.NAME_CONTAINS: NameContainsCondition,
    ConditionTypes.TAG_IS: TagIsCondition,
    ConditionTypes.REGION_IS: RegionIsCondition,
    ConditionTypes.RESOURCE_TYPE_IS: ResourceTypeIsCondition,
    ConditionTypes.CLOUD_IS: CloudIsCondition,
    ConditionTypes.TAG_EXISTS: TagExistsCondition,
    ConditionTypes.TAG_VALUE_STARTS_WITH: TagValueStartsWith
}


class RuleApplyController(BaseController, MongoMixin):
    @staticmethod
    def apply_rules(res_info, rules):
        def short_rules_info(rls):
            if not isinstance(rls, list):
                rls = [rls]
            return [{
                'id': r.rule.id,
                'name': r.rule.name,
                'pool_id': r.rule.pool_id
            } for r in rls]

        for rule in rules:
            if rule.match(res_info):
                return rule.owner_id, rule.pool_id, short_rules_info(rule)
        return None, None, []

    def reapply_rules(self, user_info, organization_id, pool_id,
                      include_children=False):
        user_id = user_info['id']
        employee = EmployeeController(
            self.session, self._config, self.token
        ).get_employee_by_user_and_organization(user_id, organization_id)
        pool = self.session.query(Pool).filter(
            Pool.id == pool_id,
            Pool.deleted.is_(False),
        ).one_or_none()
        if pool is None:
            raise NotFoundException(Err.OE0002, [Pool.__name__, pool_id])
        target = 'pool {}'.format(pool.name)
        meta = {
            'target': target,
            'object_name': employee.organization.name
        }
        self.publish_activities_task(
            employee.organization_id, employee.organization_id,
            'organization', 'rules_processing_started', meta,
            'organization.rules_processing_started', add_token=True)

        cloud_account_map, employee_allowed_pools = self.collect_relations(
            organization_id=organization_id)

        resource_filter = {
            '$or': [
                {'cloud_account_id': {'$in': list(cloud_account_map.keys())}},
                {'organization_id': organization_id}],
            'cluster_id': {'$exists': False}}
        if include_children:
            pool_objects = BaseHierarchicalController(
                self.session, self._config, self.token
            ).get_item_hierarchy('id', pool_id, 'parent_id', Pool,
                                 include_item=True)
            pool_ids = [b.id for b in pool_objects]
            resource_filter['pool_id'] = {'$in': pool_ids}
        else:
            resource_filter['pool_id'] = pool_id

        rules = self.get_valid_rules(organization_id, employee_allowed_pools)

        resources_ids = list(self.resources_collection.find(
            resource_filter, {'_id': 1}))

        total_count = 0
        update_count = 0
        resource_update_chunk = []
        events = []
        applied_rules_map = {}
        for i in range(0, len(resources_ids), CHUNK_SIZE):
            resource_id_chunk = [x['_id'] for x in resources_ids[i:i+CHUNK_SIZE]]
            resources = self.resources_collection.find(
                {'_id': {'$in': resource_id_chunk}})
            for resource in resources:
                resource_id = resource['_id']
                sub_resources = []
                if resource.get('cluster_type_id'):
                    sub_resources = [
                        x['_id'] for x in self.resources_collection.find(
                            {'cluster_id': resource_id}, {'_id': 1})]
                total_count += 1
                cloud_account = cloud_account_map.get(
                    resource.get('cloud_account_id'))
                tags = encoded_tags(resource.get('tags', {}), decode=True)
                resource['tags'] = tags
                origin_pool_id = copy(resource.get('pool_id'))
                origin_employee_id = copy(resource.get('employee_id'))

                resource['pool_id'] = None
                resource['employee_id'] = None

                r_data, r_events = self.handle_assignment_data(
                    organization_id, resource, cloud_account,
                    employee_allowed_pools, rules)
                for applied_rule in r_data.get('applied_rules', []):
                    if not applied_rules_map.get(applied_rule['id']):
                        pool_id = applied_rule['pool_id']
                        applied_rules_map[applied_rule['id']] = {
                            'id': applied_rule['id'],
                            'name': applied_rule['name'],
                            'count': 0,
                            'pool_id': pool_id
                        }
                    applied_rules_map[applied_rule['id']]['count'] += 1
                same_pool = r_data.get('pool_id', False) == origin_pool_id
                same_employee = r_data.get('employee_id',
                                           False) == origin_employee_id
                if same_pool and same_employee:
                    continue
                else:
                    update_count += 1
                    for r in [resource_id] + sub_resources:
                        resource_update_chunk.append(UpdateOne(
                            filter={'_id': r},
                            update={
                                '$set': {
                                    k: resource[k]
                                    for k in ['pool_id', 'employee_id',
                                              'applied_rules']
                                    if k in resource
                                },
                            },
                        ))
                    events.extend(r_events)
        if applied_rules_map:
            pools_for_org = PoolController(
                self.session, self._config, self.token
            ).get_organization_pools(organization_id)
            pool_names = {b['id']: b['name'] for b in pools_for_org}
            for rule in applied_rules_map.values():
                rule.update({
                    'pool_name': pool_names.get(rule['pool_id'])
                })
                meta = {
                    'pool_name': rule['pool_name'],
                    'object_name': rule['name'],
                    'rule_count': rule['count'],
                    'pool_id': rule['pool_id']
                }
                self.publish_activities_task(
                    organization_id, rule['id'], 'rule', 'rule_applied', meta,
                    'rule.rule_applied', add_token=True)
        chunk_size = 200
        for i in range(0, len(resource_update_chunk), chunk_size):
            self.resources_collection.bulk_write(
                resource_update_chunk[i:i + chunk_size])
        for e in events:
            self.publish_cloud_acc_activities(*e)
        meta = {
            'target': target,
            'total': total_count,
            'object_name': employee.organization.name
        }
        self.publish_activities_task(
            employee.organization_id, employee.organization_id,
            'organization', 'rules_processing_completed', meta,
            'organization.rules_processing_completed', add_token=True)
        return {
            "processed": total_count,
            "updated_assignments": update_count,
        }

    def _get_pools_children_ids(self, pool_children_ids_map, pool_ids):
        res = set()
        for b_id in pool_ids:
            children = pool_children_ids_map.get(b_id)
            if children:
                res.update(self._get_pools_children_ids(
                    pool_children_ids_map, children))
            res.update([b_id])
        return res

    def collect_relations(self, cloud_account_ids=None, organization_id=None):
        if cloud_account_ids is not None:
            ca_filter = CloudAccount.id.in_(cloud_account_ids)
        else:
            ca_filter = CloudAccount.organization_id == organization_id
        query_set = self.session.query(
            CloudAccount, Employee, Pool
        ).outerjoin(Employee, and_(
            Employee.organization_id == CloudAccount.organization_id,
            Employee.deleted.is_(False)
        )).outerjoin(Pool, and_(
            Pool.organization_id == CloudAccount.organization_id,
            Pool.deleted.is_(False)
        )).filter(
            ca_filter,
            CloudAccount.deleted.is_(False)
        )
        pools_map = {}
        auth_id_employee_map = {}
        cloud_account_map = {}
        for ca, employee, pool in query_set.all():
            if ca:
                cloud_account_map[ca.id] = ca
            if employee:
                auth_id_employee_map[employee.auth_user_id] = employee
            if pool:
                pools_map[pool.id] = pool
        pool_children_map = {}
        for b in pools_map.values():
            if b.parent_id is None:
                continue
            if not pool_children_map.get(b.parent_id):
                pool_children_map[b.parent_id] = []
            pool_children_map[b.parent_id].append(b.id)
        actions = ["MANAGE_OWN_RESOURCES", "MANAGE_RESOURCES"]
        user_action_pool_map = self.get_bulk_allowed_action_pools_map(
            auth_id_employee_map.keys(), actions)
        employee_allowed_pools = {}
        for auth_user_id, action_pool_map in user_action_pool_map.items():
            employee_id = auth_id_employee_map[auth_user_id].id
            all_pool_ids = set()
            for pool_ids in action_pool_map.values():
                all_pool_ids.update(self._get_pools_children_ids(
                    pool_children_map, pool_ids))
            employee_allowed_pools[employee_id] = all_pool_ids

        return cloud_account_map, employee_allowed_pools

    def handle_assignment_data(self, organization_id, resource_data,
                               cloud_account, employee_allowed_pools, rules):
        employee_id = resource_data.pop(
            'employee_id', resource_data.pop('owner_id', None))
        resource_events = []
        # avoiding duplications/conflicts
        resource_data.pop('owner_id', None)
        pool_id = resource_data.pop('pool_id', None)
        if employee_id and pool_id:
            if pool_id in employee_allowed_pools.get(employee_id, []):
                resource_data.update({
                    'employee_id': employee_id,
                    'pool_id': pool_id,
                })
            elif cloud_account:  # clusters doesn't belong to ca. Ignoring
                resource_events.append(
                    (
                        cloud_account,
                        resource_data.get('resource_type', 'Resource'),
                        resource_data.get('name'),
                        resource_data.get('cloud_resource_id')
                    )
                )
        employee_id = resource_data.get('employee_id')
        pool_id = resource_data.get('pool_id')
        if not employee_id or not pool_id:
            try:
                employee_id, pool_id, applied_rules = self.apply_rules(
                    resource_data, rules)
                if employee_id and pool_id and applied_rules:
                    resource_data.update({
                        'employee_id': employee_id,
                        'pool_id': pool_id,
                        'applied_rules': applied_rules
                    })
                else:
                    # assign to (root pool - root pool default owner)
                    root_pool = self.session.query(Pool).filter(
                        Pool.organization_id == organization_id,
                        Pool.deleted.is_(False),
                        Pool.parent_id.is_(None)).one_or_none()
                    owner = root_pool.default_owner_id
                    resource_data.update({
                        'employee_id': owner,
                        'pool_id': root_pool.id,
                    })
                    resource_data.pop('applied_rules', None)
            except Exception as ex:
                LOG.exception('rule apply failed: %s', ex)
                raise
                # TODO add event with exception
        return resource_data, resource_events

    def publish_cloud_acc_activities(self, cloud_account, obj_type,
                                     obj_name, obj_id):
        meta = {
            'object_name': cloud_account.name,
            'level': 'WARNING',
            'resource_type': obj_type,
            'res_name': obj_name,
            'cloud_resource_id': obj_id
        }
        self.publish_activities_task(
            cloud_account.organization_id, cloud_account.id, 'cloud_account',
            'root_assigned_resource', meta,
            'cloud_account.root_assigned_resource', add_token=True)

    def get_valid_rules(self, organization_id, employee_allowed_pools):
        all_rules = self.session.query(Rule).filter(and_(
            Rule.deleted.is_(False),
            Rule.organization_id == organization_id,
            Rule.active.is_(True)
        )).order_by(Rule.priority).all()
        valid_rules = []
        invalid_rules = []
        for rule in all_rules:
            allowed_pools = employee_allowed_pools.get(rule.owner_id, [])
            if rule.pool_id in allowed_pools:
                valid_rules.append(RuleWrapper(rule))
            else:
                rule.active = False
                self.session.add(rule)
                invalid_rules.append(rule)
        for invalid_rule in invalid_rules:
            meta = {
                'pool_name': invalid_rule.pool.name,
                'pool_id': invalid_rule.pool_id,
                'object_name': invalid_rule.name,
                'level': 'WARNING',
                'owner_name': invalid_rule.owner.name,
                'owner_id': invalid_rule.owner_id
            }
            self.publish_activities_task(
                organization_id, invalid_rule.id, 'rule', 'rule_deactivated',
                meta, 'rule.rule_deactivated', add_token=True)
        self.session.commit()
        return valid_rules


class RuleApplyAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return RuleApplyController
