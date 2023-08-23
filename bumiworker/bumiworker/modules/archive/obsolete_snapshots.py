import logging

from collections import defaultdict
from datetime import datetime, timedelta

from bumiworker.bumiworker.consts import ArchiveReason
from bumiworker.bumiworker.modules.base import ArchiveBase
from bumiworker.bumiworker.modules.recommendations.obsolete_snapshots import (
    ObsoleteSnapshots as ObsoleteSnapshotsRecommendation, SUPPORTED_CLOUDS,
    AWS_CLOUD)

LOG = logging.getLogger(__name__)


class ObsoleteSnapshots(ArchiveBase, ObsoleteSnapshotsRecommendation):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reason_description_map[ArchiveReason.RECOMMENDATION_APPLIED] = (
            'snapshot deleted')

    @property
    def supported_cloud_types(self):
        return SUPPORTED_CLOUDS

    def _get_active_snapshots(self, cloud_account_id):
        return self.mongo_client.restapi.resources.distinct(
            'cloud_resource_id', {'$and': [
                {'active': True},
                {'deleted_at': 0},
                {'resource_type': 'Snapshot'},
                {'cloud_account_id': cloud_account_id},
            ]})

    def _get(self, previous_options, optimizations, cloud_accounts_map,
             **kwargs):
        now = datetime.utcnow()
        days_threshold = previous_options['days_threshold']
        obsolete_threshold = timedelta(days_threshold)

        account_optimizations_map = defaultdict(list)
        for optimization in optimizations:
            account_optimizations_map[optimization['cloud_account_id']].append(
                optimization)

        result = []
        for cloud_account_id, optimizations_ in account_optimizations_map.items():
            if cloud_account_id not in cloud_accounts_map:
                for optimization in optimizations_:
                    self._set_reason_properties(
                        optimization, ArchiveReason.CLOUD_ACCOUNT_DELETED)
                    result.append(optimization)
                continue

            cloud_config = cloud_accounts_map[cloud_account_id]['config']
            cloud_config['type'] = cloud_accounts_map[cloud_account_id]['type']

            snapshots_used_by_images = {}
            if cloud_config.get('type') == AWS_CLOUD:
                snapshots_used_by_images = self.get_snapshots_used_by_images(
                    now, cloud_config)
            snapshots_using_volumes = self._get_snapshots_using_volumes(
                now, cloud_account_id)
            snapshots_used_by_volumes = self.get_snapshots_used_by_volumes(
                now, cloud_account_id, obsolete_threshold)
            not_deleted_snapshots = set(self._get_active_snapshots(
                cloud_account_id))
            for optimization in optimizations_:
                if optimization['cloud_resource_id'] in snapshots_used_by_images:
                    self._set_reason_properties(
                        optimization, ArchiveReason.RECOMMENDATION_IRRELEVANT,
                        'used by AMI source')
                elif (optimization['cloud_resource_id'] in snapshots_using_volumes or
                      optimization['cloud_resource_id'] in snapshots_used_by_volumes):
                    self._set_reason_properties(
                        optimization, ArchiveReason.RECOMMENDATION_IRRELEVANT,
                        'used by volume')
                elif optimization['cloud_resource_id'] not in not_deleted_snapshots:
                    self._set_reason_properties(
                        optimization, ArchiveReason.RECOMMENDATION_APPLIED)
                else:
                    self._set_reason_properties(
                        optimization, ArchiveReason.OPTIONS_CHANGED)
                result.append(optimization)
        return result


def main(organization_id, config_client, created_at, **kwargs):
    return ObsoleteSnapshots(
        organization_id, config_client, created_at).get()
