from concurrent.futures.thread import ThreadPoolExecutor
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from kombu.log import get_logger
from pymongo import UpdateOne

from tools.cloud_adapter.cloud import Cloud as CloudAdapter

from bumiworker.bumiworker.consts import ArchiveReason
from bumiworker.bumiworker.modules.base import ArchiveBase, ModuleBase

BULK_SIZE = 2000
DAYS_IN_MONTH = 30
LOG = get_logger(__name__)


class ObsoleteSnapshotsBase(ModuleBase):
    def _get(self):
        supported_clouds = self.get_supported_clouds()
        (_, _, skip_cloud_accounts) = self.get_options_values()
        config_map = self.get_cloud_accounts(supported_clouds,
                                             skip_cloud_accounts)
        configs = list(config_map.values())
        if not configs:
            return []
        return self._collect_resources(configs)

    def get_supported_clouds(self):
        raise NotImplementedError

    def get_obsolete_resources(self, now, cloud_account_id, config,
                               obsolete_threshold):
        raise NotImplementedError

    def merge_last_used(self, collection, to_merge):
        for resource_id, last_used in to_merge.items():
            current_last_used = collection.get(resource_id)
            if current_last_used is None or current_last_used < last_used:
                collection[resource_id] = last_used

    def update_last_used(self, cloud_account_id, to_update):
        updates = []
        for resource_id, last_used in to_update.items():
            updates.append(UpdateOne(
                filter={
                    'cloud_resource_id': resource_id,
                    'cloud_account_id': cloud_account_id
                },
                update={'$set': {'meta.last_used': int(last_used.timestamp())}}
            ))
            if len(updates) == BULK_SIZE:
                self.mongo_client.restapi.resources.bulk_write(updates)
                updates = []
        if updates:
            self.mongo_client.restapi.resources.bulk_write(updates)

    def get_resources_pipeline(self, resource_type, excluded_ids,
                               cloud_account_id, now, obsolete_threshold):
        return [
            {
                '$match': {
                    'cloud_account_id': cloud_account_id,
                    'active': True,
                    'deleted_at': 0,
                    'cloud_resource_id': {'$nin': excluded_ids},
                    'resource_type': resource_type,
                    '$or': [
                        {'meta.last_used': {'$exists': False}},
                        {'meta.last_used': {'$lt': int(
                            (now - obsolete_threshold).timestamp())}}
                    ]
                }
            }
        ]

    def get_snapshots_used_by_images(self, now, cloud_config):
        adapter = CloudAdapter.get_adapter(cloud_config)
        images = []
        snapshot_ids = set()
        try:
            with ThreadPoolExecutor(max_workers=50) as executor:
                futures = []
                for func, params in adapter.image_discovery_calls():
                    futures.append(executor.submit(func, *params))
                for f in futures:
                    images.extend(f.result())
        except Exception as ex:
            setattr(ex, 'cloud_account_id', cloud_config.get('id'))
            raise ex
        for image in images:
            for mapping in image.block_device_mappings:
                snapshot_id = mapping.get('snapshot_id')
                if snapshot_id:
                    snapshot_ids.add(snapshot_id)
        return {s: now for s in snapshot_ids}

    def get_snapshots_used_by_volumes(self, now, cloud_account_id,
                                      obsolete_threshold):
        last_seen = int((now - obsolete_threshold).timestamp())
        pipeline_volumes_parents = [
            {
                '$match': {
                    'last_seen': {'$gte': last_seen},
                    '_last_seen_date': {
                        '$gte': self.timestamp_to_day_start(last_seen)},
                    'deleted_at': 0,
                    'resource_type': 'Volume',
                    'cloud_account_id': cloud_account_id
                }
            },
            {
                '$group': {
                    '_id': '$meta.snapshot_id',
                    'last_used': {'$max': '$last_seen'}
                }
            }
        ]
        volumes_parents = self.mongo_client.restapi.resources.aggregate(
            pipeline_volumes_parents)
        return {x['_id']: datetime.fromtimestamp(
            x['last_used'], tz=timezone.utc) for x in volumes_parents}

    def _get_expenses(self, snapshot_ids, cloud_account_ids, min_start_dt):
        start_date = min_start_dt.replace(
            hour=0, minute=0, second=0, microsecond=0)
        month_before_start = start_date - timedelta(days=DAYS_IN_MONTH)
        snapshots = list(self.mongo_client.restapi.resources.find({
            'cloud_account_id': {'$in': cloud_account_ids},
            'cloud_resource_id': {'$in': snapshot_ids},
        }, ['cloud_resource_id']))
        query = """
            SELECT cloud_resource_id, sum(cost * sign),
                min(date) as min_d, max(date)
            FROM expenses
            JOIN resources ON resource_id = resources._id
            WHERE date >= %(month_before_start)s AND date < %(start_date)s
            GROUP BY cloud_resource_id
            HAVING min_d < %(start_date)s
        """
        return self.clickhouse_client.execute(
            query=query,
            external_tables=[{
                'name': 'resources',
                'structure': [
                    ('_id', 'String'),
                    ('cloud_resource_id', 'String')
                ],
                'data': snapshots
            }],
            params={
                'month_before_start': month_before_start,
                'start_date': start_date
            })

    def _collect_resources(self, configs):
        now = datetime.now(tz=timezone.utc)
        (days_threshold, excluded_pools, _) = self.get_options_values()
        obsolete_threshold = timedelta(days=days_threshold)
        configs_map = {}
        resources_map = {}
        for config in configs:
            config.update(config.get('config', {}))
            configs_map[config['id']] = config
            resources = self.get_obsolete_resources(
                now, config['id'], config, obsolete_threshold)
            resources_map.update(
                {s['cloud_resource_id']: s for s in resources})
        if not resources_map:
            return []

        res = []
        resource_ids = list(resources_map.keys())
        cloud_account_ids = list(configs_map.keys())
        for i in range(0, len(resource_ids), BULK_SIZE):
            bulk_ids = resource_ids[i:i + BULK_SIZE]
            expenses = self._get_expenses(bulk_ids, cloud_account_ids,
                                          now - obsolete_threshold)
            for expense in expenses:
                resource_id, saving_base, start_date, end_date = expense
                resource = resources_map.get(resource_id)
                if resource:
                    if saving_base <= 0:
                        continue
                    end_date = end_date + timedelta(days=1)
                    date_range = end_date - start_date
                    lifetime_multiplier = date_range / timedelta(days=1)
                    saving = saving_base / lifetime_multiplier * DAYS_IN_MONTH
                    cloud_account = configs_map.get(
                        resource.get('cloud_account_id'), {})
                    res.append({
                        'cloud_resource_id': resource.get('cloud_resource_id'),
                        'resource_name': resource.get('name'),
                        'resource_id': resource.get('_id'),
                        'cloud_account_id': cloud_account.get('id'),
                        'cloud_type': cloud_account.get('type'),
                        'cloud_account_name': cloud_account.get('name'),
                        'first_seen': int(start_date.timestamp()),
                        'last_seen': int(end_date.timestamp()),
                        'saving': saving,
                        'region': resource.get('region'),
                        'folder_id': resource['meta'].get('folder_id'),
                        'last_used': resource['meta'].get('last_used') or 0,
                        'is_excluded': resource.get(
                            'pool_id') in excluded_pools,
                        # For snapshot chains that have nested snapshots
                        'child_snapshots': resource.get('meta', {}).get(
                            'snapshots')
                    })
        return res


