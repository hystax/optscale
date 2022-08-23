import logging
from collections import defaultdict
from rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api_server.controllers.expense import CleanExpenseController
from rest_api_server.utils import encode_string, get_nil_uuid

LOG = logging.getLogger(__name__)
DAY_IN_SECONDS = 86400


class AvailableFiltersController(CleanExpenseController):
    JOIN_TRAFFIC_EXPENSES = False

    def split_params(self, organization_id, params):
        query_filters, data_filters, extra_filters = self._split_params(
            organization_id, params)
        extra_filters['last_recommend_run'] = self.get_last_run_ts_by_org_id(
            organization_id)
        return query_filters, data_filters, extra_filters

    def get_extended_input_filters(self, filters):
        input_filters = filters.copy()
        pool_ids = input_filters.pop('pool_id', [])
        if pool_ids:
            input_filters['pool_id'] = [
                x.removesuffix(self.WITH_SUBPOOLS_SIGN) for x in pool_ids]
        return input_filters

    def identify_resource(self, e):
        if e.get('cluster_type_id'):
            return self.CLUSTER_IDENTITY
        elif e.get('is_environment'):
            return self.ENVIRONMENT_IDENTITY
        else:
            return self.REGULAR_IDENTITY

    @staticmethod
    def _get_base_result(filter_values):
        return {
            'filter_values': filter_values
        }

    def process_data(self, resources_data, organization_id, filters, **kwargs):
        input_filters = self.get_extended_input_filters(filters)
        _, organization_cloud_accs = self.get_organization_and_cloud_accs(
            organization_id)
        entities = self._get_join_entities(
            organization_id, organization_cloud_accs)
        unique_values = self.collect_unique_values(resources_data, entities)
        filter_values = self.get_filter_values(unique_values, input_filters)
        return self._get_base_result(filter_values)

    def collect_unique_values(self, resource_data, entities):
        result = defaultdict(dict)
        r_sets = defaultdict(set)
        cl_resource_acc_type_map = {}
        for r in resource_data:
            _id = r.pop('_id')
            cloud_account_id = _id.get('cloud_account_id')
            cloud_account = entities.get(
                'cloud_account_id', {}).get(cloud_account_id, {})
            for cl_res_id in r.pop('cloud_resource_ids', {}):
                cl_resource_acc_type_map[cl_res_id] = cloud_account.get('type')
            for entity_name, v in self.JOINED_ENTITY_MAP.items():
                res_key, entity_key, fields = v
                keys = r.pop(res_key, {})
                for key in keys:
                    if key in result[entity_name]:
                        continue
                    entity = entities.get(entity_key, {}).get(key)
                    result[entity_name][key] = {
                        i: entity[i] for i in fields
                    } if entity else key
            for field in ['service_name', 'region', 'k8s_node',
                          'k8s_service', 'k8s_namespace']:
                r_keys = r.pop(field, {})
                for r_key in r_keys:
                    if r_key not in result[field]:
                        result[field][r_key] = {
                            'name': r_key,
                            'cloud_type': cloud_account.get('type')
                        } if r_key else r_key
            resource_types = r.pop('resource_type', {})
            rt_identifier = self.identify_resource(_id)
            for resource_type in resource_types:
                rt_key = resource_type, rt_identifier
                if rt_key not in result['resource_type']:
                    result['resource_type'][rt_key] = {
                        'name': rt_key[0], 'type': rt_key[1]
                    }
            tags = r.pop('tags', {})
            decoded_tags = []
            for tag in tags:
                tag = encode_string(tag, decode=True) if tag else tag
                decoded_tags.append(tag)
            if decoded_tags:
                for t in ['tag', 'without_tag']:
                    r_sets[t].update(decoded_tags)
            for k, v in r.items():
                r_sets[k].update(v)
        result.update(r_sets)
        # add all available optscale entities
        for entity_name, v in self.JOINED_ENTITY_MAP.items():
            _, entity_key, fields = v
            entities_dict = entities.get(entity_key, {})
            for entity_id, entity in entities_dict.items():
                result[entity_name].update({
                    entity_id: {f: entity[f] for f in fields}})
        if cl_resource_acc_type_map:
            result.update(self.get_traffic_filters(
                list(result['cloud_account'].keys()),
                cl_resource_acc_type_map))
        return result

    def get_traffic_filters(self, cloud_account_ids, cl_resource_acc_type_map):
        res_filters = self.execute_clickhouse(
            query="""
                SELECT distinct(resources.cloud_type, from, to)
                FROM traffic_expenses
                JOIN resources ON traffic_expenses.resource_id = resources.id
                WHERE cloud_account_id in %(cloud_account_ids)s
                    AND traffic_expenses.date >= %(start_date)s
                    AND traffic_expenses.date <= %(end_date)s
            """,
            params={
                'start_date': self.start_date,
                'end_date': self.end_date,
                'cloud_account_ids': [
                    c_id for c_id in cloud_account_ids if c_id
                ]
            },
            external_tables=[
                {
                    'name': 'resources',
                    'structure': [
                        ('id', 'String'),
                        ('cloud_type', 'String')
                    ],
                    'data': [
                        {'id': k, 'cloud_type': v}
                        for k, v in cl_resource_acc_type_map.items() if v]
                }
            ]
        )
        result_set = defaultdict(set)
        for (cloud_type, _from, _to), in res_filters:
            result_set['traffic_from'].add((cloud_type, _from))
            result_set['traffic_to'].add((cloud_type, _to))
        result = {}
        for k, values in result_set.items():
            regions = [{'name': v[1], 'cloud_type': v[0]} for v in values]
            if regions:
                regions.append('ANY')
            result[k] = regions
        return result

    def generate_filters_pipeline(self, organization_id, start_date, end_date,
                                  params, data_filters):
        query = super().generate_filters_pipeline(
            organization_id, start_date, end_date, params,
            data_filters)
        query['$and'].append({'cluster_id': None})
        return query

    def get_filter_values(self, uniq_values_map, filters):
        filters['pool'] = filters.pop('pool_id', [])
        filters['cloud_account'] = filters.pop('cloud_account_id', [])
        filters['owner'] = filters.pop('owner_id', [])
        for field in ['active', 'recommendations', 'constraint_violated']:
            value = filters.pop(field, None)
            filters[field] = [] if value is None else [value]
        for k in filters:
            if isinstance(filters[k], list):
                filters[k] = [x if x != get_nil_uuid() else None
                              for x in filters[k]]
        return self._get_filter_values(uniq_values_map, filters)

    def _get_filter_values(self, uniq_values_map, filters):
        filter_values = {}
        for field, values in uniq_values_map.items():
            if filters.get(field, []):
                filter_values[field] = []
            else:
                if isinstance(values, dict):
                    values = values.values()
                filter_values[field] = list(values)
        for src_k, dst_k in [('tag', 'without_tag'), ('without_tag', 'tag')]:
            if filters.get(src_k):
                filter_values[dst_k] = list(set(
                    filter_values.pop(dst_k, [])) - set(filters[src_k]))
        return filter_values

    def _aggregate_resource_data(self, match_query, **kwargs):
        last_recommend_run = kwargs['last_recommend_run']
        collected_filters = [
            'service_name', 'pool_id', 'employee_id', 'k8s_node', 'region',
            'resource_type', 'k8s_namespace', 'k8s_service', 'cloud_account_id'
        ]
        group_stage = {
            f: {'$addToSet': {'$ifNull': ['$%s' % f, None]}}
            for f in collected_filters
        }
        for bool_field in ['active', 'constraint_violated']:
            group_stage.update({
                bool_field: {'$addToSet': {'$cond': {
                    'if': {'$eq': ['$%s' % bool_field, True]},
                    'then': True,
                    'else': False
                }}},
            })
        group_stage.update({
            'recommendations': {'$addToSet': {'$cond': {
                'if': {'$and': [
                    {'$ne': ['$recommendations', None]},
                    {'$gte': [
                        '$recommendations.run_timestamp', last_recommend_run
                    ]}
                ]},
                'then': True,
                'else': False
            }}}
        })
        group_stage.update({
            '_id': {
                'cloud_account_id': '$cloud_account_id',
                'cluster_type_id': '$cluster_type_id',
                'is_environment': '$is_environment',
                'day': {'$trunc': {
                    '$divide': ['$first_seen', DAY_IN_SECONDS]}},
            },
            'tags': {'$addToSet': '$tags.k'},
            'cloud_resource_ids': {'$addToSet': '$cloud_resource_id'},
        })
        return self.resources_collection.aggregate([
            {'$match': match_query},
            {'$addFields': {'tags': {'$objectToArray': "$tags"}}},
            {'$unwind': {
                'path': "$tags",
                'preserveNullAndEmptyArrays': True
            }},
            {'$group': group_stage}
        ], allowDiskUse=True)


class AvailableFiltersAsyncController(BaseAsyncControllerWrapper):

    def _get_controller_class(self):
        return AvailableFiltersController
