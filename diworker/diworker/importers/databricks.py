#!/usr/bin/env python
import json
import csv
import logging
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from tools.cloud_adapter.clouds.databricks import DEFAULT_SKU_PRICES
from diworker.diworker.importers.base import BaseReportImporter

LOG = logging.getLogger(__name__)
CHUNK_SIZE = 200
META_FIELDS = ['sku', 'clusterNodeType', 'clusterOwnerUserId',
               'clusterOwnerUserName', 'workspaceId']


class DatabricksReportImporter(BaseReportImporter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.discovered_skus = set()

    def get_unique_field_list(self):
        return [
            'end_date',
            'resource_id',
            'cloud_account_id',
            'sku'
        ]

    def get_update_fields(self):
        custom_fields = {'start_date', 'cost', 'dbus', 'machineHours', 'tags',
                         'clusterCustomTags', 'clusterOwnerUserId'}
        return list(custom_fields)

    def datetime_from_str(self, date_str):
        return datetime.strptime(
            date_str, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc)

    def str_from_datetime(self, date_obj):
        return date_obj.replace(tzinfo=timezone.utc).strftime(
            '%Y-%m-%dT%H:%M:%S.%fZ')

    def detect_period_start(self):
        super().detect_period_start()
        self.period_start = self.period_start.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0)

    def load_raw_data(self):
        start_date = self.period_start.strftime("%Y-%m")
        end_date = datetime.utcnow().strftime("%Y-%m")
        usages = self.cloud_adapter.download_usage(
            start_date, end_date)
        if not usages:
            return
        reader = csv.DictReader(usages, delimiter=',')
        chunk = []
        sku_prices = DEFAULT_SKU_PRICES.copy()
        sku_prices.update(self.cloud_acc['config'].get('cost_model', {}))
        for usage_obj in reader:
            if len(chunk) == CHUNK_SIZE:
                self.update_raw_records(chunk)
                chunk = []
            self._fill_custom_fields(usage_obj, sku_prices)
            self._clean_tree(usage_obj)
            if usage_obj['start_date'] >= self.period_start.replace(
                    tzinfo=timezone.utc):
                chunk.append(usage_obj)
        if chunk:
            self.update_raw_records(chunk)

    def _clean_tree(self, tree):
        for k, v in tree.copy().items():
            if isinstance(v, dict):
                self._clean_tree(v)
            elif v is None:
                del tree[k]

    def _fill_custom_fields(self, u, sku_prices):
        sku = u['sku']
        dbus = float(u.get('dbus', 0))
        price = sku_prices.get(sku)
        if price is None:
            self.discovered_skus.add(sku)
            price = 0
        u['cost'] = dbus * price
        u['resource_id'] = u['clusterId']
        end_date = self.datetime_from_str(u['timestamp']).replace(
            tzinfo=timezone.utc)
        u['end_date'] = end_date
        u['start_date'] = end_date - timedelta(
            hours=float(u.get('machineHours', 0)))
        u['cloud_account_id'] = self.cloud_acc_id

    def _get_cloud_extras(self, info):
        res = defaultdict(dict)
        for k in META_FIELDS:
            val = info.get(k)
            if val:
                res['meta'][k] = val
        return res

    def get_resource_info_from_expenses(self, expenses):
        first_seen = datetime.utcnow()
        last_seen = datetime.utcfromtimestamp(0)
        meta_dict = {}
        resource_type = None
        name = None
        tags = {}
        for e in expenses:
            r_tags = json.loads(e.get('tags', '{}'))
            if not resource_type and 'ResourceClass' in r_tags:
                resource_type = r_tags['ResourceClass']
            tags.update(r_tags)
            tags.update(json.loads(e.get('clusterCustomTags', '{}')))
            start_date = e['start_date']
            if start_date and start_date < first_seen:
                first_seen = start_date
            end_date = e['end_date']
            if end_date and end_date > last_seen:
                last_seen = end_date
            if not name:
                name = e.get('clusterName')
            for k in META_FIELDS:
                v = e.get(k)
                if v is not None and k not in meta_dict:
                    meta_dict[k] = v
        if last_seen < first_seen:
            last_seen = first_seen
        info = {
            'name': name,
            'type': resource_type or 'Node',
            'tags': tags,
            'first_seen': int(first_seen.timestamp()),
            'last_seen': int(last_seen.timestamp()),
            **meta_dict
        }
        LOG.debug('Detected resource info: %s', info)
        return info

    def get_resource_data(self, r_id, info,
                          unique_id_field='cloud_resource_id'):
        return {
            unique_id_field: r_id,
            'resource_type': info['type'],
            'name': info['name'],
            'tags': info['tags'],
            'first_seen': info['first_seen'],
            'last_seen': info['last_seen'],
            **self._get_cloud_extras(info)
        }

    def update_cloud_import_time(self, ts):
        super().update_cloud_import_time(ts)
        cost_map = self.cloud_acc['config'].get('cost_model', {})
        cost_map.update({k: 0 for k in self.discovered_skus})
        self.rest_cl.sku_cost_model_update(
            self.cloud_acc_id, {'value': cost_map})

    def recalculate_raw_expenses(self):
        expenses = self.mongo_raw.find({'cloud_account_id': self.cloud_acc_id})
        chunk = []
        sku_prices = DEFAULT_SKU_PRICES.copy()
        sku_prices.update(self.cloud_acc['config'].get('cost_model', {}))
        for e in expenses:
            if len(chunk) == CHUNK_SIZE:
                self.update_raw_records(chunk)
                chunk = []
            sku = e['sku']
            dbus = float(e.get('dbus', 0))
            price = sku_prices.get(sku) or 0
            cost = price * dbus
            if cost != e['cost']:
                e['cost'] = cost
                chunk.append(e)
        if chunk:
            self.update_raw_records(chunk)
