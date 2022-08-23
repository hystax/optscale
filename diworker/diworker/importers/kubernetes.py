#!/usr/bin/env python
import logging
import math

from collections import defaultdict
from datetime import datetime, timedelta
from pymongo import UpdateOne

from diworker.utils import bytes_to_gb
from diworker.importers.base import BaseReportImporter

from insider_client.client import Client as InsiderClient

LOG = logging.getLogger(__name__)
CHUNK_SIZE = 200
SECONDS_IN_HOUR = 3600
GB = 1024 * 1024 * 1024


class NodeCollectionException(Exception):
    pass


class PriceCollectionException(Exception):
    pass


class Node:
    def __init__(self, name, cpu=None, memory=None, region=None, flavor=None,
                 os_type=None, provider_id=None, hourly_price=None,
                 cost_model=None, **kwargs):
        self.name = name
        self.region = region
        self.flavor = flavor
        self.os_type = os_type
        self.provider_id = provider_id
        self.cpu = cpu
        self.memory = memory
        self.cost_model = cost_model
        self.hourly_price = hourly_price

    @property
    def provider(self):
        if self.provider_id is None:
            return None
        return next(iter(self.provider_id.split(':///')), None)

    @property
    def is_cloud_deployed(self):
        return self.provider_id is not None

    def as_dict(self):
        return {
            'name': self.name,
            'flavor': self.flavor,
            'provider_id': self.provider_id,
            'hourly_price': self.hourly_price,
            'cpu': self.cpu,
            'memory': self.memory
        }

    def __str__(self):
        return 'Node %s (provider %s, flavor %s, os type %s, region %s)' % (
            self.name, self.provider, self.flavor, self.os_type, self.region)


class NodesProvider:
    def __init__(self, cloud_adapter, insider_client, default_cost_model):
        self._cloud_adapter = cloud_adapter
        self._insider_client = insider_client
        self.default_cost_model = default_cost_model
        self._nodes = {}

    def _get_node_names(self, period, dt):
        pod_infos = self._cloud_adapter.get_metric(
            'last_over_time(kube_pod_info{node != ""}[%sd:1h])[%sd:1d]' % (
                period, period), int(dt.timestamp()))
        return {pod_info['metric']['node'] for pod_info in pod_infos}

    @property
    def default_hourly_price(self):
        if not self.default_cost_model:
            return None
        return sum(self.default_cost_model.values())

    @staticmethod
    def _price_to_cost_model(price):
        price_options = ['cpu_hourly_cost', 'memory_hourly_cost']
        return {
            k: float(price['price']) / len(price_options) for k in price_options
        }

    def load_data(self, period, dt):
        node_metrics = {}
        node_names = self._get_node_names(period, dt)
        names_filter = '|'.join(node_names)
        node_labels = self._cloud_adapter.get_metric(
            'last_over_time(kube_node_labels{node=~"%s"}[%sd: 1h])[%sd: 1d]' % (
                names_filter, period, period), dt.timestamp())
        for node_label in node_labels:
            metric = node_label.get('metric', {})
            node_metrics[metric['node']] = {
                'name': metric['node'],
                'region': metric.get('label_topology_kubernetes_io_region'),
                'flavor': metric.get('label_node_kubernetes_io_instance_type'),
                'os_type': metric.get('label_kubernetes_io_os'),
            }

        node_capacities = self._cloud_adapter.get_metric(
            'last_over_time(kube_node_status_capacity'
            '{resource =~ "cpu|memory", node =~ "%s"}[%sd:1h])[%sd: 1d]' % (
                names_filter, period, period), int(dt.timestamp()))
        for node_capacity in node_capacities:
            metric = node_capacity.get('metric', {})
            val = int(max(map(lambda x: x[1], node_capacity.get('values', []))))
            if metric['resource'] == 'memory':
                val = math.ceil(val / GB)
            node_metrics[metric['node']][metric['resource']] = val

        node_infos = self._cloud_adapter.get_metric(
            'last_over_time(kube_node_info{node=~"%s"}[%sd: 1h])[%sd: 1d]' % (
                names_filter, period, period), dt.timestamp())
        for node_info in node_infos:
            metric = node_info.get('metric', {})
            provider_id = metric.get('provider_id')
            node_metrics[metric['node']].update({'provider_id': provider_id})

        for name, metric in node_metrics.items():
            node = Node(**metric, cost_model=self.default_cost_model,
                        hourly_price=self.default_hourly_price)
            if node.is_cloud_deployed:
                _, res = self._insider_client.get_flavor_prices(
                    cloud_type=node.provider, flavor=node.flavor,
                    region=node.region, os_type=node.os_type
                )
                prices = res.get('prices', [])
                if not prices:
                    raise PriceCollectionException('Failed to find node %s price' % node)
                node.cost_model = self._price_to_cost_model(prices[0])
                node.hourly_price = float(prices[0]['price'])
                LOG.info('Detected cloud node %s. '
                         'Flavor based cost model will be used', node)
            else:
                LOG.info('Detected local node %s. '
                         'Default cost model will be used', node)
            self._nodes[name] = node

    def get(self, name):
        node = self._nodes.get(name)
        if not node:
            raise NodeCollectionException('Failed to find node %s' % name)
        return node

    def list(self):
        return list(self._nodes.values())

    def dump_nodes(self):
        return [n.as_dict() for n in self._nodes.values()]


