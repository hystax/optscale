import logging

from collections import defaultdict
from datetime import datetime, timedelta, timezone

from bumiworker.bumiworker.consts import ArchiveReason
from bumiworker.bumiworker.modules.base import ArchiveBase
from bumiworker.bumiworker.modules.recommendations.obsolete_images import (
    ObsoleteImages as ObsoleteImagesRecommendation, SUPPORTED_CLOUD_TYPES)

LOG = logging.getLogger(__name__)


class ObsoleteImages(ArchiveBase, ObsoleteImagesRecommendation):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reason_description_map[ArchiveReason.RECOMMENDATION_APPLIED] = (
            'image deleted')

    @property
    def supported_cloud_types(self):
        return SUPPORTED_CLOUD_TYPES

    def _get(self, previous_options, optimizations, cloud_accounts_map,
             **kwargs):
        days_threshold = previous_options['days_threshold']
        account_optimizations_map = defaultdict(list)
        for optimization in optimizations:
            account_optimizations_map[optimization['cloud_account_id']].append(
                optimization)
        for ca_id in list(cloud_accounts_map.keys()):
            if ca_id not in account_optimizations_map:
                cloud_accounts_map.pop(ca_id)
        result = []
        starting_point = datetime.now(timezone.utc) - timedelta(
            days=days_threshold)

        images_map = self._get_images_map(cloud_accounts_map.values(), starting_point)
        used_image_ids = self.mongo_client.restapi.resources.distinct(
            'meta.image_id', {
                'cloud_account_id': {'$in': list(cloud_accounts_map.keys())},
                'resource_type': 'Instance',
                'meta.image_id': {'$in': list(images_map.keys())},
                '_last_seen_date': {'$gte': self.timestamp_to_day_start(
                    starting_point.timestamp())},
                'first_seen': {'$gte': starting_point.timestamp()}
            }
        )
        for cloud_account_id, optimizations_ in account_optimizations_map.items():
            if cloud_account_id not in cloud_accounts_map:
                for optimization in optimizations_:
                    self._set_reason_properties(
                        optimization, ArchiveReason.CLOUD_ACCOUNT_DELETED)
                    result.append(optimization)
                continue
            for optimization in optimizations_:
                resource_id = optimization['cloud_resource_id']
                if resource_id not in images_map:
                    self._set_reason_properties(
                        optimization, ArchiveReason.RECOMMENDATION_APPLIED)
                elif resource_id in used_image_ids:
                    self._set_reason_properties(
                        optimization, ArchiveReason.RECOMMENDATION_IRRELEVANT)
                else:
                    self._set_reason_properties(
                        optimization, ArchiveReason.OPTIONS_CHANGED)
                result.append(optimization)
        return result


def main(organization_id, config_client, created_at, **kwargs):
    return ObsoleteImages(
        organization_id, config_client, created_at).get()
