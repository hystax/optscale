import logging
from collections import defaultdict
from rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api_server.controllers.breakdown_expense import BreakdownBaseController
from rest_api_server.utils import encode_string

LOG = logging.getLogger(__name__)
DAY_IN_SECONDS = 86400


class BreakdownTagController(BreakdownBaseController):
    def split_params(self, organization_id, params):
        return self._split_params(organization_id, params)

    def _aggregate_resource_data(self, match_query, **kwargs):
        group_stage = {
            '_id': {
                'tag': '$tags.k',
                'cluster_type_id': '$cluster_type_id',
                'day': {'$cond': {
                    'if': {'$ifNull': ['$tags.k', False]},
                    'then': None,
                    'else': {'$trunc': {
                        '$divide': ['$first_seen', DAY_IN_SECONDS]}},
                }}
            },
            'resources': {'$addToSet': '$_id'},
        }
        return self.resources_collection.aggregate([
            {'$match': match_query},
            {'$addFields': {'tags': {'$objectToArray': "$tags"}}},
            {'$unwind': {
                'path': "$tags",
                'preserveNullAndEmptyArrays': True
            }},
            {'$group': group_stage}
        ], allowDiskUse=True)

    def _extract_values_from_data(self, resources_data):
        clusters = set()
        cnt_map = defaultdict(int)
        resources_table = []
        for data in resources_data:
            _id = data.pop('_id')
            cluster_type_id = _id.get('cluster_type_id')
            r_ids = data.pop('resources', [])
            if cluster_type_id:
                clusters.update(r_ids)
                continue
            tag = _id.get('tag')
            resources_table.extend(
                [{'id': r_id, 'tag': tag} for r_id in r_ids])
            cnt_map[tag] += len(r_ids)
        if clusters and not resources_table:
            sub_resources = self.resources_collection.find(
                {'cluster_id': {'$in': list(clusters)}, 'deleted_at': 0},
                ['tags'])
            for s in sub_resources:
                for tag in s.get('tags', {}).keys():
                    resources_table.append({'id': s['_id'], 'tag': tag})
                    cnt_map[tag] += 1
        return resources_table, cnt_map

    def get_breakdown_expenses(self, cloud_account_ids, resources):
        expenses = self.execute_clickhouse(
            query="""
                SELECT resources.tag, sum(cost*sign)
                FROM expenses
                JOIN resources ON expenses.resource_id = resources.id
                WHERE expenses.date >= %(start_date)s
                    AND expenses.date <= %(end_date)s
                    AND cloud_account_id in %(cloud_account_ids)s
                GROUP BY resources.tag
            """,
            params={
                'start_date': self.start_date,
                'end_date': self.end_date,
                'cloud_account_ids': list(cloud_account_ids)
            },
            external_tables=[{
                'name': 'resources',
                'structure': [
                    ('id', 'String'),
                    ('tag', 'Nullable(String)'),
                ],
                'data': resources
            }],
        )
        return {e[0]: e[1] for e in expenses}

    def process_data(self, resources_data, organization_id, filters, **kwargs):
        extracted_values = self._extract_values_from_data(resources_data)
        resources_table, cnt_map = extracted_values
        _, organization_cloud_accs = self.get_organization_and_cloud_accs(
            organization_id)
        cloud_account_ids = list(map(lambda x: x.id, organization_cloud_accs))
        expenses = self.get_breakdown_expenses(
            cloud_account_ids, resources_table)
        breakdown = []
        for tag, cnt in cnt_map.items():
            breakdown.append({
                'tag': encode_string(tag, decode=True) if tag else None,
                'cost': expenses.get(tag, 0),
                'count': cnt
            })
        return {
            'breakdown': breakdown,
            'start_date': self.start_date,
            'end_date': self.end_date,
        }


class BreakdownTagAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return BreakdownTagController
