import json
import logging
from cloud_adapter.cloud import Cloud as CloudAdapter
from rest_api_server.controllers.expense import CleanExpenseController
from rest_api_server.controllers.base_async import BaseAsyncControllerWrapper

DAY_IN_SECONDS = 86400
LOG = logging.getLogger(__name__)


class TrafficExpenseController(CleanExpenseController):
    JOIN_TRAFFIC_EXPENSES = False

    def _aggregate_resource_data(self, match_query, **kwargs):
        group_stage = {
            '_id': {
                'cloud_account_id': '$cloud_account_id',
                'day': {'$trunc': {
                    '$divide': ['$first_seen', DAY_IN_SECONDS]}},
            },
            'resources': {'$addToSet': '$cloud_resource_id'},
            'cluster_ids': {'$addToSet': {'$cond': {
                'if': {'$ifNull': ['$cluster_type_id', False]},
                'then': '$_id',
                'else': None
            }}}
        }
        return self.resources_collection.aggregate([
            {'$match': match_query},
            {'$group': group_stage}
        ], allowDiskUse=True)

    @staticmethod
    def _get_configs(cloud_accs):
        res = list()
        for cloud_acc in cloud_accs:
            cloud_config = cloud_acc.decoded_config
            cloud_config['type'] = cloud_acc.type.value
            cloud_config['id'] = cloud_acc.id
            res.append(cloud_config)
        return res

    @staticmethod
    def _get_coordinates(config):
        cloud_adapter = CloudAdapter.get_adapter(config)
        res = cloud_adapter.get_regions_coordinates()
        coordinates_result = {}
        for k, v in res.items():
            coordinates = {
                'latitude': v.get('latitude'),
                'longitude': v.get('longitude'),
                'name': k
            }
            coordinates_result[k.lower()] = coordinates
        return coordinates_result

    @staticmethod
    def _extract_coordinates(coordinates, targets):
        result = []
        for target in targets:
            res_part = dict(name=target)
            target_coords = coordinates.get(target.lower())
            if target_coords:
                res_part.update(target_coords)
            result.append(res_part)
        return result

    def _extract_values_from_data(self, resources_data):
        clusters, cloud_resource_ids = set(), set()
        for data in resources_data:
            _id = data.pop('_id')
            r_ids = data.pop('resources', [])
            cluster_ids = list(filter(
                lambda x: x is not None, data.pop('cluster_ids', [])))
            if cluster_ids:
                clusters.update(cluster_ids)
            else:
                cloud_resource_ids.update(r_ids)
        if clusters:
            sub_resources = self.resources_collection.find(
                {'cluster_id': {'$in': list(clusters)}, 'deleted_at': 0},
                ['cloud_resource_id'])
            for s in sub_resources:
                cloud_resource_ids.add(s.get('cloud_resource_id'))
        return cloud_resource_ids

    def process_data(self, resources_data, organization_id, filters, **kwargs):
        cloud_resource_ids = self._extract_values_from_data(
            resources_data)
        _, organization_cloud_accs = self.get_organization_and_cloud_accs(
            organization_id)
        cloud_accounts_map = {
            ca_config['id']: ca_config for ca_config in self._get_configs(
                organization_cloud_accs)
        }
        expenses = self.get_traffic_expenses(
            list(cloud_accounts_map.keys()), cloud_resource_ids)
        traffic_expenses = {}
        ca_coordinates_map = {}
        total_cost, total_usage = 0, 0
        for e in expenses:
            cloud_account_id, _from, _to, usage, cost = e
            if cloud_account_id not in ca_coordinates_map:
                ca_coordinates_map[cloud_account_id] = self._get_coordinates(
                    cloud_accounts_map[cloud_account_id])
            region_coordinates = ca_coordinates_map[cloud_account_id]
            # TODO: We should think about cache for coordinates by cloud_type
            from_coords, to_coords = self._extract_coordinates(
                region_coordinates, [_from, _to])
            total_cost += cost
            total_usage += usage
            cloud_type = cloud_accounts_map[cloud_account_id]['type']
            grp_key = cloud_type, from_coords['name'], to_coords['name']
            if grp_key in traffic_expenses:
                traffic_expenses[grp_key]['cost'] += cost
                traffic_expenses[grp_key]['usage'] += usage
            else:
                traffic_expenses[grp_key] = {
                    'cloud_type': cloud_type,
                    'from': from_coords,
                    'to': to_coords,
                    'usage': usage,
                    'cost': cost
                }
        return {
            'traffic_expenses': list(traffic_expenses.values()),
            'start_date': self.start_date,
            'end_date': self.end_date,
            'total_cost': total_cost,
            'total_usage': total_usage
        }

    def get_traffic_expenses(self, cloud_account_ids, cloud_resource_ids):
        return self.execute_clickhouse(
            query="""
                SELECT cloud_account_id, from, to,
                    sum(usage*sign), sum(cost*sign)
                FROM traffic_expenses
                JOIN resources ON traffic_expenses.resource_id = resources.id
                WHERE traffic_expenses.date >= %(start_date)s
                    AND traffic_expenses.date <= %(end_date)s
                    AND cloud_account_id in %(cloud_account_ids)s
                GROUP BY cloud_account_id, from, to
            """,
            params={
                'start_date': self.start_date,
                'end_date': self.end_date,
                'cloud_account_ids': cloud_account_ids
            },
            external_tables=[{
                'name': 'resources',
                'structure': [
                    ('id', 'String'),
                ],
                'data': [{'id': r_id} for r_id in cloud_resource_ids]
            }]
        )


class TrafficExpenseAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return TrafficExpenseController
