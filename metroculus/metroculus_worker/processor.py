import math
from collections import defaultdict
import time
from kombu.log import get_logger
from datetime import datetime, timedelta, timezone
from pymongo import MongoClient, UpdateOne
from clickhouse_driver import Client as ClickHouseClient
from optscale_client.rest_api_client.client_v2 import Client as RestClient
from tools.cloud_adapter.cloud import Cloud as CloudAdapter

LOG = get_logger(__name__)
K8S_RESOURCE_TYPE = 'K8s Pod'
SUPPORTED_RESOURCE_TYPES = ['Instance', 'RDS Instance', K8S_RESOURCE_TYPE]
METRIC_INTERVAL = 900
METRIC_BULK_SIZE = 25
POD_LIMIT_KEY = 'pod_limits'
NAMESPACE_RESOURCE_QUOTAS_KEY = 'namespace_resource_quotas'
NEBIUS_CLOUD_TYPE = 'nebius'
KUBERNETES_CLOUD_TYPE = 'kubernetes_cnr'
POD_CPU_AVERAGE_USAGE_KEY = 'pod_cpu_average_usage'
MSEC_IN_SEC = 1000
K8S_METRIC_QUERY_MAP = {
    POD_LIMIT_KEY: {
        POD_CPU_AVERAGE_USAGE_KEY:
            'idelta(container_cpu_usage_seconds_total{'
            'cloud_account_id = "%s", pod != "", name=""}[%sm:%ss])[%sm:%ss]',
        'pod_memory_average_usage':
            'avg_over_time(container_memory_usage_bytes{'
            'cloud_account_id = "%s", pod != "", name=""}[%sm:%ss])[%sm:%ss]',
        'pod_cpu_provision':
            'kube_pod_container_resource_limits{'
            'cloud_account_id = "%s", resource="cpu"}[%sm:%ss]',
        'pod_cpu_requests':
            'kube_pod_container_resource_requests{'
            'cloud_account_id = "%s", resource="cpu"}[%sm:%ss]',
        'pod_memory_provision':
            'kube_pod_container_resource_limits{'
            'cloud_account_id = "%s", resource="memory"}[%sm:%ss]',
        'pod_memory_requests':
            'kube_pod_container_resource_requests{'
            'cloud_account_id = "%s", resource="memory"}[%sm:%ss]',
    },
    NAMESPACE_RESOURCE_QUOTAS_KEY: {
        'namespace_cpu_provision_used':
            'kube_resourcequota{cloud_account_id = "%s", '
            'resource="limits.cpu", type="used"}[%sm:%ss]',
        'namespace_memory_provision_used':
            'kube_resourcequota{cloud_account_id = "%s", '
            'resource="limits.memory", type="used"}[%sm:%ss]',
        'namespace_cpu_requests_used':
            'kube_resourcequota{cloud_account_id = "%s", '
            'resource="requests.cpu", type="used"}[%sm:%ss]',
        'namespace_memory_requests_used':
            'kube_resourcequota{cloud_account_id = "%s", '
            'resource="requests.memory", type="used"}[%sm:%ss]',
        'namespace_quota_cpu_provision_hard':
            'kube_resourcequota{cloud_account_id = "%s", '
            'resource="limits.cpu", type="hard"}[%sm:%ss]',
        'namespace_quota_memory_provision_hard':
            'kube_resourcequota{cloud_account_id = "%s", '
            'resource="limits.memory", type="hard"}[%sm:%ss]',
        'namespace_quota_cpu_provision_medium':
            'kube_resourcequota{cloud_account_id = "%s", '
            'resource="limits.cpu", type="medium"}[%sm:%ss]',
        'namespace_quota_memory_provision_medium':
            'kube_resourcequota{cloud_account_id = "%s", '
            'resource="limits.memory", type="medium"}[%sm:%ss]',
        'namespace_quota_cpu_provision_low':
            'kube_resourcequota{cloud_account_id = "%s", '
            'resource="limits.cpu", type="low"}[%sm:%ss]',
        'namespace_quota_memory_provision_low':
            'kube_resourcequota{cloud_account_id = "%s", '
            'resource="limits.memory", type="low"}[%sm:%ss]',
        'namespace_quota_cpu_requests_hard':
            'kube_resourcequota{cloud_account_id = "%s", '
            'resource="requests.cpu", type="hard"}[%sm:%ss]',
        'namespace_quota_memory_requests_hard':
            'kube_resourcequota{cloud_account_id = "%s", '
            'resource="requests.memory", type="hard"}[%sm:%ss]',
        'namespace_quota_cpu_requests_medium':
            'kube_resourcequota{cloud_account_id = "%s", '
            'resource="requests.cpu", type="medium"}[%sm:%ss]',
        'namespace_quota_memory_requests_medium':
            'kube_resourcequota{cloud_account_id = "%s", '
            'resource="requests.memory", type="medium"}[%sm:%ss]',
        'namespace_quota_cpu_requests_low':
            'kube_resourcequota{cloud_account_id = "%s", '
            'resource="requests.cpu", type="low"}[%sm:%ss]',
        'namespace_quota_memory_requests_low':
            'kube_resourcequota{cloud_account_id = "%s", '
            'resource="requests.memory", type="low"}[%sm:%ss]',
    }
}


