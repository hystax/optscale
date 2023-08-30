from collections import defaultdict
from optscale_client.metroculus_client.client import Client as MetroculusClient
from rest_api.rest_api_server.controllers.base import BaseController, MongoMixin
from rest_api.rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.models.enums import CloudTypes
from rest_api.rest_api_server.models.models import CloudAccount
from rest_api.rest_api_server.utils import bytes_to_gb, encoded_tags
from tools.optscale_exceptions.common_exc import WrongArgumentsException


class K8sRightsizingController(BaseController, MongoMixin):
    def __init__(self, db_session, config=None, token=None, engine=None):
        super().__init__(db_session, config, token, engine)
        self._metroculus_cl = None
        self._metric_func_keys_map = {}

    @property
    def metroculus_cl(self):
        if self._metroculus_cl is None:
            self._metroculus_cl = MetroculusClient(
                url=self._config.metroculus_url(),
                secret=self._config.cluster_secret())
        return self._metroculus_cl

    def _sum_metrics(self, aggregation_metric, k8s_metric, metric_key,
                     aggregation_func=None, remap_key=None):
        zero_value = 0.0
        if not remap_key:
            remap_key = metric_key
        if remap_key not in aggregation_metric:
            aggregation_metric[remap_key] = zero_value
        metric_value = k8s_metric.get(metric_key, zero_value)
        aggregation_metric[remap_key] += aggregation_func(
            metric_value) if aggregation_func else metric_value

    def sum_metrics(self, aggregation_metric, k8s_metric, metric_key):
        self._sum_metrics(aggregation_metric, k8s_metric, metric_key)

    def sum_in_period(self, aggregation_metric, k8s_metric, metric_key_set):
        metric_key, remap_key = metric_key_set
        self._sum_metrics(aggregation_metric, k8s_metric, metric_key,
                          remap_key=remap_key)

    def sum_in_gb_in_period(self, aggregation_metric, k8s_metric,
                            metric_key_set):
        metric_key, remap_key = metric_key_set

        def bytes_to_gb_in_period(bytes_num):
            return bytes_to_gb(bytes_num)
        self._sum_metrics(aggregation_metric, k8s_metric, metric_key,
                          bytes_to_gb_in_period, remap_key)

    def get_metric(self, aggregation_metric, k8s_metric, metric_key):
        zero_value = 0.0
        if metric_key not in aggregation_metric:
            aggregation_metric[metric_key] = zero_value
        if aggregation_metric[metric_key] == zero_value:
            aggregation_metric[metric_key] = k8s_metric.get(metric_key)

    @property
    def metric_func_keys_map(self):
        if not self._metric_func_keys_map:
            self._metric_func_keys_map = {
                self.sum_metrics: [
                    'average_pod_cpu_used', 'pod_cpu_provision',
                    'pod_cpu_requests', 'average_pod_memory_used',
                    'pod_memory_provision', 'pod_memory_requests',
                    'total_pod_cpu_requests'
                ],
                self.sum_in_period: [
                    ('total_pod_cpu_used', 'total_pod_cpu_hours')
                ],
                self.sum_in_gb_in_period: [
                    ('total_pod_memory_used', 'total_pod_memory_gb'),
                    ('total_pod_memory_requests',
                     'total_pod_memory_requests_gb')
                ],
                self.get_metric: [
                    'namespace_cpu_provision_used',
                    'namespace_memory_provision_used',
                    'namespace_quota_cpu_provision_hard',
                    'namespace_quota_memory_provision_hard',
                    'namespace_quota_cpu_provision_medium',
                    'namespace_quota_memory_provision_medium',
                    'namespace_quota_cpu_provision_low',
                    'namespace_quota_memory_provision_low',
                    'namespace_cpu_requests_used',
                    'namespace_memory_requests_used',
                    'namespace_quota_cpu_requests_hard',
                    'namespace_quota_memory_requests_hard',
                    'namespace_quota_cpu_requests_medium',
                    'namespace_quota_memory_requests_medium',
                    'namespace_quota_cpu_requests_low',
                    'namespace_quota_memory_requests_low'
                ]
            }
        return self._metric_func_keys_map

    def _get_cloud_accounts(self, organization_id, cloud_account_id):
        cloud_accounts = self.session.query(
            CloudAccount.id, CloudAccount.name).filter(
            CloudAccount.deleted.is_(False),
            CloudAccount.organization_id == organization_id,
            CloudAccount.type == CloudTypes.KUBERNETES_CNR
        ).all()
        cloud_account_id_name_map = {ca[0]: ca[1] for ca in cloud_accounts}
        if cloud_account_id:
            if cloud_account_id not in cloud_account_id_name_map:
                raise WrongArgumentsException(
                    Err.OE0005, [CloudAccount.__name__, cloud_account_id])
            cloud_account_id_name_map = {
                cloud_account_id: cloud_account_id_name_map[cloud_account_id]}
        return cloud_account_id_name_map

    def get(self, organization_id, **params):
        start_date = params.get('start_date')
        end_date = params.get('end_date')
        cloud_account_id = params.get('cloud_account_id')
        cloud_account_map = self._get_cloud_accounts(
            organization_id, cloud_account_id)
        k8s_resource_map = defaultdict(dict)
        for res_info in self.mongo_client.restapi.resources.find({
            'cloud_account_id': {'$in': list(cloud_account_map.keys())},
            'deleted_at': 0, 'resource_type': 'K8s Pod', 'active': True},
                ['_id', 'cloud_account_id', 'k8s_namespace', 'tags',
                 'k8s_cluster']):
            tags = encoded_tags(res_info.get('tags'), True)
            app_value = tags.get('app') or tags.get('k8s_app') or tags.get(
                'component')
            k8s_resource_map[res_info['cloud_account_id']][res_info['_id']] = (
                app_value, res_info.get('k8s_namespace'),
                res_info.get('k8s_cluster'))
        cloud_app_rightsizing = {}
        for cloud_acc_id, cloud_acc_name in cloud_account_map.items():
            _, k8s_metric_resp = self.metroculus_cl.get_k8s_metrics(
                cloud_account_id=cloud_acc_id, start_date=start_date,
                end_date=end_date)
            k8s_metrics = k8s_metric_resp.get(cloud_acc_id, [])
            cloud_app_rightsizing[cloud_acc_id] = {}
            for k8s_metric in k8s_metrics:
                resource_id = k8s_metric.get('resource_id')
                app_value, namespace, cluster = k8s_resource_map.get(
                    cloud_acc_id, {}).get(resource_id, (None, None, None))
                if not app_value:
                    continue
                if app_value not in cloud_app_rightsizing[cloud_acc_id]:
                    cloud_app_rightsizing[cloud_acc_id][app_value] = {
                        'cloud_account_id': cloud_acc_id,
                        'cloud_account_name': cloud_acc_name,
                        'name': app_value,
                        'namespace': namespace,
                        'cluster': cluster
                    }
                for m_func, m_keys in self.metric_func_keys_map.items():
                    for m_key in m_keys:
                        m_func(cloud_app_rightsizing[cloud_acc_id][app_value],
                               k8s_metric, m_key)
        return {
            'start_date': start_date,
            'end_date': end_date,
            'k8s_app_rightsizing': [rightsizing_info for app_info in
                                    cloud_app_rightsizing.values()
                                    for rightsizing_info in app_info.values()]
        }


class K8sRightsizingAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return K8sRightsizingController
