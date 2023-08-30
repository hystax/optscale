import json
import logging
from datetime import datetime

from retrying import retry
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import and_

from tools.optscale_exceptions.common_exc import (
    WrongArgumentsException, ConflictException, ForbiddenException,
    NotFoundException)
from rest_api.rest_api_server.controllers.assignment import AssignmentController

from rest_api.rest_api_server.controllers.base import (BaseController, PriorityMixin)
from rest_api.rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api.rest_api_server.controllers.pool import PoolController
from rest_api.rest_api_server.controllers.employee import EmployeeController
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.models.enums import ConditionTypes
from rest_api.rest_api_server.models.models import (Rule, Condition, Employee,
                                                    CloudAccount)
from rest_api.rest_api_server.utils import (
    check_list_attribute, check_string_attribute, raise_not_provided_exception,
    raise_does_not_exist_exception, check_bool_attribute, check_dict_attribute,
    RetriableException, should_retry, check_int_attribute, gen_id)


LOG = logging.getLogger(__name__)
RULE_PRIORITY_RETRIES = dict(
    stop_max_attempt_number=6, wait_fixed=500, retry_on_exception=should_retry
)


class RuleController(BaseController, PriorityMixin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._employee_ctrl = None
        self._pool_ctrl = None
        self._assignment_ctrl = None

    @property
    def employee_ctrl(self):
        if not self._employee_ctrl:
            self._employee_ctrl = EmployeeController(
                self.session, self._config, self.token
            )
        return self._employee_ctrl

    @property
    def pool_ctrl(self):
        if not self._pool_ctrl:
            self._pool_ctrl = PoolController(
                self.session, self._config, self.token
            )
        return self._pool_ctrl

    @property
    def assignment_ctrl(self):
        if not self._assignment_ctrl:
            self._assignment_ctrl = AssignmentController(
                self.session, self._config, self.token
            )
        return self._assignment_ctrl

    def _get_model_type(self):
        return Rule

    @staticmethod
    def _validate_parameters(**params):
        allowed_parameters = ['name', 'pool_id', 'owner_id', 'conditions',
                              'active', 'priority']
        for param in allowed_parameters:
            value = params.get(param)
            if value is not None:
                if param == 'conditions':
                    check_list_attribute(param, value)
                elif param == 'active':
                    check_bool_attribute(param, value)
                elif param == 'priority':
                    check_int_attribute(param, value, min_length=1)
                else:
                    check_string_attribute(param, value)
        unexpected_params = [
            p for p in params.keys() if p not in allowed_parameters]
        if unexpected_params:
            raise WrongArgumentsException(Err.OE0212, [unexpected_params])
        if 'conditions' in params:
            conditions = params.get('conditions')
            if conditions is None:
                raise_not_provided_exception('conditions')
            RuleController._validate_conditions_data(conditions)

    @staticmethod
    def _validate_tags_meta_info(meta_info):
        allowed_parameters = ["key", "value"]
        try:
            value = json.loads(meta_info)
        except Exception:
            raise WrongArgumentsException(Err.OE0219, ['meta_info'])
        check_dict_attribute('', value)
        check_string_attribute("key", value.get("key"))
        check_string_attribute("value", value.get("value"))
        unexpected_params = [
            p for p in value.keys() if p not in allowed_parameters]
        if unexpected_params:
            raise WrongArgumentsException(Err.OE0212, [unexpected_params])

    @staticmethod
    def _validate_conditions_data(conditions):
        allowed_parameters = ['type', 'meta_info', 'id']
        for condition in conditions:
            check_dict_attribute('condition', condition)
            for param in allowed_parameters:
                value = condition.get(param)
                if value is not None:
                    if param == 'type':
                        if value not in ConditionTypes.values():
                            raise WrongArgumentsException(Err.OE0430, [value])
                    if (param == 'meta_info' and
                            condition.get('type') in ConditionTypes.complex_types()):
                        check_string_attribute(param, value)
                        RuleController._validate_tags_meta_info(value)
                    else:
                        check_string_attribute(param, value)
            unexpected_params = [
                p for p in condition.keys() if p not in allowed_parameters]
            if unexpected_params:
                raise WrongArgumentsException(Err.OE0212, [unexpected_params])

    def _check_name_already_exist(self, name, organization_id):
        same_name_rules = self.list(organization_id=organization_id,
                                    name=name)
        if same_name_rules:
            raise ConflictException(Err.OE0149, [Rule.__name__, name])

    def _prepare_rule_data(self, employee, organization_id, is_deprioritized=False, **kwargs):
        name = kwargs.get('name')
        if not name:
            raise_not_provided_exception('name')
        self._check_name_already_exist(name, organization_id)
        active = kwargs.get('active', True)
        owner = None
        owner_id = kwargs.get('owner_id')
        if owner_id is None:
            raise_not_provided_exception('owner_id')
        else:
            owner = self.employee_ctrl.get(
                owner_id, organization_id=organization_id)
            if not owner:
                raise_does_not_exist_exception('owner_id', owner_id)
        pool_id = kwargs.get('pool_id')
        pool = None
        if pool_id is None:
            raise_not_provided_exception('pool_id')
        else:
            pool = self.pool_ctrl.get(pool_id)
            if not pool:
                raise_does_not_exist_exception('pool_id', pool_id)
            elif not pool.organization_id == organization_id:
                raise_does_not_exist_exception('pool_id', pool_id)
        conditions = kwargs.get('conditions')
        if not conditions:
            raise_not_provided_exception('conditions')
        all_rules = self._get_rules(organization_id)
        default_priority = len(all_rules) + 1
        rule = Rule(
            id=gen_id(),
            name=name, creator_id=employee.id,
            organization_id=organization_id,
            active=active,
            priority=default_priority,
            pool_id=pool_id, owner_id=owner_id
        )
        if is_deprioritized:
            priority = default_priority
        else:
            priority = kwargs.get('priority')
            if priority is None:
                priority = 1

        all_rules.append(rule)
        self.set_priority(all_rules, rule, priority)
        rule.priority = priority
        rule.conditions = self._prepare_conditions(conditions)
        return rule, pool, owner

    @staticmethod
    def _prepare_conditions(conditions_array):
        conditions = []
        for cond in conditions_array:
            meta_info = cond.get('meta_info')
            if not meta_info:
                raise_not_provided_exception('meta_info')
            type_ = cond.get('type')
            if not type_:
                raise_not_provided_exception('type')
            condition = Condition(type=ConditionTypes(type_),
                                  meta_info=meta_info)
            conditions.append(condition)
        return conditions

    def _get_rules(self, organization_id, **kwargs):
        query = self.session.query(
            Rule
        ).filter(
            and_(
                Rule.deleted.is_(False),
                Rule.organization_id == organization_id
            )
        ).order_by(Rule.priority)
        if len(kwargs) > 0:
            query = query.filter_by(**kwargs)
        return query.all()

    def _get_rules_split(self, organization_id, **kwargs):
        return self._get_rules(organization_id, **kwargs)

    def get_cloud_entities(self, rule_ids):
        cloud_list = self.session.query(Condition.meta_info).filter(
            Condition.deleted.is_(False),
            Condition.rule_id.in_(rule_ids),
        ).subquery()
        cloud_account = self.session.query(CloudAccount).filter(
            CloudAccount.deleted.is_(False),
            CloudAccount.id.in_(cloud_list),
        ).all()
        ca_map = {ca.id: ca.to_dict(secure=True) for ca in cloud_account}
        return {'entities': ca_map}

    def get_rules(self, organization_id, owner_id=None,
                  pool_id=None, valid_rules_only=None):
        additional_params = {}
        if owner_id:
            additional_params['owner_id'] = owner_id
        if pool_id:
            additional_params['pool_id'] = pool_id
        if valid_rules_only:
            additional_params['active'] = True
        rules = self._get_rules(organization_id, **additional_params)
        return self._get_rules_output(rules)

    def _get_rules_output(self, rules):
        employee_ids = set()
        pool_ids = set()
        for rule in rules:
            employee_ids.add(rule.owner_id)
            employee_ids.add(rule.creator_id)
            pool_ids.add(rule.pool_id)
        pool_details_map = self.assignment_ctrl.get_pools_details_map(
            pool_ids)
        employee_details_map = self.get_owners_dict(employee_ids)
        result = self.get_cloud_entities([r.id for r in rules])
        result.update(**{
            'rules': self.extend_rule_output(rules, pool_details_map,
                                             employee_details_map)
        })
        return result

    def get_owners_dict(self, employee_ids):
        result = self.session.query(
            Employee
        ).filter(
            Employee.deleted.is_(False),
            Employee.id.in_(employee_ids)
        ).all()
        return {e.id: e.name for e in result}

    @staticmethod
    def extend_rule_output(rules, pool_details_map,
                           employee_details_map):
        formatted_rules = []
        for rule in rules:
            formatted_rule = rule.to_dict()
            formatted_rule['creator_name'] = employee_details_map.get(
                rule.creator_id)
            formatted_rule['owner_name'] = employee_details_map.get(
                rule.owner_id)
            if rule.pool_id:
                formatted_rule['pool_name'] = pool_details_map.get(
                    rule.pool_id, {}).get('name')
                formatted_rule['pool_purpose'] = pool_details_map.get(
                    rule.pool_id, {}).get('purpose')
            else:
                formatted_rule['pool_name'] = None
                formatted_rule['pool_purpose'] = None
            formatted_rules.append(formatted_rule)
        return formatted_rules

    @retry(**RULE_PRIORITY_RETRIES)
    def create_rule(self, user_id, organization_id, token, is_deprioritized=False, **kwargs):
        # TODO implement permissions check OSB-412
        self._validate_parameters(**kwargs)
        employee = self.employee_ctrl.get_employee_by_user_and_organization(
            user_id, organization_id=organization_id)
        try:
            result = self._prepare_rule_data(employee, organization_id, is_deprioritized, **kwargs)
            rule, pool, owner = result
            if owner and pool:
                if not self.assignment_ctrl.validate_owner(owner, pool, token):
                    raise ForbiddenException(Err.OE0379, [owner.name])
            self.session.add(rule)
            self.session.commit()
        except IntegrityError as exc:
            LOG.warning('Unable to create rule: %s', str(exc))
            self.session.rollback()
            self.session.expunge_all()
            raise RetriableException(exc)
        meta = {
            'object_name': rule.organization.name,
            'rule_name': rule.name,
            'rule_id': rule.id,
            'pool_name': pool.name,
            'pool_id': pool.id
        }
        self.publish_activities_task(
            rule.organization_id, rule.organization_id, 'organization',
            'rule_created', meta, 'organization.rule_created', add_token=True)
        return self.get_rule_info(rule)

    def get(self, item_id, **kwargs):
        rule = super().get(item_id, **kwargs)
        if not rule:
            raise NotFoundException(Err.OE0002, [Rule.__name__, item_id])
        return rule

    def get_rule_info(self, rule):
        employee_ids = {rule.creator_id}
        if rule.owner_id:
            employee_ids.add(rule.owner_id)
        pool_ids = {rule.pool_id} if rule.pool_id else {}
        pool_details_map = self.assignment_ctrl.get_pools_details_map(
            pool_ids)
        employee_details_map = self.get_owners_dict(employee_ids)
        return self.extend_rule_output([rule], pool_details_map,
                                       employee_details_map)[0]

    def _process_rule_fields_update(self, original, organization_id, token,
                                    **kwargs):
        if 'name' in kwargs:
            new_name = kwargs.get('name')
            if new_name is None:
                raise_not_provided_exception('name')
            if new_name != original.name:
                self._check_name_already_exist(new_name,
                                               original.organization_id)
                original.name = new_name
        if 'active' in kwargs:
            value = kwargs.get('active')
            if value is None:
                raise_not_provided_exception('active')
            original.active = value
        if 'owner_id' in kwargs:
            new_owner_id = kwargs.get('owner_id')
            if new_owner_id is None:
                raise_not_provided_exception('owner_id')
            else:
                owner = self.employee_ctrl.get(
                    new_owner_id, organization_id=organization_id)
                if not owner:
                    raise_does_not_exist_exception('owner_id', new_owner_id)
            original.owner_id = new_owner_id
        else:
            owner = self.employee_ctrl.get(
                original.owner_id, organization_id=organization_id)
        if 'pool_id' in kwargs:
            new_pool_id = kwargs.get('pool_id')
            pool = None
            if new_pool_id is None:
                raise_not_provided_exception('pool_id')
            else:
                pool = self.pool_ctrl.get(new_pool_id)
                if not pool:
                    raise_does_not_exist_exception('pool_id', new_pool_id)
                elif not pool.organization_id == organization_id:
                    raise_does_not_exist_exception('pool_id', new_pool_id)
            original.pool_id = new_pool_id
        else:
            pool = self.pool_ctrl.get(original.pool_id)
        new_priority = kwargs.get('priority')
        if new_priority is not None and new_priority != original.priority:
            all_rules = self._get_rules(original.organization_id)
            self.set_priority(all_rules, original, new_priority)
        if original.owner_id and original.pool_id:
            if not self.assignment_ctrl.validate_owner(
                    owner, pool, token=token):
                raise ForbiddenException(Err.OE0379, [owner.name])
        return original

    def _process_conditions_update(self, original, conditions):
        now_ts = int(datetime.utcnow().timestamp())
        new_conditions = []
        updated_conditions_map = {}
        for condition in conditions:
            if 'id' not in condition:
                new_conditions.append(condition)
            else:
                updated_conditions_map[condition['id']] = condition
        deleted_condition_ids = [
            condition.id for condition in original.conditions
            if condition.id not in updated_conditions_map.keys()]
        for condition in original.conditions:
            if condition.id in deleted_condition_ids:
                condition.deleted_at = now_ts
            else:
                if 'type' in updated_conditions_map[condition.id]:
                    type_ = updated_conditions_map[condition.id]['type']
                    if type_ not in ConditionTypes.values():
                        raise WrongArgumentsException(Err.OE0430, [type_])
                    condition.type = ConditionTypes(type_)
                if 'meta_info' in updated_conditions_map[condition.id]:
                    meta = updated_conditions_map[condition.id]['meta_info']
                    if not meta:
                        raise_not_provided_exception('meta_info')
                    condition.meta_info = updated_conditions_map[
                        condition.id]['meta_info']
        original.conditions.extend(self._prepare_conditions(new_conditions))
        return original

    @retry(**RULE_PRIORITY_RETRIES)
    def edit_rule(self, item_id, token, **kwargs):
        # TODO implement permissions check OSB-412
        rule = self.get(item_id)
        if not rule:
            raise NotFoundException(Err.OE0002, [Rule.__name__, item_id])
        organization_id = rule.organization_id
        extra_keys_to_ignore = [
            'creator_name', 'owner_name', 'pool_name', 'creator_id',
            'organization_id', 'pool_purpose', 'id', 'created_at']
        for key in extra_keys_to_ignore:
            kwargs.pop(key, None)
        self._validate_parameters(**kwargs)
        try:
            rule = self._process_rule_fields_update(rule, organization_id,
                                                    token, **kwargs)
            if 'conditions' in kwargs:
                conditions = kwargs.get('conditions')
                rule = self._process_conditions_update(rule, conditions)
            self.session.add(rule)
            self.session.commit()
        except IntegrityError as exc:
            LOG.warning('Unable to change rule priority: %s', str(exc))
            self.session.rollback()
            self.session.expunge_all()
            raise RetriableException(exc)

        meta = {
            'object_name': rule.organization.name,
            'rule_name': rule.name,
            'rule_id': rule.id,
        }
        self.publish_activities_task(
            rule.organization_id, rule.organization_id, 'organization',
            'rule_updated', meta, 'organization.rule_updated', add_token=True)
        return self.get_rule_info(rule)

    def update_priority(self, rule_id, **kwargs):
        rule = self.get(rule_id)
        action = kwargs.pop('action', None)
        all_rules = self._get_rules(rule.organization_id)
        return self.change_priority(
            action, rule, all_rules, self._get_rules_output)

    @retry(**RULE_PRIORITY_RETRIES)
    def delete(self, item_id, **kwargs):
        # TODO implement permissions check OSB-412
        now_ts = int(datetime.utcnow().timestamp())
        rule = self.get(item_id, **kwargs)
        all_rules = self._get_rules(rule.organization_id)
        try:
            for condition in rule.conditions:
                if not condition.deleted:
                    condition.deleted_at = now_ts
                self.session.add(condition)
            if rule.priority != len(all_rules):
                self.set_priority(all_rules, rule, len(all_rules))
            rule.deleted_at = now_ts
            self.session.commit()
            meta = {
                'object_name': rule.organization.name,
                'rule_name': rule.name,
                'rule_id': rule.id,
            }
            self.publish_activities_task(
                rule.organization_id, rule.organization_id, 'organization',
                'rule_deleted', meta, 'organization.rule_deleted',
                add_token=True)
        except IntegrityError as exc:
            LOG.warning('Unable to delete rule: %s', str(exc))
            self.session.rollback()
            self.session.expunge_all()
            raise RetriableException(exc)


class RuleAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return RuleController
