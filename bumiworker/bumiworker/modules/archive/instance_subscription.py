import logging

from collections import defaultdict
from datetime import datetime, timedelta, timezone

from bumiworker.bumiworker.consts import ArchiveReason
from bumiworker.bumiworker.modules.base import ArchiveBase
from bumiworker.bumiworker.modules.recommendations.instance_subscription import (
    InstanceSubscription as InstanceSubscriptionRecommendation,
    SUPPORTED_CLOUD_TYPES, SUBSCRIPTION_ITEM
)

LOG = logging.getLogger(__name__)


class InstanceSubscription(ArchiveBase, InstanceSubscriptionRecommendation):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reason_description_map[ArchiveReason.RESOURCE_DELETED] = (
            'instance deleted')
        self.reason_description_map[ArchiveReason.FAILED_DEPENDENCY] = (
            'subscription unavailable')
        self.reason_description_map[ArchiveReason.RECOMMENDATION_IRRELEVANT] = (
            'discounts applied')

    @property
    def supported_cloud_types(self):
        return SUPPORTED_CLOUD_TYPES

    def _has_discounts(self, raw_info):
        if raw_info.get('cost') == 0:
            # savings plan applied
            return True
        for key in ['coupons_discount', 'resource_package_discount']:
            if key in raw_info and float(raw_info[key]):
                return True

    def _get(self, previous_options, optimizations, cloud_accounts_map,
             **kwargs):
        now = datetime.now(tz=timezone.utc)
        days_threshold = previous_options['days_threshold']
        range_start_ts = int(
            (now - timedelta(days=days_threshold)).timestamp())

        account_optimizations_map = defaultdict(list)
        for optimization in optimizations:
            account_optimizations_map[optimization['cloud_account_id']].append(
                optimization)

        cloud_acc_instance_map = self.get_cloud_acc_instances_map(
            list(account_optimizations_map.keys()), range_start_ts
        )

        result = []
        for cloud_account_id, optimizations_ in account_optimizations_map.items():
            if cloud_account_id not in cloud_accounts_map:
                for optimization in optimizations_:
                    self._set_reason_properties(
                        optimization, ArchiveReason.CLOUD_ACCOUNT_DELETED)
                    result.append(optimization)
                continue

            cloud_resource_ids = [x['cloud_resource_id']
                                  for x in optimizations_]
            raw_expenses = self.get_raw_expenses(
                cloud_account_id, now, cloud_resource_ids)
            raw_expenses_map = {x['_id']: x for x in raw_expenses}
            active_resources = cloud_acc_instance_map.get(cloud_account_id, {})

            for optimization in optimizations_:
                cloud_resource_id = optimization['cloud_resource_id']
                instance = active_resources.get(cloud_resource_id)
                raw_info = raw_expenses_map.get(cloud_resource_id, {})
                if not instance:
                    reason = ArchiveReason.RESOURCE_DELETED
                elif SUBSCRIPTION_ITEM in raw_info['billing_item']:
                    reason = ArchiveReason.RECOMMENDATION_APPLIED
                elif self._has_discounts(raw_info):
                    reason = ArchiveReason.RECOMMENDATION_IRRELEVANT
                elif any(x is None for x in self.get_subscriptions_costs(
                            cloud_resource_id, instance['meta']['flavor'],
                            instance['region'])):
                    reason = ArchiveReason.FAILED_DEPENDENCY
                else:
                    reason = ArchiveReason.OPTIONS_CHANGED
                self._set_reason_properties(optimization, reason)
                result.append(optimization)
        return result


def main(organization_id, config_client, created_at, **kwargs):
    return InstanceSubscription(
        organization_id, config_client, created_at).get()
