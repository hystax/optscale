from collections import defaultdict

from bumiworker.bumiworker.consts import ArchiveReason
from bumiworker.bumiworker.modules.base import ArchiveBase
from bumiworker.bumiworker.modules.recommendations.nebius_migration import (
    NebiusMigration as NebiusMigrationRecommendation
)


class NebiusMigration(ArchiveBase, NebiusMigrationRecommendation):

    @property
    def supported_cloud_types(self):
        return list(self.get_cloud_funcs_map().keys())

    def _get(self, previous_options, optimizations, cloud_accounts_map,
             **kwargs):
        result = []
        if not self._is_nebius_option_enabled():
            return result

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
    return NebiusMigration(
        organization_id, config_client, created_at).get()
