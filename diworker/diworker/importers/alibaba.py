#!/usr/bin/env python
import logging
import re
from calendar import monthrange
from datetime import datetime, timedelta, timezone

from diworker.diworker.importers.base import BaseReportImporter
from diworker.diworker.utils import bytes_to_gb
from optscale_client.herald_client.client_v2 import Client as HeraldClient

LOG = logging.getLogger(__name__)
CHUNK_SIZE = 200
SYSTEM_DISK_BILLING_ITEMS = [
    'System Disk Size',  # Ordinary VMs
    'systemdisk'  # Subscription VMs
]
BOX_USAGE_BILLING_ITEMS = [
    'Cloud server configuration',  # Ordinary instances
    'instance_type',  # Subscription instances
    'Class Code',  # RDS instances
    'Instance Type'  # Subscription RDS instances
]


class AlibabaReportImporter(BaseReportImporter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _get_system_disk_ids(self, current_day):
        # Daily raw usage is not aligned to start/end in request.
        # For example, you may request data from 2021-05-23T00:00Z to
        # 2021-05-24T00:00Z, but get it for 2021-05-23T16:00Z to
        # 2021-05-24T16:00Z. Let's include previous day into request
        # to avoid losing any data.
        start_time = current_day - timedelta(days=1)
        end_time = current_day + timedelta(days=1)
        return {
            item['AttachedInstanceId']: item['InstanceId']
            for item in self.cloud_adapter.get_raw_usage(
                'YunDisk', 'Hour', start_time, end_time)
            if item['Portable'] == '0'
        }

    def _get_snapshot_chain_usage(self, current_day):
        # There is no daily snapshot chain usage, only hourly.
        # Let's sum the results by day manually.
        start_time = current_day
        end_time = current_day + timedelta(days=1)
        snapshot_usage = self.cloud_adapter.get_raw_usage(
            'EcsSnapshot', 'Hour', start_time, end_time)
        chain_size = {}
        total_size = {}
        for item in snapshot_usage:
            region_id = item['Region']
            chain_id = item['LinkId']
            size_bytes = int(item['Size'])
            if region_id not in chain_size:
                chain_size[region_id] = {}
            if chain_id not in chain_size[region_id]:
                chain_size[region_id][chain_id] = 0
            if region_id not in total_size:
                total_size[region_id] = 0
            chain_size[region_id][chain_id] += size_bytes
            total_size[region_id] += size_bytes
        return chain_size, total_size

    def _process_system_disk_item(self, chunk, current_day, billing_item,
                                  system_disk_ids):
        # Alibaba bills system disks as a part of instance
        # expenses. It doesn't fit into OptScale model well, so
        # let's replace instance IDs with disk IDs and get rid of
        # instance-related information
        instance_id = billing_item['InstanceID']
        tags = self.extract_tags(billing_item['Tag'])
        disk_id = system_disk_ids.get(instance_id) or tags.get(
            'acs:ecs:sourceSystemDiskId')
        if disk_id:
            billing_item['InstanceID'] = disk_id
            # Remove instance name and tags
            # We do not have a way to obtain system disk name and
            # tags, so let's just make these entries empty
            billing_item['Tag'] = ''
            billing_item['NickName'] = ''
        else:
            LOG.warning(
                f'Could not find System Disk ID for {instance_id} '
                f'on {current_day}, adding entry as is')
        self._process_common_item(
            chunk, current_day, billing_item)

    def _process_box_usage_billing_item(self, chunk, current_day,
                                        billing_item):
        billing_item['box_usage'] = True
        self._process_common_item(
            chunk, current_day, billing_item)

    def _process_snapshot_item(self, chunk, current_day, billing_item,
                               snap_chain_size, snap_total_size):
        # Alibaba bills snapshots per total regional size, but
        # there is also raw usage data for snapshot chains. Let's
        # try to split regional expenses into snapshot chains
        region_id = billing_item['InstanceID']
        region_cost = billing_item['PretaxGrossAmount']
        region_chain_size = snap_chain_size.get(region_id)
        region_total_size = snap_total_size.get(region_id)
        if region_chain_size and region_total_size:
            for chain_id, size in region_chain_size.items():
                chain_item = billing_item.copy()
                chain_item['InstanceID'] = chain_id
                chain_item['Usage'] = bytes_to_gb(size)
                chain_item['PretaxGrossAmount'] = region_cost * (
                        size / region_total_size)
                for field in self._get_discount_fields():
                    chain_item[field] = float(chain_item[field]) * (
                        size / region_total_size)
                self._process_common_item(
                    chunk, current_day, chain_item)
        else:
            LOG.warning(
                f'Could not find Snapshot Chain usage for '
                f'{region_id} on {current_day}, adding entry as is')
            self._process_common_item(
                chunk, current_day, billing_item)

    def _process_common_item(self, chunk, current_day, billing_item):
        billing_item['cloud_account_id'] = self.cloud_acc_id
        billing_item['cost'] = round(billing_item['PretaxGrossAmount'] - sum(
            float(billing_item[x]) for x in self._get_discount_fields()), 8)
        billing_item['start_date'] = current_day
        billing_item['end_date'] = current_day + timedelta(days=1)
        billing_item['resource_id'] = billing_item['InstanceID']
        chunk.append(billing_item)
        if len(chunk) >= CHUNK_SIZE:
            self._flush_raw_chunk(chunk)

    def _flush_raw_chunk(self, chunk):
        if chunk:
            self.update_raw_records(chunk)
            chunk.clear()

    def load_raw_data(self):
        chunk = []
        now = datetime.utcnow()
        current_day = self.period_start.replace(
            hour=0, minute=0, second=0, microsecond=0)
        while current_day <= now:
            billing_items = self.cloud_adapter.get_billing_items(current_day)
            # sometimes Alibaba splits the same expenses for a date into
            # several bills, so merge them into one
            items = list(billing_items)
            billing_items_merged = self._merge_same_billing_items(items)

            system_disk_ids = self._get_system_disk_ids(current_day)
            snap_chain_size, snap_total_size = self._get_snapshot_chain_usage(
                current_day)
            skip_refunds = False
            if self.cloud_acc['config'].get('skip_refunds'):
                skip_refunds = True
            for billing_item in billing_items_merged:
                billing_item['report_identity'] = self.report_identity
                if skip_refunds and billing_item['Item'] == 'Refund':
                    LOG.info('Found refund for resource %s, billing item %s. '
                             'Skipping it!' % (
                                billing_item.get('InstanceID'),
                                billing_item.get('BillingItem')))
                    continue
                elif billing_item['BillingItem'] in SYSTEM_DISK_BILLING_ITEMS:
                    self._process_system_disk_item(
                        chunk, current_day, billing_item, system_disk_ids)
                elif (billing_item['ProductCode'] == 'snapshot' and
                      billing_item['BillingItemCode'] == 'Size'):
                    self._process_snapshot_item(
                        chunk, current_day, billing_item, snap_chain_size,
                        snap_total_size)
                elif billing_item['BillingItem'] in BOX_USAGE_BILLING_ITEMS:
                    self._process_box_usage_billing_item(
                        chunk, current_day, billing_item)
                else:
                    self._process_common_item(
                        chunk, current_day, billing_item)
            current_day += timedelta(days=1)
        self._flush_raw_chunk(chunk)
        self.generate_rdd_records(self.cloud_acc_id)
        self.clear_rudiments()

    def _get_discount_fields(self):
        return [
            'InvoiceDiscount',
            'DeductedByCoupons',
        ]

    def get_update_fields(self, optscale_f_incl=True):
        cloud_fields = [
            'PretaxGrossAmount',
            'PretaxAmount',
            'Usage',
            'NickName',
            'Zone',
            'InstanceSpec',
            'InstanceConfig'
        ] + self._get_discount_fields()
        optscale_fields = ['cost']
        if optscale_f_incl:
            return cloud_fields + optscale_fields
        else:
            return cloud_fields

    def extract_tags(self, raw_tags):
        tags = {}
        failed_items = []
        if raw_tags:
            for item in raw_tags.split(';'):
                match = re.match(r'^\s*key:(.+)\s+value:(.*)\s*$', item)
                if match:
                    tags[match.group(1)] = match.group(2)
                else:
                    failed_items.append(item)
        if failed_items:
            LOG.warning(f'Could not parse tag items: {failed_items}')
        return tags

    def _get_resource_type(self, expense):
        product_code = expense['ProductCode']
        billing_item = expense.get('BillingItem')
        billing_item_code = expense.get('BillingItemCode')
        product_detail = expense['ProductDetail']
        if (product_code == 'yundisk' or
                billing_item in SYSTEM_DISK_BILLING_ITEMS):
            return 'Volume'
        elif 'RDD' in expense['resource_id']:
            return 'Round Down Discount'
        elif product_code == 'ecs':
            return 'Instance'
        elif product_code == 'snapshot' and billing_item_code == 'Size':
            return 'Snapshot Chain'
        elif product_code == 'snapshot':
            return 'Snapshot Storage'
        elif product_code == 'oss':
            return 'Object Storage'
        elif product_code == 'rds':
            return 'RDS Instance'
        elif product_detail == 'Elastic IP':
            return 'IP Address'
        elif product_detail == 'sls_intl':
            return 'Log Storage'
        else:
            return product_detail

    def get_resource_info_from_expenses(self, expenses):
        first_seen = datetime.utcnow()
        last_seen = datetime.utcfromtimestamp(0).replace()
        for e in expenses:
            start_date = e['start_date']
            if start_date and start_date < first_seen:
                first_seen = start_date
            end_date = e['end_date']
            if end_date and end_date > last_seen:
                last_seen = end_date
        if last_seen < first_seen:
            last_seen = first_seen

        tags = self.extract_tags(expenses[-1]['Tag'])
        info = {
            'name': expenses[-1]['NickName'] or None,
            'type': self._get_resource_type(expenses[-1]),
            'region': expenses[-1]['Region'] or None,
            'service_name': expenses[-1]['ProductName'],
            'tags': tags,
            'first_seen': int(first_seen.timestamp()),
            'last_seen': int(last_seen.timestamp()),
        }
        LOG.debug('Detected resource info: %s', info)
        return info

    def get_unique_field_list(self, optscale_f_incl=True, inst_id_incl=False):
        base_fields = [
            'CommodityCode',
            'Item',
            'BillingItem',
            'BillingType',
            'ProductCode',
            'ProductType',
            'UsageUnit',
            'ListPrice'
        ]
        optscale_fields = ['start_date', 'resource_id', 'cloud_account_id']
        inst_id = ['InstanceID']
        if optscale_f_incl:
            base_fields += optscale_fields
        if inst_id_incl:
            base_fields += inst_id
        return base_fields

    def _merge_same_billing_items(self, items):
        unique_fields = self.get_unique_field_list(optscale_f_incl=False,
                                                   inst_id_incl=True)
        update_fields = self.get_update_fields(optscale_f_incl=False)

        b_item_map = {}
        for b_item in items:
            key = tuple(b_item.get(f) for f in unique_fields)
            if not b_item_map.get(key):
                b_item_map[key] = [b_item]
            else:
                b_item_map[key].append(b_item)

        for k, items_list in b_item_map.items():
            if len(items_list) > 1:
                common_item = {k: v for k, v in items_list[0].items()
                               if k not in update_fields}
                for field in update_fields:
                    common_item[field] = sum(
                        float(i[field]) for i in items_list if i[field])
                b_item_map[k] = [common_item]
        updated_billing_items = [v[0] for v in b_item_map.values()]
        return updated_billing_items

    def get_full_months_in_period(self):
        full_month_dates = []
        start = self.period_start
        end = datetime.utcnow()
        month_start = datetime(
            year=start.year, month=start.month, day=1,
            hour=0, minute=0, second=0)
        _, last_day = monthrange(start.year, start.month)
        month_end = datetime(
            year=start.year, month=start.month, day=last_day,
            hour=23, minute=59, second=59)

        if start.year == end.year and start.month == end.month:
            if start == month_start and end == month_end:
                full_month_dates.append(end)
        else:
            if start == month_start and end > month_end:
                full_month_dates.append(start)
            next_month_start = month_end + timedelta(seconds=1)

            while next_month_start < end.replace(day=1, hour=0, minute=0,
                                                 second=0, microsecond=0):
                _, last_day = monthrange(next_month_start.year,
                                         next_month_start.month)
                full_month_dates.append(next_month_start)
                new_month = next_month_start.month + 1
                if new_month <= 12:
                    next_month_start = next_month_start.replace(month=new_month)
                else:
                    new_year = next_month_start.year + 1
                    next_month_start = next_month_start.replace(year=new_year,
                                                                month=1)
        return full_month_dates

    def generate_rdd_records(self, cloud_account_id):
        LOG.info('Generating RDD raw expenses for cloud '
                 'account: %s', cloud_account_id)
        chunk = []
        full_months = list(set(self.get_full_months_in_period()))
        for date in full_months:
            _, last_day = monthrange(date.year, date.month)
            resource_id_rdd_map = self.cloud_adapter.get_round_down_discount(date)
            for res_id, rdd in resource_id_rdd_map.items():
                rdd['start_date'] = date.replace(day=last_day, hour=0,
                                                 minute=0, second=0)
                rdd['end_date'] = date.replace(day=last_day, hour=23,
                                               minute=59, second=59)
                rdd['cloud_account_id'] = self.cloud_acc_id
                rdd['cost'] = -abs(rdd['cost'])
                rdd['NickName'] = res_id
                rdd['Region'] = ''
                rdd['Tag'] = ''
                rdd['report_identity'] = self.report_identity
                chunk.append(rdd)
                if len(chunk) >= CHUNK_SIZE:
                    self.update_raw_records(chunk)
        if chunk:
            self.update_raw_records(chunk)

    def send_service_incorrect_expenses_email(self, cloud_account, period,
                                              clean_expenses, cloud_expenses):
        _, organization = self.rest_cl.organization_get(
            cloud_account['organization_id'])
        recipient = self.config_cl.optscale_error_email_recipient()
        if not recipient:
            return
        title = "Incorrect expenses for Alibaba cloud account"
        subject = '[%s] %s' % (self.config_cl.public_ip(), title)
        template_params = {
            'texts': {
                'organization': {
                    'id': organization['id'],
                    'name': organization['name']},
                'cloud_account': {
                    'id': cloud_account['id'],
                    'name': cloud_account['name'],
                },
                'period': period,
                'clean_expenses': clean_expenses,
                'cloud_expenses': cloud_expenses
            }}
        HeraldClient(url=self.config_cl.herald_url(),
                     secret=self.config_cl.cluster_secret()).email_send(
            [recipient], subject, template_params=template_params,
            template_type="incorrect_alibaba_expenses")

    def check_exp_for_previous_month(self, now):
        billing_date = now - timedelta(days=now.day)
        bill = self.cloud_adapter.get_bill_overview(billing_date)
        total_cloud_bill = 0
        for data in bill.get('Data', {}).get('Items', {}).get('Item', []):
            if 'AfterTaxAmount' in data:
                total_cloud_bill += data['AfterTaxAmount']
            else:
                total_cloud_bill += data['OutstandingAmount']

        params = {'cloud_account_id': self.cloud_acc_id}
        _, last_day = monthrange(billing_date.year, billing_date.month)
        start_date = billing_date.replace(day=1, hour=0, minute=0, second=0)
        end_date = billing_date.replace(day=last_day, hour=23, minute=59,
                                        second=59)
        _, expenses = self.rest_cl.summary_expenses_get(
            self.cloud_acc['organization_id'], int(start_date.timestamp()),
            int(end_date.timestamp()), params)
        if round(expenses['total_cost'], 2) != round(total_cloud_bill, 2):
            LOG.error(
                'Total cost of cloud expenses %s doesn\'t match to clean '
                'expenses total cost %s' % (
                    total_cloud_bill, round(expenses['total_cost'], 2)))
            self.send_service_incorrect_expenses_email(
                self.cloud_acc, billing_date.strftime('%Y-%m'),
                round(expenses['total_cost'], 2), total_cloud_bill)

    def fix_snapshot_chain_expenses(self):
        """Diworker calculates snapshot chains cost by getting snapshot chains
        regional expenses costs which includes all snapshot chains and
        getting usage in bytes for this date split by snapshot chain.
        Alibaba's apis sometimes doesn't return snapshot chains usage data,
        but may return this data later (for example it doesn't return usage
        for the current hour). In this case diworker creates a 'regional'
        snapshot chain resource with expenses not split by existing snapshot
        chains in this region.
        These 'regional' snapshot chains resources and expenses should be
        deleted as soon as diworker got snapshot chains usage and calculated
        personal costs for every snapshot chain in the region.

        This func removes clean expenses for snapshot chains without raw
        expenses, updates last_seen and last_expense for snapshot chain
        resources or deletes 'regional' snapshot chains resources if it hasn't
        raw expenses"""

        sc_ids_map = {
            x['cloud_resource_id']: x['_id']
            for x in self.mongo_resources.find({
                'cloud_account_id': self.cloud_acc_id,
                '_last_seen_date': {'$gte': self.period_start},
                'resource_type': 'Snapshot Chain',
                'active': {'$exists': False}},
                {'_id': 1, 'cloud_resource_id': 1})}
        sc_cloud_res_ids = list(sc_ids_map.keys())
        sc_cloud_without_expenses = set()
        for i in range(0, len(sc_cloud_res_ids), CHUNK_SIZE):
            sc_cloud_chunk = sc_cloud_res_ids[i:i + CHUNK_SIZE]
            sc_cloud_with_expenses = set(self.mongo_raw.distinct(
                    'resource_id', {'cloud_account_id': self.cloud_acc_id,
                                    'start_date': {'$gte': self.period_start},
                                    'resource_id': {'$in': sc_cloud_chunk}}))
            sc_cloud_without_expenses.update(
                set(sc_cloud_chunk) - sc_cloud_with_expenses)
        if sc_cloud_without_expenses:
            LOG.info('Removing clean expenses for snapshot chains: %s',
                     sc_cloud_without_expenses)
            sc_without_expenses = [
                sc_ids_map[x] for x in sc_cloud_without_expenses
            ]
            existing_expenses = self.clickhouse_cl.execute(
                """SELECT resource_id, date, SUM(cost * sign) AS total_cost
                   FROM expenses
                   WHERE cloud_account_id = %(cloud_account_id)s
                       AND date >= %(from_dt)s
                       AND date <= %(to_dt)s
                       AND resource_id in %(resource_ids)s
                   GROUP BY resource_id, date
                   HAVING SUM(sign) > 0""",
                params={
                    'cloud_account_id': self.cloud_acc_id,
                    'from_dt': self.period_start,
                    'to_dt': datetime.now(tz=timezone.utc).replace(tzinfo=None),
                    'resource_ids': sc_without_expenses
                })
            clickhouse_expenses = []
            for resource_id, date, total_cost in existing_expenses:
                clickhouse_expenses.append({
                    'cloud_account_id': self.cloud_acc_id,
                    'resource_id': resource_id,
                    'date': date,
                    'cost': total_cost,
                    'sign': -1
                })
            self.update_clickhouse_expenses(clickhouse_expenses)
            LOG.info('Updating last_seen and last_expense for snapshot chains')
            last_expense_info = {}
            raw_expenses = self.mongo_raw.aggregate([
                {'$match': {
                    'cloud_account_id': self.cloud_acc_id,
                    'start_date': {'$lt': self.period_start},
                    'resource_id': {'$in': list(sc_cloud_without_expenses)}}},
                {'$sort': {'start_date': -1}},
                {'$group': {
                    '_id': '$resource_id',
                    'start_date': {'$first': '$start_date'},
                    'cost': {'$first': '$cost'}
                }}
            ])
            for expense in raw_expenses:
                last_expense_info[sc_ids_map[expense['_id']]] = (
                    expense['start_date'], expense['cost'])
            # update last_expense, last_seen for snapshot chains with expenses
            self.update_resource_expense_info(
                self.cloud_acc_id, last_expense_info)
            # delete snapshot chain resources without expenses
            if len(last_expense_info) < len(sc_cloud_without_expenses):
                for cloud_resource_id in sc_cloud_without_expenses:
                    resource_id = sc_ids_map[cloud_resource_id]
                    if resource_id not in last_expense_info:
                        self.mongo_resources.delete_one({'_id': resource_id})

    def generate_clean_records(self, regeneration=False):
        super().generate_clean_records(regeneration=regeneration)
        if self.cloud_acc['last_import_at'] != 0:
            self.fix_snapshot_chain_expenses()
        now = datetime.utcnow()
        if (self.period_start.month != now.month or
                self.period_start.year != now.year):
            self.check_exp_for_previous_month(now)

    def create_traffic_processing_tasks(self):
        self._create_traffic_processing_tasks()
