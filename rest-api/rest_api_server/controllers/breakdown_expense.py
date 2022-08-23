import logging
from collections import defaultdict
from datetime import datetime, timezone
from rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api_server.controllers.expense import CleanExpenseController
from rest_api_server.exceptions import Err

from optscale_exceptions.common_exc import WrongArgumentsException

LOG = logging.getLogger(__name__)
DAY_IN_SECONDS = 86400
DAYS_IN_YEAR = 365


class BreakdownBaseController(CleanExpenseController):
    JOIN_TRAFFIC_EXPENSES = False

    def split_params(self, organization_id, params):
        query_filters, data_filters, extra_filters = self._split_params(
            organization_id, params)
        extra_filters['breakdown_by'] = query_filters.pop('breakdown_by', None)
        return query_filters, data_filters, extra_filters

    def get_db_entities_info(self, organization_id, organization_cloud_acc,
                             unique_values):
        entities = self._get_join_entities(
            organization_id, organization_cloud_acc)
        entities = self.update_unique_values(unique_values, entities)
        return entities

    def update_unique_values(self, unique_values, entities):
        result = defaultdict(dict)
        for entity_name, v in self.JOINED_ENTITY_MAP.items():
            res_key, entity_key, fields = v
            keys = unique_values.pop(res_key, {})
            for key in keys:
                if not key or key in result[entity_name]:
                    continue
                entity = entities.get(entity_key, {}).get(key)
                result[entity_name][key] = {
                    i: entity[i] for i in fields
                }
        result.update(unique_values)
        return result

    @staticmethod
    def _get_breakdown_dates(start_date, end_date):
        first_breakdown = int(datetime.utcfromtimestamp(start_date).replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc
        ).timestamp())
        last_breakdown = int(datetime.utcfromtimestamp(end_date).replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc
        ).timestamp())
        return [x for x in range(first_breakdown, last_breakdown + 1,
                                 DAY_IN_SECONDS)]

    def get_breakdown_entity_map(self, entities, breakdown_by):
        entity_key = None
        for k, v in self.JOINED_ENTITY_MAP.items():
            if v[0] == breakdown_by:
                entity_key = k
                break
        if not entity_key:
            return {}
        return entities.get(entity_key, {})

    def get_value_resource_type(self, value, is_cluster=False, is_env=False):
        if is_cluster:
            identity = self.CLUSTER_IDENTITY
        elif is_env:
            identity = self.ENVIRONMENT_IDENTITY
        else:
            identity = None
        return self.IDENTITY_DELIMITER.join(
            [value, identity]) if identity else value