class MetricsProcessor(object):
    def __init__(self, config_cl, cloud_account_id):
        self.config_cl = config_cl
        self.cloud_account_id = cloud_account_id
        self._clickhouse_client = None
        self._rest_client = None
        self._mongo_client = None

    @property
    def clickhouse_client(self):
        if not self._clickhouse_client:
            user, password, host, db_name = self.config_cl.clickhouse_params()
            self._clickhouse_client = ClickHouseClient(
                host=host, password=password, database=db_name, user=user)
        return self._clickhouse_client

    @property
    def mongo_client(self):
        if not self._mongo_client:
            mongo_params = self.config_cl.mongo_params()
            mongo_conn_string = "mongodb://%s:%s@%s:%s" % mongo_params[:-1]
            self._mongo_client = MongoClient(mongo_conn_string)
        return self._mongo_client

    @property
    def rest_client(self):
        if self._rest_client is None:
            self._rest_client = RestClient(
                url=self.config_cl.restapi_url(), verify=False)
            self._rest_client.secret = self.config_cl.cluster_secret()
        return self._rest_client

    def get_metrics_dates(self, table_name, cloud_account_id, resource_ids):
        metric_dates = self.clickhouse_client.execute(
            '''
            SELECT resource_id, max(date)
            FROM %s
            WHERE cloud_account_id='%s'
            AND resource_id IN %s
            GROUP BY resource_id
            ''' % (table_name, cloud_account_id, list(resource_ids))
        )
        return {k: v for k, v in metric_dates}

    def update_metrics_flag(self, cloud_account_id, resource_ids):
        if resource_ids:
            self.mongo_client.restapi.resources.bulk_write([
                UpdateOne(
                    filter={'_id': r_id, 'cloud_account_id': cloud_account_id},
                    update={'$set': {'has_metrics': True}}
                ) for r_id in resource_ids
            ])

    def _get_cloud_adapter(self, cloud_account):
        cloud_config = cloud_account.copy()
        cloud_config.update(cloud_config.pop('config'))
        if cloud_config['type'] == 'kubernetes_cnr':
            cloud_config['url'] = self.config_cl.thanos_query_url()
        return CloudAdapter.get_adapter(cloud_config)

    def update_getting_metrics_time(self, ts=None):
        if ts is None:
            ts = int(time.time())
        self.rest_client.cloud_account_update(
            self.cloud_account_id,
            {'last_getting_metrics_at': ts,
             'last_getting_metric_attempt_at': ts})

    def update_getting_metrics_attempt(self, ts=None, error=None):
        if ts is None:
            ts = int(time.time())
        self.rest_client.cloud_account_update(
            self.cloud_account_id,
            {'last_getting_metric_attempt_at': ts,
             'last_getting_metric_attempt_error': error})

    def start(self):
        LOG.info('Starting getting metrics '
                 'for cloud account %s' % self.cloud_account_id)
        now = datetime.utcnow()
        _, cloud_account = self.rest_client.cloud_account_get(
            self.cloud_account_id)
        start_period = now - timedelta(days=30)
        start_period = start_period.replace(minute=0, second=0, microsecond=0)
        cloud_func_map = {
            'aws_cnr': ('average_metrics', self.get_aws_metrics),
            'azure_cnr': ('average_metrics', self.get_azure_metrics),
            'alibaba_cnr': ('average_metrics', self.get_alibaba_metrics),
            KUBERNETES_CLOUD_TYPE: ('k8s_metrics', self.get_k8s_metrics),
            'gcp_cnr': ('average_metrics', self.get_gcp_metrics),
            NEBIUS_CLOUD_TYPE: ('average_metrics', self.get_nebius_metrics),
        }
        cloud_type = cloud_account['type']
        metric_table_name, cloud_func = cloud_func_map.get(cloud_type,
                                                           (None, None))
        if not metric_table_name or not cloud_func:
            raise ValueError(
                'Cloud %s is not supported' % cloud_type)

        adapter = self._get_cloud_adapter(cloud_account)
        cloud_account_resources = list(
            self.mongo_client.restapi.resources.find({
                'cloud_account_id': cloud_account['id'],
                'active': True,
                'resource_type': {'$in': SUPPORTED_RESOURCE_TYPES}
            }, ['_id', 'last_seen', 'cloud_resource_id',
                'region', 'resource_type', 'name', 'k8s_namespace',
                'meta.source_cluster_id']
            ))
        if not cloud_account_resources:
            return []
        resource_map = {
            x['_id']: {
                'last_seen': x['last_seen'],
                'cloud_resource_id': x['cloud_resource_id'],
                'region': x.get('region'),
                'resource_type': x['resource_type'],
                'pod_name': x.get('name'),
                'pod_namespace': x.get('k8s_namespace'),
                'name': x.get('name'),
                'source_cluster_id': x.get('meta', {}).get('source_cluster_id')
            } for x in cloud_account_resources
        }
        resource_metric_dates_map = self.get_metrics_dates(
            metric_table_name, cloud_account['id'], resource_map.keys())
        resource_ids = set()
        grouped_resources_map = {}
        resource_ids_map = {}
        end_date = datetime.fromtimestamp(
            math.floor(now.timestamp() / METRIC_INTERVAL) * METRIC_INTERVAL)
        if cloud_type == KUBERNETES_CLOUD_TYPE:
            # we make one request to prometheus for all resources, if this is
            # the first time for cloud acc then we get for all period,
            # if we already have metrics for resources, even for the new
            # resources we get metrics together with existing resources for
            # the last period
            start_date = start_period
            cloud_resource_ids = []
            for r_id, resource in resource_map.items():
                last_metric_date = resource_metric_dates_map.get(
                    r_id, datetime.fromtimestamp(0))
                start_date = max(last_metric_date, start_date)
                resource_ids_map[resource['cloud_resource_id']] = (
                    r_id, resource.get('pod_name'),
                    resource.get('pod_namespace'))
                cloud_resource_ids.append(resource['cloud_resource_id'])
            start_date += timedelta(seconds=METRIC_INTERVAL)
            grouped_resources_map[(
                None, K8S_RESOURCE_TYPE, start_date, end_date,
            )] = cloud_resource_ids
        else:
            for r_id, resource in resource_map.items():
                last_seen = datetime.utcfromtimestamp(resource['last_seen'])
                last_metric_date = resource_metric_dates_map.get(
                    r_id, datetime.fromtimestamp(0))
                start_date = max(last_metric_date, start_period) + timedelta(
                    seconds=METRIC_INTERVAL)
                if start_date + timedelta(hours=2) > last_seen:
                    continue
                resource_ids_map[resource['cloud_resource_id']] = r_id
                cloud_resource_id = resource['cloud_resource_id']
                if cloud_type == NEBIUS_CLOUD_TYPE:
                    # resource_id from metric API contains name of
                    # resource instead of id if exists
                    resource_ids_map[resource['name']] = r_id
                    if resource.get('source_cluster_id'):
                        cloud_resource_id = resource['source_cluster_id']
                grouped_resources_map.setdefault((
                    resource['region'],
                    resource['resource_type'],
                    start_date,
                    end_date,
                ), []).append(cloud_resource_id)
        for (region, r_type, start_date, end_date
             ), cloud_resource_ids in grouped_resources_map.items():
            if start_date >= end_date:
                continue
            all_bulk_ids, metric_chunk = [], []
            # for k8s we don't need to bulk request to prometheus to get
            # relevant values for pods and namespaces we need to use
            if cloud_type == KUBERNETES_CLOUD_TYPE:
                all_bulk_ids = [cloud_resource_ids]
            else:
                for i in range(0, len(cloud_resource_ids), METRIC_BULK_SIZE):
                    all_bulk_ids.append(
                        cloud_resource_ids[i:i + METRIC_BULK_SIZE])
            for bulk_ids in all_bulk_ids:
                metrics = cloud_func(
                    cloud_account['id'], bulk_ids, resource_ids_map,
                    r_type, adapter, region, start_date, end_date)
                metric_chunk.extend(metrics)
            for i in range(0, len(metric_chunk), METRIC_BULK_SIZE):
                chunk = metric_chunk[i:i + METRIC_BULK_SIZE]
                self.clickhouse_client.execute(
                    'INSERT INTO %s VALUES' % metric_table_name, chunk)
                resource_ids.update(r['resource_id'] for r in chunk)
        if cloud_type != KUBERNETES_CLOUD_TYPE:
            self.update_metrics_flag(self.cloud_account_id, resource_ids)
        self.update_getting_metrics_time()
        return list(resource_ids)

    @staticmethod
    def get_aws_metrics(cloud_account_id, cloud_resource_ids, resource_ids_map,
                        r_type, adapter, region, start_date, end_date):
        result = []
        for name, (cloud_metric_namespace, cloud_metric_name) in {
            'cpu': ('AWS/EC2', 'CPUUtilization'),
            'ram': ('CWAgent', 'mem_used_percent'),
            'disk_read_io': ('AWS/EC2', 'DiskReadOps'),
            'disk_write_io': ('AWS/EC2', 'DiskWriteOps'),
            'network_in_io': ('AWS/EC2', 'NetworkIn'),
            'network_out_io': ('AWS/EC2', 'NetworkOut')
        }.items():
            last_start_date = start_date
            while last_start_date < end_date:
                end_dt = last_start_date + timedelta(days=10)
                if end_dt > end_date:
                    end_dt = end_date
                response = adapter.get_metric(
                    cloud_metric_namespace, cloud_metric_name,
                    cloud_resource_ids, region, METRIC_INTERVAL,
                    last_start_date, end_dt)
                for cloud_resource_id, metrics in response.items():
                    for metric in metrics:
                        value = metric.get('Average')
                        # if not value does not fit, 0 is valid value
                        if value is None:
                            continue
                        if name in ['network_in_io', 'network_out_io']:
                            # change bytes per min to bytes per second
                            value = value / 60
                        result.append({
                            'cloud_account_id': cloud_account_id,
                            'resource_id': resource_ids_map[cloud_resource_id],
                            'date': metric['Timestamp'],
                            'metric': name,
                            'value': value
                        })
                last_start_date = end_dt + timedelta(seconds=METRIC_INTERVAL)
        return result

    @staticmethod
    def get_azure_metrics(cloud_account_id, cloud_resource_ids,
                          resource_ids_map, r_type, adapter, region,
                          start_date, end_date):
        def datetime_from_str(date_str):
            return datetime.strptime(
                date_str, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)

        result = []
        metric_names_map = {
            'Percentage CPU': 'cpu',
            'Disk Read Operations/Sec': 'disk_read_io',
            'Disk Write Operations/Sec': 'disk_write_io',
            'Network In Total': 'network_in_io',
            'Network Out Total': 'network_out_io',
        }
        response = adapter.get_metric(
            'microsoft.compute/virtualmachines', list(metric_names_map.keys()),
            cloud_resource_ids, METRIC_INTERVAL, start_date, end_date)
        for cloud_resource_id, metrics in response.items():
            for cloud_metric_name, points in metrics.items():
                for point in points:
                    metric_name = metric_names_map[cloud_metric_name]
                    value = point.get('average')
                    if value is None:
                        continue
                    if metric_name in ['network_in_io', 'network_out_io']:
                        # change bytes per min to bytes per second
                        value = value / 60
                    result.append({
                        'cloud_account_id': cloud_account_id,
                        'resource_id': resource_ids_map[cloud_resource_id],
                        'date': datetime_from_str(point['timeStamp']),
                        'metric': metric_name,
                        'value': value
                    })
        return result

    @staticmethod
    def get_alibaba_metrics(cloud_account_id, cloud_resource_ids,
                            resource_ids_map, r_type, adapter, region,
                            start_date, end_date):
        common_metrics_map = {
            'Instance': ('acs_ecs_dashboard', [
                # Hypervisor metric, not recommended by Alibaba
                ('cpu', ['CPUUtilization']),
                # Agent metric, if exists, will overwrite previous metric
                ('cpu', ['cpu_total']),
                ('ram', ['memory_usedutilization']),
                ('disk_read_io', ['DiskReadIOPS']),
                ('disk_write_io', ['DiskWriteIOPS']),
                ('network_in_io', ['InternetInRate', 'IntranetInRate']),
                ('network_out_io', ['InternetOutRate', 'IntranetOutRate'])
            ]),
            'RDS Instance': ('acs_rds_dashboard', [
                ('cpu', ['CpuUsage']),
                ('ram', ['MemoryUsage']),
                ('network_in_io', ['SQLServer_NetworkInNew',
                                   'MySQL_NetworkInNew']),
                ('network_out_io', ['SQLServer_NetworkOutNew',
                                    'MySQL_NetworkOutNew'])
            ])
        }
        namespace, metrics_list = common_metrics_map[r_type]
        metrics_map = {}
        result = []
        for name, cloud_metric_names in metrics_list:
            sum_map = {}
            for cloud_metric_name in cloud_metric_names:
                response = adapter.get_metric(
                    namespace, cloud_metric_name, cloud_resource_ids, region,
                    METRIC_INTERVAL, start_date, end_date)
                instance_items = {}
                for item in response:
                    instance_items.setdefault(
                        item['instanceId'], []).append(item)
                for cloud_resource_id, metrics in instance_items.items():
                    for metric in metrics:
                        value = metric.get('Average')
                        if value is None:
                            continue
                        if name in ['network_in_io', 'network_out_io']:
                            # change bit/s to byte/s
                            value = value / 8
                        timestamp = metric['timestamp'] / 1000
                        m = sum_map.get((cloud_resource_id, timestamp))
                        if not m:
                            sum_map[(cloud_resource_id, timestamp)] = {
                                'cloud_account_id': cloud_account_id,
                                'resource_id': resource_ids_map[
                                    cloud_resource_id],
                                'date': datetime.fromtimestamp(timestamp),
                                'metric': name,
                                'value': value
                            }
                        else:
                            sum_map[(cloud_resource_id, timestamp)][
                                'value'] += value
            metrics_map.setdefault(name, {}).update(sum_map)
        for points in metrics_map.values():
            result.extend(points.values())
        return result

    @staticmethod
    def get_k8s_metrics(cloud_account_id, cloud_resource_ids, resource_ids_map,
                        r_type, adapter, region, start_date, end_date):
        result = []
        namespace_pod_map = defaultdict(dict)
        default_metric_value = 0.0
        for cloud_resource_id, (
                res_id, pod, namespace) in resource_ids_map.items():
            namespace_pod_map[namespace][pod] = res_id
        period = int((end_date - start_date).total_seconds() / 60.0)
        params = (cloud_account_id, period, METRIC_INTERVAL)
        extended_params = params + params[1:]
        now = int(end_date.timestamp())
        default_limit_values = defaultdict(float)
        for limit_key in [POD_LIMIT_KEY, NAMESPACE_RESOURCE_QUOTAS_KEY]:
            default_limit_values.update(
                {k8s_metric_key: default_metric_value for k8s_metric_key in
                 K8S_METRIC_QUERY_MAP.get(limit_key, {})})
        k8s_metric_map = {}
        for metric_type, metric_query_map in K8S_METRIC_QUERY_MAP.items():
            for metric_name, query_format in metric_query_map.items():
                query_format_count = query_format.count('%s')
                if query_format_count == len(params):
                    query = query_format % params
                elif query_format_count == len(extended_params):
                    query = query_format % extended_params
                else:
                    continue
                metric_usages = adapter.get_metric(query, now)
                for metric_usage in metric_usages:
                    metric = metric_usage['metric']
                    pod = metric.get('pod')
                    namespace = metric.get('namespace')
                    if namespace not in k8s_metric_map:
                        k8s_metric_map[namespace] = {}
                    if metric_type not in k8s_metric_map[namespace]:
                        k8s_metric_map[namespace][metric_type] = {}
                    if metric_type == POD_LIMIT_KEY:
                        if pod not in k8s_metric_map[namespace][metric_type]:
                            k8s_metric_map[namespace][metric_type][pod] = {}
                    k8s_metric_entry_map = (
                        k8s_metric_map[namespace][metric_type][pod]
                        if pod else
                        k8s_metric_map[namespace][metric_type])
                    usage_values = metric_usage.get('values')
                    for usage_value in usage_values:
                        metric_date = usage_value[0]
                        metric_value = float(usage_value[1])
                        if metric_date not in k8s_metric_entry_map:
                            k8s_metric_entry_map[metric_date] = {}
                        if metric_name == POD_CPU_AVERAGE_USAGE_KEY:
                            metric_value = max(metric_value / METRIC_INTERVAL,
                                               default_metric_value)
                        k8s_metric_entry_map[metric_date][
                            metric_name] = metric_value
        for namespace, metric_value in k8s_metric_map.items():
            namespace_resource_quotas_map = metric_value.get(
                NAMESPACE_RESOURCE_QUOTAS_KEY)
            pod_limits_map = metric_value.get(POD_LIMIT_KEY)
            if not pod_limits_map:
                continue
            for pod_name, pod_info in pod_limits_map.items():
                resource_id = namespace_pod_map.get(
                    namespace, {}).get(pod_name)
                if not resource_id:
                    continue
                for pod_date, pod_metrics in pod_info.items():
                    if (namespace_resource_quotas_map and
                            namespace_resource_quotas_map.get(pod_date)):
                        pod_metrics.update(
                            namespace_resource_quotas_map[pod_date])
                    result.append({
                        'cloud_account_id': cloud_account_id,
                        'resource_id': resource_id,
                        'date': datetime.fromtimestamp(pod_date),
                        **{
                            metric_name: pod_metrics[metric_name]
                            if pod_metrics.get(metric_name) else default_value
                            for metric_name, default_value
                            in default_limit_values.items()}
                    })
        return result

    @staticmethod
    def get_gcp_metrics(cloud_account_id, cloud_resource_ids, resource_ids_map,
                        r_type, adapter, region, start_date, end_date):
        result = []

        # to get metric values INCLUDING start_date, we need to query metrics
        # for 15 minutes before the start_date
        start_date -= timedelta(seconds=METRIC_INTERVAL)

        # Note that we NEED ram_size be queried before ram_used to calculate % usage.
        # We rely on the fact that from python3.6 dictionaries remember the
        # order of items inserted.
        metric_cloud_names_map = {
            "cpu": "compute.googleapis.com/instance/cpu/utilization",
            "network_in_io": "compute.googleapis.com/instance/network/received_bytes_count",
            "network_out_io": "compute.googleapis.com/instance/network/sent_bytes_count",
            "ram_size": "compute.googleapis.com/instance/memory/balloon/ram_size",
            "ram": "compute.googleapis.com/instance/memory/balloon/ram_used",
            "disk_read_io": "compute.googleapis.com/instance/disk/read_ops_count",
            "disk_write_io": "compute.googleapis.com/instance/disk/write_ops_count",
        }
        ram_sizes = {}
        for metric_name, cloud_metric_name in metric_cloud_names_map.items():
            response = adapter.get_metric(
                cloud_metric_name,
                cloud_resource_ids, METRIC_INTERVAL,
                start_date, end_date)
            for record in response:
                cloud_resource_id = str(record.resource.labels["instance_id"])
                resource_id = resource_ids_map.get(cloud_resource_id)
                if resource_id is None:
                    LOG.warn(
                        "Unknown cloud resource id returned - %s",
                        cloud_resource_id)
                    continue
                # some metrics can contain records that belong not to the instance itself and to
                # its devices, e.g. disk_read_io for instance and for each of its disks.
                # here we filter out such extra records.
                cloud_resource_name = record.metric.labels["instance_name"]
                cloud_device_name = record.metric.labels.get("device_name")
                if cloud_device_name and cloud_resource_name != cloud_device_name:
                    continue
                # skip the first value in the list of points.
                # we rely on the fact that the points are always returned ordered by date
                # and the newest date is the first. we want to skip the newest date because
                # the value of the latest metric changes over time and it is better to request
                # it again later.
                for point in list(record.points)[1:]:
                    value = point.value.double_value
                    date = datetime.fromtimestamp(
                        point.interval.start_time.timestamp())
                    if metric_name in [
                        'network_in_io',
                        'network_out_io',
                        'disk_read_io',
                            'disk_write_io']:
                        # change values per min to values per second
                        value = value / 60
                    # to determine RAM value in % instead of absolute values,
                    # we need to know values of 2 metrics - ram_used and ram_size - for the same time
                    # so we store ram_size in a map and pop values from it later when processing ram_used.
                    # we rely on the fact that the metrics API returns metrics in the same order
                    # as they were requested.
                    elif metric_name == "ram_size":
                        key = (resource_id, date)
                        ram_sizes[key] = value
                        continue
                    elif metric_name == "ram":
                        key = (resource_id, date)
                        ram_size = ram_sizes.pop(key, None)
                        if ram_size is None:
                            LOG.warn(
                                "Unexpected ram_used without ram_size for GCP")
                            # should never happen as we query ram_size before
                            # ram_used
                            continue
                        # Gcp can sometimes report ram_size as 0 (saw this for windows server instance).
                        # Set ram usage to 0 in this case to avoid division by
                        # zero.
                        value = value / ram_size * 100 if ram_size else 0.0
                    elif metric_name == "cpu":
                        # metrics API returns CPU usage in range [0;1].
                        # transform it into %.
                        value *= 100
                    result.append({
                        'cloud_account_id': cloud_account_id,
                        'resource_id': resource_id,
                        'date': date,
                        'metric': metric_name,
                        'value': value
                    })
        return result

    def get_nebius_metrics(self, cloud_account_id, cloud_resource_ids,
                           resource_ids_map, r_type, adapter, region,
                           start_date, end_date):
        result = []
        metrics = defaultdict(lambda: defaultdict(dict))
        resource_metrics_map = {
            'Instance': {
                'cpu': 'cpu_usage',
                'disk_read_io': 'disk_read_ops',
                'disk_write_io': 'disk_write_ops',
                'network_in_io': 'network_received_bytes',
                'network_out_io': 'network_sent_bytes'},
            'RDS Instance': {
                'cpu': 'load.avg_15min',
                'disk_read_io': 'io.read_count',
                'disk_write_io': 'io.write_count',
                'network_in_io': 'net.bytes_recv',
                'network_out_io': 'net.bytes_sent',
                'ram': 'mem.used_bytes',
                'ram_size': 'mem.total_bytes'
            }
        }
        metric_names_map = resource_metrics_map.get(r_type)
        folders = adapter.folders
        for metric_name, cloud_metric_name in metric_names_map.items():
            for folder in folders:
                try:
                    response = adapter.get_metric(
                        cloud_metric_name, cloud_resource_ids, start_date,
                        end_date, METRIC_INTERVAL, folder)
                    for resp_metrics in response['metrics']:
                        timestamps = resp_metrics['timeseries']['timestamps']
                        values = resp_metrics['timeseries']['doubleValues']
                        cloud_resource_id = resp_metrics['labels']['resource_id']
                        if r_type == 'RDS Instance':
                            cloud_resource_id = resp_metrics['labels']['host']
                        if cloud_resource_id not in resource_ids_map:
                            continue
                        for i, point in enumerate(values):
                            timestamp = timestamps[i] / MSEC_IN_SEC
                            value = float(
                                values[i]) if values[i] != 'NaN' else 0
                            date = datetime.fromtimestamp(timestamp)
                            metrics[metric_name][
                                resource_ids_map[cloud_resource_id]][date] = value
                except Exception as exc:
                    LOG.error(f'Failed getting metric {metric_name} for '
                              f'folder: {folder}, exc: {str(exc)}')
                    continue
        if r_type == 'RDS Instance':
            ram_metrics = metrics.pop('ram', {})
            ram_size_metrics = metrics.pop('ram_size', {})
            for res_id, date_values in ram_metrics.items():
                for date, ram in date_values.items():
                    ram_size = ram_size_metrics.get(res_id, {}).get(date)
                    if ram_size:
                        ram_percent = ram * 100 / ram_size
                        metrics['ram'][res_id][date] = ram_percent
        for metric_name, values in metrics.items():
            for res_id, date_values in values.items():
                for date, value in date_values.items():
                    result.append({
                        'cloud_account_id': cloud_account_id,
                        'resource_id': res_id,
                        'date': date,
                        'metric': metric_name,
                        'value': value
                    })
        return result
