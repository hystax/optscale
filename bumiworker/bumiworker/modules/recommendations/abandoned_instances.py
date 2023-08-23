import logging
from collections import OrderedDict
from datetime import datetime, timedelta
from optscale_client.metroculus_client.client import Client as MetroculusClient

from bumiworker.bumiworker.modules.abandoned_base import AbandonedBase

SUPPORTED_CLOUD_TYPES = [
    'aws_cnr',
    'azure_cnr',
    'alibaba_cnr',
    'nebius',
]

LOG = logging.getLogger(__name__)

METRICS_BULK_SIZE = 50

DEFAULT_DAYS_THRESHOLD = 7
DEFAULT_CPU_PERCENT_THRESHOLD = 5
DEFAULT_NETWORK_BPS_THRESHOLD = 1000


class AbandonedInstances(AbandonedBase):
    def __init__(self, organization_id, config_client, created_at):
        super().__init__(organization_id, config_client, created_at)
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
        self._insider_cl = None
        self._metroculus_cl = None

    @property
    def metroculus_cl(self):
        if self._metroculus_cl is None:
            self._metroculus_cl = MetroculusClient(
                url=self.config_cl.metroculus_url(),
                secret=self.config_cl.cluster_secret(),
                verify=False)
        return self._metroculus_cl

    def _are_below_metrics(self, cloud_account_id, resource_ids, start_date,
                           end_date, cpu_percent_threshold,
                           network_bps_threshold):
        result = set()
        _, all_metrics = self.metroculus_cl.get_aggregated_metrics(
            cloud_account_id, resource_ids, int(start_date.timestamp()),
            int(end_date.timestamp()))

        for resource_id, metrics in all_metrics.items():
            cpu_metric = metrics.get('cpu', {}).get('avg')
            net_in_metric = metrics.get('network_in_io', {}).get('avg')
            net_out_metric = metrics.get('network_out_io', {}).get('avg')
            if cpu_metric is None or cpu_metric > cpu_percent_threshold:
                continue
            if net_in_metric is None or net_out_metric is None:
                continue
            net_total_metric = net_in_metric + net_out_metric
            if net_total_metric > network_bps_threshold:
                continue
            result.add(resource_id)
        return result

    def _get_resources_below_metric(
            self, cloud_account_id, resource_ids, start_date, end_date,
            cpu_percent_threshold, network_bps_threshold):
        resources_below_metric = set()
        for i in range(0, len(resource_ids), METRICS_BULK_SIZE):
            resources_below_metric.update(self._are_below_metrics(
                cloud_account_id=cloud_account_id,
                resource_ids=resource_ids[i:i + METRICS_BULK_SIZE],
                start_date=start_date,
                end_date=end_date,
                cpu_percent_threshold=cpu_percent_threshold,
                network_bps_threshold=network_bps_threshold
            ))
        return resources_below_metric

    def _get(self):
        (days_threshold, cpu_percent_threshold, network_bps_threshold,
         excluded_pools, skip_cloud_accounts) = self.get_options_values()

        now = datetime.utcnow()
        start_date = now - timedelta(days=days_threshold)

        cloud_accounts = self.get_cloud_accounts(SUPPORTED_CLOUD_TYPES,
                                                 skip_cloud_accounts)
        instances_by_account = self.get_active_resources(
            list(cloud_accounts.keys()), start_date, 'Instance')
        employees = self.get_employees()
        pools = self.get_pools()

        result_map = {}
        for account in cloud_accounts.values():
            account_instances = instances_by_account[account['id']]
            if account_instances:
                instance_ids = list(map(lambda x: x['_id'], account_instances))
                resources_below_metric = self._get_resources_below_metric(
                    account['id'], instance_ids, start_date=start_date,
                    end_date=now, cpu_percent_threshold=cpu_percent_threshold,
                    network_bps_threshold=network_bps_threshold)
                for instance in account_instances:
                    if instance['_id'] in resources_below_metric:
                        region = instance.get('region') or instance.get(
                            'meta', {}).get('zone_id')
                        result_map[instance['_id']] = {
                            'resource_id': instance['_id'],
                            'resource_name': instance.get('name'),
                            'cloud_resource_id': instance['cloud_resource_id'],
                            'region': region,
                            'cloud_account_id': account['id'],
                            'cloud_type': account['type'],
                            'owner': self._extract_owner(
                                instance.get('employee_id'), employees),
                            'pool': self._extract_pool(
                                instance.get('pool_id'), pools),
                            'is_excluded': instance.get(
                                'pool_id') in excluded_pools,
                        }

        matched_resource_ids = list(result_map.keys())
        expenses = self.get_month_saving_by_daily_avg_expenses(
            matched_resource_ids, start_date)
        for resource_id in matched_resource_ids:
            if expenses.get(resource_id, 0) > 0:
                result_map[resource_id]['saving'] = expenses[resource_id]
            else:
                result_map.pop(resource_id)

        return list(result_map.values())


def main(organization_id, config_client, created_at, **kwargs):
    return AbandonedInstances(
        organization_id, config_client, created_at).get()


def get_module_email_name():
    return 'Abandoned Instances'