class BreakdownExpenseController(BreakdownBaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._previous_period_start = None

    @staticmethod
    def update_params(**params):
        start_date = params.get('start_date')
        end_date = params.get('end_date')
        start_dt = datetime.utcfromtimestamp(start_date).replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
        end_dt = datetime.utcfromtimestamp(end_date).replace(
            hour=23, minute=59, second=59, microsecond=0, tzinfo=timezone.utc)
        params.update({
            'start_date': int(start_dt.timestamp()),
            'end_date': int(end_dt.timestamp())
        })
        return params

    def check_filters(self, filters, organization_id):
        super().check_filters(filters, organization_id)
        start_dt = filters.get('start_date')
        end_dt = filters.get('end_date')
        if (end_dt - start_dt) / DAY_IN_SECONDS > DAYS_IN_YEAR:
            raise WrongArgumentsException(Err.OE0515, [])

    def get(self, organization_id, **params):
        params = self.update_params(**params)
        return super().get(organization_id, **params)

    def fill_empty_days(self, breakdown):
        empty_days = list(filter(
            lambda x: x not in breakdown,
            self._get_breakdown_dates(self.start_date, self.end_date)
        ))
        breakdown.update({dt: {} for dt in empty_days})

    @property
    def previous_period_start(self):
        if not self._previous_period_start:
            interval = self.end_date - self.start_date + 1
            prev_start = self.start_date - interval
            self._previous_period_start = prev_start if prev_start > 0 else 0
        return self._previous_period_start

    def generate_filters_pipeline(self, organization_id, start_date, end_date,
                                  params, data_filters):
        return super().generate_filters_pipeline(
            organization_id, self.previous_period_start, end_date, params,
            data_filters)

    def process_data(self, resources_data, organization_id, filters, **kwargs):
        breakdown_by = kwargs.get('breakdown_by')
        extracted_values = self._extract_values_from_data(
            resources_data, filters, breakdown_by=breakdown_by)
        resource_cluster_map, resource_breakdown_map = extracted_values
        ids_for_pop = set()
        for k, v in resource_cluster_map.items():
            value = resource_breakdown_map.get(v)
            resource_breakdown_map[k] = value
            ids_for_pop.add(v)
        for pop_id in ids_for_pop:
            resource_breakdown_map.pop(pop_id, None)
        _, organization_cloud_accs = self.get_organization_and_cloud_accs(
            organization_id)
        cloud_account_ids = list(map(lambda x: x.id, organization_cloud_accs))
        breakdown_expenses = self.get_breakdown_expenses(
            cloud_account_ids, resource_breakdown_map)
        unique_values = {breakdown_by: set(resource_breakdown_map.values())}
        entities = self.get_db_entities_info(
            organization_id, organization_cloud_accs, unique_values)
        breakdown_entities = self.get_breakdown_entity_map(
            entities, breakdown_by)
        result = self._get_base_result(
            breakdown_by, breakdown_expenses, breakdown_entities)
        return result

    def _get_base_result(self, breakdown_by, breakdown_expenses, entities_map):
        totals = {
            'total': 0,
            'previous_total': 0,
            'previous_range_start': self.previous_period_start,
        }
        breakdown = defaultdict(dict)
        counts = {}
        previous_period_dt = datetime.utcfromtimestamp(
            self.previous_period_start)
        start_dt = datetime.utcfromtimestamp(self.start_date)
        for breakdown_date, day_info in breakdown_expenses.items():
            for k, cost in day_info.items():
                if k not in counts:
                    counts[k] = {'total': 0, 'previous_total': 0,
                                 **entities_map.get(k, {})}
                if breakdown_date < previous_period_dt:
                    continue
                if breakdown_date < start_dt:
                    totals['previous_total'] += cost
                    counts[k]['previous_total'] += cost
                    continue
                totals['total'] += cost
                dt_timestamp = int(breakdown_date.replace(
                    hour=0, minute=0, second=0, microsecond=0,
                    tzinfo=timezone.utc).timestamp())
                breakdown[dt_timestamp][k] = {
                    'cost': cost, **entities_map.get(k, {})
                }
                counts[k]['total'] += cost
        self.fill_empty_days(breakdown)
        res = {
            'counts': counts,
            'breakdown': breakdown,
            'start_date': self.start_date,
            'end_date': self.end_date,
            **totals
        }
        if breakdown_by:
            res['breakdown_by'] = breakdown_by
        return res

    def _extract_values_from_data(self, resources_data, input_filters,
                                  breakdown_by):
        clustered_resources_map = {}
        input_ca_ids = input_filters.get('cloud_account_id', [])
        cluster_ids = []
        breakdown_map = {}
        for data in resources_data:
            _id = data.pop('_id')
            ca_id = _id.get('cloud_account_id')
            cluster_id = _id.get('cluster_id')
            r_ids = data.pop('resources', [])
            is_cluster = False
            is_env = _id.pop('is_environment', False)
            if ca_id is None and cluster_id is None:
                is_cluster = True
                cluster_ids.extend(r_ids)
            if ca_id:
                if cluster_id and not input_ca_ids:
                    clustered_resources_map.update(
                        {r: cluster_id for r in r_ids})
            for r in r_ids:
                value = _id.get(breakdown_by)
                if breakdown_by == 'resource_type' and (is_cluster or is_env):
                    value = self.get_value_resource_type(
                        value, is_cluster, is_env)
                breakdown_map[r] = value
        ext_cluster_ids = set()
        for cl_id in cluster_ids:
            if cl_id not in set(clustered_resources_map.values()):
                ext_cluster_ids.add(cl_id)
        if ext_cluster_ids:
            sub_resources = self.resources_collection.find(
                {'cluster_id': {'$in': list(ext_cluster_ids)}}, ['cluster_id'])
            for s in sub_resources:
                clustered_resources_map[s['_id']] = s['cluster_id']
        return clustered_resources_map, breakdown_map

    def get_breakdown_expenses(self, cloud_account_ids, resources):
        external_table = [
            {'id': k, 'group_field': v}
            for k, v in resources.items()
        ]
        start_dt = datetime.utcfromtimestamp(self.previous_period_start)
        end_dt = datetime.utcfromtimestamp(self.end_date)
        expenses = self.execute_clickhouse(
            query="""
                SELECT
                    resources.group_field, date, sum(cost*sign)
                FROM expenses
                JOIN resources ON expenses.resource_id = resources.id
                WHERE expenses.date >= %(start_date)s
                    AND expenses.date <= %(end_date)s
                    AND cloud_account_id in %(cloud_account_ids)s
                GROUP BY resources.group_field, date
            """,
            params={
                'start_date': start_dt,
                'end_date': end_dt,
                'cloud_account_ids': list(cloud_account_ids)
            },
            external_tables=[{
                'name': 'resources',
                'structure': [
                    ('id', 'String'),
                    ('group_field', 'Nullable(String)'),
                ],
                'data': external_table
            }],
        )
        result = defaultdict(dict)
        for value, date, cost in expenses:
            result[date].update({value: cost})
        return result

    def _aggregate_resource_data(self, match_query, **kwargs):
        group_by = kwargs.get('breakdown_by')
        group_dict = {
            'cloud_account_id': '$cloud_account_id',
            'cluster_id': '$cluster_id',
            'is_environment': '$is_environment',
            'day': {'$trunc': {
                '$divide': ['$first_seen', DAY_IN_SECONDS]}},
        }
        if group_by and group_by not in group_dict:
            group_dict[group_by] = '$%s' % group_by
        group_stage = {
            '_id': group_dict,
            'resources': {'$addToSet': '$_id'},
        }
        return self.resources_collection.aggregate([
            {'$match': match_query},
            {'$group': group_stage}
        ], allowDiskUse=True)


class BreakdownExpenseAsyncController(BaseAsyncControllerWrapper):

    def _get_controller_class(self):
        return BreakdownExpenseController