class ObsoleteSnapshotsArchiveBase(ArchiveBase):

    @property
    def resource_type(self):
        return None

    def _get_active_resources(self, cloud_account_id):
        return self.mongo_client.restapi.resources.distinct(
            'cloud_resource_id', {'$and': [
                {'active': True},
                {'deleted_at': 0},
                {'resource_type': self.resource_type},
                {'cloud_account_id': cloud_account_id},
            ]})

    def get_used_resources(self, now, cloud_account_id, cloud_config,
                           obsolete_threshold):
        raise NotImplementedError

    def _get(self, previous_options, optimizations, cloud_accounts_map,
             **kwargs):
        now = datetime.utcnow()
        days_threshold = previous_options['days_threshold']
        obsolete_threshold = timedelta(days_threshold)

        account_optimizations_map = defaultdict(list)
        for optimization in optimizations:
            account_optimizations_map[optimization['cloud_account_id']].append(
                optimization)

        result = []
        for cloud_account_id, optimizations_ in account_optimizations_map.items():
            if cloud_account_id not in cloud_accounts_map:
                for optimization in optimizations_:
                    self._set_reason_properties(
                        optimization, ArchiveReason.CLOUD_ACCOUNT_DELETED)
                    result.append(optimization)
                continue

            cloud_config = cloud_accounts_map[cloud_account_id]
            cloud_config.update(cloud_config.get('config', {}))

            (res_used_by_images, res_using_volumes,
             res_used_by_volumes) = self.get_used_resources(
                now, cloud_account_id, cloud_config, obsolete_threshold)

            not_deleted_res = set(self._get_active_resources(cloud_account_id))
            for optimization in optimizations_:
                if optimization['cloud_resource_id'] in res_used_by_images:
                    self._set_reason_properties(
                        optimization, ArchiveReason.RECOMMENDATION_IRRELEVANT,
                        'used by AMI source')
                elif (optimization['cloud_resource_id'] in res_using_volumes or
                      optimization['cloud_resource_id'] in res_used_by_volumes):
                    self._set_reason_properties(
                        optimization, ArchiveReason.RECOMMENDATION_IRRELEVANT,
                        'used by volume')
                elif optimization['cloud_resource_id'] not in not_deleted_res:
                    self._set_reason_properties(
                        optimization, ArchiveReason.RECOMMENDATION_APPLIED)
                else:
                    self._set_reason_properties(
                        optimization, ArchiveReason.OPTIONS_CHANGED)
                result.append(optimization)
        return result
