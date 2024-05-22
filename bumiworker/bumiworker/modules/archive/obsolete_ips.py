from collections import defaultdict
from datetime import datetime, timedelta, timezone

from bumiworker.bumiworker.modules.base import ArchiveBase, ArchiveReason
from bumiworker.bumiworker.modules.recommendations.obsolete_ips import (
    ObsoleteIps as ObsoleteIpsRecommendation, SUPPORTED_CLOUD_TYPES
)


class ObsoleteIps(ArchiveBase, ObsoleteIpsRecommendation):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reason_description_map[ArchiveReason.RECOMMENDATION_APPLIED] = (
            'ip address deleted')
        self.reason_description_map[
            ArchiveReason.RECOMMENDATION_IRRELEVANT] = (
            'ip address is in use or was in use in threshold')

    @property
    def supported_cloud_types(self):
        return SUPPORTED_CLOUD_TYPES

    def _get(self, previous_options, optimizations, cloud_accounts_map,
             **kwargs):
        now = datetime.now(tz=timezone.utc)
        days_threshold = previous_options['days_threshold']
        start_date_ts = int((now - timedelta(days_threshold)).timestamp())

        account_optimizations_map = defaultdict(list)
        resource_ids = []
        for optimization in optimizations:
            account_optimizations_map[optimization['cloud_account_id']].append(
                optimization)
            resource_ids.append(optimization['resource_id'])

        active_ips = self.mongo_client.restapi.resources.find(
                {'_id': {'$in': resource_ids}, 'active': True},
                {'_id': 1, 'meta.last_used': 1})
        active_ip_last_used = {x['_id']: x.get('meta', {}).get('last_used', 0)
                               for x in active_ips}

        result = []
        for cloud_account_id, optimizations_ in account_optimizations_map.items():
            if cloud_account_id not in cloud_accounts_map:
                for optimization in optimizations_:
                    self._set_reason_properties(
                        optimization, ArchiveReason.CLOUD_ACCOUNT_DELETED)
                    result.append(optimization)
                continue

            for optimization in optimizations_:
                resource_id = optimization['resource_id']
                if resource_id not in active_ip_last_used:
                    self._set_reason_properties(
                        optimization, ArchiveReason.RECOMMENDATION_APPLIED)
                    result.append(optimization)
                    continue
                last_used = active_ip_last_used[resource_id]
                reason = ArchiveReason.RECOMMENDATION_IRRELEVANT if (
                        last_used >= start_date_ts
                ) else ArchiveReason.OPTIONS_CHANGED
                self._set_reason_properties(optimization, reason)
                result.append(optimization)
        return result


def main(organization_id, config_client, created_at, **kwargs):
    return ObsoleteIps(organization_id, config_client, created_at).get()
