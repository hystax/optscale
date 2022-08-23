import logging
import re
from datetime import datetime
from hashlib import sha1
from urllib.parse import urlparse, quote

import requests as requests
from requests.auth import HTTPBasicAuth

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
        CloudParameter(name='url', type=str, required=True),
        CloudParameter(name='port', type=int, required=True),
        CloudParameter(name='user', type=str, required=False),
        CloudParameter(name='password', type=str, required=False,
                       protected=True),
    ]

    SUPPORTS_REPORT_UPLOAD = False

    _PROMETHEUS_DEFAULT_USER = 'optscale'
    _PROMETHEUS_DEFAULT_PROTOCOL = 'https'
    _PROMETHEUS_DEFAULT_TIMEOUT_SEC = 60

    def __init__(self, cloud_config, *args, **kwargs):
        self.config = cloud_config
        self._url = None

    def discovery_calls_map(self):
        return {
            PodResource: self.pod_discovery_calls,
        }

    @property
    def cloud_account_id(self):
        return self.config.get('cloud_account_id')

    @property
    def cloud_account_name(self):
        return self.config.get('cloud_account_name')

    @property
    def organization_id(self):
        return self.config.get('organization_id')

    @property
    def _prometheus_url(self):
        if not self._url:
            url = self.config['url']
            if not re.match(r'^\w+://', url):
                url = '{}://{}'.format(self._PROMETHEUS_DEFAULT_PROTOCOL, url)
            try:
                parsed_url = urlparse(url)
            except ValueError:
                raise InvalidParameterException(
                    'Could not parse url `{}`'.format(url))
            url = '{}://{}:{}'.format(
                parsed_url.scheme,
                parsed_url.hostname,
                self.config['port']
            )
            self._url = url
        return self._url

    def _prometheus_request(self, path, method='get', return_json=True,
                            params=None, data=None, json=None):
        auth = None
        if self.config.get('password'):
            auth = HTTPBasicAuth(
                username=self.config.get(
                    'user', self._PROMETHEUS_DEFAULT_USER),
                password=self.config['password']
            )
        try:
            response = requests.request(
                method=method,
                url=self._prometheus_url + path,
                verify=False,
                params=params,
                data=data,
                json=json,
                auth=auth,
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

    def _check_ready(self):
        response = self._prometheus_request('/-/ready', return_json=False)
        if response != 'Prometheus is Ready.\n':
            raise InvalidParameterException(
                'Prometheus is not ready, or the provided URL belongs to '
                'other service')

    def _get_targets(self):
        return self._prometheus_request('/api/v1/targets').get('data', {})

    def _get_active_targets(self):
        return self._get_targets().get('activeTargets', [])

    def _get_pods_info_metrics(self, now):
        pod_info_result_list = self.get_metric('kube_pod_info', now)
        return self._get_result_metrics(pod_info_result_list)

    def _get_pod_labels(self, now):
        pod_label_result_list = self.get_metric('kube_pod_labels', now)
        pod_label_metrics = self._get_result_metrics(pod_label_result_list)
        pod_name_labels_map = {}
        for pod_label_metric in pod_label_metrics:
            pod_name = pod_label_metric.get('pod')
            pod_labels = {label_key.split('_', maxsplit=1)[1]: label_value
                          for label_key, label_value in pod_label_metric.items() if label_key.startswith('label_')}
            pod_name_labels_map[pod_name] = pod_labels
        return pod_name_labels_map

    def get_pod_services(self):
        all_targets = self._get_targets()
        pod_service_map = {}
        for target_types, target_data in all_targets.items():
            for target in target_data:
                discovered_label = target.get('discoveredLabels', {})
                service_name = discovered_label.get('__meta_kubernetes_service_name')
                pod_name = discovered_label.get('__meta_kubernetes_pod_name')
                if service_name and pod_name:
                    pod_service_map.update({pod_name: service_name})
        return pod_service_map

    @staticmethod
    def _get_result_metrics(info_result_list):
        return [info_result.get('metric', {}) for info_result in info_result_list]

    def validate_credentials(self, org_id=None):
        try:
            self._check_ready()
            active_targets = self._get_active_targets()
            if len(active_targets) == 0:
                raise InvalidParameterException(
                    'Found no active metric targets')
            node_targets = [x for x in active_targets
                            if x.get('scrapePool') == 'kubernetes-nodes']
            if len(node_targets) == 0:
                raise InvalidParameterException(
                    'Found no active node targets, please check that '
                    '`kubernetes-nodes` scrape pool exists in Prometheus')
            LOG.info('Discovered {} node target(s) for organization '
                     '{}: {}'.format(len(node_targets), org_id, node_targets))
        except Exception as exc:
            LOG.error('Error validating Kubernetes account for '
                      'organization {}: {}'.format(org_id, str(exc)))
            raise
        return {'account_id': sha1(self._prometheus_url.encode()).hexdigest(),
                'warnings': []}

    @staticmethod
    def prometeus_query_path():
        return '/api/v1/query'

    def get_metric(self, query, time=None):
        path = self.prometeus_query_path() + '?query=%s' % quote(query)
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
        pod_service_map = self.get_pod_services()
        for pod_metric in pod_info_metrics:
            pod_name = pod_metric.get('pod')
            labels = pod_name_labels_map.get(pod_name)
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
                k8s_service=pod_service_map.get(pod_name),
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
