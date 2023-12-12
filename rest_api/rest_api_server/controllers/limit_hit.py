from datetime import datetime
import logging

from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import func

from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.controllers.base import BaseController
from rest_api.rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api.rest_api_server.controllers.pool_policy import PoolPolicyController
from rest_api.rest_api_server.controllers.cloud_resource import CloudResourceController
from rest_api.rest_api_server.controllers.resource_constraint import (
    ResourceConstraintController)
from rest_api.rest_api_server.controllers.pool_alert import PoolAlertController
from rest_api.rest_api_server.models.enums import (
    ConstraintLimitStates, ConstraintTypes, LimitHitsSelector,
    ThresholdBasedTypes)
from rest_api.rest_api_server.models.models import (
    ConstraintLimitHit, Pool, Employee, Organization,
    CloudAccount)

from tools.optscale_exceptions.common_exc import NotFoundException


LOG = logging.getLogger(__name__)


class LimitHitsController(BaseController):
    def __init__(self, db_session, config=None, token=None, engine=None):
        super().__init__(db_session, config, token, engine)
        self._cloud_resource_ctrl = None

    @property
    def cloud_resource_ctrl(self):
        if self._cloud_resource_ctrl is None:
            self._cloud_resource_ctrl = CloudResourceController(
                self.session, self._config, self.token)
        return self._cloud_resource_ctrl

    def _get_model_type(self):
        return ConstraintLimitHit

    @property
    def checks(self):
        return [
            lambda x, y: x.get('type') == y.type,
            lambda x, y: x.get('pool_id') == y.pool_id,
            lambda x, y: x.get('constraint_limit') == y.constraint_limit
        ]

    def get_resource_owner(self, resource_id):
        auth_user_id = self.cloud_resource_ctrl.get_owner(resource_id)
        return auth_user_id

    def list(self, object_id, selection_type=None, **kwargs):
        if selection_type and isinstance(selection_type, LimitHitsSelector):
            if selection_type == LimitHitsSelector.pool_id:
                obj = self.session.query(Pool).filter(
                    Pool.deleted.is_(False),
                    Pool.id == object_id
                ).scalar()
                if not obj:
                    raise NotFoundException(
                        Err.OE0002, [Pool.__name__, object_id])
            elif selection_type == LimitHitsSelector.resource_id:
                self.cloud_resource_ctrl.get(object_id)
            kwargs.update({selection_type.value: object_id})

        query = self.session.query(self._get_model_type()).filter(
            self.model_type.deleted_at.is_(False))
        if len(kwargs) > 0:
            query = query.filter_by(**kwargs)
        return query.all()

    def _get_resources_hits(self, resource_ids):
        t = self.session.query(
            ConstraintLimitHit.resource_id,
            func.max(ConstraintLimitHit.created_at).label('max_created_at'),
            ConstraintLimitHit.type
        ).filter(
            ConstraintLimitHit.deleted.is_(False)
        ).group_by(
            ConstraintLimitHit.resource_id, ConstraintLimitHit.type
        ).subquery('t')
        query = self.session.query(
            ConstraintLimitHit
        ).join(
            t, and_(
                t.c.resource_id == ConstraintLimitHit.resource_id,
                t.c.type == ConstraintLimitHit.type,
                t.c.max_created_at == ConstraintLimitHit.created_at
            )
        ).filter(and_(
            ConstraintLimitHit.deleted.is_(False),
            ConstraintLimitHit.resource_id.in_(resource_ids))
        ).group_by(
            ConstraintLimitHit.resource_id, ConstraintLimitHit.type)
        return query.all()

    def _get_pool_hierarchy(self, organization_id):
        organization = self.session.query(
            Organization
        ).filter(
            Organization.id == organization_id
        ).scalar()
        cte = self.session.query(Pool).filter(
            and_(
                Pool.deleted.is_(False),
                Pool.id == organization.pool_id
            )
        ).cte(recursive=True, name='hierarchy')
        rec = cte.union_all(
            self.session.query(Pool).filter(
                Pool.parent_id == cte.c.id,
                Pool.deleted.is_(False)
            )
        )
        return organization, self.session.query(rec).all()

    def _get_resource_info_map(self, resource_ids, pool_names_map,
                               cloud_account_names_map):
        resources = self.cloud_resource_ctrl.resources_collection.find(
            {'_id': {'$in': resource_ids}}
        )
        resources_map = {
            r['_id']: {
                'resource_id': r['_id'],
                'cloud_account_name': cloud_account_names_map.get(
                    r.get('cloud_account_id')),
                'resource_type': r.get('resource_type'),
                'cloud_resource_id': r.get('cloud_resource_id'),
                'resource_name': r.get('name'),
                'employee_id': r.get('employee_id'),
                'pool_id': r.get('pool_id'),
                'cluster_type_id': r.get('cluster_type_id')
            } for r in resources
        }
        resource_employee_map = {
            k: v['employee_id'] for k, v in resources_map.items()
            if v['employee_id'] is not None
        }
        employees = self.session.query(
            Employee
        ).filter(
            Employee.id.in_(set(resource_employee_map.values()))
        ).all()
        employees_info = {
            e.id: {
                'name': e.name, 'auth_user_id': e.auth_user_id
            } for e in employees
        }

        for _, resource in resources_map.items():
            employee_id = resource['employee_id']
            pool_id = resource['pool_id']
            if employee_id:
                employee_info = employees_info[employee_id]
                resource.update({
                    'employee_name': employee_info['name'],
                    'auth_user_id': employee_info['auth_user_id']
                })
            if pool_id:
                resource.update({'pool_name': pool_names_map[pool_id]})
        return resources_map

    def _count_owner_resources(self, limit_hits, resource_info_map):
        user_res = {}
        pool_res = {}
        resource_user_map = {}
        for resource_id, resource in resource_info_map.items():
            user_id = resource.pop('auth_user_id', None)
            if not user_id:
                continue
            if not user_res.get(user_id):
                user_res[user_id] = {}
            user_res[user_id][resource_id] = []
            resource_user_map[resource_id] = user_id
        for limit_hit in limit_hits:
            user_id = resource_user_map.get(limit_hit.resource_id)
            resource_info = resource_info_map[
                limit_hit.resource_id].copy()
            resource_info.update({
                'type': limit_hit.type.value,
                'ttl_value': limit_hit.ttl_value,
                'expense_value': limit_hit.expense_value,
            })
            user_res[user_id][limit_hit.resource_id].append(resource_info)
            pool_id = resource_info.get('pool_id', None)
            if not pool_res.get(pool_id):
                pool_res[pool_id] = []
            pool_res[pool_id].append(resource_info)
        return user_res, pool_res

    def _get_recipients(self, scope_ids, role_purposes=None, user_ids=None):
        recipients = []
        if not scope_ids:
            return recipients
        if role_purposes:
            _, recipients = self.auth_client.user_roles_get(
                scope_ids=scope_ids, role_purposes=role_purposes)
        if user_ids:
            _, recipients = self.auth_client.user_roles_get(
                scope_ids=scope_ids, user_ids=user_ids)
        return recipients

    def send_alerts(self, organization_id, limit_hits):
        organization, pools = self._get_pool_hierarchy(organization_id)
        resource_ids = list(set(map(lambda x: x.resource_id, limit_hits)))
        pool_names_map = {b.id: b.name for b in pools}
        cloud_account_names_map = {
            ca.id: ca.name for ca in self.session.query(CloudAccount).filter(
                CloudAccount.organization_id == organization_id
            ).all()
        }
        resource_info_map = self._get_resource_info_map(
            resource_ids, pool_names_map, cloud_account_names_map)
        user_hit_map, pool_res = self._count_owner_resources(
            limit_hits, resource_info_map)
        # user_id -> res_id -> hits info

        scope_ids = list(map(lambda x: x.id, pools))
        # we need to add organization id here
        scope_ids.append(organization_id)
        user_ids = list(user_hit_map.keys())

        rss_owners = self._get_recipients(
            scope_ids=scope_ids, user_ids=user_ids)
        for rss_owner in rss_owners:
            hit_list = []
            res_hits = user_hit_map.get(rss_owner['user_id'], {})
            for hits in res_hits.values():
                hit_list.extend(hits)
            if hit_list:
                meta = {'violations': hit_list}
                self.publish_activities_task(
                    organization.id, rss_owner['user_id'], 'user',
                    'constraint_violated', meta,
                    'alert.violation.constraint_violated')

        pool_alerts_map = PoolAlertController(
            self.session, self._config, self.token).get_pool_alerts_map(
            scope_ids, ThresholdBasedTypes.CONSTRAINT)
        for pool_id, res_data in pool_res.items():
            if pool_alerts_map.get(pool_id):
                for alert_id in pool_alerts_map[pool_id]:
                    meta = {
                        'alert_id': alert_id,
                        'violations': res_data
                    }
                    self.publish_activities_task(
                        organization_id, pool_id, 'pool', 'constraint_violated',
                        meta, 'alert.violation.constraint_violated')

    def collect_processing_data(self, resources):
        res = {}
        for r in resources:
            r_id = r['_id']
            cluster_id = r.get('cluster_id')
            mindate = datetime.fromtimestamp(r.get('first_seen', 0))
            last_expense_cost = r.get('last_expense', {}).get('cost', 0)
            last_expense_date = datetime.fromtimestamp(
                r.get('last_expense', {}).get('date', 0)
            )
            resource_cost = r.get('total_cost', 0)
            if cluster_id:
                if cluster_id in res:
                    res[cluster_id]['total_cost'] += resource_cost
                    res[cluster_id]['mindate'] = min(
                        res[cluster_id]['mindate'], mindate)
                    continue
                r_id = cluster_id
            r.update({
                'resource_id': r_id,
                'total_cost': resource_cost,
                'mindate': mindate,
                'last_expense_cost': last_expense_cost,
                'last_expense_date': last_expense_date
            })
            res[r_id] = r
        return res

    def set_limits_in_green_state(self, not_violated_limit_hits,
                                  resource_data_map, now, organization_id):
        resource_ids = [res_type[0] for res_type in list(not_violated_limit_hits)]
        limits = self._get_resources_hits(resource_ids)
        limit_res_id_type_map = {
            (limit.resource_id, limit.type): limit for limit in limits
        }
        new_green_limit_hits = []
        for res_id_type in not_violated_limit_hits:
            limit = limit_res_id_type_map.get(res_id_type)
            if limit and limit.state == ConstraintLimitStates.RED:
                resource_id = limit.resource_id
                limit_type = limit.type
                limit_val = (
                    now if limit_type == ConstraintTypes.TTL else
                    ResourceConstraintController.get_resource_hit_value(
                        resource_data_map.get(resource_id), limit_type, now))
                ttl_value = int(limit_val) if (
                    limit_type == ConstraintTypes.TTL) else None
                expense_value = limit_val if (
                    limit_type != ConstraintTypes.TTL) else None
                new_green_limit_hits.append(
                    ConstraintLimitHit(
                        resource_id=resource_id,
                        pool_id=limit.pool_id,
                        type=limit_type,
                        constraint_limit=limit.constraint_limit,
                        ttl_value=ttl_value,
                        expense_value=expense_value,
                        time=now,
                        organization_id=organization_id,
                        state=ConstraintLimitStates.GREEN
                    )
                )
        if new_green_limit_hits:
            self.session.add_all(new_green_limit_hits)
        self.session.commit()

    def process_resources(self, organization_id, resources):
        if not resources:
            return []
        now = int(datetime.utcnow().timestamp())
        resource_data_map = self.collect_processing_data(resources)
        resource_ids = list(resource_data_map.keys())
        resource_limit_hit_map = {
            (limit_hit.resource_id, limit_hit.type): limit_hit for limit_hit in
            self._get_resources_hits(resource_ids)}
        violations = {}
        for c in [PoolPolicyController, ResourceConstraintController]:
            violations.update(c(self.session, self._config).get_violations(
                organization_id, resource_data_map, now))
        violated_resource_ids = list(set([r[0] for r in violations.keys()]))

        violated_res_constr_map = {
            (x.resource_id, x.type): x for x in ResourceConstraintController(
                self.session, self._config).get_by_ids(
                organization_id, violated_resource_ids)
        }
        violated_limit_hits = {}
        for hit in self._get_resources_hits(violated_resource_ids):
            violation_key = (hit.resource_id, hit.type)
            if violations.get(violation_key):
                violated_limit_hits[violation_key] = hit

        not_violated_limit_hits = list(set(resource_limit_hit_map.keys()) - set(
            violated_limit_hits.keys()))
        if not_violated_limit_hits:
            self.set_limits_in_green_state(not_violated_limit_hits,
                                           resource_data_map, now,
                                           organization_id)

        result = []
        new_hits = []
        start_day = int(datetime.fromtimestamp(now).replace(
            hour=0, minute=0, second=0, microsecond=0).timestamp())
        for k, v in violations.items():
            # Do not mark resources with violated pool policy if resource
            # has not violated resource constraint
            if not v.get('pool_id') or not violated_res_constr_map.get(k):
                result.append(k[0])
            limit_hit = violated_limit_hits.get(k)
            resource_info = {'resource_id': k[0], 'type': k[1], **v}
            if limit_hit:
                hit_type = limit_hit.type
                hit_day_start = int(datetime.fromtimestamp(
                    limit_hit.created_at).replace(
                    hour=0, minute=0, second=0, microsecond=0).timestamp())
                if (all(map(lambda check: check(resource_info, limit_hit),
                            self.checks)) and
                        limit_hit.state == ConstraintLimitStates.RED and
                        (hit_type != ConstraintTypes.DAILY_EXPENSE_LIMIT or
                         start_day == hit_day_start)):
                    continue
            new_hits.append(ConstraintLimitHit(
                resource_id=resource_info.get('resource_id'),
                pool_id=resource_info.get('pool_id'),
                type=resource_info.get('type'),
                constraint_limit=resource_info.get('constraint_limit'),
                ttl_value=resource_info.get('ttl_value'),
                expense_value=resource_info.get('expense_value'),
                time=now,
                organization_id=organization_id,
                state=ConstraintLimitStates.RED
            ))
        self.session.flush()
        if new_hits:
            self.session.add_all(new_hits)
        try:
            self.session.commit()
        except SQLAlchemyError as ex:
            # concurrent db operations
            LOG.error("Error inserting resources because of %s", str(ex))
            self.session.rollback()
            raise

        self.send_alerts(organization_id, new_hits)
        return result


class LimitHitsAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return LimitHitsController
