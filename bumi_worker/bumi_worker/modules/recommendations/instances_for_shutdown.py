import logging
from collections import OrderedDict, defaultdict
from datetime import datetime, timedelta
from bumi_worker.modules.base import DAYS_IN_MONTH
from metroculus_client.client import Client as MetroculusClient

from bumi_worker.modules.abandoned_base import AbandonedBase

DAYS_IN_WEEK = 7
HOURS_IN_DAY = 24

SUPPORTED_CLOUD_TYPES = [
    'aws_cnr',
    'azure_cnr',
    'alibaba_cnr'
]

LOG = logging.getLogger(__name__)

METRICS_BULK_SIZE = 50

DEFAULT_DAYS_THRESHOLD = 14
DEFAULT_CPU_PERCENT_THRESHOLD = 5
DEFAULT_NETWORK_BPS_THRESHOLD = 1000


class InstancesForShutdown(AbandonedBase):
    def __init__(self, organization_id, config_client, created_at, **kwargs):
        super().__init__(organization_id, config_client, created_at, **kwargs)
        self.option_ordered_map = OrderedDict({
            'days_threshold': {
                'default': DEFAULT_DAYS_THRESHOLD},
            'cpu_percent_threshold': {
                'default': DEFAULT_CPU_PERCENT_THRESHOLD},
            'network_bps_threshold': {
                'default': DEFAULT_NETWORK_BPS_THRESHOLD},
            'excluded_pools': {
                'default': {},
                'clean_func': self.clean_excluded_pools,
            },
            'skip_cloud_accounts': {'default': []}
        })
        self._metroculus_cl = None

    @property
    def metroculus_cl(self):
        if self._metroculus_cl is None:
            self._metroculus_cl = MetroculusClient(
                url=self.config_cl.metroculus_url(),
                secret=self.config_cl.cluster_secret(),
                verify=False)
        return self._metroculus_cl

    @staticmethod
    def _interval_number_to_day_hour(interval_number):
        # transform a linear interval number into a pair (day of week, hour)
        # e.g. transform 0 into (0, 0) and 25 into (1, 1)
        return interval_number // HOURS_IN_DAY, interval_number % HOURS_IN_DAY

    @staticmethod
    def _interval_range_to_json(start, end):
        start_day, start_hour = InstancesForShutdown._interval_number_to_day_hour(
            start)
        end_day, end_hour = InstancesForShutdown._interval_number_to_day_hour(
            end)
        return {
            "start": {
                "day_of_week": start_day,
                "hour": start_hour
            },
            "end": {
                "day_of_week": end_day,
                "hour": end_hour
            }
        }

    @staticmethod
    def _merge_intervals(intervals):
        # transform a list of interval numbers into ranges
        # e.g. transofrm [0,1,2,3,4,5,9,10] into [(0, 5), (9,10)]
        result = []
        if not intervals:
            return result
        current_range_start = intervals[0]
        last_interval = intervals[0]
        # add a really large fake last value
        # to avoid writing extra code for handling the last element
        for interval in intervals[1:] + [1000000000]:
            if interval != last_interval + 1:
                result.append(
                    InstancesForShutdown._interval_range_to_json(current_range_start, last_interval))
                current_range_start = interval
            last_interval = interval
        return result

    def _get_inactivity_intervals(
            self, cloud_account_id, resource_ids, start_date, end_date,
            cpu_percent_threshold, network_bps_threshold):
        inactivity_intervals = defaultdict(list)

        _, activity_breakdown = self.metroculus_cl.get_activity_breakdown(
            cloud_account_id, resource_ids, int(start_date.timestamp()),
            int(end_date.timestamp()), ['cpu', 'network_in_io', 'network_out_io'])

        for resource_id, metrics_breakdown in activity_breakdown.items():
            cpu_breakdown = metrics_breakdown.get('cpu')
            net_in_breakdown = metrics_breakdown.get('network_in_io')
            net_out_breakdown = metrics_breakdown.get('network_out_io')

            if not cpu_breakdown or not net_in_breakdown or not net_out_breakdown:
                continue

            for interval_number in range(DAYS_IN_WEEK*HOURS_IN_DAY):
                cpu = cpu_breakdown[interval_number]
                if cpu is None or cpu > cpu_percent_threshold:
                    continue
                net_in = net_in_breakdown[interval_number]
                net_out = net_out_breakdown[interval_number]
                if net_in is None or net_out is None:
                    continue
                net_total = net_in + net_out
                if net_total > network_bps_threshold:
                    continue
                inactivity_intervals[resource_id].append(interval_number)

        return inactivity_intervals

    def _get_resource_savings(self, daily_expenses, inactivity_intervals):
        weekly_savings = daily_expenses / HOURS_IN_DAY * len(inactivity_intervals)
        montly_savings = weekly_savings / DAYS_IN_WEEK * DAYS_IN_MONTH
        return montly_savings

    def _get(self):
        (days_threshold, cpu_percent_threshold, network_bps_threshold,
         excluded_pools, skip_cloud_accounts) = self.get_options_values()

        today = datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0)
        start_date = today - timedelta(days=days_threshold)
        end_date = today
        cloud_accounts = self.get_cloud_accounts(SUPPORTED_CLOUD_TYPES,
                                                 skip_cloud_accounts)
        instances_by_account = self.get_active_resources(
            list(cloud_accounts.keys()), start_date, 'Instance')
        employees = self.get_employees()
        pools = self.get_pools()

        result_map = {}
        for account in cloud_accounts.values():
            account_instances = instances_by_account[account['id']]
            if not account_instances:
                continue
            instance_ids = list(map(lambda x: x['_id'], account_instances))

            resources_with_inactivity = dict()
            for i in range(0, len(instance_ids), METRICS_BULK_SIZE):
                resources_with_inactivity.update(self._get_inactivity_intervals(
                    cloud_account_id=account['id'],
                    resource_ids=instance_ids[i:i+METRICS_BULK_SIZE],
                    start_date=start_date,
                    end_date=end_date,
                    cpu_percent_threshold=cpu_percent_threshold,
                    network_bps_threshold=network_bps_threshold
                ))

            for instance in account_instances:
                instance_id = instance['_id']
                resource_inactivity_intervals = resources_with_inactivity.get(
                    instance_id)
                if not resource_inactivity_intervals:
                    continue
                result_map[instance_id] = {
                    'resource_id': instance_id,
                    'resource_name': instance.get('name'),
                    'cloud_resource_id': instance['cloud_resource_id'],
                    'region': instance['region'],
                    'cloud_account_id': account['id'],
                    'cloud_type': account['type'],
                    'owner': self._extract_owner(
                        instance.get('employee_id'), employees),
                    'pool': self._extract_pool(
                        instance.get('pool_id'), pools),
                    'is_excluded': instance.get(
                        'pool_id') in excluded_pools,
                    'inactivity_periods': self._merge_intervals(
                        resource_inactivity_intervals)
                }

            matched_resource_ids = list(resources_with_inactivity.keys())
            daily_expenses = self.get_avg_daily_expenses(
                matched_resource_ids, start_date)
            for resource_id in matched_resource_ids:
                inactivity_intervals = resources_with_inactivity.get(
                    resource_id, [])
                savings = self._get_resource_savings(
                    daily_expenses.get(resource_id, 0), inactivity_intervals)
                if savings > 0:
                    result_map[resource_id]['saving'] = savings
                else:
                    result_map.pop(resource_id)

        return list(result_map.values())


def main(organization_id, config_client, created_at, **kwargs):
    return InstancesForShutdown(organization_id, config_client, created_at).get()


def get_module_email_name():
    return 'Instances For Shutdown'