class KubernetesReportImporter(BaseReportImporter):
    """
    Kubernetes Report Importer
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._insider_client = None
        self._nodes_provider = None
        self.period_start = None
        if self.cloud_acc.get('last_import_at'):
            last_import_at = self.get_last_import_date(self.cloud_acc_id)
            if last_import_at:
                self.period_start = last_import_at.replace(
                    hour=0, minute=0, second=0, microsecond=0)
        if self.period_start is None:
            self.set_period_start()

    def prepare(self):
        pass

    @property
    def nodes_provider(self):
        if self._nodes_provider is None:
            ca_cost_model = self.cloud_acc['config'].get('cost_model')
            if not ca_cost_model:
                raise ValueError(
                    'Cost_model for cloud_account %s is not provided' %
                    self.cloud_acc['id'])
            self._nodes_provider = NodesProvider(
                cloud_adapter=self.cloud_adapter,
                insider_client=self.insider_client,
                default_cost_model=ca_cost_model)
        return self._nodes_provider

    @property
    def insider_client(self):
        if self._insider_client is None:
            self._insider_client = InsiderClient(
                url=self.config_cl.insider_url(),
                secret=self.config_cl.cluster_secret(),
                verify=False)
        return self._insider_client

    def get_node_info(self, days, dt):
        pod_infos = self.cloud_adapter.get_metric(
            'avg_over_time(kube_pod_info{node != ""}[%sd:1h])[%sd:1d]' % (
                days, days), int(dt.timestamp()))
        pod_nodes = {pod_info['metric']['node'] for pod_info in pod_infos}
        # Here for azure we have capacity for node and for pool of scalesets.
        # Scaleset has huge capacity of cpu and memory that we don't really use,
        # so ignore it and get capacity from nodes that we really use.
        infos = self.cloud_adapter.get_metric(
            'avg_over_time(kube_node_status_capacity'
            '{resource =~ \'cpu|memory\'}[%sd:1h])[%sd:1d]' % (
                days, days), int(dt.timestamp()))
        info_timestamp_map = defaultdict(dict)
        node_usage_map = defaultdict(dict)
        for info in infos:
            resource = info['metric']['resource']
            node_name = info['metric']['node']
            if node_name not in pod_nodes:
                continue
            for timestamp, value in info.get('values', []):
                node_usage_map[node_name].update({resource: float(value)})
                info_timestamp_map[timestamp].update(node_usage_map)
        return info_timestamp_map

    @staticmethod
    def calculate_total_pods_metrics(metrics):
        total_values_map = defaultdict(dict)
        for r in metrics:
            node_name = r['metric']['instance']
            for dt_timestamp, value in r['values']:
                if not total_values_map[dt_timestamp].get(node_name):
                    total_values_map[dt_timestamp][node_name] = 0
                total_values_map[dt_timestamp][node_name] += float(value)
        return total_values_map

    def recalculate_raw_expenses(self):
        metric_resource_map = {
            'container_memory_usage_bytes': self.get_cost_by_avg_memory_usage,
            'container_cpu_usage_seconds_total': self.get_cost_by_cpu_usage_delta
        }

        base_filters = {
            'cloud_account_id': self.cloud_acc_id,
            'node_info': {'$exists': True},
            'total_pods_value': {'$exists': True},
            'node_kubernetes_io_instance_type': None
        }
        resource_ids = self.mongo_raw.distinct('resource_id', base_filters)
        resource_count = len(resource_ids)
        LOG.info('resource_count: %s', resource_count)
        progress = 0
        changes = []

        default_node = Node(
            name='dummy', cost_model=self.nodes_provider.default_cost_model)

        for i in range(0, resource_count, CHUNK_SIZE):
            new_progress = round(i / resource_count * 100)
            if new_progress != progress:
                progress = new_progress
                LOG.info('Progress: %s', progress)

            filters = base_filters.copy()
            filters['resource_id'] = {'$in': resource_ids[i:i + CHUNK_SIZE]}
            for expense in self.mongo_raw.find(filters):
                if expense['cost'] == 0:
                    continue

                cost_func = metric_resource_map.get(
                    expense['metric'])

                start_date = expense['start_date']
                end_date = expense['end_date']
                worked_hrs = (end_date - start_date + timedelta(seconds=1)
                              ).total_seconds() / SECONDS_IN_HOUR

                node_info = expense.get('node_info')
                total_metrics = expense.get('total_pods_value')
                cost = cost_func(default_node, node_info, expense['value'],
                                 total_metrics, worked_hrs)
                changes.append(UpdateOne(
                    filter={'_id': expense['_id']},
                    update={'$set': {'cost': cost}},
                ))

            if changes:
                self.mongo_raw.bulk_write(changes)

    def load_raw_data(self):
        now = datetime.utcnow()
        dt = now + timedelta(days=1)
        days = (dt - self.period_start).days
        LOG.info('Loading metrics for period %s - %s' % (
            self.period_start, dt))
        meter_map = {
            'container_memory_usage_bytes': (
                'avg_over_time(%s{pod != "", name =""}[%sd: 1h])[%sd: 1d]',
                self.get_cost_by_avg_memory_usage),
            'container_cpu_usage_seconds_total': (
                'idelta(%s{pod != "", name =""}[%sd: 1h])[%sd: 1d]',
                self.get_cost_by_cpu_usage_delta)
        }
        node_info = self.get_node_info(days, dt)
        self.nodes_provider.load_data(period=days, dt=dt)
        _pod_service_map = self.cloud_adapter.get_pod_services()
        chunk = []
        for metric_name, query_cost_func_set in meter_map.items():
            query, cost_func = query_cost_func_set
            resp = self.cloud_adapter.get_metric(
                query % (metric_name, days, days), dt.timestamp())
            total_metrics = self.calculate_total_pods_metrics(resp)
            for r in resp:
                node_name = r['metric']['instance']
                node = self.nodes_provider.get(node_name)
                for value_set in r['values']:
                    if len(chunk) == CHUNK_SIZE:
                        self.update_raw_records(chunk)
                        chunk = []
                    dt_timestamp, value = value_set
                    expense = r['metric'].copy()
                    pod_name = expense.get('pod')
                    resource_id = expense.pop('id').split('/pod')[-1]
                    start_date = datetime.utcfromtimestamp(
                        dt_timestamp) - timedelta(days=1)
                    end_date = datetime.utcfromtimestamp(dt_timestamp)
                    if end_date > now:
                        end_date = now
                    worked_hrs = (end_date - start_date
                                  ).total_seconds() / SECONDS_IN_HOUR
                    end_date = end_date - timedelta(seconds=1)
                    cost = cost_func(
                        node, node_info[dt_timestamp][node_name], value,
                        total_metrics[dt_timestamp][node_name], worked_hrs)
                    expense.update({
                        'metric': metric_name,
                        'value': value,
                        'timestamp': dt_timestamp,
                        'start_date': start_date,
                        'end_date': end_date,
                        'cloud_account_id': self.cloud_acc_id,
                        'resource_id': resource_id,
                        'cost': cost,
                        'node_info': node_info[dt_timestamp][node_name],
                        'total_pods_value': total_metrics[dt_timestamp][node_name],
                        'service': _pod_service_map.get(pod_name)
                    })
                    chunk.append(expense)
        if chunk:
            self.update_raw_records(chunk)

    @staticmethod
    def get_cost_by_avg_memory_usage(node, node_capacity, value,
                                     total_pods_value, worked_hrs):
        hourly_cost = node.cost_model['memory_hourly_cost']
        node_cost = bytes_to_gb(node_capacity['memory']) * hourly_cost * worked_hrs
        cost = bytes_to_gb(
            float(value)) * node_cost / bytes_to_gb(total_pods_value)
        return cost

    @staticmethod
    def get_cost_by_cpu_usage_delta(node, node_capacity, value,
                                    total_pods_value, worked_hrs):
        hourly_cost = node.cost_model['cpu_hourly_cost']
        node_cost = node_capacity['cpu'] * hourly_cost * worked_hrs
        cost = float(value) * node_cost / total_pods_value
        return cost

    def get_update_fields(self):
        return [
            'value',
            'cost'
        ]

    def get_unique_field_list(self):
        return [
            'start_date',
            'resource_id',
            'cloud_account_id',
            'metric',
            'pod',
        ]

    def get_resource_info_from_expenses(self, expenses):
        first_seen = datetime.utcnow()
        k8s_node, name, k8s_namespace, k8s_service, job = None, None, None, None, None
        last_seen = datetime.utcfromtimestamp(0).replace()
        for e in expenses:
            if not name:
                name = e.get('pod')
            if not k8s_node:
                k8s_node = e.get('kubernetes_io_hostname')
            if not k8s_namespace:
                k8s_namespace = e.get('namespace')
            if not k8s_service:
                k8s_service = e.get('service')
            if not job:
                job = e.get('job')
            start_date = e['start_date']
            if start_date and start_date < first_seen:
                first_seen = start_date
            end_date = e['end_date']
            if end_date and end_date > last_seen:
                last_seen = end_date
        if last_seen < first_seen:
            last_seen = first_seen
        info = {
            'name': name,
            'type': 'K8s Pod',
            'tags': {},
            'first_seen': int(first_seen.timestamp()),
            'last_seen': int(last_seen.timestamp()),
            'k8s_node': k8s_node,
            'k8s_namespace': k8s_namespace,
            'k8s_service': k8s_service
        }
        LOG.debug('Detected resource info: %s', info)
        return info

    def get_resource_data(self, r_id, info):
        return {
            'cloud_resource_id': r_id,
            'resource_type': info['type'],
            'name': info['name'],
            'tags': info['tags'],
            'service_name': info.get('service_name'),
            'first_seen': info['first_seen'],
            'last_seen': info['last_seen'],
            'k8s_node': info['k8s_node'],
            'k8s_namespace': info['k8s_namespace'],
            'k8s_service': info['k8s_service'],
            **self._get_fake_cad_extras(info)
        }

    def generate_clean_records(self, regeneration=False):
        base_filters = [
            {'cloud_account_id': self.cloud_acc_id},
        ]
        if not regeneration:
            base_filters.append({'start_date': {'$gte': self.period_start}})
        distinct_filters = {}
        for f in base_filters:
            distinct_filters.update(f)
        resource_ids = self.mongo_raw.distinct('resource_id', distinct_filters)
        resource_count = len(resource_ids)

        progress = 0
        for i in range(0, resource_count, CHUNK_SIZE):
            new_progress = round(i / resource_count * 100)
            if new_progress != progress:
                progress = new_progress
                LOG.info('Progress: %s', progress)

            filters = base_filters + [{'resource_id': {
                '$in': resource_ids[i:i + CHUNK_SIZE]
            }}]
            expenses = self.mongo_raw.aggregate([
                {'$match': {
                    '$and': filters,
                }},
                {'$group': {
                    '_id': '$resource_id',
                    'expenses': {'$push': '$$ROOT'}
                }},
            ])

            chunk = {e['_id']: e['expenses'] for e in expenses}
            self.save_clean_expenses(self.cloud_acc_id, chunk)
        LOG.info('resource_count: %s', resource_count)

    def clean_expenses_for_resource(self, resource_id, expenses):
        clean_expenses = {}
        for e in expenses:
            usage_date = e['start_date']
            if usage_date in clean_expenses:
                clean_expenses[usage_date]['cost'] += e['cost']
            else:
                clean_expenses[usage_date] = {
                    'date': usage_date,
                    'cost': e['cost'],
                    'resource_id': resource_id,
                    'cloud_account_id': e['cloud_account_id']
                }
        return clean_expenses

    def update_cloud_import_time(self, ts):
        if self.recalculate:
            _, res = self.rest_cl.node_list(self.cloud_acc_id)
            nodes = []
            for ca_node in res.get('nodes', []):
                node = Node(**ca_node)
                if not node.is_cloud_deployed:
                    node.cost_model = self.nodes_provider.default_cost_model
                    node.hourly_price = self.nodes_provider.default_hourly_price
                nodes.append(node.as_dict())
            nodes_data = {'nodes': nodes}
            self.rest_cl.node_create_bulk(self.cloud_acc_id, nodes_data)
        else:
            nodes = self.nodes_provider.dump_nodes()
            for node in nodes:
                node['last_seen'] = ts
            nodes_data = {'nodes': nodes}
            self.rest_cl.node_create_bulk(self.cloud_acc_id, nodes_data)
            super().update_cloud_import_time(ts)
