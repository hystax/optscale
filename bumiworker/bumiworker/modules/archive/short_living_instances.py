import logging
from collections import defaultdict

from bumiworker.bumiworker.consts import ArchiveReason
from bumiworker.bumiworker.modules.base import ArchiveBase
from bumiworker.bumiworker.modules.recommendations.short_living_instances import (
    ShortLivingInstances as ShortLivingInstancesRecommendation,
    SUPPORTED_CLOUD_TYPES
)

HOURS_IN_MONTH = 30 * 24

LOG = logging.getLogger(__name__)


class ShortLivingInstances(ArchiveBase, ShortLivingInstancesRecommendation):

    @property
    def supported_cloud_types(self):
        return SUPPORTED_CLOUD_TYPES

    def _get(self, previous_options, optimizations, cloud_accounts_map,
             **kwargs):
        result = []

        account_optimizations_map = defaultdict(list)
        for optimization in optimizations:
            account_optimizations_map[optimization['cloud_account_id']].append(
                optimization)

        for cloud_account_id, optimizations_ in account_optimizations_map.items():
            reason = ArchiveReason.OPTIONS_CHANGED if (
                cloud_account_id in cloud_accounts_map
            ) else ArchiveReason.CLOUD_ACCOUNT_DELETED
            for optimization in optimizations_:
                self._set_reason_properties(optimization, reason)
                result.append(optimization)
        return result


def main(organization_id, config_client, created_at, **kwargs):
    return ShortLivingInstances(
        organization_id, config_client, created_at).get()
