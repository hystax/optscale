#!/usr/bin/env python
import csv
import logging
from collections import defaultdict
from datetime import datetime, timezone

from diworker.diworker.importers.base import CSVBaseReportImporter

LOG = logging.getLogger(__name__)
CHUNK_SIZE = 500


class NebiusReportImporter(CSVBaseReportImporter):
    TAG_PREFIXES = ['labels.user_labels.', 'labels.system_labels.']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def get_unique_field_list(include_date=True):
        unique_list = [
            'resource_id',
            'sku_id',
            'cloud_account_id'
        ]
        if include_date:
            unique_list.extend([
                'date'
            ])
        return unique_list

    def get_update_fields(self):
        return [
            'cost',
            'pricing_quantity',
            'credit',
            'monetary_grant_credit',
            'cud_credit',
            'misc_credit',
            'updated_at',
            'report_identity',
            '_rec_n'
        ]

    def get_current_reports(self, reports_groups, last_import_modified_at):
        current_reports = defaultdict(list)
        reports_count = 0
        for date, reports in reports_groups.items():
            for report in reports:
                if report.get('LastModified', -1) > last_import_modified_at:
                    current_reports[date].append(report)
                    reports_count += 1
        LOG.info('Selected %s reports', reports_count)
        return current_reports

    def get_raw_upsert_filters(self, expense):
        filters = super().get_raw_upsert_filters(expense)
        filters.update({
            '$or': [
                {'report_identity': {'$ne': self.report_identity}},
                {'_rec_n': expense['_rec_n']}
            ]
        })
        return filters

    @staticmethod
    def _datetime_from_expense(expense, key):
        value = expense[key]
        if isinstance(value, str):
            return datetime.strptime(
                expense[key], '%Y-%m-%d').replace(tzinfo=timezone.utc)
        return value.replace(tzinfo=timezone.utc)

    def compose_resource_id(self, expense):
        return expense['sku_name']

    def load_report(self, report_path, account_id_ca_id_map):
        skipped_accounts = set()
        billing_period = None
        LOG.info('loading report %s', report_path)

        billing_period, skipped_accounts = self.load_csv_report(
            report_path, account_id_ca_id_map, billing_period,
            skipped_accounts)

        if billing_period:
            self.billing_periods.add(billing_period)
        if len(skipped_accounts) > 0:
            LOG.warning('Import skipped for following accounts: %s. Looks like '
                        'credentials for them weren\'t added or added '
                        'incorrectly or they are not marked as linked',
                        skipped_accounts)

    def load_csv_report(self, report_path, account_id_ca_id_map,
                        billing_period, skipped_accounts):
        date_start = datetime.utcnow()
        with open(report_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            chunk = []
            record_number = 0
            for row in reader:
                if billing_period is None:
                    billing_period = row['date']
                    LOG.info('detected billing period: %s', billing_period)

                if len(chunk) == CHUNK_SIZE:
                    self.update_raw_records(chunk)
                    chunk = []
                    now = datetime.utcnow()
                    if (now - date_start).total_seconds() > 60:
                        LOG.info('report %s: processed %s rows',
                                 report_path, record_number)
                        date_start = now

                cloud_account_id = account_id_ca_id_map.get(
                    row['cloud_id'])
                if cloud_account_id is None:
                    skipped_accounts.add(row['cloud_id'])
                    continue

                self.detected_cloud_accounts.add(cloud_account_id)
                date = self._datetime_from_expense(row, 'date')
                if date < self.min_date_import_threshold:
                    continue
                row['start_date'] = date.replace(
                    hour=0, minute=0, second=0, microsecond=0)
                row['end_date'] = date.replace(
                    hour=23, minute=59, second=59)
                row['cloud_account_id'] = cloud_account_id
                if not row.get('resource_id'):
                    row['resource_id'] = self.compose_resource_id(row)
                row['cost'] = float(row['cost'])
                row['report_identity'] = self.report_identity
                record_number += 1
                row['_rec_n'] = record_number
                chunk.append(row)
            if chunk:
                self.update_raw_records(chunk)
        return billing_period, skipped_accounts

    def collect_tags(self, expense):
        tags = {}
        for k, v in expense.items():
            for prefix in self.TAG_PREFIXES:
                if prefix in k and v:
                    k.replace(prefix, '', 1)
                    tags[k] = v
        return tags

    def get_resource_ids(self, cloud_account_id, billing_period):
        base_filters = {
            'cloud_account_id': cloud_account_id,
            'start_date': {'$gte': self.min_date_import_threshold}
        }
        if billing_period:
            base_filters['date'] = billing_period
        resource_ids = self.mongo_raw.aggregate([
            {'$match': base_filters},
            {'$group': {'_id': '$resource_id'}}
        ], allowDiskUse=True)
        return [x['_id'] for x in resource_ids]

    def _get_billing_period_filters(self, billing_period):
        return {
            'date': billing_period,
            'start_date': {'$gte': self.min_date_import_threshold}
        }

    def get_resource_type(self, expense):
        sku_name = expense['sku_name']
        service_name = expense['service_name']
        if 'Snapshot' in sku_name:
            return 'Snapshot'
        elif 'Image' in sku_name:
            return 'Image'
        elif 'IP address' in sku_name:
            return 'IP Address'
        elif 'Object Storage' in service_name:
            return 'Bucket'
        elif 'storage' in sku_name and service_name == 'Compute Cloud':
            return 'Volume'
        elif (service_name == 'Compute Cloud' and
              any(x in sku_name for x in ['AMD', 'Intel', 'RAM'])):
            return 'Instance'
        elif ('Managed Service for' in service_name and
              any(x in sku_name for x in ['AMD', 'Intel', 'RAM'])):
            return 'RDS Instance'
        else:
            return sku_name

    def get_resource_info_from_expenses(self, expenses):
        first_seen = datetime.utcnow()
        last_seen = datetime.utcfromtimestamp(0).replace()
        tags = {}
        for e in expenses:
            start_date = e['start_date']
            if start_date and start_date < first_seen:
                first_seen = start_date
            end_date = e['end_date']
            if end_date and end_date > last_seen:
                last_seen = end_date
            tags.update(self.collect_tags(e))
        if last_seen < first_seen:
            last_seen = first_seen

        info = {
            'name': None,
            'type': self.get_resource_type(expenses[-1]),
            'region': None,
            'service_name': expenses[-1]['service_name'],
            'tags': tags,
            'first_seen': int(first_seen.timestamp()),
            'last_seen': int(last_seen.timestamp()),
        }
        LOG.debug('Detected resource info: %s', info)
        return info

    def create_traffic_processing_tasks(self):
        self._create_traffic_processing_tasks()
