import base64
import logging
import uuid
from typing import Dict, Any, Union

import requests

from datetime import datetime
from urllib.parse import quote


from cloud_adapter.exceptions import (
    InvalidParameterException,
    CloudConnectionError
)
from cloud_adapter.clouds.base import CloudBase
from cloud_adapter.model import PodResource
from cloud_adapter.utils import CloudParameter

LOG = logging.getLogger(__name__)


class Kubernetes(CloudBase):
    BILLING_CREDS = [
        CloudParameter(name='user', type=str, required=True),
        CloudParameter(name='password', type=str, required=True),
        CloudParameter(name='credentials', type=str, required=False,
                       protected=True, readonly=True),
    ]

    SUPPORTS_REPORT_UPLOAD = False

    _PROMETHEUS_DEFAULT_TIMEOUT_SEC = 60

    def __init__(self, cloud_config, *args, **kwargs):
        self.config = cloud_config
        self._url = None

    @property
    def url(self):
        return self.config.get('url')

    def discovery_calls_map(self):
        return {
            PodResource: self.pod_discovery_calls,
        }

    @property
    def cloud_account_id(self):
        return self.config.get('cloud_account_id') or self.config.get('id')

    @property
    def cloud_account_name(self):
        return self.config.get('cloud_account_name')

    @property
    def organization_id(self):
        return self.config.get('organization_id')

    def _prometheus_request(self, path, method='get', return_json=True,
                            params=None, data=None, json=None):
        try:
            response = requests.request(
                method=method,
                url=self.url + path,
                verify=False,
                params=params,
                data=data,
                json=json,
                timeout=self._PROMETHEUS_DEFAULT_TIMEOUT_SEC
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as exc:
            raise InvalidParameterException(
                'Received an HTTP error while contacting '
                'Prometheus: {}'.format(str(exc)))
        except requests.exceptions.ConnectionError as exc:
            raise CloudConnectionError(
                'Could not connect to Prometheus: {}'.format(str(exc)))
        except requests.exceptions.RequestException as exc:
            raise CloudConnectionError(
                'Error contacting Prometheus: {}'.format(str(exc)))
        return response.json() if return_json else response.text

    def _get_pods_info_metrics(self, now):
        pod_info_result_list = self.get_metric(
            'kube_pod_info{cloud_account_id="%s"}' % self.cloud_account_id,
            now)
        return self._get_result_metrics(pod_info_result_list)

    @staticmethod
    def _extract_labels(metric: Dict[str, Any]) -> Dict[str, Any]:
        return {label_key.split('_', maxsplit=1)[1]: label_value
                for label_key, label_value in metric.items()
                if label_key.startswith('label_')}

    def _get_pod_labels(self, now):
        pod_label_result_list = self.get_metric(
            'kube_pod_labels{cloud_account_id="%s"}' % self.cloud_account_id,
            now)
        pod_label_metrics = self._get_result_metrics(pod_label_result_list)
        pod_name_labels_map = {}
        for pod_label_metric in pod_label_metrics:
            pod_name = pod_label_metric.get('pod')
            pod_labels = self._extract_labels(pod_label_metric)
            pod_name_labels_map[pod_name] = pod_labels
        return pod_name_labels_map

    def _get_service_selectors(self, now: int) -> Dict[str, Dict[str, Any]]:
        service_selectors_result_list = self.get_metric(
            'kube_service_selectors{cloud_account_id="%s"}' %
            self.cloud_account_id, now)
        service_selectors_metrics = self._get_result_metrics(
            service_selectors_result_list)

        service_selector_map = {}
        for metric in service_selectors_metrics:
            service_name = metric.get('service')
            selector = self._extract_labels(metric)
            if selector:
                service_selector_map[service_name] = selector
        return service_selector_map

    @staticmethod
    def _get_service(
            pod_labels: Dict[str, Any],
            service_selector_map: Dict[str, Dict[str, Any]]
    ) -> Union[str, None]:
        for service, selector in service_selector_map.items():
            if all(map(lambda k: selector[k] == pod_labels.get(k),
                       selector.keys())):
                return service

    def get_pod_services(self, now: Union[int, None] = None):
        res = {}
        pod_name_labels_map = self._get_pod_labels(now)
        service_selectors_map = self._get_service_selectors(now)
        for pod, labels in pod_name_labels_map.items():
            service = self._get_service(labels, service_selectors_map)
            if service:
                res[pod] = service
        return res

    @staticmethod
    def _get_result_metrics(info_result_list):
        return [info_result.get('metric', {})
                for info_result in info_result_list]

    @classmethod
    def configure_credentials(cls, config):
        user = config.get('user')
        password = config.get('password')
        credentials = base64.b64encode(
            f'{user}:{password}'.encode()).decode()
        return {'credentials': credentials, 'user': user}

    def validate_credentials(self, org_id=None):
        return {'account_id': str(uuid.uuid4()), 'warnings': []}

    @staticmethod
    def prometheus_query_path():
        return '/api/v1/query'

    def get_metric(self, query, time=None):
        path = self.prometheus_query_path() + '?query=%s' % quote(query)
        if time:
            path += '&time=%s' % time
        data = self._prometheus_request(path)
        return data.get('data', {}).get('result', [])

    def configure_report(self):
        pass

    def configure_last_import_modified_at(self):
        pass

    def volume_discovery_calls(self):
        return []

    def instance_discovery_calls(self):
        return []

    def snapshot_discovery_calls(self):
        return []

    def bucket_discovery_calls(self):
        return []

    def discover_pod_resources(self):
        now = int(datetime.utcnow().timestamp())
        pod_name_labels_map = self._get_pod_labels(now)
        pod_info_metrics = self._get_pods_info_metrics(now)
        service_selectors_map = self._get_service_selectors(now)
        for pod_metric in pod_info_metrics:
            pod_name = pod_metric.get('pod')
            labels = pod_name_labels_map.get(pod_name)
            service = self._get_service(labels, service_selectors_map)
            pod_resource = PodResource(
                cloud_resource_id=pod_metric.get('uid'),
                name=pod_name,
                cloud_account_id=self.cloud_account_id,
                organization_id=self.organization_id,
                tags=labels,
                created_by_kind=pod_metric.get('created_by_kind'),
                created_by_name=pod_metric.get('created_by_name'),
                host_ip=pod_metric.get('host_ip'),
                instance_address=pod_metric.get('instance'),
                k8s_node=pod_metric.get('node'),
                k8s_namespace=pod_metric.get('namespace'),
                pod_ip=pod_metric.get('pod_ip'),
                k8s_service=service,
                k8s_cluster=pod_metric.get('cluster')
            )
            yield pod_resource

    def pod_discovery_calls(self):
        return [(self.discover_pod_resources, ())]

    def snapshot_chain_discovery_calls(self):
        return []

    def rds_instance_discovery_calls(self):
        return []

    def ip_address_discovery_calls(self):
        # For Kubernetes cloud we don't have ips as a separate resources
        return []

    def get_regions_coordinates(self):
        return {}

    def set_currency(self, currency):
        pass
