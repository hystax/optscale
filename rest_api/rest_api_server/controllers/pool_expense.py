from calendar import monthrange
from datetime import datetime, timedelta

from tools.optscale_exceptions.common_exc import NotFoundException

from rest_api.rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api.rest_api_server.controllers.organization import PoolController
from rest_api.rest_api_server.controllers.expense import ExpenseController
from rest_api.rest_api_server.controllers.base import (BaseController,
                                                       BaseHierarchicalController)
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.models.models import Organization, Pool
from rest_api.rest_api_server.utils import get_nil_uuid


class PoolExpenseController(BaseController):
    RESULT_POOL_FIELDS = ['id', 'purpose', 'name', 'limit',
                          'this_month_expenses', 'this_month_forecast']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._today = None
        self._last_month_end = None
        self._last_month_start = None
        self._this_month_end = None
        self._expense_ctrl = None

    def _get_model_type(self):
        return Pool

    @property
    def today(self):
        if self._today is None:
            self._today = datetime.utcnow()
        return self._today

    @property
    def last_month_start(self):
        if self._last_month_start is None:
            self._last_month_start = self.last_month_end.replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )
        return self._last_month_start

    @property
    def last_month_end(self):
        if self._last_month_end is None:
            self._last_month_end = self.today.replace(
                day=1, hour=0, minute=0, second=0, microsecond=0) - timedelta(
                seconds=1)
        return self._last_month_end

    @property
    def this_month_end(self):
        if self._this_month_end is None:
            _, days_in_this_month = monthrange(self.today.year,
                                               self.today.month)
            self._this_month_end = self.last_month_end + timedelta(
                days=days_in_this_month)
        return self._this_month_end

    @property
    def expense_ctrl(self):
        if self._expense_ctrl is None:
            self._expense_ctrl = ExpenseController(self._config)
        return self._expense_ctrl

    def get_pool_limit_costs(self, root_pool_id, filter_field=None,
                             filter_list=None):
        pool_objects = BaseHierarchicalController(
            self.session, self._config, self.token
        ).get_item_hierarchy('id', root_pool_id, 'parent_id', Pool,
                             include_item=True)
        pool_map = {}
        for pool in pool_objects:
            pool_map[pool.id] = {
                'children': [b.id for b in pool_objects
                             if b.parent_id == pool.id],
            }

        if filter_field is None and filter_list is None:
            filter_field = 'pool_id'
            filter_list = list(pool_map.keys())

        grouping_field = 'pool_id'
        db_result = list(self.expense_ctrl.get_expenses(
            filter_field, filter_list, self.last_month_start, self.today,
            group_by=grouping_field
        ))

        result = {}
        for group in db_result:
            _id = group['_id'][grouping_field]
            date = group['_id']['date']
            cost = group['cost']

            if _id not in result:
                result[_id] = [0, 0, date]
            if result[_id][2] > date:
                result[_id][2] = date
            if date > self.last_month_end:
                result[_id][0] += cost
            else:
                result[_id][1] += cost

        def calculate_costs(pool_id):
            cost = result.get(pool_id, [0, 0, None])
            children_costs = [calculate_costs(child_id) for child_id
                              in pool_map[pool_id]['children']]
            dates = [c[2] for c in children_costs if c[2]]
            if cost[2]:
                dates.append(cost[2])
            total = [
                cost[0] + sum(c[0] for c in children_costs),
                cost[1] + sum(c[1] for c in children_costs),
                min(dates) if dates else None
            ]
            pool_map[pool_id].update({
                'this_month_cost': total[0],
                'last_month_cost': total[1],
                'min_date': total[2]
            })
            return total

        calculate_costs(root_pool_id)
        if None in result:
            pool_map[get_nil_uuid()] = {
                'this_month_cost': result[None][0],
                'last_month_cost': result[None][1],
                'min_date': result[None][2]
            }

        return pool_map

    def get_pool_info(self, pool_ids):
        response = self.session.query(
            Pool.id, Pool.purpose, Pool.limit, Pool.name
        ).filter(
            Pool.deleted.is_(False),
            Pool.id.in_(pool_ids)
        ).all()
        pools = {}
        for info in response:
            b_id, b_purpose, limit, b_name = info
            pools[b_id] = {
                'id': b_id,
                'name': b_name,
                'purpose': b_purpose,
                'limit': limit
            }
        return pools

    def get_expenses(self, org_id, token):
        pools = self.session.query(
            Pool
        ).filter(
            Pool.deleted.is_(False),
            Pool.organization_id == org_id
        ).all()
        if not pools:
            raise NotFoundException(Err.OE0002, [Organization.__name__, org_id])

        pool_parent_map = {pool.id: pool.parent_id for pool in pools}
        pool_map = {pool.id: pool for pool in pools}
        org = pools[0].organization
        org_pool_id = pools[0].organization.pool_id
        pool_ctrl = PoolController(self.session, self._config,
                                   self.token)
        action_pool_map = pool_ctrl.get_actions_assignment_map(
            org, token,
            actions=["MANAGE_OWN_RESOURCES", "MANAGE_RESOURCES"])
        assignments = set(action_pool_map['MANAGE_OWN_RESOURCES'] + action_pool_map[
            'MANAGE_RESOURCES']).intersection(set(pool_map.keys()))
        if not assignments:
            assignments = set(pool_map.keys())
        root_pool_ids = []
        for pool_id in assignments:
            upper_hierarchy = []
            current_pool_id = pool_id
            while pool_parent_map.get(current_pool_id) is not None:
                parent_id = pool_parent_map[current_pool_id]
                upper_hierarchy.append(parent_id)
                current_pool_id = parent_id

            if not any(pool_id in assignments
                       for pool_id in upper_hierarchy):
                root_pool_ids.append(pool_id)

        root_pool_map = self.get_pool_info(root_pool_ids)
        filter_field, filter_list = None, None
        pool_cost_map = self.get_pool_limit_costs(
            root_pool_id=org_pool_id,
            filter_field=filter_field,
            filter_list=filter_list)

        last_month_total = 0
        this_month_total = 0
        this_month_forecast_total = 0
        pool_limit_total = 0
        pool_ids = list(root_pool_map.keys())
        for pool_id in pool_ids:
            pool_limit_costs = pool_cost_map.get(
                pool_id, {'this_month_cost': 0, 'last_month_cost': 0,
                          'min_date': None})
            last_month_total += pool_limit_costs['last_month_cost']
            this_month_total += pool_limit_costs['this_month_cost']
            forecast = self.expense_ctrl.get_monthly_forecast(
                pool_limit_costs['last_month_cost'] + pool_limit_costs[
                    'this_month_cost'], pool_limit_costs['this_month_cost'],
                pool_limit_costs['min_date'])
            this_month_forecast_total += forecast
            pool_limit_total += root_pool_map[pool_id]['limit']
            root_pool_map[pool_id].update({
                'this_month_expenses': pool_limit_costs['this_month_cost'],
                'this_month_forecast': forecast,
            })

        result = {
            'expenses': {
                'last_month': {
                    'total': last_month_total,
                    'date': int(self.last_month_end.timestamp()),
                },
                'this_month': {
                    'total': this_month_total,
                    'date': int(self.today.timestamp()),
                },
                'this_month_forecast': {
                    'total': this_month_forecast_total,
                    'date': int(self.this_month_end.timestamp()),
                }
            },
            'total': pool_limit_total,
            'pools': [
                {
                    field: b[field] for field in self.RESULT_POOL_FIELDS
                } for b in sorted(root_pool_map.values(),
                                  key=lambda x: x.get('limit'), reverse=True)
            ]
        }
        return result


class PoolExpenseAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return PoolExpenseController
