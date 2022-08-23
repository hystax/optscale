from datetime import datetime
from collections import defaultdict

from sqlalchemy import true
from sqlalchemy.sql import and_
from rest_api_server.exceptions import Err
from optscale_exceptions.common_exc import ConflictException
from rest_api_server.models.enums import ConstraintTypes
from rest_api_server.models.models import (PoolPolicy, Pool,
                                           ResourceConstraint, Organization)
from rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api_server.controllers.constraint_base import ConstraintBaseController
from rest_api_server.utils import check_int_attribute


MIN_TTL = 0
MAX_TTL = 720


class PoolPolicyController(ConstraintBaseController):
    def _get_model_type(self):
        return PoolPolicy

    def get_relation_field(self):
        return 'pool_id'

    def get_model_name(self):
        return Pool.__name__

    def create(self, **kwargs):
        policy = super().create(**kwargs)
        pool = policy.pool
        meta = {
            'object_name': pool.name,
            'policy_type': policy.type.value
        }
        action = 'policy_created'
        self.publish_activities_task(
            pool.organization_id, pool.id, 'pool', action, meta,
            'pool.{action}'.format(action=action), add_token=True)
        return policy

    def delete(self, item_id):
        policy = super().delete(item_id)
        pool = policy.pool
        meta = {
            'object_name': pool.name,
            'policy_type': policy.type.value
        }
        action = 'policy_deleted'
        self.publish_activities_task(
            pool.organization_id, pool.id, 'pool', action, meta,
            'pool.{action}'.format(action=action), add_token=True)
        return policy

    def edit(self, item_id, **kwargs):
        policy = self.get(item_id)
        policy_dict = policy.to_dict()
        updates = {k: v for k, v in kwargs.items() if policy_dict.get(k) != kwargs[k]}
        upd_policy = super().edit(item_id, **kwargs)
        pool = policy.pool
        meta = {
            'object_name': pool.name,
            'policy_type': policy.type.value
        }
        if upd_policy and upd_policy.active != policy_dict['active']:
            updates.pop('active', None)
            action_type = 'enabled' if upd_policy.active else 'disabled'
            action = 'policy_{action_type}'.format(action_type=action_type)
            self.publish_activities_task(
                pool.organization_id, pool.id, 'pool', action, meta,
                'pool.{action}'.format(action=action), add_token=True)
        if updates:
            meta.update({'params': ', '.join(
                ['%s: %s' % (k, v) for k, v in updates.items()])})
            self.publish_activities_task(
                pool.organization_id, pool.id, 'pool',
                'policy_updated', meta, 'pool.policy_updated', add_token=True)
        return upd_policy

    def raise409(self, constraint_type, field_id):
        raise ConflictException(Err.OE0440, [constraint_type, field_id])

    def check_limit(self, constraint_type, limit):
        lengths = {
            'min_length': MIN_TTL
        }
        if constraint_type == ConstraintTypes.TTL:
            lengths.update({'max_length': MAX_TTL})
        check_int_attribute('limit', limit, **lengths)

    def get_by_ids(self, org_id, pool_ids):
        constraint_types = self.supported_constraint_types(org_id)
        return self.session.query(PoolPolicy).filter(
            and_(
                PoolPolicy.pool_id.in_(pool_ids),
                PoolPolicy.deleted.is_(False),
                PoolPolicy.active == true(),
                PoolPolicy.limit > 0,
                PoolPolicy.type.in_(constraint_types)
            )).all()

    def get_organization_id_from_entity(self, pool):
        return pool.organization_id

    def get_entity(self, item_id):
        return self.session.query(Pool).filter(and_(
            Pool.id == item_id,
            Pool.deleted.is_(False)
        )).one_or_none()

    def handle_ttl_hit(self, resource_data, constraint, now):
        created_at = int(resource_data.get(
            'mindate', datetime.utcnow()).timestamp())
        ts_limit = created_at + constraint.limit * 3600
        if now > ts_limit:
            return ts_limit, now

    def get_exclusions(self, organization_id):
        if not organization_id:
            return set()
        q = self.session.query(
            ResourceConstraint.resource_id
        ).filter(and_(
            ResourceConstraint.deleted.is_(False),
            ResourceConstraint.organization_id == organization_id
        ))
        return {x[0] for x in q.all()}

    def get_violations(self, org_id, resource_data_map, now):
        pool_id_resources_map = defaultdict(list)
        for resource_data in resource_data_map.values():
            if not resource_data.get('pool_id'):
                continue
            pool_id_resources_map[resource_data['pool_id']].append(resource_data)

        policies = self.get_by_ids(org_id, list(pool_id_resources_map.keys()))
        pool_id_policies_map = defaultdict(list)
        for policy in policies:
            pool_id_policies_map[policy.pool_id].append(policy)

        res = {}
        excluded_resource_ids = self.get_exclusions(org_id)
        for pool_id, policies in pool_id_policies_map.items():
            resources_data = pool_id_resources_map.get(pool_id)
            if not resources_data:
                continue
            for policy in policies:
                for resource_data in resources_data:
                    if resource_data['resource_id'] in excluded_resource_ids:
                        continue
                    violation = self.handle_resource(resource_data, policy, now)
                    if violation:
                        res[(resource_data['resource_id'], policy.type)] = violation
        return res


class PoolPolicyOrganizationController(PoolPolicyController):
    def get_pool_policies(self, organization_id):
        return self.session.query(
            Pool, PoolPolicy
        ).outerjoin(
            PoolPolicy, and_(
                PoolPolicy.deleted.is_(False),
                PoolPolicy.pool_id == Pool.id
            )
        ).filter(
            and_(
                Pool.deleted.is_(False),
                Pool.organization_id == organization_id,
            )
        ).all()


class PoolPolicyAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return PoolPolicyController


class PoolPolicyOrganizationAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return PoolPolicyOrganizationController
