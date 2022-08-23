import logging
import math
from datetime import datetime
from metroculus_api.utils import (
    check_string, check_positive_integer, check_non_negative_integer,
    seconds_to_hour)
from metroculus_api.controllers.base import (BaseController,
                                             BaseAsyncControllerWrapper)

LOG = logging.getLogger(__name__)
METRIC_INTERVAL = 900


class K8sMetricsController(BaseController):
    @staticmethod
    def validate_parameters(**kwargs):
        check_string('cloud_account_id', kwargs.get('cloud_account_id'))
        check_non_negative_integer('start_date', kwargs.get('start_date'))
        check_positive_integer('end_date', kwargs.get('end_date'))

    def get(self, **kwargs):
        self.validate_parameters(**kwargs)
        cloud_account_id = kwargs.get('cloud_account_id')
        start_dt_timestamp = kwargs.get('start_date')
        end_dt_timestamp = kwargs.get('end_date')
        period = seconds_to_hour(end_dt_timestamp - start_dt_timestamp)
        start_date = datetime.fromtimestamp(math.floor(
            start_dt_timestamp / METRIC_INTERVAL) * METRIC_INTERVAL)
        end_date = datetime.fromtimestamp(math.floor(
            end_dt_timestamp / METRIC_INTERVAL) * METRIC_INTERVAL)
        k8s_metrics = self._get_metrics(cloud_account_id, start_date, end_date)
        metric_values = {
            'start_date': start_dt_timestamp,
            'end_date': end_dt_timestamp,
            cloud_account_id: []}
        for k8s_metric in k8s_metrics:
            (resource_id, pod_cpu_average_usage, pod_memory_average_usage,
             pod_cpu_provision, pod_cpu_requests, pod_cpu_average_requests,
             pod_memory_provision, pod_memory_requests,
             pod_memory_average_requests, namespace_cpu_provision_used,
             namespace_memory_provision_used,
             namespace_quota_cpu_provision_hard,
             namespace_quota_memory_provision_hard,
             namespace_quota_cpu_provision_medium,
             namespace_quota_memory_provision_medium,
             namespace_quota_cpu_provision_low,
             namespace_quota_memory_provision_low,
             namespace_cpu_requests_used, namespace_memory_requests_used,
             namespace_quota_cpu_requests_hard,
             namespace_quota_memory_requests_hard,
             namespace_quota_cpu_requests_medium,
             namespace_quota_memory_requests_medium,
             namespace_quota_cpu_requests_low,
             namespace_quota_memory_requests_low) = k8s_metric
            metric_values[cloud_account_id].append({
                'resource_id': resource_id,
                'average_pod_cpu_used': pod_cpu_average_usage,
                'average_pod_memory_used': pod_memory_average_usage,
                'pod_cpu_provision': pod_cpu_provision,
                'pod_cpu_requests': pod_cpu_requests,
                'pod_memory_provision': pod_memory_provision,
                'pod_memory_requests': pod_memory_requests,
                'total_pod_cpu_requests': pod_cpu_average_requests * period,
                'total_pod_memory_requests': (pod_memory_average_requests *
                                              period),
                'total_pod_cpu_used': pod_cpu_average_usage * period,
                'total_pod_memory_used': pod_memory_average_usage * period,
                'namespace_cpu_provision_used': namespace_cpu_provision_used,
                'namespace_memory_provision_used':
                    namespace_memory_provision_used,
                'namespace_quota_cpu_provision_hard':
                    namespace_quota_cpu_provision_hard,
                'namespace_quota_memory_provision_hard':
                    namespace_quota_memory_provision_hard,
                'namespace_quota_cpu_provision_medium':
                    namespace_quota_cpu_provision_medium,
                'namespace_quota_memory_provision_medium':
                    namespace_quota_memory_provision_medium,
                'namespace_quota_cpu_provision_low':
                    namespace_quota_cpu_provision_low,
                'namespace_quota_memory_provision_low':
                    namespace_quota_memory_provision_low,
                'namespace_cpu_requests_used': namespace_cpu_requests_used,
                'namespace_memory_requests_used':
                    namespace_memory_requests_used,
                'namespace_quota_cpu_requests_hard':
                    namespace_quota_cpu_requests_hard,
                'namespace_quota_memory_requests_hard':
                    namespace_quota_memory_requests_hard,
                'namespace_quota_cpu_requests_medium':
                    namespace_quota_cpu_requests_medium,
                'namespace_quota_memory_requests_medium':
                    namespace_quota_memory_requests_medium,
                'namespace_quota_cpu_requests_low':
                    namespace_quota_cpu_requests_low,
                'namespace_quota_memory_requests_low':
                    namespace_quota_memory_requests_low
            })
        return metric_values

    def _get_metrics(self, cloud_account_id, start_date, end_date):
        return self.clickhouse_client.execute(
            f'''
            SELECT resource_id, AVG(pod_cpu_average_usage),
            AVG(pod_memory_average_usage), argMax(pod_cpu_provision, date),
            argMax(pod_cpu_requests, date), AVG(pod_cpu_requests),
            argMax(pod_memory_provision, date),
            argMax(pod_memory_requests, date), AVG(pod_memory_requests),
            argMax(namespace_cpu_provision_used, date),
            argMax(namespace_memory_provision_used, date),
            argMax(namespace_quota_cpu_provision_hard, date),
            argMax(namespace_quota_memory_provision_hard, date),
            argMax(namespace_quota_cpu_provision_medium, date),
            argMax(namespace_quota_memory_provision_medium, date),
            argMax(namespace_quota_cpu_provision_low, date),
            argMax(namespace_quota_memory_provision_low, date),
            argMax(namespace_cpu_requests_used, date),
            argMax(namespace_memory_requests_used, date),
            argMax(namespace_quota_cpu_requests_hard, date),
            argMax(namespace_quota_memory_requests_hard, date),
            argMax(namespace_quota_cpu_requests_medium, date),
            argMax(namespace_quota_memory_requests_medium, date),
            argMax(namespace_quota_cpu_requests_low, date),
            argMax(namespace_quota_memory_requests_low, date)
            FROM k8s_metrics
            WHERE cloud_account_id = '{cloud_account_id}'
                AND date >= '{start_date}'
                AND date <= '{end_date}'
            GROUP BY resource_id
            '''
        )


class K8sMetricsAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return K8sMetricsController
