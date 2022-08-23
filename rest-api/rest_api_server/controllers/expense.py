import json
import logging
import re
from calendar import monthrange
from datetime import datetime, timedelta
from collections import defaultdict
from optscale_exceptions.common_exc import (FailedDependency, NotFoundException,
                                            WrongArgumentsException)
from rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api_server.exceptions import Err
from rest_api_server.models.models import (Organization, Pool, CloudAccount,
                                           Employee)
from sqlalchemy import and_

from rest_api_server.utils import get_nil_uuid, encode_string, encoded_tags
from rest_api_server.controllers.base import (BaseController,
                                              BaseHierarchicalController,
                                              MongoMixin, ClickHouseMixin,
                                              ResourceFormatMixin)

from cloud_adapter.cloud import Cloud as CloudAdapter

LOG = logging.getLogger(__name__)
NOT_SET_NAME = '(not set)'
DAY_IN_SECONDS = 86400


class ExpenseController(MongoMixin, ClickHouseMixin):

    def __init__(self, config=None):
        super().__init__()
        self._config = config

    def get_expenses_for_pools(self, start_date, end_date, pool_ids):
        return self.get_expenses(
            'pool_id', pool_ids, start_date, end_date, group_by='pool_id')

    def get_expenses(self, filter_field, filter_list, start_date, end_date,
                     group_by=None):
        return self._get_expenses_clickhouse(
            filter_field, filter_list, start_date, end_date, group_by)

    def _get_expenses_clickhouse(
            self, filter_field, filter_list, start_date, end_date,
            group_by=None):
        if not isinstance(filter_list, list):
            filter_list = list(filter_list)

        # TODO: this is super ugly, remove it
        resource_field_mappings = {
            # From expense field to resource field
            'owner_id': 'employee_id',
            'resource_id': '_id',
        }

        resource_fields = {'_id': 1, 'cloud_account_id': 1}
        if group_by:
            resource_fields[resource_field_mappings.get(
                group_by, group_by)] = 1
        resource_results = self.resources_collection.find({
            resource_field_mappings.get(
                filter_field, filter_field): {'$in': filter_list},
            'last_seen': {'$gte': int(start_date.timestamp())},
        }, resource_fields)

        external_resource_table = [{
            '_id': x['_id'],
            'cloud_account_id': x['cloud_account_id'],
            'group_field': x.get(resource_field_mappings.get(
                group_by, group_by))
        } for x in resource_results if x.get('cloud_account_id')]
        expenses_results = self.execute_clickhouse(
            query="""
                SELECT
                    date, group_field, SUM(cost * sign) AS total_cost
                FROM expenses
                JOIN resources ON expenses.resource_id = resources._id
                    AND expenses.cloud_account_id = resources.cloud_account_id
                WHERE date >= %(start_date)s
                    AND date <= %(end_date)s
                GROUP BY date, group_field
                HAVING SUM(sign) > 0
                ORDER BY total_cost DESC
            """,
            params={
                'start_date': start_date,
                'end_date': end_date,
            },
            external_tables=[{
                'name': 'resources',
                'structure': [
                    ('_id', 'String'),
                    ('cloud_account_id', 'String'),
                    ('group_field', 'Nullable(String)'),
                ],
                'data': external_resource_table
            }],
        )

        return [{
            '_id': {
                'date': x[0],
                group_by: x[1]
            },
            'cost': x[2]
        } for x in expenses_results]

    def get_cloud_expenses_with_resource_info(self, cloud_acc_list, start_date,
                                              end_date):
        pipeline = [
            {
                '$match': {
                    '$and': [
                        {'cloud_account_id': {'$in': cloud_acc_list}},
                        {'first_seen': {'$lt': int(end_date.timestamp())}},
                        {'last_seen': {'$gte': int(start_date.timestamp())}},
                    ]
                }
            },
            {
                '$group': {
                    '_id': '$cloud_account_id',
                    'count': {'$sum': 1}
                }
            }
        ]
        resource_counts = list(self.resources_collection.aggregate(pipeline))
        query = """
            SELECT cloud_account_id, SUM(cost * sign), count
            FROM expenses
            JOIN cloud_accounts
                ON expenses.cloud_account_id = cloud_accounts._id
            WHERE date >= %(start_date)s AND date < %(end_date)s
            GROUP BY cloud_account_id, count
        """
        return self.execute_clickhouse(
            query=query,
            params={
                'start_date': start_date,
                'end_date': end_date
            },
            external_tables=[{
                'name': 'cloud_accounts',
                'structure': [
                    ('_id', 'String'),
                    ('count', 'Int32')
                ],
                'data': resource_counts
            }],
        )

    def get_monthly_forecast(self, cost, month_cost, first_expense=None):
        today = datetime.today()
        month_start = today.replace(
                day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month_start = (month_start - timedelta(days=1)).replace(day=1)
        start_date = max(last_month_start, first_expense) if (
            first_expense) else last_month_start
        worked_days = (today - month_start).days
        forecast_days = (today - start_date).days
        daily_forecast = cost / forecast_days if forecast_days > 0 else cost
        _, days_in_month = monthrange(today.year, today.month)
        forecast = month_cost + daily_forecast * (days_in_month - worked_days)
        return round(forecast, 2)

    def _get_first_cloud_account_expense(self, cloud_account_ids, date,
                                         field=None, values=None):
        if (field and not values) or not cloud_account_ids:
            return []
        if field and re.search(r'[^_A-Za-z0-9]', field):
            raise ValueError('Suspected SQL injection ')
        query = f"""
            SELECT {field if field else 'cloud_account_id'}, min(date)
            FROM expenses
            WHERE cloud_account_id
                IN cloud_account_ids{' AND %s IN values' %
                                     field if field else ''}
                AND date >= %(date)s
            GROUP BY cloud_account_id{', %s' % field if field else ''}
        """
        external_tables = [
            {
                'name': 'cloud_account_ids',
                'structure': [('id', 'String')],
                'data': [{'id': r_id} for r_id in cloud_account_ids]
            }
        ]
        if values:
            external_tables.append({
                'name': 'values',
                'structure': [('id', 'String')],
                'data': [{'id': r_id} for r_id in values]
            })
        return self.execute_clickhouse(
            query=query,
            params={
                'date': date
            },
            external_tables=external_tables
        )

    def get_first_expenses_for_forecast(self, field, values):
        prev_month_start = (datetime.utcnow().replace(day=1) - timedelta(
            days=1)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if field in ['cloud_account_id']:
            result = self._get_first_cloud_account_expense(
                values, prev_month_start)
        else:
            # TODO: Not the optimal solution to get expenses dates.
            #  We can get all the necessary dates at the time of receiving the
            #  expenses for the previous month
            resources = list(self.resources_collection.find(
                {field: {'$in': values}, 'cloud_account_id': {'$ne': None}},
                ['cloud_account_id', field]))
            r_ids = list(map(lambda x: x['_id'], resources))
            cloud_account_ids = set(
                map(lambda x: x.get('cloud_account_id'), resources))
            expenses = self._get_first_cloud_account_expense(
                list(cloud_account_ids), prev_month_start, 'resource_id',
                r_ids)
            expenses_map = {e[0]: e[1] for e in expenses}
            result = {}
            for resource in resources:
                value = resource.get(field)
                date = expenses_map.get(resource['_id'])
                if not date:
                    continue
                if value not in result or result[value] > date:
                    result[value] = date
            result = [(k, v) for k, v in result.items()]
        return {r[0]: r[1] for r in result}

    def get_raw_expenses(self, start_date, end_date, filters):
        match_filters = [{'start_date': {'$lt': end_date}}]
        if start_date:
            match_filters.append({'start_date': {'$gte': start_date}})
        nil_uuid = get_nil_uuid()
        for filter_key, filter_values in filters.items():
            for n, filter_value in enumerate(filter_values):
                if filter_value == nil_uuid:
                    filter_values[n] = None
            match_filter = {
                filter_key: {'$in': filter_values}
            }
            match_filters.append(match_filter)
        pipeline = [
            {'$match': {'$and': match_filters}}
        ]
        return self.raw_expenses_collection.aggregate(pipeline)

    def get_traffic_expenses_summary(self, resources):
        external_table = []
        for r in resources:
            cloud_resource_id = r.get('cloud_resource_id')
            cloud_account_id = r.get('cloud_account_id')
            if not cloud_resource_id or not cloud_account_id:
                continue
            external_table.append({
                'id': r['_id'],
                'cloud_account_id': cloud_account_id,
                'resource_id': cloud_resource_id
            })
        traffic_expenses = self.execute_clickhouse(
            query="""
                SELECT resources.id, sum(cost*sign), sum(usage*sign)
                FROM traffic_expenses
                JOIN resources
                    ON traffic_expenses.resource_id = resources.resource_id
                    AND traffic_expenses.cloud_account_id =
                        resources.cloud_account_id
                WHERE cloud_account_id in %(cloud_account_ids)s
                GROUP BY resources.id
            """,
            params={
                'cloud_account_ids': list(set([
                    r['cloud_account_id'] for r in external_table
                ]))
            },
            external_tables=[{
                'name': 'resources',
                'structure': [
                    ('id', 'String'),
                    ('cloud_account_id', 'String'),
                    ('resource_id', 'String')
                ],
                'data': external_table
            }]
        )
        return {
            res_id: {'cost': cost, 'usage': usage}
            for res_id, cost, usage in traffic_expenses
        }

    def get_resource_expense_summary(self, resource_ids,
                                     join_traffic_expenses=False):
        if not resource_ids:
            return {}
        summary_fields = [
            'cloud_resource_id', 'service_name', 'cloud_account_id', 'region',
            'resource_type', 'pool_id', 'created_at', 'last_seen',
            'first_seen', 'total_cost'
        ]
        resources = self.resources_collection.find(
            {'_id': {'$in': resource_ids}}, summary_fields)
        resources_map = {r['_id']: r for r in resources}
        traffic_expenses = self.get_traffic_expenses_summary(
            resources_map.values()) if join_traffic_expenses else {}
        self._update_summary(resources_map, traffic_expenses)
        return resources_map

    @staticmethod
    def _update_summary(resources_map, traffic_expenses):
        for r_id, resource in resources_map.items():
            total_cost = resource.get('total_cost', 0)
            res_created = datetime.fromtimestamp(resource.pop('created_at', 0))
            mindate_ts = resource.get('first_seen')
            mindate = datetime.utcfromtimestamp(
                mindate_ts) if mindate_ts else res_created
            maxdate_ts = resource.get('last_seen')
            maxdate = datetime.utcfromtimestamp(
                maxdate_ts) if maxdate_ts else res_created
            resource.update({
                '_id': {'resource_id': r_id},
                'resource_id': r_id,
                'maxdate': maxdate,
                'mindate': mindate,
                'total_cost': total_cost
            })
            traffic_expense = traffic_expenses.get(r_id)
            if traffic_expense:
                resource.update({
                    'total_traffic_expenses': traffic_expense['cost'],
                    'total_traffic_usage': traffic_expense['usage']
                })

    def delete_cloud_expenses(self, cloud_account_id):
        self.execute_clickhouse(
            'ALTER TABLE expenses DELETE WHERE cloud_account_id=%(ca_id)s',
            params={'ca_id': cloud_account_id})


class FormattedExpenseController(BaseController):
    GROUPING_FIELD = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id_pool_map = None

    def get_hierarchy_down(self, pool_id):
        return BaseHierarchicalController(
            self.session, self._config, self.token
        ).get_item_hierarchy('id', pool_id, 'parent_id',
                             Pool, include_item=True)

    def fill_id_pool_map(self, pool):
        result = self.get_hierarchy_down(pool.id)
        pool_ids = list(map(lambda x: x.id, result))

        self.id_pool_map = {pool.id: pool.to_dict()
                            for pool in result}
        return pool_ids

    @property
    def expense_ctrl(self):
        return ExpenseController(self._config)

    def get_filter_params(self, obj):
        raise NotImplementedError

    def get_result_base(self, obj, prev_start_ts):
        return {
            'expenses': {
                'total': 0,
                'previous_total': 0,
                'previous_range_start': prev_start_ts,
                'id': obj.id,
                'name': obj.name,
                'breakdown': {},
            }
        }

    def get_formatted_result(self, db_result, obj, starting_time, prev_start_ts):
        result = self.get_result_base(obj, prev_start_ts)
        for group in db_result:
            if group['_id']['date'] >= starting_time:
                result['expenses']['total'] += group['cost']
                date = str(int(group['_id']['date'].timestamp()))
                result['expenses']['breakdown'][date] = group['cost']
            else:
                result['expenses']['previous_total'] += group['cost']
        return result

    def _get_organization_id(self, obj):
        if isinstance(obj, list) and len(obj) > 0:
            return getattr(obj[0], 'organization_id', None)
        else:
            return getattr(obj, 'organization_id', None)

    def get_formatted_expenses(self, obj, start_date, end_date):
        field, filter_list = self.get_filter_params(obj)
        start = datetime.fromtimestamp(start_date)
        end = datetime.fromtimestamp(end_date)
        delta = self.get_delta(end, end_date, start, start_date)

        previous_start = start - delta
        db_result = list(self.expense_ctrl.get_expenses(
            field, filter_list, previous_start, end,
            group_by=self.GROUPING_FIELD
        ))
        prev_start_ts = int(previous_start.timestamp())
        return self.get_formatted_result(db_result, obj, start, prev_start_ts)

    def get_delta(self, end, end_date, start, start_date):
        if (end_date - start_date) % 24 * 3600 != 0:
            delta = timedelta((end - start).days + 1)
        else:
            delta = timedelta((end - start).days)
        return delta


class FilteredFormattedExpenseController(FormattedExpenseController):
    FILTER_NAME = None

    def get_info_map(self, db_result, obj):
        raise NotImplementedError

    def get_breakdown_group_base(self, info):
        return {
            'id': info['id'],
            'name': info['name'],
        }

    def get_breakdown_group_day(self, info, cost):
        base = self.get_breakdown_group_base(info)
        base['expense'] = cost
        return base

    def get_breakdown_group_type(self, info):
        base = self.get_breakdown_group_base(info)
        base['total'] = info.get('cost', 0)
        base['previous_total'] = info.get('previous_cost', 0)
        return base

    def show_expenses_for_all_days(self, result):
        pass

    def get_formatted_result(self, db_result, obj, starting_time, prev_start_ts):
        result = self.get_result_base(obj, prev_start_ts)
        info_map = self.get_info_map(db_result, obj)

        for group in db_result:
            _id = group.get('_id', {}).get(self.GROUPING_FIELD)
            if not info_map.get(_id):
                continue

            if group['_id']['date'] >= starting_time:
                result['expenses']['total'] += group['cost']
                if 'cost' not in info_map[_id]:
                    info_map[_id]['cost'] = 0
                info_map[_id]['cost'] += group['cost']
            else:
                result['expenses']['previous_total'] += group['cost']
                if 'previous_cost' not in info_map[_id]:
                    info_map[_id]['previous_cost'] = 0
                info_map[_id]['previous_cost'] += group['cost']
                continue

            date = str(int(group['_id']['date'].timestamp()))
            if date not in result['expenses']['breakdown']:
                result['expenses']['breakdown'][date] = []

            info_map_id = info_map[_id]
            expense_for_current_date = next((expense for expense in result['expenses']['breakdown'][date]
                                             if expense['id'] == info_map_id['id']), None)
            if expense_for_current_date:
                expense_for_current_date['expense'] += group['cost']
            else:
                result['expenses']['breakdown'][date].append(
                    self.get_breakdown_group_day(info_map_id, group['cost'])
                )

        self.show_expenses_for_all_days(result)
        result['expenses'][self.FILTER_NAME] = sorted(
            [self.get_breakdown_group_type(info)
             for info in {x['id']: x for x in info_map.values()}.values()
             if info.get('cost', 0) != 0],
            key=lambda x: x['total'], reverse=True)
        return result


class PoolFormattedExpenseController(FormattedExpenseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id_pool_map = None
        self._cloud_map = None

    def get_filter_params(self, obj):
        if obj.parent_id is not None:
            db_filter_field = 'pool_id'
            db_filter_list = self.fill_id_pool_map(obj)
        else:
            db_filter_field = 'cloud_account_id'
            clouds = self.session.query(CloudAccount).filter(and_(
                CloudAccount.organization_id == obj.organization_id,
                CloudAccount.deleted.is_(False)
            )).order_by(CloudAccount.created_at).all()

            self._cloud_map = {x.id: x.to_dict() for x in clouds}
            # keeping consistent order to simplify unit testing
            db_filter_list = [x.id for x in clouds]
        return db_filter_field, db_filter_list


class CloudFilteredFormattedExpenseController(FilteredFormattedExpenseController):
    GROUPING_FIELD = 'cloud_account_id'
    FILTER_NAME = 'cloud'

    def get_cloud_map(self, db_result):
        cloud_ids = set([x.get('_id', {}).get(self.GROUPING_FIELD) for x in db_result])
        return {
            cloud.id: cloud.to_dict()
            for cloud in self.session.query(CloudAccount).filter(and_(
                CloudAccount.id.in_(cloud_ids),
                CloudAccount.deleted.is_(False)
            )).all()
        }

    def get_info_map(self, db_result, obj):
        return self.get_cloud_map(db_result)

    def get_breakdown_group_base(self, info):
        base = super().get_breakdown_group_base(info)
        base['type'] = info['type']
        return base


class CloudFilteredPoolFormattedExpenseController(
    CloudFilteredFormattedExpenseController, PoolFormattedExpenseController
):
    def get_info_map(self, db_result, obj):
        if self._cloud_map is None:
            self._cloud_map = self.get_cloud_map(db_result)
        return self._cloud_map


class PoolFilteredExpenseController(FilteredFormattedExpenseController):
    GROUPING_FIELD = 'pool_id'
    FILTER_NAME = 'pool'

    def get_breakdown_group_base(self, info):
        base = super().get_breakdown_group_base(info)
        base['purpose'] = info.get('purpose')
        return base

    def get_info_map(self, db_result, obj):
        if self.id_pool_map is None:
            self.fill_id_pool_map(obj)
        nil_uuid = get_nil_uuid()
        self.id_pool_map[None] = {
            'id': nil_uuid,
            'name': NOT_SET_NAME,
            'purpose': NOT_SET_NAME,
            'cost': 0,
        }
        return self.id_pool_map


class PoolExpensesExportFilteredExpenseController(PoolFilteredExpenseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.all_day_starts = None

    @staticmethod
    def _get_all_day_starts(start_date, delta):
        all_day_starts = list()
        start = datetime.fromtimestamp(start_date)
        day_start = start.replace(hour=0, minute=0, second=0)
        delta_days = delta.days
        if start == day_start:
            all_day_starts.append(start_date)
            delta_days = delta_days - 1
        for i in range(delta_days):
            all_day_starts.append(int(datetime.timestamp(day_start + timedelta(days=i + 1))))
        all_day_starts.sort()
        return all_day_starts

    def show_expenses_for_all_days(self, result):
        not_existing_dates = list(
            set(self.all_day_starts) - set(int(key) for key in result['expenses']['breakdown'].keys())
        )
        not_existing_dates.sort()
        for not_existing_date in not_existing_dates:
            result['expenses']['breakdown'][not_existing_date] = [self.get_breakdown_group_day(
                {'id': get_nil_uuid(), 'name': '(not set)'}, float(0))]

    def get_formatted_expenses(self, obj, start_date, end_date):
        start = datetime.fromtimestamp(start_date)
        end = datetime.fromtimestamp(end_date)
        delta = self.get_delta(end, end_date, start, start_date)
        self.all_day_starts = self._get_all_day_starts(start_date, delta)
        return super().get_formatted_expenses(obj, start_date, end_date)


class PoolFilteredPoolFormattedExpenseController(
    PoolFilteredExpenseController,
    PoolFormattedExpenseController,
):
    pass


class PoolExpensesExportFilteredPoolFormattedExpenseController(
    PoolExpensesExportFilteredExpenseController,
    PoolFormattedExpenseController
):
    pass


class EmployeeFilteredExpenseController(FilteredFormattedExpenseController):
    GROUPING_FIELD = 'owner_id'
    FILTER_NAME = 'employee'

    def get_info_map(self, db_result, obj):
        employee_ids = set([x.get('_id', {}).get(self.GROUPING_FIELD) for x in db_result])
        employee_map = {
            e.id: e.to_dict()
            for e in self.session.query(Employee).filter(and_(
                Employee.id.in_(employee_ids),
                Employee.deleted.is_(False)
            )).all()
        }
        nil_uuid = get_nil_uuid()
        employee_map[None] = {
            'id': nil_uuid,
            'name': NOT_SET_NAME,
            'cost': 0,
        }
        return employee_map


class EmployeeFilteredPoolFormattedExpenseController(
    EmployeeFilteredExpenseController,
    PoolFormattedExpenseController,
):
    pass


class CloudFormattedExpenseController(FormattedExpenseController):
    def get_filter_params(self, obj):
        return 'cloud_account_id', [obj.id]

    def get_result_base(self, obj, prev_start):
        res = super().get_result_base(obj, prev_start)
        res['expenses']['type'] = obj.type.value
        return res


class EmployeeFormattedExpenseController(FormattedExpenseController):
    def get_filter_params(self, obj):
        return 'owner_id', [obj.id]


class ExpenseOnlyInfoMixin:
    def get_info_map(self, db_result, obj):
        group_names = set([x.get('_id', {}).get(self.GROUPING_FIELD) for x in db_result])
        info_map = {}
        for name in group_names:
            if name is None:
                info_map[None] = {
                    'name': NOT_SET_NAME,
                    'id': get_nil_uuid(),
                    'cost': 0,
                }
            else:
                info_map[name] = {
                    'name': name,
                    'id': name,
                    'cost': 0,
                }
        return info_map


class ServiceFilteredCloudFormattedExpenseController(
    ExpenseOnlyInfoMixin,
    FilteredFormattedExpenseController,
    CloudFormattedExpenseController,
):
    GROUPING_FIELD = 'service_name'
    FILTER_NAME = 'service'


class RegionFilteredCloudFormattedExpenseController(
    ExpenseOnlyInfoMixin,
    FilteredFormattedExpenseController,
    CloudFormattedExpenseController,
):
    GROUPING_FIELD = 'region'
    FILTER_NAME = 'region'


class NodeFilteredCloudFormattedExpenseController(
    ExpenseOnlyInfoMixin,
    FilteredFormattedExpenseController,
    CloudFormattedExpenseController,
):
    GROUPING_FIELD = 'k8s_node'
    FILTER_NAME = 'k8s_node'


class NamespaceFilteredCloudFormattedExpenseController(
    ExpenseOnlyInfoMixin,
    FilteredFormattedExpenseController,
    CloudFormattedExpenseController,
):
    GROUPING_FIELD = 'k8s_namespace'
    FILTER_NAME = 'k8s_namespace'


class K8sServiceFilteredCloudFormattedExpenseController(
    ExpenseOnlyInfoMixin,
    FilteredFormattedExpenseController,
    CloudFormattedExpenseController,
):
    GROUPING_FIELD = 'k8s_service'
    FILTER_NAME = 'k8s_service'


class ResourceTypeFilteredCloudFormattedExpenseController(
    ExpenseOnlyInfoMixin,
    FilteredFormattedExpenseController,
    CloudFormattedExpenseController,
):
    GROUPING_FIELD = 'resource_type'
    FILTER_NAME = 'resource_type'


class EmployeeFilteredCloudFormattedExpenseController(
    EmployeeFilteredExpenseController,
    CloudFormattedExpenseController,
):
    pass


class PoolChildMixin:
    def fill_id_pool_map(self, obj):
        return super().fill_id_pool_map(obj.organization.pool)


class PoolFilteredCloudFormattedExpenseController(
    PoolChildMixin,
    PoolFilteredExpenseController,
    CloudFormattedExpenseController,
):
    pass


class CloudFilteredEmployeeFormattedExpenseController(
    CloudFilteredFormattedExpenseController,
    EmployeeFormattedExpenseController,
):
    pass


class PoolFilteredEmployeeFormattedExpenseController(
    PoolChildMixin,
    PoolFilteredExpenseController,
    EmployeeFormattedExpenseController,
):
    pass


class OrgCloudAccMixin:
    def get_organization_and_cloud_accs(self, organization_id):
        organization_cloud_acc_set = self.session.query(
            Organization, CloudAccount
        ).outerjoin(CloudAccount, and_(
            CloudAccount.organization_id == Organization.id,
            CloudAccount.deleted.is_(False)
        )).filter(
            Organization.id == organization_id,
            Organization.deleted.is_(False),
        ).all()
        organization, organization_cloud_acc = None, []
        for set_item in organization_cloud_acc_set:
            org, cloud_acc = set_item
            if not organization:
                organization = org
            if cloud_acc:
                organization_cloud_acc.append(cloud_acc)
        if not organization:
            raise NotFoundException(
                Err.OE0002, ['Organization', organization_id])
        if not organization_cloud_acc:
            raise FailedDependency(Err.OE0445,
                                   [organization.name, organization.id])
        return organization, organization_cloud_acc


class CleanExpenseController(BaseController, MongoMixin, ClickHouseMixin,
                             ResourceFormatMixin, OrgCloudAccMixin):
    EXPENSES_KEY = 'clean_expenses'
    JOIN_TRAFFIC_EXPENSES = True
    CHECKED_FILTERS = {
        'pool_id': Pool,
        'cloud_account_id': CloudAccount,
        'owner_id': Employee
    }
    # resource to entity fields accordance
    # entity_name: resource_field, entity_map_field, joined fields
    JOINED_ENTITY_MAP = {
        'cloud_account': ('cloud_account_id', 'cloud_account_id',
                          ['id', 'name', 'type']),
        'owner': ('employee_id', 'owner_id', ['id', 'name']),
        'pool': ('pool_id', 'pool_id', ['id', 'name', 'purpose'])
    }
    WITH_SUBPOOLS_SIGN = '+'
    IDENTITY_DELIMITER = ':'

    REGULAR_IDENTITY = 'regular'
    CLUSTER_IDENTITY = 'cluster'
    ENVIRONMENT_IDENTITY = 'environment'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_date = None
        self.end_date = None

    def join_db_info(self, resources_map, expenses, organization_id,
                     organization_cloud_acc):
        entities = self._get_join_entities(
            organization_id, organization_cloud_acc, resources_map)
        expenses_data = self._fill_expenses_data(
            expenses, entities)
        return expenses_data

    @staticmethod
    def _extend_expense(expense, entities):
        for key in ['cloud_account_id', 'resource_id']:
            value = expense.get(key)
            if not value:
                continue
            entity = entities.get(key, {}).get(value)
            if not entity:
                continue
            for replaced_key in ['name', 'type']:
                entity_v = entity.get(replaced_key)
                if entity_v:
                    e_key = key.replace("id", replaced_key)
                    expense.update({e_key: entity_v})
        key_map = {
            'owner_id': (
                'owner', expense.get('employee_id'), ['id', 'name']),
            'pool_id': (
                'pool', expense.get('pool_id'), ['id', 'name', 'purpose'])
        }
        for key, (entity_name, entity_value, entity_keys) in key_map.items():
            expense[entity_name] = None
            entity = entities.get(key, {}).get(entity_value)
            if not entity or not entity.get('name'):
                continue
            expense[entity_name] = {
                entity_key: entity.get(
                    entity_key) for entity_key in entity_keys
            }
        expense['resource_id'] = expense['id']
        expense['resource_name'] = expense.pop('name', None)
        expense['active'] = expense.get('active', False)
        expense['is_environment'] = expense.get('is_environment', False)
        expense['shareable'] = expense.get('shareable', False)
        expense['saving'] = expense.get('saving', 0)
        expense['constraint_violated'] = expense.get(
            'constraint_violated', False)
        expense['tags'] = expense.get('tags', {})

    @staticmethod
    def _get_total_saving(resources_map):
        total_saving = 0
        for resource_id, resource in resources_map.items():
            if resource.get('cluster_id'):
                # will be processed as a part of cluster record
                continue
            total_saving += resource['saving']
        return {'total_saving': total_saving}

    def _fill_expenses_data(self, expenses, entities):
        result_expenses = {}
        expenses_map = {e['resource_id']: e for e in expenses}
        for resource_id, resource in entities.get('resource_id', {}).items():
            if resource.get('cluster_id'):
                # will be processed as a part of cluster record
                continue
            expense = expenses_map.get(resource_id, {})
            resource['cost'] = expense.get('cost', 0)
            self._extend_expense(resource, entities)
            result_expenses[resource_id] = resource
        expenses = sorted(list(result_expenses.values()),
                          key=lambda x: x['cost'], reverse=True)
        return {
            self.EXPENSES_KEY: expenses,
        }

    def _get_cluster_entities(self, resources_map):
        res = {}
        for r_id, r_val in resources_map.items():
            if r_val.get('cluster_id'):
                if resources_map.get(r_val['cluster_id']):
                    res[r_val['cluster_id']] = resources_map[r_val['cluster_id']]
        return res

    def _get_join_entities(self, organization_id, organization_cloud_acc,
                           resources_map=None):
        result = {
            'cloud_account_id': {
                cloud_acc.id: cloud_acc.to_dict(
                    secure=True) for cloud_acc in organization_cloud_acc
            },
            'owner_id': self._get_object_entities(organization_id, Employee),
            'pool_id': self._get_object_entities(organization_id, Pool),
        }
        if resources_map:
            result.update({
                'cluster_id': self._get_cluster_entities(resources_map),
                'resource_id': resources_map
            })
        return result

    def get_clustered_expenses(self, cloud_account_ids, clustered_resources_map,
                               start_date, end_date):
        expenses, total_cost = self.get_expenses(
            cloud_account_ids, list(clustered_resources_map.keys()),
            start_date, end_date)
        processed_expenses = self._process_clustered_expenses(
            expenses, clustered_resources_map)
        return processed_expenses, total_cost

    def _process_clustered_expenses(self, expenses, clustered_resources_map):
        result = {}
        for e in expenses:
            r_id = e['resource_id']
            cluster_id = clustered_resources_map.get(r_id)
            if cluster_id not in result:
                result[cluster_id] = {'resource_id': cluster_id, 'cost': 0}
            result[cluster_id]['cost'] += e.get('cost', 0)
        return list(result.values())

    def get_expenses(self, cloud_account_ids, resource_ids, start_date,
                     end_date, limit=None) -> tuple:
        return self._get_expenses_clickhouse(
            cloud_account_ids, resource_ids, start_date, end_date, limit)

    def _get_expenses_clickhouse(self, cloud_account_ids, resource_ids,
                                 start_date, end_date, limit) -> tuple:
        query = """
            SELECT
                cloud_account_id,
                resource_id,
                SUM(cost * sign) AS total_cost
            FROM expenses
            WHERE cloud_account_id IN cloud_account_ids
                AND resource_id IN resource_ids
                AND date >= %(start_date)s
                AND date <= %(end_date)s
            GROUP BY cloud_account_id, resource_id
            WITH TOTALS
            HAVING SUM(sign) > 0
            ORDER BY total_cost DESC
        """
        if limit:
            query += 'LIMIT %(limit)s'
        result = self.execute_clickhouse(
            query=query,
            params={
                'start_date': start_date,
                'end_date': end_date,
                'limit': limit
            },
            external_tables=[
                {
                    'name': 'resource_ids',
                    'structure': [('_id', 'String')],
                    'data': [{'_id': r_id} for r_id in resource_ids]
                },
                {
                    'name': 'cloud_account_ids',
                    'structure': [('_id', 'String')],
                    'data': [{'_id': r_id} for r_id in cloud_account_ids]
                }
            ],
        )
        totals = result.pop(-1)
        return [{
            'cloud_account_id': x[0],
            'resource_id': x[1],
            'cost': x[2]
        } for x in result], totals[2]

    def _get_object_entities(self, organization_id, model):
        objects = self.session.query(model).filter(
            model.organization_id == organization_id,
            model.deleted.is_(False)
        ).all()
        return {x.id: x.to_dict() for x in objects}

    def get_pools_children(self, pool_ids):
        res = set()
        bhc = BaseHierarchicalController(
            self.session, self._config, self.token)
        for pool_id in pool_ids:
            children = bhc.get_item_hierarchy(
                'id', pool_id, 'parent_id', Pool, True)
            res.update(map(lambda x: x.id, children))
        return list(res)

    def _split_params(self, organization_id, params):
        pool_ids_excl, pool_ids_incl = self.get_pool_ids_excl_incl(
            params.get('pool_id'))
        pool_ids = pool_ids_excl
        pool_ids.extend(self.get_pools_children(pool_ids_incl))
        if pool_ids:
            params['pool_id'] = list(set(pool_ids))
        if params.get('owner_id'):
            params['employee_id'] = params.pop('owner_id')
        nil_uuid = get_nil_uuid()
        if not params.get('cloud_account_id'):
            _, cloud_accs = self.get_organization_and_cloud_accs(
                organization_id)
            params['cloud_account_id'] = list(map(
                lambda x: x.id, cloud_accs)) + [nil_uuid]

        for filter_name in ['tag', 'without_tag']:
            tags = params.pop(filter_name, [])
            if tags:
                params[filter_name] = []
                for t in tags:
                    if t != nil_uuid:
                        params[filter_name].append(encode_string(t))
                    else:
                        params[filter_name].append(t)

        extra = {'active', 'recommendations', 'constraint_violated',
                 'service_name', 'created_by_kind', 'created_by_name',
                 'k8s_namespace', 'k8s_node', 'k8s_service', 'traffic_from',
                 'traffic_to'}
        other_filters = {}
        for f_key in extra:
            f_val = params.pop(f_key, None)
            if f_val is not None:
                if isinstance(f_val, list):
                    for i, v in enumerate(f_val):
                        if v == nil_uuid:
                            f_val[i] = None
                other_filters[f_key] = f_val
        return params, other_filters, {}

    def split_params(self, organization_id, params):
        query_filters, data_filters, extra_filters = self._split_params(
            organization_id, params)
        extra_filters['limit'] = query_filters.pop('limit', None)
        return query_filters, data_filters, extra_filters

    @staticmethod
    def _transform_regex(regex_val):
        return re.escape(regex_val).replace(r'\*', r'.*').replace(r'\?', r'.?')

    def _parse_filter_with_type(self, value):
        """Parse resource type string.

        :param str value: filter value in
            name:identity format.
        :returns: tuple with resource_type and identity.
        """
        return value.rsplit(self.IDENTITY_DELIMITER, 1)

    def get_resource_type_condition(self, resource_types):
        if not resource_types:
            return []

        identity_resource_types_map = defaultdict(list)
        for resource_type in resource_types:
            try:
                type_, identity = self._parse_filter_with_type(resource_type)
            except ValueError:
                raise WrongArgumentsException(
                    Err.OE0218, ['resource_type', resource_type])
            if identity not in [self.REGULAR_IDENTITY, self.CLUSTER_IDENTITY,
                                self.ENVIRONMENT_IDENTITY]:
                raise WrongArgumentsException(Err.OE0499, [])
            identity_resource_types_map[identity].append(type_)

        type_filters = []
        for identity, resource_types in identity_resource_types_map.items():
            resource_type_cond = {
                'cluster_type_id': {'$exists': False},
                'cluster_id': {'$exists': False},
                'is_environment': {'$ne': True},
                'resource_type': {'$in': resource_types}
            }
            if identity == self.CLUSTER_IDENTITY:
                resource_type_cond.pop('cluster_type_id')
                resource_type_cond.pop('cluster_id')
                resource_type_cond['$or'] = [
                    {'cluster_type_id': {'$exists': True}},
                    {'cluster_id': {'$exists': True}}
                ]
            elif identity == self.ENVIRONMENT_IDENTITY:
                resource_type_cond['is_environment'] = True
            type_filters.append({'$and': [resource_type_cond]})

        return type_filters

    def _aggregate_resource_data(self, match_query, **kwargs):
        group_stage = {
            '_id': {
                'cloud_account_id': '$cloud_account_id',
                'cluster_id': '$cluster_id',
                'day': {'$trunc': {
                    '$divide': ['$first_seen', DAY_IN_SECONDS]}},
            },
            'resources': {'$addToSet': '$_id'},
        }
        return self.resources_collection.aggregate([
            {'$match': match_query},
            {'$group': group_stage}
        ], allowDiskUse=True)

    def generate_filters_pipeline(self, organization_id, start_date,
                                  end_date, params, data_filters):
        nil_uuid = get_nil_uuid()
        main_filters = {}
        cloud_account_ids = params.pop('cloud_account_id')
        for cloud_account_id in cloud_account_ids:
            # dict is unhashable so collect via dict
            if cloud_account_id == nil_uuid:
                main_filters[True] = {'$and': [
                    {'organization_id': organization_id},
                    {'cloud_account_id': None}
                ]}
            else:
                main_filters[False] = {'cloud_account_id': {'$in': cloud_account_ids}}
        query = {
            '$and': [
                {'$or': list(main_filters.values())},
                {'first_seen': {'$lte': end_date}},
                {'last_seen': {'$gte': start_date}},
                {'deleted_at': 0}
            ]
        }
        resource_type_condition = self.get_resource_type_condition(
            params.pop('resource_type', []))
        if resource_type_condition:
            query['$and'].append({'$or': resource_type_condition})

        for filter_name in ['tag', 'without_tag']:
            tag_params = params.pop(filter_name, None)
            empty_cond = {} if filter_name == 'tag' else {'$ne': {}}
            filled_cond = filter_name == 'tag'
            if tag_params:
                tag_filter = []
                for v in tag_params:
                    if v == nil_uuid:
                        tag_filter.append({'tags': empty_cond})
                    else:
                        tag_filter.append(
                            {'tags.%s' % v: {'$exists': filled_cond}})
                query['$and'].append({'$or': tag_filter})

        for regex_key, query_key in {
            'name_like': 'name',
            'cloud_resource_id_like': 'cloud_resource_id'
        }.items():
            regex_val = params.pop(regex_key, None)
            if regex_val:
                query_val = self._transform_regex(regex_val)
                query['$and'].append({
                    query_key: {'$regex': query_val, '$options': 'i'}
                })

        for filter_key, filter_values in params.items():
            for n, filter_value in enumerate(filter_values):
                if filter_value == nil_uuid:
                    filter_values[n] = None
            query['$and'].append({filter_key: {'$in': filter_values}})

        for string_field in [
            'service_name', 'created_by_kind', 'created_by_name',
            'k8s_namespace', 'k8s_node', 'k8s_service', 'cloud_resource_id'
        ]:
            name_set = data_filters.get(string_field)
            if name_set is not None:
                query['$and'].append(
                    {string_field: {'$in': list(set(name_set))}})

        for bool_field in ['active', 'constraint_violated']:
            bool_value = data_filters.get(bool_field)
            if bool_value is not None:
                value = True if bool_value else {'$ne': True}
                query['$and'].append({bool_field: value})

        recommend_filter = data_filters.get('recommendations')
        if recommend_filter is not None:
            last_run = self.get_last_run_ts_by_org_id(organization_id)
            if recommend_filter:
                query['$and'].append({
                    'recommendations.run_timestamp': {'$gte': last_run}
                })
            else:
                query['$and'].append({'$or': [
                    {'recommendations': None},
                    {'recommendations.run_timestamp': {'$lt': last_run}}
                ]})
        return query

    def get_resources_data(self, organization_id, query_filters, data_filters,
                           extra_params):
        query = self.generate_filters_pipeline(
            organization_id, self.start_date, self.end_date, query_filters,
            data_filters)
        return self._aggregate_resource_data(query, **extra_params)

    def _get_resources_base(self, resource_ids, cloud_account_ids,
                            organization_id):
        resources = self.resources_collection.find({
            '_id': {'$in': resource_ids},
            '$or': [
                {'cloud_account_id': {'$in': cloud_account_ids}},
                {'organization_id': organization_id}
            ]
        })
        return resources

    def get_resources(self, organization_id, cloud_account_ids,
                      resource_ids, clustered_resources_map):
        resources = self._get_resources_base(resource_ids, cloud_account_ids,
                                             organization_id)
        res = {}
        last_run = self.get_last_run_ts_by_org_id(organization_id)
        cluster_id_resources_map = defaultdict(list)
        for resource_id, cluster_id in clustered_resources_map.items():
            cluster_id_resources_map[cluster_id].append(resource_id)
        for r in resources:
            formatted_r = self.format_resource(r, last_run)
            res[formatted_r['id']] = formatted_r
        for cluster_id, resources in cluster_id_resources_map.items():
            cluster = res.get(cluster_id)
            if not cluster:
                continue
            saving = 0
            for r_id in resources:
                saving += res.get(r_id, {}).get('saving', 0)
            if saving:
                cluster['saving'] = saving
        return res

    def check_filters(self, filters, organization_id):
        exists_filters = list(filter(
            lambda x: x in filters.keys(), self.CHECKED_FILTERS.keys()))
        for current_filter in exists_filters:
            extra_ids = self.check_existence(
                filters[current_filter], self.CHECKED_FILTERS[current_filter],
                organization_id)
            if extra_ids:
                raise NotFoundException(
                    Err.OE0470, [current_filter, extra_ids])

    def get_pool_ids_excl_incl(self, ids):
        if isinstance(ids, list):
            pool_ids_excl = [x for x in ids if not x.endswith(
                self.WITH_SUBPOOLS_SIGN)]
            pool_ids_incl = [x.removesuffix(
                self.WITH_SUBPOOLS_SIGN) for x in ids if x.endswith(
                self.WITH_SUBPOOLS_SIGN)]
            return pool_ids_excl, pool_ids_incl
        else:
            return [], []

    def check_existence(self, ids, model, organization_id):
        check_ids = ids
        if model == Pool:
            pool_ids_excl, pool_ids_incl = self.get_pool_ids_excl_incl(ids)
            check_ids = pool_ids_incl + pool_ids_excl
        found = self.session.query(model.id).filter(
            model.id.in_(check_ids),
            model.deleted.is_(False),
            model.organization_id == organization_id
        ).all()
        found = {x[0] for x in found}
        found.add(get_nil_uuid())
        result = list(filter(lambda x: x not in found, check_ids))
        return result

    def _get_resource_traffic_expenses(
            self, cloud_account_types, from_list, to_list):
        where_exp = """
            cloud_account_id in %(cloud_account_ids)s
            AND date >= %(start_date)s
            AND date <= %(end_date)s
        """
        params = {
            'start_date': self.start_date,
            'end_date': self.end_date,
            'cloud_account_ids': list(cloud_account_types.keys())
        }
        if from_list and None not in from_list:
            where_exp += "AND from in %(from)s"
            params['from'] = [f[0] for f in from_list if f]
        if to_list and None not in to_list:
            where_exp += "AND to in %(to)s"
            params['to'] = [t[0] for t in to_list if t]
        traffic_expenses = self.execute_clickhouse(
            query=f"""
                SELECT cloud_account_id, resource_id, from, to,
                    sum(usage*sign), sum(cost*sign)
                FROM traffic_expenses
                WHERE {where_exp}
                GROUP BY cloud_account_id, resource_id, from, to
            """,
            params=params
        )
        traffic_expenses_map = defaultdict(list)
        for t in traffic_expenses:
            ca_id = t[0]
            cloud_type = cloud_account_types[ca_id].lower()
            from_ = t[2]
            to_ = t[3]
            if (from_list and (from_, cloud_type) not in from_list) or (
                    to_list and (to_, cloud_type) not in to_list):
                continue
            traffic_expenses_map[t[1]].append({
                'from': from_,
                'to': to_,
                'usage': t[4],
                'cost': t[5]
            })
        return traffic_expenses_map

    def _parse_traffic_filters(self, name, filters):
        list_filters = filters.pop(name, None)
        result = []
        if list_filters:
            for k in list_filters:
                if k in ['ANY', None]:
                    result.append(k)
                    continue
                try:
                    name, identity = self._parse_filter_with_type(k)
                except ValueError:
                    raise WrongArgumentsException(Err.OE0218, [name, k])
                result.append((name, identity.lower()))
        return result

    def _get_cloud_account_types(self, cloud_account_ids):
        res = self.session.query(
            CloudAccount.id, CloudAccount.type.name
        ).filter(
            CloudAccount.id.in_(cloud_account_ids),
            CloudAccount.deleted.is_(False)
        ).all()
        return {k[0]: k[1] for k in res}

    def _process_traffic_filters(self, cloud_account_ids, filters):
        from_list = self._parse_traffic_filters('traffic_from', filters)
        to_list = self._parse_traffic_filters('traffic_to', filters)
        traffic_filters_are_set = False
        if from_list or to_list:
            traffic_filters_are_set = True
        traffic_expenses_map = {}
        if (from_list and None in from_list) or (to_list and None in to_list):
            traffic_expenses_map = {None: {}}
        if from_list and 'ANY' in from_list:
            from_list = None
        if to_list and 'ANY' in to_list:
            to_list = None
        if not traffic_expenses_map and (traffic_filters_are_set or
                                         self.JOIN_TRAFFIC_EXPENSES):
            cloud_account_types = self._get_cloud_account_types(
                cloud_account_ids)
            traffic_expenses_map = self._get_resource_traffic_expenses(
                cloud_account_types, from_list, to_list)
        if traffic_filters_are_set:
            filters.update(
                {'cloud_resource_id': list(traffic_expenses_map.keys())})
        return traffic_expenses_map

    def process_data(self, resources_data, organization_id, filters, **kwargs):
        (not_clustered_resources, clustered_resources_map,
         joined_ids) = self._extract_unique_values_from_resources(
            resources_data, filters)
        not_clustered_expenses, clustered_expenses = [], []
        total_cost = 0
        cloud_account_ids = kwargs['cloud_account_id']
        limit = kwargs['limit']
        _, organization_cloud_accs = self.get_organization_and_cloud_accs(
            organization_id)
        if not_clustered_resources:
            not_clustered_expenses, cost = self.get_expenses(
                cloud_account_ids, not_clustered_resources, self.start_date,
                self.end_date, limit)
            total_cost += cost
        if clustered_resources_map:
            all_account_ids = list(map(
                lambda x: x.id, organization_cloud_accs)) + [get_nil_uuid()]
            clustered_expenses, cost = self.get_clustered_expenses(
                all_account_ids, clustered_resources_map, self.start_date,
                self.end_date)
            total_cost += cost
        expenses = sorted(not_clustered_expenses + clustered_expenses,
                          key=lambda x: x['cost'], reverse=True)
        all_resources_map = self.get_resources(
            organization_id, cloud_account_ids, list(joined_ids),
            clustered_resources_map)
        total_saving = self._get_total_saving(all_resources_map)
        resource_ids = set()
        if limit:
            expenses = expenses[:limit]
            resource_ids.update(
                list(map(lambda x: x.get('resource_id'), expenses))
            )
            for r_id in joined_ids:
                if len(resource_ids) == limit:
                    break
                resource_ids.add(r_id)
        else:
            resource_ids.update(joined_ids)
        resources_map = {k: v for k, v in all_resources_map.items()
                         if k in resource_ids}
        expenses_data = self.join_db_info(
            resources_map, expenses, organization_id,
            organization_cloud_accs)
        total_count = len(not_clustered_resources
                          ) + len(set(clustered_resources_map.values()))
        res = {
            'start_date': self.start_date,
            'end_date': self.end_date,
            'total_count': total_count,
            'total_cost': total_cost,
            **expenses_data,
            **total_saving
        }
        if limit:
            res['limit'] = limit
        return res

    def get(self, organization_id, **params):
        filters = params.copy()
        for k, v in params.items():
            if v is None:
                filters.pop(k)
        self.check_filters(filters, organization_id)
        self.start_date = params.pop('start_date')
        self.end_date = params.pop('end_date')
        query_filters, data_filters, extra_params = self.split_params(
            organization_id, params.copy())
        traffic_expenses_map = self._process_traffic_filters(
            query_filters['cloud_account_id'], data_filters)
        resources_data = self.get_resources_data(
            organization_id, query_filters.copy(),
            data_filters.copy(), extra_params.copy())
        result = self.process_data(
            resources_data, organization_id, filters,
            **query_filters, **extra_params)
        if self.JOIN_TRAFFIC_EXPENSES:
            self.join_traffic_expenses(result, traffic_expenses_map)
        return result

    def join_traffic_expenses(self, result, traffic_expenses_map):
        for e in result[self.EXPENSES_KEY]:
            cloud_resource_id = e.get('cloud_resource_id')
            if not cloud_resource_id:
                continue
            traffic_expenses = traffic_expenses_map.get(cloud_resource_id)
            if traffic_expenses:
                e['traffic_expenses'] = traffic_expenses

    def _extract_unique_values_from_resources(
            self, resources_data, input_filters, include_subresources=True):
        not_clustered_resources = []
        clustered_resources_map = {}
        cloud_account_ids = set()
        input_resource_ids = input_filters.get('resource_id', [])
        input_ca_ids = input_filters.get('cloud_account_id', [])
        cluster_ids = []
        for data in resources_data:
            _id = data.pop('_id')
            ca_id = _id.get('cloud_account_id')
            cluster_id = _id.get('cluster_id')
            r_ids = data.pop('resources', [])
            if ca_id is None and cluster_id is None:
                cluster_ids.extend(r_ids)
            if ca_id:
                cloud_account_ids.add(ca_id)
                if cluster_id:
                    if input_ca_ids:
                        # hide clustered resources if ca_id specified
                        continue
                    res_ids_in = list(filter(
                        lambda x: x in input_resource_ids, r_ids))
                    # show specified clustered resources outside of cluster
                    not_clustered_resources.extend(res_ids_in)
                    clustered_resources_map.update(
                        {r: cluster_id for r in r_ids if r not in res_ids_in})
                else:
                    not_clustered_resources.extend(r_ids)
        ext_cluster_ids = set()
        for cl_id in cluster_ids:
            if cl_id not in set(clustered_resources_map.values()):
                ext_cluster_ids.add(cl_id)
        if ext_cluster_ids:
            sub_resources = self.resources_collection.find(
                {'cluster_id': {'$in': list(ext_cluster_ids)}}, ['cluster_id'])
            for s in sub_resources:
                clustered_resources_map[s['_id']] = s['cluster_id']
        resource_ids = not_clustered_resources + list(
            set(clustered_resources_map.values()))
        if include_subresources:
            resource_ids += list(clustered_resources_map.keys())
        return not_clustered_resources, clustered_resources_map, resource_ids

    def format_resource(self, resource, last_run_ts):
        optional_params = ['name', 'region', 'employee_id', 'pool_id',
                           'meta', 'tags', 'last_seen', 'is_environment']
        default_values = {
            'last_seen': 0, 'meta': {}, 'tags': {}, 'is_environment': False
        }
        exclude_fields = ['excluded_recommendations',
                          'dismissed_recommendations', 'dismissed']
        if resource.get('_id'):
            resource['id'] = resource.pop('_id')
        for nullable_field in optional_params:
            if nullable_field not in resource:
                resource[nullable_field] = default_values.get(
                    nullable_field)
        active = resource.get('active', False)
        if not active:
            resource['meta']['cloud_console_link'] = None
        resource['tags'] = encoded_tags(resource.get('tags'), True)

        recommendations = resource.pop('recommendations', None)
        for field in exclude_fields:
            resource.pop(field, None)
        saving = 0
        if recommendations and last_run_ts <= recommendations.get(
                'run_timestamp', 0):
            for r in recommendations.get('modules', {}):
                saving += r.get('saving', 0)
        resource['saving'] = saving
        return resource


class CleanExpenseAsyncController(BaseAsyncControllerWrapper):

    def _get_controller_class(self):
        return CleanExpenseController


class RawExpenseController(CleanExpenseController):
    EXPENSES_KEY = 'raw_expenses'
    JOIN_TRAFFIC_EXPENSES = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._expense_ctrl = None

    @property
    def expense_ctrl(self):
        if not self._expense_ctrl:
            self._expense_ctrl = ExpenseController(self._config)
        return self._expense_ctrl

    def get_organization_id(self, resource_id):
        resource = self.resources_collection.find_one(
            {"_id": resource_id, "deleted_at": 0})
        if not resource:
            raise NotFoundException(
                Err.OE0002, ['Resource', resource_id])
        if resource.get('cluster_type_id'):
            return resource['organization_id']

        cloud_account_id = resource['cloud_account_id']
        cloud_account = self.session.query(CloudAccount).filter(and_(
            CloudAccount.deleted.is_(False),
            CloudAccount.id == cloud_account_id,
        )).one_or_none()
        if cloud_account is None:
            raise NotFoundException(
                Err.OE0002, ['Resource', resource['id']])
        return cloud_account.organization_id

    def _get_total_saving(self, resources_map):
        return {}

    def expand_resources_by_id(self, resource_ids):
        children_ids = list(self.resources_collection.distinct(
            '_id', {'cluster_id': {'$in': resource_ids}}))
        return list(set(resource_ids + children_ids))

    def _split_params(self, organization_id, params):
        resource_ids = params.pop('resource_id', [])
        if resource_ids:
            params['_id'] = self.expand_resources_by_id(
                resource_ids)
        return super()._split_params(organization_id, params)

    def get(self, resource_id, **params):
        organization_id = self.get_organization_id(resource_id)
        params['resource_id'] = [resource_id]
        return super().get(organization_id=organization_id, **params)

    def process_data(self, resources_data, organization_id, filters, **kwargs):
        res = super().process_data(resources_data, organization_id,
                                   filters, **kwargs)
        res.pop('total_count', None)
        return res

    def get_expenses(self, cloud_account_ids, resource_ids, start_date,
                     end_date, limit=None) -> tuple:
        start = datetime.fromtimestamp(start_date)
        end = datetime.fromtimestamp(end_date)
        cloud_resource_ids, cloud_account_ids = self._get_cloud_resource_ids(
            resource_ids)
        filters = {
            'cloud_account_id': cloud_account_ids,
            'resource_id': cloud_resource_ids
        }
        expenses = list(self.expense_ctrl.get_raw_expenses(
            start, end, filters))
        return expenses, self.get_expenses_total_cost(expenses)

    def _get_cloud_resource_ids(self, resource_ids):
        result = self.resources_collection.aggregate([
            {'$match': {'_id': {'$in': resource_ids}}},
            {'$group': {
                '_id': 0,
                'cloud_resource_ids': {'$addToSet': '$cloud_resource_id'},
                'cloud_account_ids': {'$addToSet': '$cloud_account_id'}
            }}
        ])
        cloud_resource_ids, cloud_account_ids = set(), set()
        for r in result:
            cloud_resource_ids.update(r['cloud_resource_ids'])
            cloud_account_ids.update(r['cloud_account_ids'])
        return list(cloud_resource_ids), list(cloud_account_ids)

    def _process_clustered_expenses(self, expenses, clustered_resources_map):
        return expenses

    def _fill_expenses_data(self, expenses, *args, **kwargs):
        return {
            self.EXPENSES_KEY: expenses
        }

    def get_expenses_total_cost(self, expenses):
        start_date = datetime.fromtimestamp(self.start_date)
        end_date = datetime.fromtimestamp(self.end_date)
        interval = (end_date - start_date).days
        if start_date + timedelta(days=interval) < end_date:
            interval += 1

        expenses_cost = 0
        for e in expenses:
            if e['end_date'] < end_date and e['start_date'] >= start_date:
                expenses_cost += e['cost']
                continue

            billing_period = (e['end_date'] - e['start_date']).days
            if e['start_date'] + timedelta(days=billing_period) < e['end_date']:
                billing_period += 1

            # split expenses with (end_date - start_date > 1 day) by days
            if billing_period > 1:
                cost_per_day = e['cost'] / billing_period
                billing_days = min([billing_period, interval])
                expenses_cost += cost_per_day * billing_days
            else:
                expenses_cost += e['cost']
        return expenses_cost

    def get_resources(self, organization_id, cloud_account_ids,
                      resource_ids, clustered_resources_map):
        return {}

    def _get_join_entities(self, organization_id, organization_cloud_acc,
                           resources_map=None):
        return {}


class RawExpenseAsyncController(BaseAsyncControllerWrapper):

    def _get_controller_class(self):
        return RawExpenseController


class SummaryExpenseController(CleanExpenseController):
    JOIN_TRAFFIC_EXPENSES = False

    def _get_resources_base(self, resource_ids, cloud_account_ids,
                            organization_id):
        resources = self.resources_collection.find({
            '_id': {'$in': resource_ids},
            '$or': [
                {'cloud_account_id': {'$in': cloud_account_ids}},
                {'organization_id': organization_id}
            ]
        }, ['_id', 'recommendations', 'cluster_id'])
        return resources

    def join_db_info(self, resources_map, expenses, organization_id,
                     organization_cloud_acc):
        total_saving = 0
        resources_map = resources_map or {}
        for resource in resources_map.values():
            if resource.get('cluster_id'):
                # will be processed as a part of cluster record
                continue
            total_saving += resource.get('saving')
        return {
            'total_saving': total_saving,
        }


class SummaryExpenseAsyncController(BaseAsyncControllerWrapper):

    def _get_controller_class(self):
        return SummaryExpenseController


class RegionExpenseController(FilteredFormattedExpenseController,
                              OrgCloudAccMixin):
    GROUPING_FIELD = 'region'
    FILTER_NAME = 'regions'

    def get_filter_params(self, objects):
        obj_ids = list(map(lambda x: x.id, objects))
        return 'cloud_account_id', obj_ids

    def get_result_base(self, prev_start_ts):
        return {
            'total': 0,
            'previous_total': 0,
            'previous_range_start': prev_start_ts,
            'regions': []
        }

    def get_configs(self, cloud_accs):
        res = list()
        for cloud_acc in cloud_accs:
            cloud_config = cloud_acc.decoded_config
            cloud_config['type'] = cloud_acc.type.value
            cloud_config['cloud_account_id'] = cloud_acc.id
            cloud_config['cloud_account_name'] = cloud_acc.name
            cloud_config['organization_id'] = cloud_acc.organization_id
            res.append(cloud_config)
        return res

    def _generate_info_map_element(self, region, info, cloud_type=None):
        region_name = None
        if region is not None:
            # For Azure and Alibaba we use region display names in
            # expenses, so let's use names as keys if names exist in
            # coords map
            region_name = info.get('name', region)
        return {
            region_name: {
                'name': region_name,
                'id': region,
                'total': 0,
                'previous_total': 0,
                'longitude': info.get('longitude'),
                'latitude': info.get('latitude'),
                'type': cloud_type
            }}

    def get_info_map(self, cloud_accs):
        cloud_configs = self.get_configs(cloud_accs)
        res = {}
        scanned = []
        for cloud_config in cloud_configs:
            cloud_type = cloud_config['type']
            if cloud_type in scanned:
                continue
            adapter = CloudAdapter.get_adapter(cloud_config)
            regions = adapter.get_regions_coordinates()
            for region_id, info in regions.items():
                res.update(self._generate_info_map_element(
                    region_id, info, cloud_type
                ))
            scanned.append(cloud_config['type'])
        return res

    def get_expenses(self, org_id, start_date, end_date):
        _, organization_cloud_accs = self.get_organization_and_cloud_accs(org_id)
        return self.get_formatted_expenses(organization_cloud_accs,
                                           start_date, end_date)

    def get_formatted_result(self, db_result, cloud_accs, starting_time, prev_start_ts):
        result = self.get_result_base(prev_start_ts)
        info_map = self.get_info_map(cloud_accs)

        for group in db_result:
            region = group.get('_id', {}).get(self.GROUPING_FIELD)
            if region is None and not info_map.get(region):
                info_map.update(
                    self._generate_info_map_element(None, {'longitude': None, 'latitude': None})
                )
            if region not in info_map.keys():
                continue

            if group['_id']['date'] >= starting_time:
                result['total'] += group['cost']
                info_map[region]['total'] += group['cost']
            else:
                result['previous_total'] += group['cost']
                info_map[region]['previous_total'] += group['cost']
                continue

        result['total'] = round(result['total'], 6)
        result[self.FILTER_NAME] = list(info_map.values())
        return result


class RegionExpenseAsyncController(BaseAsyncControllerWrapper):

    def _get_controller_class(self):
        return RegionExpenseController
