import json
import logging
from datetime import datetime, time, timedelta

from sqlalchemy.sql import and_, exists
from sqlalchemy import Enum
from rest_api.rest_api_server.exceptions import Err
from tools.optscale_exceptions.common_exc import (
    NotFoundException, WrongArgumentsException)
from rest_api.rest_api_server.models.enums import ConstraintTypes
from rest_api.rest_api_server.models.models import OrganizationOption
from rest_api.rest_api_server.controllers.base import BaseController

LOG = logging.getLogger(__name__)


class ConstraintBaseController(BaseController):
    def get_relation_field(self):
        raise NotImplementedError

    def get_model_name(self):
        raise NotImplementedError

    def create(self, **kwargs):
        entity_id = kwargs.get(self.get_relation_field())
        entity = self.get_entity(entity_id)
        self._check_input(entity_id, entity, **kwargs)
        kwargs['organization_id'] = self.get_organization_id_from_entity(entity)
        return super().create(**kwargs)

    def edit(self, item_id, **kwargs):
        limit = kwargs.get('limit')
        if limit is not None:
            constraint = self.get(item_id)
            self.check_limit(constraint.type, limit)
        return super().edit(item_id, **kwargs)

    def raise409(self, constraint_type, field_id):
        raise NotImplementedError

    def check_policy_exists(self, field_id, constraint_type):
        field_name = self.get_relation_field()
        constraint_exist = self.session.query(
            exists().where(and_(
                getattr(self.model_type, field_name) == field_id,
                self.model_type.type == constraint_type,
                self.model_type.deleted.is_(False)
            ))
        ).scalar()
        return constraint_exist

    def get_entity(self, entity_id):
        raise NotImplementedError

    def get_organization_id_from_entity(self, entity):
        raise NotImplementedError

    def _check_input(self, entity_id, entity, **kwargs):
        if not entity:
            raise NotFoundException(
                Err.OE0002, [self.get_model_name(), entity_id])
        limit = kwargs.get('limit')
        type_param = kwargs.get('type')
        if not type_param:
            raise WrongArgumentsException(Err.OE0216, ['type'])
        try:
            constraint_type = Enum(ConstraintTypes).enum_class(type_param)
        except ValueError as ex:
            raise WrongArgumentsException(Err.OE0004, [str(ex)])
        constraint_exist = self.check_policy_exists(entity_id, constraint_type)
        if constraint_exist:
            self.raise409(constraint_type, entity_id)
        self.check_limit(constraint_type, limit)

    def check_limit(self, constraint_type, limit):
        raise NotImplementedError

    def supported_constraint_types(self, org_id):
        option = self.session.query(OrganizationOption).filter(
                OrganizationOption.name == 'features',
                OrganizationOption.organization_id == org_id,
                OrganizationOption.deleted_at == 0
            ).one_or_none()
        try:
            option_dict = json.loads(option.value)
            tel_enabled = bool(option_dict.get(
                'total_expense_limit_enabled')) if option else False
        except Exception as exc:
            LOG.warning('Invalid features option value for org %s: %s',
                        org_id, str(exc))
            tel_enabled = False
        constraint_types = [
            ConstraintTypes.TTL, ConstraintTypes.DAILY_EXPENSE_LIMIT]
        if tel_enabled:
            constraint_types.append(ConstraintTypes.TOTAL_EXPENSE_LIMIT)
        return constraint_types

    def get_by_ids(self, org_id, obj_ids):
        raise NotImplementedError

    def get_violations(self, org_id, resource_data_map, now):
        raise NotImplementedError

    @staticmethod
    def get_resource_hit_value(resource_data, constraint_type, now):
        limit_value_map = {
            ConstraintTypes.TTL: (now - int(resource_data.get(
                'mindate', datetime.utcnow()).timestamp())) // 3600,
            ConstraintTypes.TOTAL_EXPENSE_LIMIT: resource_data.get(
                'total_cost', 0),
            ConstraintTypes.DAILY_EXPENSE_LIMIT: resource_data.get(
                'last_expense_cost', 0)
        }
        return limit_value_map.get(constraint_type)

    def handle_ttl_hit(self, resource_data, constraint, now):
        lifetime = self.get_resource_hit_value(resource_data, constraint.type,
                                               now)
        if lifetime > constraint.limit:
            return constraint.limit, lifetime

    def handle_pool_hit(self, resource_data, constraint, now):
        cost = self.get_resource_hit_value(resource_data, constraint.type, now)
        if cost > constraint.limit:
            return constraint.limit, cost

    def handle_daily_hit(self, resource_data, constraint, now):
        midnight = datetime.combine(datetime.today(), time.min)
        yesterday_midnight = midnight - timedelta(days=1)
        if yesterday_midnight > resource_data.get('last_expense_date', 0):
            # we hit daily violation only in case if the last expense was today or yesterday
            return
        cost = self.get_resource_hit_value(resource_data, constraint.type, now)
        if cost > constraint.limit:
            return constraint.limit, cost

    def handle_resource(self, resource_data, constraint, now):
        constraint_type_func_map = {
            ConstraintTypes.TTL: self.handle_ttl_hit,
            ConstraintTypes.TOTAL_EXPENSE_LIMIT: self.handle_pool_hit,
            ConstraintTypes.DAILY_EXPENSE_LIMIT: self.handle_daily_hit
        }
        handle_res = None
        func = constraint_type_func_map.get(
            constraint.type)
        if func:
            handle_res = func(resource_data, constraint, now)
        if handle_res:
            ttl_value = int(handle_res[1]) if (
                    constraint.type == ConstraintTypes.TTL) else None
            expense_value = handle_res[1] if (
                    constraint.type != ConstraintTypes.TTL) else None
            return {
                'pool_id': resource_data.get('pool_id'),
                'constraint_limit': handle_res[0],
                'ttl_value': ttl_value,
                'expense_value': expense_value,
                'time': now
            }

    def list(self, **kwargs):
        entity_id = kwargs.get(self.get_relation_field())
        if self.get_entity(entity_id) is None:
            raise NotFoundException(Err.OE0002, [self.get_model_name(), entity_id])
        return super().list(**kwargs)
