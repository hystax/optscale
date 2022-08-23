import logging
from datetime import datetime

from optscale_exceptions.common_exc import (NotFoundException, FailedDependency,
                                            WrongArgumentsException)
from rest_api_server.controllers.base import (BaseController, MongoMixin,
                                              ClickHouseMixin)
from rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api_server.controllers.expense import ExpenseController
from rest_api_server.controllers.resource_constraint import (
    ConstraintBaseController
)
from rest_api_server.exceptions import Err
from rest_api_server.models.enums import ConstraintTypes
from rest_api_server.models.models import (Pool, PoolPolicy, CloudAccount,
                                           Employee)

LOG = logging.getLogger(__name__)
BULK_SIZE = 1000


class TtlAnalysisController(BaseController, MongoMixin, ClickHouseMixin):
    def _get_model_type(self):
        return Pool

    def _get_resource_expenses(self, pool_id, start_date, end_date):
        resources = list(self.resources_collection.find(
            {'pool_id': pool_id}, []))
        query = """
            SELECT resource_id, SUM(sign * cost)
            FROM expenses
            JOIN resources ON resource_id = resources._id
            WHERE date >= %(start_date)s
                AND date <= %(end_date)s
            GROUP BY resource_id
        """
        expenses = self.execute_clickhouse(
            query=query,
            external_tables=[{
                'name': 'resources',
                'structure': [('_id', 'String')],
                'data': resources
            }], params={
                'start_date': start_date,
                'end_date': end_date
            })
        return {e[0]: e[1] for e in expenses}

    def get(self, pool_id, start_date, end_date=None, ttl=None):
        pool = super().get(pool_id)
        if pool is None:
            raise NotFoundException(Err.OE0002, [Pool.__name__, pool_id])

        if end_date is None:
            end_date = int(datetime.utcnow().timestamp())

        if start_date > end_date:
            raise WrongArgumentsException(Err.OE0446, ['end_date', 'start_date'])

        if ttl is None:
            policy = self.session.query(PoolPolicy).filter(
                PoolPolicy.deleted.is_(False),
                PoolPolicy.pool_id == pool_id,
                PoolPolicy.type == ConstraintTypes.TTL,
            ).one_or_none()
            if policy:
                ttl = policy.limit
            else:
                raise FailedDependency(Err.OE0457, [])

        start_ts = start_date
        end_ts = end_date
        start_date = datetime.fromtimestamp(float(start_date))
        end_date = datetime.fromtimestamp(float(end_date))

        resource_expenses = self._get_resource_expenses(
            pool_id, start_date, end_date)
        resources_to_process = list(resource_expenses.keys())
        resource_tracked = len(resources_to_process)
        total_expenses = sum(resource_expenses.values())

        tmp_policy = PoolPolicy(
            type=ConstraintTypes.TTL,
            limit=ttl,
            active=True,
            pool_id=pool_id,
            organization_id=pool.organization_id,
        )
        constraint_ctrl = ConstraintBaseController(self.session, self._config,
                                                   self.token)

        outside_of_ttl = []
        for i in range(0, resource_tracked, BULK_SIZE):
            chunk = resources_to_process[i:i + BULK_SIZE]
            resources = {r['_id']: r for r in self.resources_collection.find({
                'last_seen': {'$gte': start_ts},
                '_id': {'$in': chunk},
                'active': True
            })}
            resource_id_expenses_map = ExpenseController(
                self._config).get_resource_expense_summary(list(resources.keys()))

            for resource_id, expense in resource_id_expenses_map.items():
                resource = resources.get(resource_id)
                last_seen_in_range = min(end_ts, resource['last_seen'])
                hit = constraint_ctrl.handle_resource(
                    expense, tmp_policy, last_seen_in_range)
                if hit is not None and hit['ttl_value']:
                    hours_outside_ttl = hit['ttl_value'] - ttl
                    resource_range_start = max(expense['mindate'], start_date)
                    last_seen_date = datetime.fromtimestamp(last_seen_in_range)
                    range_delta = last_seen_date - resource_range_start
                    hours_in_range = range_delta.total_seconds() // 3600
                    if hours_outside_ttl > hours_in_range:
                        hours_outside_ttl = hours_in_range

                    cost_in_range = resource_expenses.get(resource_id)
                    expense_per_hour = cost_in_range / hours_in_range
                    expenses_outside_of_ttl = expense_per_hour * hours_outside_ttl
                    outside_of_ttl.append({
                        'id': resource['_id'],
                        'cloud_resource_id': resource['cloud_resource_id'],
                        'name': resource.get('name'),
                        'type': resource['resource_type'],
                        'owner_id': resource['employee_id'],
                        'cloud_account_id': resource['cloud_account_id'],
                        'hours_outside_of_ttl': hours_outside_ttl,
                        'expenses_outside_of_ttl': expenses_outside_of_ttl,
                    })

        cloud_account_ids, owner_ids = set(), set()
        for resource in outside_of_ttl:
            cloud_account_ids.add(resource['cloud_account_id'])
            owner_ids.add(resource['owner_id'])

        cloud_accounts = self.session.query(CloudAccount).filter(
            CloudAccount.id.in_(list(cloud_account_ids))
        ).all()
        cloud_account_map = {ca.id: ca for ca in cloud_accounts}
        employees = self.session.query(Employee).filter(
            Employee.id.in_(list(owner_ids))
        ).all()
        employee_map = {e.id: e for e in employees}

        expenses_outside_of_ttl = 0
        for resource in outside_of_ttl:
            ca = cloud_account_map.get(resource['cloud_account_id'])
            owner = employee_map.get(resource['owner_id'])
            resource['owner_name'] = owner.name
            resource['cloud_account_name'] = ca.name
            resource['cloud_type'] = ca.type.value
            expenses_outside_of_ttl += resource['expenses_outside_of_ttl']

        return {
            "resources_tracked": resource_tracked,
            "resources_outside_of_ttl": len(outside_of_ttl),
            "total_expenses": total_expenses,
            "expenses_outside_of_ttl": expenses_outside_of_ttl,
            "resources": outside_of_ttl,
        }


class TtlAnalysisAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return TtlAnalysisController
