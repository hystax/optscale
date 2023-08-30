import logging
from collections import defaultdict
from datetime import datetime

from rest_api.rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api.rest_api_server.controllers.breakdown_expense import BreakdownBaseController
from rest_api.rest_api_server.exceptions import Err

from tools.optscale_exceptions.common_exc import WrongArgumentsException

LOG = logging.getLogger(__name__)
SECONDS_IN_DAY = 86400


class ResourceCountController(BreakdownBaseController):
    collected_filters = ['cloud_account_id', 'employee_id', 'pool_id']

    @staticmethod
    def get_base_breakdown(start_date, end_date):
        breakdown = {}
        current_breakdown = int(datetime.fromtimestamp(start_date).replace(
            hour=0, minute=0, second=0, microsecond=0).timestamp())
        first_breakdown = current_breakdown
        while current_breakdown < end_date:
            breakdown[current_breakdown] = {}
            current_breakdown += SECONDS_IN_DAY
        last_breakdown = current_breakdown - SECONDS_IN_DAY
        return {'breakdown': breakdown, 'first_breakdown': first_breakdown,
                'last_breakdown': last_breakdown}

    def get_value_resource_type(self, value, **kwargs):
        return super().get_value_resource_type(
            value.get('resource_type'), value.get('is_cluster'),
            value.get('is_environment'))

    def _get_resources_breakdowns(
            self, match_query, breakdown_by, start_date, end_date,
            collected_filters):
        breakdowns = self._get_breakdown_dates(start_date, end_date)
        if breakdown_by == 'resource_type':
            group_value = {
                    'resource_type': '$resource_type',
                    'is_cluster': '$cluster_type_id',
                    'is_environment': '$is_environment'
            }
        else:
            group_value = '$%s' % breakdown_by

        match_stage = {
            '$match': match_query
        }

        add_stage = {
            '$addFields': {
                'first_breakdown': {
                    '$subtract': [
                        '$first_seen', {
                            '$mod': ['$first_seen', SECONDS_IN_DAY]}]
                },
                'last_breakdown':
                    {
                        '$subtract': [
                            '$last_seen', {
                                '$mod': ['$last_seen', SECONDS_IN_DAY]}
                        ]},
                'cloud_account_id': {
                    '$ifNull': ['$cloud_account_id', None]},
            },
        }

        facet_stage = {'$facet': {}}
        # collect filters values
        facet_stage['$facet'].update({
            f: [{'$project': {'_id': 1, f: '$%s' % f}},
                {'$group': {'_id': None, f: {'$addToSet': '$%s' % f}}}]
            for f in collected_filters})

        # collect totals
        facet_stage['$facet'].update({'total': [{'$count': 'count'}]})
        facet_stage['$facet'].update({'totals': [{
            '$group': {'_id': group_value, 'count': {'$sum': 1}}}, {
            '$project': {'_id': '$_id', 'count': '$count'}
        }]})

        # collect breakdown counts
        brkdwns = {'%s' % b: {'$sum': {'$cond': [{'$and': [
            {'$lte': ['$first_breakdown', b]},
            {'$gte': ['$last_breakdown', b]}]}, 1, 0]}} for b in breakdowns}
        brkdwns_created = {'%s_crt' % b: {'$sum': {'$cond': [{'$and': [
            {'$eq': ['$first_breakdown', b]},
            {'$ne': [b, breakdowns[0]]}]}, 1, 0]}} for b in breakdowns}
        brkdwns_removed = {'%s_rmv' % b: {'$sum': {'$cond': [{'$and': [
            {'$eq': ['$last_breakdown', b - SECONDS_IN_DAY]},
            {'$ne': [b, breakdowns[0]]}]}, 1, 0]}} for b in breakdowns}

        facet_stage['$facet'].update({'breakdowns': [
            {'$group': {'_id': group_value, **brkdwns, **brkdwns_created,
                        **brkdwns_removed}},
            {'$project': {
                '_id': '$_id',
                'breakdowns': {
                    'count': {'%s' % b: '$%s' % b for b in breakdowns},
                    'created': {'%s' % b: '$%s_crt' % b
                                for b in breakdowns},
                    'deleted_day_before': {'%s' % b: '$%s_rmv' % b
                                           for b in breakdowns},
                    'average': {'$divide': [{'$sum': ['$%s' % b
                                                      for b in breakdowns]},
                                            len(breakdowns)]}
                }}}]})

        pipeline = [
            match_stage,
            add_stage,
            facet_stage
        ]
        return self.resources_collection.aggregate(pipeline, allowDiskUse=True)

    def get_resource_type_condition(self, resource_types):
        if not resource_types:
            return [{'cluster_id': {'$exists': False}}]

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
                resource_type_cond['cluster_type_id'] = {'$exists': True}
            elif identity == self.ENVIRONMENT_IDENTITY:
                resource_type_cond['is_environment'] = True
            type_filters.append({'$and': [resource_type_cond]})

        return type_filters

    def get_resources_data(self, organization_id, query_filters, data_filters,
                           extra_params):
        query = self.generate_filters_pipeline(
            organization_id, self.start_date, self.end_date, query_filters,
            data_filters)
        raw_result = self._get_resources_breakdowns(
            query, extra_params['breakdown_by'],
            self.start_date, self.end_date, self.collected_filters)
        return raw_result

    def process_data(self, breakdown_info, organization_id, filters, **kwargs):
        breakdown_by = kwargs['breakdown_by']
        result = self.get_base_result(
            self.start_date, self.end_date, breakdown_by)
        unique_values = {f: set() for f in self.collected_filters}
        result['breakdown'] = defaultdict(dict)
        row = list(breakdown_info)[0]
        for f in unique_values.keys():
            if row[f]:
                unique_values[f].update(row[f][0][f])
        _, organization_cloud_accs = self.get_organization_and_cloud_accs(
            organization_id)
        entities = self.get_db_entities_info(
            organization_id, organization_cloud_accs, unique_values)
        breakdown_entities = self.get_breakdown_entity_map(
            entities, breakdown_by)
        if row['total']:
            result['count'] = row['total'][0]['count']
        else:
            result['count'] = 0
        if breakdown_by == 'resource_type':
            result['counts'] = {
                self.get_value_resource_type(x['_id']): {
                    'total': x['count']} for x in row['totals']}
        else:
            result['counts'] = {x['_id']: {
                'total': x['count'],
                **breakdown_entities.get(x['_id'], {})
            } for x in row['totals']}

        breakdowns_all = row['breakdowns']
        for breakdown_by_type in breakdowns_all:
            breakdown_counters = breakdown_by_type['breakdowns']
            if breakdown_by == 'resource_type':
                value = self.get_value_resource_type(breakdown_by_type['_id'])
            else:
                value = breakdown_by_type['_id']
            counts = breakdown_counters['count']
            created = breakdown_counters['created']
            deleted_day_before = breakdown_counters['deleted_day_before']
            result['counts'][value]['average'] = breakdown_counters['average']
            for timestamp, r_count in counts.items():
                r_created = created[timestamp]
                r_deleted = deleted_day_before[timestamp]
                if not result['breakdown'].get(timestamp):
                    result['breakdown'][timestamp] = {}
                result['breakdown'][timestamp].update({value: {
                    'count': r_count,
                    'created': r_created,
                    'deleted_day_before': r_deleted,
                    **breakdown_entities.get(value, {})
                }})
        return result

    def get_base_result(self, start_date, end_date, breakdown_by):
        res = {
            'start_date': start_date,
            'end_date': end_date,
            'count': 0,
            **self.get_base_breakdown(start_date, end_date),
        }
        if breakdown_by:
            res['breakdown_by'] = breakdown_by
        return res


class ResourceCountAsyncController(BaseAsyncControllerWrapper):

    def _get_controller_class(self):
        return ResourceCountController
