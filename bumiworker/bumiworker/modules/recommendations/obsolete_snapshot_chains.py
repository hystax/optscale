import logging
from collections import OrderedDict


from bumiworker.bumiworker.modules.obsolete_snapshots_base import ObsoleteSnapshotsBase

SUPPORTED_CLOUDS = [
    'alibaba_cnr',
]

LOG = logging.getLogger(__name__)

DEFAULT_DAYS_THRESHOLD = 3


class ObsoleteSnapshotChains(ObsoleteSnapshotsBase):
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
        snapshots_to_chains = self._get_snapshots_to_chains(
            cloud_account_id)

        snapshots_used_by_images = self.get_snapshots_used_by_images(
            now, config)
        chains_used_by_images = self._group_by_chains(
            snapshots_to_chains, snapshots_used_by_images)
        LOG.info('%s chains are used by images for account %s',
                 len(chains_used_by_images), cloud_account_id)

        snapshots_used_by_volumes = self.get_snapshots_used_by_volumes(
            now, cloud_account_id, obsolete_threshold)
        chains_used_by_volumes = self._group_by_chains(
            snapshots_to_chains, snapshots_used_by_volumes)
        LOG.info('%s chains are used by volumes for account %s',
                 len(chains_used_by_volumes), cloud_account_id)

        chains_using_volumes = self._get_chains_using_volumes(
            now, cloud_account_id)
        LOG.info('%s chains are using volumes for account %s',
                 len(chains_using_volumes), cloud_account_id)

        chains_in_use = {}
        self.merge_last_used(chains_in_use, chains_used_by_images)
        self.merge_last_used(chains_in_use, chains_used_by_volumes)
        self.merge_last_used(chains_in_use, chains_using_volumes)

        # we record the last use of snapshot chains, because it
        # will be difficult to calculate it after the fact
        self.update_last_used(cloud_account_id, chains_in_use)

        pipeline_chains = self.get_resources_pipeline(
            resource_type='Snapshot Chain',
            excluded_ids=list(chains_in_use.keys()),
            cloud_account_id=cloud_account_id,
            now=now,
            obsolete_threshold=obsolete_threshold,
        )
        return self.mongo_client.restapi.resources.aggregate(pipeline_chains)

    def _get_chains_using_volumes(self, now, cloud_account_id):
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
                {'resource_type': 'Snapshot Chain'},
                {'cloud_account_id': cloud_account_id},
                {'meta.volume_id': {'$in': active_volumes}}
            ]})
        return {c: now for c in chain_ids}

    def _get_snapshots_to_chains(self, cloud_account_id):
        snapshots_to_chains = {}
        active_chains = self.mongo_client.restapi.resources.find(
            {'$and': [
                {'active': True},
                {'deleted_at': 0},
                {'resource_type': 'Snapshot Chain'},
                {'cloud_account_id': cloud_account_id},
            ]}
        )
        for chain in active_chains:
            for snapshot_info in chain['meta']['snapshots']:
                snapshots_to_chains[snapshot_info[
                    'cloud_resource_id']] = chain['cloud_resource_id']
        return snapshots_to_chains

    def _group_by_chains(self, snapshots_to_chains, resource_map):
        grouped_by_chains = {}
        for resource_id, last_used in resource_map.items():
            chain_id = snapshots_to_chains.get(resource_id)
            if chain_id is not None:
                current_last_used = grouped_by_chains.get(chain_id)
                if current_last_used is None or current_last_used < last_used:
                    grouped_by_chains[chain_id] = last_used
        return grouped_by_chains


def main(organization_id, config_client, created_at, **kwargs):
    return ObsoleteSnapshotChains(
        organization_id, config_client, created_at).get()


def get_module_email_name():
    return 'Obsolete Snapshot Chains'
