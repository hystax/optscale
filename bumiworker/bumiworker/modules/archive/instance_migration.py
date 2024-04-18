import logging
from collections import defaultdict

from bumiworker.bumiworker.consts import ArchiveReason
from bumiworker.bumiworker.modules.base import ArchiveBase
from bumiworker.bumiworker.modules.recommendations.instance_migration import (
    InstanceMigration as InstanceMigrationRecommendation,
    SUPPORTED_CLOUD_TYPES
)

HOURS_IN_MONTH = 30 * 24

LOG = logging.getLogger(__name__)


class InstanceMigration(ArchiveBase, InstanceMigrationRecommendation):
    def __init__(self, organization_id, config_client, created_at):
        super().__init__(organization_id, config_client, created_at)

    @property
    def supported_cloud_types(self):
        return SUPPORTED_CLOUD_TYPES

    def _get(self, previous_options, optimizations, cloud_accounts_map,
             **kwargs):
        result = []
        cloud_account_map = self.get_cloud_accounts(self.supported_cloud_types)

        account_optimizations_map = defaultdict(list)
        for optimization in optimizations:
            account_optimizations_map[optimization['cloud_account_id']].append(
                optimization)

        _, response = self.rest_client.cloud_resources_discover(
            self.organization_id, 'instance')
        active_cloud_res_ids = {
            x['cloud_resource_id']: x['region'] for x in response['data']
            if x['cloud_account_id'] in list(cloud_account_map.keys())}

        for cloud_account_id, optimizations_ in account_optimizations_map.items():
            if cloud_account_id not in cloud_accounts_map:
                for optimization in optimizations_:
                    self._set_reason_properties(
                        optimization, ArchiveReason.CLOUD_ACCOUNT_DELETED)
                    result.append(optimization)
                continue
            for optimization in optimizations_:
                if optimization['cloud_resource_id'] not in active_cloud_res_ids:
                    self._set_reason_properties(
                        optimization, ArchiveReason.RECOMMENDATION_APPLIED)
                else:
                    self._set_reason_properties(
                        optimization, ArchiveReason.OPTIONS_CHANGED)
                result.append(optimization)
        return result


def main(organization_id, config_client, created_at, **kwargs):
    return InstanceMigration(
        organization_id, config_client, created_at).get()
