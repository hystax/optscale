from concurrent.futures.thread import ThreadPoolExecutor
from collections import OrderedDict
from datetime import datetime, timedelta
from calendar import monthrange

from bumiworker.bumiworker.modules.base import ModuleBase
from tools.cloud_adapter.cloud import Cloud as CloudAdapter

DEFAULT_DAYS_THRESHOLD = 7
BULK_SIZE = 1000
SUPPORTED_CLOUD_TYPES = [
    'aws_cnr',
    'alibaba_cnr'
]


class ObsoleteImages(ModuleBase):
    def __init__(self, organization_id, config_client, created_at):
        super().__init__(organization_id, config_client, created_at)
        self.option_ordered_map = OrderedDict({
            'days_threshold': {'default': DEFAULT_DAYS_THRESHOLD},
            'skip_cloud_accounts': {'default': []}
        })

    def get_snapshot_info_map(self, account_id_type_map, snapshot_image_map,
                              last_week_time):
        alibaba_clouds = []
        aws_clouds = []
        for acc_id, acc_type in account_id_type_map.items():
            if acc_type == 'aws_cnr':
                aws_clouds.append(acc_id)
            elif acc_type == 'alibaba_cnr':
                alibaba_clouds.append(acc_id)

        bulk_ids = []
        snapshot_image_ids = list(snapshot_image_map.keys())
        for i in range(0, len(snapshot_image_ids), BULK_SIZE):
            bulk_ids = snapshot_image_ids[i:i + BULK_SIZE]
        snapshot_info_alibaba_map = {}
        snapshot_info_aws_map = {}
        if alibaba_clouds:
            snapshot_info_alibaba_map = self.get_snapshot_info_alibaba(
                bulk_ids, alibaba_clouds, last_week_time)
        if aws_clouds:
            snapshot_info_aws_map = self.get_snapshot_info_aws(
                bulk_ids, aws_clouds, last_week_time)
        return {**snapshot_info_aws_map, **snapshot_info_alibaba_map}

    def _get_snapshot_expenses(self, snapshots, start_date):
        query = """
            SELECT resource_id, cloud_resource_id,
                sum(cost * sign) / count(distinct(date))
            FROM expenses
            JOIN resources ON resource_id = resources._id AND date >= %(date)s
            GROUP BY resource_id, cloud_resource_id
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
                'date': start_date
            })

    def get_snapshot_info_aws(self, bulk_ids, account_ids,
                              last_week_time):
        snapshots = list(self.mongo_client.restapi.resources.find({
            'cloud_account_id': {'$in': account_ids},
            'cloud_resource_id': {'$in': bulk_ids},
        }, ['cloud_resource_id']))
        snapshot_expenses = self._get_snapshot_expenses(
            snapshots, last_week_time)
        snapshot_info_map = {}
        for resource_id, cloud_resource_id, cost in snapshot_expenses:
            snapshot_info_map[cloud_resource_id] = {
                'cloud_resource_id': cloud_resource_id,
                'resource_id': resource_id,
                'cost': cost
            }
        return snapshot_info_map

    def get_snapshot_info_alibaba(self, bulk_ids, account_ids,
                                  last_week_time):
        snapshot_info_map = {}
        snapshot_chain_resources_pipeline = [
            {
                '$match': {
                    '$and': [
                        {'cloud_account_id': {'$in': account_ids}},
                        {'meta.snapshots': {'$size': 1}},
                        {'_first_seen_date': {'$lte': last_week_time}},
                        {'first_seen': {
                            '$lte': int(
                                last_week_time.timestamp())}}
                    ]
                }
            },
            {
                '$project': {
                    '_id': '$_id',
                    'cloud_resource_id': '$cloud_resource_id',
                    'snapshots': '$meta.snapshots'
                }
            },
            {
                '$unwind': '$snapshots'
            },
            {
                '$match': {
                    'snapshots.cloud_resource_id': {
                        '$in': bulk_ids}
                }
            }
        ]
        snap_chains = self.mongo_client.restapi.resources.aggregate(
            snapshot_chain_resources_pipeline)
        sc_snapshot_map = {}
        external_table = []
        for sc in snap_chains:
            external_table.append({
                '_id': sc['_id'],
                'cloud_resource_id': sc['cloud_resource_id']
            })
            sc_snapshot_map[sc['cloud_resource_id']] = sc['snapshots'][
                'cloud_resource_id']

        snapshot_expenses = self._get_snapshot_expenses(
            external_table, last_week_time)
        for resource_id, cloud_resource_id, cost in snapshot_expenses:
            snapshot_info_map[sc_snapshot_map[cloud_resource_id]] = {
                'resource_id': resource_id,
                'cloud_resource_id': cloud_resource_id,
                'cost': cost
            }
        return snapshot_info_map

    def _get(self):
        (days_threshold, skip_cloud_accounts) = self.get_options_values()
        cloud_account_map = self.get_cloud_accounts(
            SUPPORTED_CLOUD_TYPES, skip_cloud_accounts)
        cloud_accounts = list(cloud_account_map.values())

        account_id_type_map = {x['id']: x['type'] for x in cloud_accounts}
        images_map = {}
        starting_point = datetime.utcnow() - timedelta(days=days_threshold)

        def process_images(cloud_account, generator):
            for image in generator:
                i = image.to_dict()
                if i['cloud_created_at'] >= int(starting_point.timestamp()):
                    continue
                i.update({
                    'cloud_account_id': cloud_account['id'],
                    'cloud_type': cloud_account['type'],
                })
                images_map.update({i['cloud_resource_id']: i})

        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = []
            for cloud_account in cloud_accounts:
                cloud_account.update(cloud_account.get('config', {}))
                cloud_adapter = CloudAdapter.get_adapter(cloud_account)

                for func, params in cloud_adapter.image_discovery_calls():
                    futures.append(executor.submit(func, *params))
                results = []
                for f in futures:
                    results.append(executor.submit(
                        process_images, cloud_account, f.result()))

        image_ids = list(images_map.keys())
        images = self.mongo_client.restapi.resources.aggregate([
            {
                '$match': {'$and': [
                    {'cloud_account_id': {'$in': list(
                        account_id_type_map.keys())}},
                    {'resource_type': 'Instance'},
                    {'meta.image_id': {'$in': image_ids}}
                ]},
            },
            {
                '$group': {
                    '_id': '$meta.image_id',
                    'last_used': {'$max': '$last_seen'}
                }
            }
        ])
        last_used_map = {i['_id']: i['last_used'] for i in images}
        result = {}
        snapshot_image_map = {}
        for image_id in image_ids:
            last_used = last_used_map.get(image_id, 0)
            if last_used >= starting_point.timestamp():
                continue
            image = images_map[image_id]
            for bdm in image['meta']['block_device_mappings']:
                snapshot_id = bdm.get('snapshot_id')
                if snapshot_id:
                    if snapshot_id not in snapshot_image_map:
                        snapshot_image_map[snapshot_id] = []
                    snapshot_image_map[snapshot_id].append(
                        image['cloud_resource_id'])

            result[image_id] = {
                'cloud_resource_id': image_id,
                'resource_name': image['name'],
                'cloud_account_id': image['cloud_account_id'],
                'cloud_type': image['cloud_type'],
                'first_seen': image['cloud_created_at'],
                'region': image['region'],
                'last_used': last_used
            }

        snapshot_info_map = self.get_snapshot_info_map(
            account_id_type_map, snapshot_image_map, starting_point)
        today = datetime.utcnow()
        _, days_in_month = monthrange(today.year, today.month)
        for snapshot_id, image_ids in snapshot_image_map.items():
            for image_id in image_ids:
                image = result.get(image_id)
                saving = image.get('saving', 0)
                if not image:
                    continue
                snapshots = image.get('snapshots', [])
                snapshot_info = snapshot_info_map.get(snapshot_id, {})
                if snapshot_info:
                    snapshot_cost = snapshot_info.get('cost', 0) * days_in_month
                    snapshot_info['cost'] = snapshot_cost
                    snapshot_info.pop('_id', None)
                    snapshots.append(snapshot_info)
                    saving += snapshot_cost
                image['saving'] = saving
                image['snapshots'] = snapshots
        return [r for r in list(result.values()) if r['saving'] != 0]


def main(organization_id, config_client, created_at, **kwargs):
    return ObsoleteImages(
        organization_id, config_client, created_at).get()


def get_module_email_name():
    return 'Obsolete Images'
