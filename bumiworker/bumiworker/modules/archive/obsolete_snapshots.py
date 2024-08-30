from bumiworker.bumiworker.consts import ArchiveReason
from bumiworker.bumiworker.modules.obsolete_snapshots_base import (
    ObsoleteSnapshotsArchiveBase
)
from bumiworker.bumiworker.modules.recommendations.obsolete_snapshots import (
    ObsoleteSnapshots as ObsoleteSnapshotsRecommendation, SUPPORTED_CLOUDS,
    AWS_CLOUD
)


class ObsoleteSnapshots(ObsoleteSnapshotsArchiveBase,
                        ObsoleteSnapshotsRecommendation):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reason_description_map[ArchiveReason.RECOMMENDATION_APPLIED] = (
            'snapshot deleted')

    @property
    def resource_type(self):
        return 'Snapshot'

    @property
    def supported_cloud_types(self):
        return SUPPORTED_CLOUDS

    def get_used_resources(self, now, cloud_account_id, cloud_config,
                           obsolete_threshold):
        snapshots_used_by_images = {}
        if cloud_config.get('type') == AWS_CLOUD:
            snapshots_used_by_images = self.get_snapshots_used_by_images(
                now, cloud_config)
        snapshots_using_volumes = self._get_snapshots_using_volumes(
            now, cloud_account_id)
        snapshots_used_by_volumes = self.get_snapshots_used_by_volumes(
            now, cloud_account_id, obsolete_threshold)
        return (snapshots_used_by_images, snapshots_using_volumes,
                snapshots_used_by_volumes)


def main(organization_id, config_client, created_at, **kwargs):
    return ObsoleteSnapshots(
        organization_id, config_client, created_at).get()
