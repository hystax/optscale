import logging
from bumi_worker.consts import ArchiveReason
from bumi_worker.modules.base import ArchiveBase
from bumi_worker.modules.recommendations.s3_public_buckets import (
    S3PublicBuckets as S3PublicBucketsRecommendation,
    SUPPORTED_CLOUD_TYPES)


LOG = logging.getLogger(__name__)


class S3PublicBuckets(ArchiveBase, S3PublicBucketsRecommendation):
    @property
    def supported_cloud_types(self):
        return SUPPORTED_CLOUD_TYPES

    def _get(self, previous_options, optimizations, cloud_accounts_map,
             **kwargs):
        _, response = self.rest_client.cloud_resources_discover(
            self.organization_id, 'bucket')
        resources_map = {r['cloud_resource_id']: r for r in response['data']}

        result = []
        for optimization in optimizations:
            if optimization['cloud_account_id'] not in cloud_accounts_map:
                self._set_reason_properties(
                    optimization, ArchiveReason.CLOUD_ACCOUNT_DELETED)
                result.append(optimization)
                continue
            resource = resources_map.get(optimization['cloud_resource_id'], {})
            if not resource:
                self._set_reason_properties(
                    optimization, ArchiveReason.RESOURCE_DELETED)
            elif (not resource.get('meta', {}).get('is_public_policy') and
                  not resource.get('meta', {}).get('is_public_acls')):
                self._set_reason_properties(
                    optimization, ArchiveReason.RECOMMENDATION_APPLIED)
            else:
                self._set_reason_properties(
                    optimization, ArchiveReason.OPTIONS_CHANGED)
            result.append(optimization)
        return result


def main(organization_id, config_client, created_at, **kwargs):
    return S3PublicBuckets(
        organization_id, config_client, created_at).get()
