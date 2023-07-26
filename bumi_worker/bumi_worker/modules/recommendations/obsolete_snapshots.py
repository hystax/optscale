import logging
from collections import OrderedDict


from bumi_worker.modules.obsolete_snapshots_base import ObsoleteSnapshotsBase

AWS_CLOUD = 'aws_cnr'
SUPPORTED_CLOUDS = [
    'aws_cnr',
    'nebius',
]

LOG = logging.getLogger(__name__)

DEFAULT_DAYS_THRESHOLD = 3


class ObsoleteSnapshots(ObsoleteSnapshotsBase):
    def __init__(self, organization_id, config_client, created_at):
        super().__init__(organization_id, config_client, created_at)
        self.option_ordered_map = OrderedDict({
            'days_threshold': {'default': DEFAULT_DAYS_THRESHOLD},
            'excluded_pools': {
                'default': {},
                'clean_func': self.clean_excluded_pools,
            },
            'skip_cloud_accounts': {'default': []}
        })

    def get_supported_clouds(self):
        return SUPPORTED_CLOUDS

    def get_obsolete_resources(self, now, cloud_account_id, config,
                               obsolete_threshold):
        snapshots_used_by_images = {}
        if config.get('type') == AWS_CLOUD:
            snapshots_used_by_images = self.get_snapshots_used_by_images(
                now, config)

        snapshots_used_by_volumes = self.get_snapshots_used_by_volumes(
            now, cloud_account_id, obsolete_threshold)

        snapshots_using_volumes = self._get_snapshots_using_volumes(
            now, cloud_account_id)

        snapshots_in_use = {}
        self.merge_last_used(snapshots_in_use, snapshots_used_by_images)
        self.merge_last_used(snapshots_in_use, snapshots_used_by_volumes)
        self.merge_last_used(snapshots_in_use, snapshots_using_volumes)

        # we record the last use of snapshots, because it
        # will be difficult to calculate it after the fact
        self.update_last_used(cloud_account_id, snapshots_in_use)

        pipeline_snapshots = self.get_resources_pipeline(
            resource_type='Snapshot',
            excluded_ids=list(snapshots_in_use.keys()),
            cloud_account_id=cloud_account_id,
            now=now,
            obsolete_threshold=obsolete_threshold,
        )
        return self.mongo_client.restapi.resources.aggregate(pipeline_snapshots)

    def _get_snapshots_using_volumes(self, now, cloud_account_id):
        active_volumes = self.mongo_client.restapi.resources.distinct(
            'cloud_resource_id', {'$and': [
                {'active': True},
                {'deleted_at': 0},
                {'resource_type': 'Volume'},
                {'cloud_account_id': cloud_account_id}
            ]})
        chain_ids = self.mongo_client.restapi.resources.distinct(
            'cloud_resource_id', {'$and': [
                {'active': True},
                {'deleted_at': 0},
                {'resource_type': 'Snapshot'},
                {'cloud_account_id': cloud_account_id},
                {'meta.volume_id': {'$in': active_volumes}}
            ]})
        return {c: now for c in chain_ids}


def main(organization_id, config_client, created_at, **kwargs):
    return ObsoleteSnapshots(
        organization_id, config_client, created_at).get()


def get_module_email_name():
    return 'Obsolete Snapshots'
