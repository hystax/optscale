from bumiworker.bumiworker.consts import ArchiveReason
from bumiworker.bumiworker.modules.reserved_instances_base import (
    ReservedInstancesArchiveBase
)
from bumiworker.bumiworker.modules.recommendations.reserved_instances import (
    ReservedInstances as ReservedInstancesRecommendation
)


class ReservedInstances(ReservedInstancesArchiveBase,
                        ReservedInstancesRecommendation):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reason_description_map[ArchiveReason.FAILED_DEPENDENCY] = (
            'no reservation offers')

    @property
    def supported_cloud_types(self):
        return list(self.SUPPORTED_CLOUD_TYPES)


def main(organization_id, config_client, created_at, **kwargs):
    return ReservedInstances(
        organization_id, config_client, created_at).get()
