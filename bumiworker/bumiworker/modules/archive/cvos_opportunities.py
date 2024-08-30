from bumiworker.bumiworker.consts import ArchiveReason
from bumiworker.bumiworker.modules.reserved_instances_base import (
    ReservedInstancesArchiveBase
)
from bumiworker.bumiworker.modules.recommendations.cvos_opportunities import (
    CVoSOpportunities as CVoSOpportunitiesRecommendation
)


class CVoSOpportunities(ReservedInstancesArchiveBase,
                        CVoSOpportunitiesRecommendation):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reason_description_map[ArchiveReason.FAILED_DEPENDENCY] = (
            'no committed volume of services agreement offers')

    @property
    def supported_cloud_types(self):
        return list(self.SUPPORTED_CLOUD_TYPES)


def main(organization_id, config_client, created_at, **kwargs):
    return CVoSOpportunities(
        organization_id, config_client, created_at).get()
