from collections import defaultdict
from datetime import datetime, timedelta

from bumiworker.bumiworker.consts import ArchiveReason
from bumiworker.bumiworker.modules.base import ArchiveBase
from bumiworker.bumiworker.modules.recommendations.abandoned_images import (
    AbandonedImages as AbandonedImagesRecommendation,
    SUPPORTED_CLOUD_TYPES
)


class AbandonedImages(ArchiveBase, AbandonedImagesRecommendation):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reason_description_map[ArchiveReason.RECOMMENDATION_APPLIED] = (
            self.reason_description_map[ArchiveReason.RESOURCE_DELETED])

    @property
    def supported_cloud_types(self):
        return SUPPORTED_CLOUD_TYPES

    def _get(self, previous_options, optimizations, cloud_accounts_map,
             **kwargs):
        days_threshold = previous_options['days_threshold']
        now = datetime.utcnow()
        start_date = now - timedelta(days=days_threshold)

        account_optimizations_map = defaultdict(list)
        for optimization in optimizations:
            account_optimizations_map[optimization['cloud_account_id']].append(
                optimization)

        images_by_account = self.get_active_resources(
            list(account_optimizations_map.keys()), start_date, 'Image')

        result = []
        for cloud_account_id, optimizations_ in account_optimizations_map.items():
            if cloud_account_id not in cloud_accounts_map:
                for optimization in optimizations_:
                    self._set_reason_properties(
                        optimization, ArchiveReason.CLOUD_ACCOUNT_DELETED)
                    result.append(optimization)
                continue

            account_images = images_by_account[cloud_account_id]
            cloud_resource_image_map = {
                account_image['cloud_resource_id']: account_image
                for account_image in account_images}
            last_used_map = self.get_last_used_map(
                cloud_account_id, list(cloud_resource_image_map.keys()))

            for optimization in optimizations_:
                cloud_resource_id = optimization['cloud_resource_id']
                image = cloud_resource_image_map.get(cloud_resource_id)
                last_used = last_used_map.get(cloud_resource_id)
                if not image:
                    reason = ArchiveReason.RECOMMENDATION_APPLIED
                elif last_used >= int(start_date.timestamp()):
                    reason = ArchiveReason.RECOMMENDATION_IRRELEVANT
                else:
                    reason = ArchiveReason.OPTIONS_CHANGED
                self._set_reason_properties(optimization, reason)
                result.append(optimization)
        return result


def main(organization_id, config_client, created_at, **kwargs):
    return AbandonedImages(
        organization_id, config_client, created_at).get()
