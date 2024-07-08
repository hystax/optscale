from bumiworker.bumiworker.consts import ArchiveReason
from bumiworker.bumiworker.modules.recommendations.obsolete_snapshot_chains import (
    ObsoleteSnapshotChains as ObsoleteSnapshotChainsRecommendation,
    SUPPORTED_CLOUDS,
)
from bumiworker.bumiworker.modules.obsolete_snapshots_base import (
    ObsoleteSnapshotsArchiveBase
)


class ObsoleteSnapshotChains(ObsoleteSnapshotsArchiveBase,
                             ObsoleteSnapshotChainsRecommendation):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reason_description_map[ArchiveReason.RECOMMENDATION_APPLIED] = (
            'snapshot chain deleted')

    @property
    def supported_cloud_types(self):
        return SUPPORTED_CLOUDS

    @property
    def resource_type(self):
        return 'Snapshot Chain'

    def get_used_resources(self, now, cloud_account_id, cloud_config,
                           obsolete_threshold):
        snapshots_to_chains = self._get_snapshots_to_chains(
            cloud_account_id)
        snapshots_used_by_images = self.get_snapshots_used_by_images(
            now, cloud_config)
        chains_used_by_images = self._group_by_chains(
            snapshots_to_chains, snapshots_used_by_images)
        snapshots_used_by_volumes = self.get_snapshots_used_by_volumes(
            now, cloud_account_id, obsolete_threshold)
        chains_used_by_volumes = self._group_by_chains(
            snapshots_to_chains, snapshots_used_by_volumes)
        chains_using_volumes = self._get_chains_using_volumes(
            now, cloud_account_id)
        return (chains_used_by_images, chains_using_volumes,
                chains_used_by_volumes)


def main(organization_id, config_client, created_at, **kwargs):
    return ObsoleteSnapshotChains(
        organization_id, config_client, created_at).get()
