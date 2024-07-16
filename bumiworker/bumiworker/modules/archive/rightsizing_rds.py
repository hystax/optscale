from bumiworker.bumiworker.consts import ArchiveReason
from bumiworker.bumiworker.modules.recommendations.rightsizing_rds import (
    RightsizingRds as RightsizingRdsRecommendation)
from bumiworker.bumiworker.modules.rightsizing_base import (
    RightsizingArchiveBase
)


class RightsizingRds(RightsizingArchiveBase, RightsizingRdsRecommendation):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reason_description_map[ArchiveReason.RECOMMENDATION_APPLIED] = (
            'flavor changed')

    def set_additional_reasons(self, cloud_resource_map, cloud_account,
                               cloud_resource_id_instance_map,
                               optimizations_dict, days_threshold, result):
        for optimization in optimizations_dict.values():
            if 'reason' not in optimization:
                self._set_reason_properties(
                    optimization, ArchiveReason.OPTIONS_CHANGED)
                result.append(optimization)


def main(organization_id, config_client, created_at, **kwargs):
    return RightsizingRds(
        organization_id, config_client, created_at).get()
