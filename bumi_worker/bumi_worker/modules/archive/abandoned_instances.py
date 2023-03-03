import logging
from collections import defaultdict
from datetime import datetime, timedelta

from bumi_worker.consts import ArchiveReason
from bumi_worker.modules.base import ArchiveBase
from bumi_worker.modules.recommendations.abandoned_instances import (
    AbandonedInstances as AbandonedInstancesRecommendation,
    SUPPORTED_CLOUD_TYPES)


LOG = logging.getLogger(__name__)


class AbandonedInstances(ArchiveBase, AbandonedInstancesRecommendation):
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
        cpu_percent_threshold = previous_options['cpu_percent_threshold']
        network_bps_threshold = previous_options['network_bps_threshold']

        now = datetime.utcnow()
        start_date = now - timedelta(days=days_threshold)
        cloud_acc_instances_map = defaultdict(dict)
        for cloud_acc_id, instances in self.get_active_resources(
                list(cloud_accounts_map.keys()), start_date, 'Instance').items():
            for instance in instances:
                instance_key = self.get_record_key(instance)
                cloud_acc_instances_map[cloud_acc_id][instance_key] = instance

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
            instance_ids = list(map(lambda x: x['resource_id'], optimizations_))
            resources_below_metric = self._get_resources_below_metric(
                cloud_account_id, instance_ids, start_date=start_date,
                end_date=now, cpu_percent_threshold=cpu_percent_threshold,
                network_bps_threshold=network_bps_threshold)
            instances_map = cloud_acc_instances_map.get(cloud_account_id, {})
            for optimization in optimizations_:
                instance_key = self.get_record_key(optimization)
                instance = instances_map.get(instance_key)
                if not instance:
                    reason = ArchiveReason.RECOMMENDATION_APPLIED
                elif instance['_id'] in resources_below_metric:
                    reason = ArchiveReason.OPTIONS_CHANGED
                else:
                    reason = ArchiveReason.RECOMMENDATION_IRRELEVANT
                self._set_reason_properties(optimization, reason)
                result.append(optimization)
        return result


def main(organization_id, config_client, created_at, **kwargs):
    return AbandonedInstances(
        organization_id, config_client, created_at).get()
