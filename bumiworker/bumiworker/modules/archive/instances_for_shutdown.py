import logging
from datetime import datetime, timezone, timedelta
from collections import defaultdict

from bumiworker.bumiworker.consts import ArchiveReason
from bumiworker.bumiworker.modules.base import ArchiveBase
from bumiworker.bumiworker.modules.recommendations.instances_for_shutdown import (
    InstancesForShutdown as InstancesForShutdownRecommendation,
    SUPPORTED_CLOUD_TYPES, DAYS_IN_WEEK, HOURS_IN_DAY
)

HOURS_IN_MONTH = 30 * 24

LOG = logging.getLogger(__name__)


class InstancesForShutdown(ArchiveBase, InstancesForShutdownRecommendation):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reason_description_map[ArchiveReason.RECOMMENDATION_APPLIED] = (
            'resource is powered off or metrics are greater than thresholds')

    @property
    def supported_cloud_types(self):
        return SUPPORTED_CLOUD_TYPES

    def _get_not_below_threshold(
            self, cloud_account_id, resource_ids, start_date, end_date,
            cpu_percent_threshold, network_bps_threshold):
        not_under_threshold = defaultdict(list)

        # fill default values like no metrics for resource
        for resource_id in resource_ids:
            not_under_threshold[resource_id] = [
                x for x in range(DAYS_IN_WEEK * HOURS_IN_DAY)
            ]

        _, activity_breakdown = self.metroculus_cl.get_activity_breakdown(
            cloud_account_id, resource_ids, int(start_date.timestamp()),
            int(end_date.timestamp()), ['cpu', 'network_in_io',
                                        'network_out_io'])

        for resource_id, metrics_breakdown in activity_breakdown.items():
            cpu_breakdown = metrics_breakdown.get('cpu')
            net_in_breakdown = metrics_breakdown.get('network_in_io')
            net_out_breakdown = metrics_breakdown.get('network_out_io')

            if (not cpu_breakdown or not net_in_breakdown or
                    not net_out_breakdown):
                continue

            for interval_number in range(DAYS_IN_WEEK*HOURS_IN_DAY):
                cpu = cpu_breakdown[interval_number]
                net_in = net_in_breakdown[interval_number]
                net_out = net_out_breakdown[interval_number]
                # instance is powered off or instance's metrics > thresholds
                if (cpu is None or net_in is None or net_out is None
                        or cpu > cpu_percent_threshold
                        or net_in + net_out > network_bps_threshold):
                    not_under_threshold[resource_id].append(interval_number)
        return not_under_threshold

    @staticmethod
    def _unmerge_intervals(intervals):
        # transform ranges to a list of interval numbers
        # e.g. transform
        # [{
        #    "start": {
        #      "day_of_week": 0,
        #      "hour": 0
        #    },
        #    "end": {
        #      "day_of_week": 0,
        #      "hour": 3
        #    }
        # }]
        # into [0,1,2,3]
        result = []
        if not intervals:
            return result
        for interval in intervals:
            start = interval['start']
            end = interval['end']
            result.extend(x for x in range(
                start['day_of_week'] * HOURS_IN_DAY + start['hour'],
                end['day_of_week'] * HOURS_IN_DAY + end['hour'] + 1))
        return result

    def _get(self, previous_options, optimizations, cloud_accounts_map,
             **kwargs):
        result = []
        days_threshold = previous_options['days_threshold']
        cpu_percent_threshold = previous_options['cpu_percent_threshold']
        network_bps_threshold = previous_options['network_bps_threshold']

        account_optimizations_map = defaultdict(list)
        for optimization in optimizations:
            account_optimizations_map[optimization['cloud_account_id']].append(
                optimization)

        now = datetime.now(tz=timezone.utc)
        today = now.replace(
            hour=0, minute=0, second=0, microsecond=0)
        start_date = today - timedelta(days=days_threshold)
        instances_by_account = self.get_active_resources(
            list(account_optimizations_map.keys()), start_date, 'Instance')

        for cloud_account_id, optimizations_ in account_optimizations_map.items():
            if cloud_account_id not in cloud_accounts_map:
                for optimization in optimizations_:
                    self._set_reason_properties(
                        optimization, ArchiveReason.CLOUD_ACCOUNT_DELETED)
                    result.append(optimization)
                continue

            active_inst_ids = [
                x['_id'] for x in instances_by_account.get(
                    cloud_account_id, [])
            ]
            not_under_threshold_intervals = self._get_not_below_threshold(
                cloud_account_id, active_inst_ids, start_date, now,
                cpu_percent_threshold, network_bps_threshold)

            (_, new_cpu_percent_threshold,
             new_network_bps_threshold, _, _) = self.get_options_values()

            for optimization in optimizations_:
                resource_id = optimization['resource_id']
                opt_intervals = self._unmerge_intervals(
                    optimization['inactivity_periods'])
                res_activity = not_under_threshold_intervals[resource_id]
                if resource_id not in active_inst_ids:
                    self._set_reason_properties(
                        optimization, ArchiveReason.RESOURCE_DELETED)
                elif (all(x in res_activity for x in opt_intervals) and
                        new_cpu_percent_threshold >= cpu_percent_threshold and
                        new_network_bps_threshold >= network_bps_threshold):
                    self._set_reason_properties(
                        optimization, ArchiveReason.RECOMMENDATION_APPLIED)
                else:
                    self._set_reason_properties(
                        optimization, ArchiveReason.OPTIONS_CHANGED)
                result.append(optimization)
        return result


def main(organization_id, config_client, created_at, **kwargs):
    return InstancesForShutdown(
        organization_id, config_client, created_at).get()
