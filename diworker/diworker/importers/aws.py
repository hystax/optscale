#!/usr/bin/env python
import csv
import gzip
import logging
import os
import pyarrow
import shutil
import uuid
import zipfile
from collections import defaultdict, OrderedDict
from datetime import datetime, timedelta, timezone
from diworker.importers.base import BaseReportImporter
from diworker.constants import AWS_PARQUET_CSV_MAP

import pyarrow.parquet as pq

LOG = logging.getLogger(__name__)
CHUNK_SIZE = 500
GZIP_ENDING = '.gz'
IGNORE_EXPENSE_TYPES = ['Credit', 'SavingsPlanNegation']
tag_prefixes = ['resource_tags_aws_', 'resource_tags_user_']


class AWSReportImporter(BaseReportImporter):
    ITEM_TYPE_ID_FIELDS = {
        'Tax': ['lineItem/TaxType', 'product/ProductName'],
        'Usage': ['lineItem/ProductCode', 'lineItem/Operation',
                  'product/region'],
    }
    STORAGE_LENS_TYPE = 'StorageLens'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.billing_periods = set()
        self.detected_cloud_accounts = set()
        self.detected_cloud_accounts.add(self.cloud_acc_id)
        self.reports_dir = str(uuid.uuid4())
        os.makedirs(self.reports_dir)
        self.report_files = defaultdict(list)
        self.last_import_modified_at = self.cloud_acc.get(
            'last_import_modified_at', 0)
        self.main_resources_product_family_map = {
            'Bucket': ['Storage', 'Data Transfer', 'Fee'],
            'Instance': ['Compute Instance', 'Stopped Instance'],
            'Snapshot': ['Storage Snapshot'],
            'Volume': ['Storage']
        }
        self.import_start_ts = int(datetime.utcnow().timestamp())
        self.current_billing_period = None

    def prepare(self):
        if self.import_file is not None:
            self.download_from_object_store()
        else:
            self.download_from_cloud()
        self.unpack_report_files()

    def get_new_report_path(self, date=''):
        return os.path.join(self.reports_dir, date, str(uuid.uuid4()))

    def download_from_object_store(self):
        bucket, filename = self.import_file.split('/')
        self.report_files['reports'] = [self.get_new_report_path()]
        with open(self.report_files['reports'][0], 'wb') as f_report:
            self.s3_client.download_fileobj(bucket, filename, f_report)

    @staticmethod
    def unzip_report(report_path, dest_dir):
        LOG.info('Extracting %s as zip archive to %s', report_path, dest_dir)
        if zipfile.is_zipfile(report_path):
            with zipfile.ZipFile(report_path, 'r') as f_zip:
                if len(f_zip.filelist) > 1:
                    raise Exception('zip excepted to have one file inside')
                f_zip.extractall(dest_dir)
                new_report_path = os.path.join(
                    dest_dir, f_zip.filelist[0].filename)

            return new_report_path

    @staticmethod
    def gunzip_report(report_path, dest_dir):
        LOG.info('Extracting %s as gzip archive to %s',
                 report_path, dest_dir)
        new_report_path = os.path.basename(report_path)
        if new_report_path.endswith(GZIP_ENDING):
            new_report_path = new_report_path[
                              :len(new_report_path) - len(GZIP_ENDING)]
        else:
            new_report_path = str(uuid.uuid4())
        new_report_path = os.path.join(dest_dir, new_report_path)
        try:
            with gzip.open(report_path, 'rb') as f_gzip:
                with open(new_report_path, 'wb') as f_out:
                    shutil.copyfileobj(f_gzip, f_out)
        except Exception:
            if os.path.exists(new_report_path):
                os.remove(new_report_path)
            return

        return new_report_path

    def unpack_report(self, report_file, date):
        dest_dir = self.get_new_report_path(date)
        os.makedirs(dest_dir, exist_ok=True)
        if zipfile.is_zipfile(report_file):
            new_report_path = self.unzip_report(report_file, dest_dir)
        else:
            new_report_path = self.gunzip_report(report_file, dest_dir)
        if new_report_path:
            os.remove(report_file)
            return new_report_path
        else:
            return report_file

    def unpack_report_files(self):
        for date, reports in self.report_files.items():
            self.report_files[date] = [
                self.unpack_report(r, date) for r in self.report_files[date]]

    def cleanup(self):
        shutil.rmtree(self.reports_dir, ignore_errors=True)
        if self.import_file:
            bucket, filename = self.import_file.split('/')
            self.s3_client.delete_object(Bucket=bucket, Key=filename)

    def download_from_cloud(self):
        current_reports = defaultdict(list)
        reports_groups = self.cloud_adapter.get_report_files()
        if self.last_import_modified_at <= 0:
            last_import_modified_at = datetime.min.replace(
                tzinfo=timezone.utc)
            LOG.info('Decided to download latest reports set')
            current_reports = defaultdict(list)
            report_groups_keys = list(reports_groups.keys())
            report_groups_keys.sort()
            # to get reports for the current and three previous months
            num_last_reports = 4 if self.need_extend_report_interval else 1
            report_groups_keys = report_groups_keys[-num_last_reports:]
            for key in report_groups_keys:
                current_reports[key].extend(reports_groups[key])
        else:
            last_import_modified_at = datetime.fromtimestamp(
                self.last_import_modified_at, tz=timezone.utc)
            for date, reports in reports_groups.items():
                for report in reports:
                    if report.get('LastModified') > last_import_modified_at:
                        current_reports[date].extend(reports)
                        break
            LOG.info('Selected %s reports', len(current_reports))

        for date, reports in current_reports.items():
            for report in reports:
                if last_import_modified_at < report['LastModified']:
                    last_import_modified_at = report['LastModified']
                target_path = self.get_new_report_path(date)
                os.makedirs(os.path.join(self.reports_dir, date),
                            exist_ok=True)
                try:
                    # python2 way
                    with open(target_path, 'wb') as f_report:
                        self.cloud_adapter.download_report_file(report['Key'],
                                                                f_report)
                except TypeError:
                    # python3 way
                    with open(target_path, 'w') as f_report:
                        self.cloud_adapter.download_report_file(report['Key'],
                                                                f_report)
                self.report_files[date].append(target_path)
        self.last_import_modified_at = int(last_import_modified_at.timestamp())

    @staticmethod
    def get_unique_field_list(include_date=True):
        # todo: if this is not enough, we may lose data on raw import
        # we need functional testing. at least verify count of records after
        # import. also total sum from CSV must match total sum for clean records
        unique_list = [
            'lineItem/LineItemDescription',
            'lineItem/LineItemType',
            'lineItem/UsageType',
            'lineItem/Operation',
            'lineItem/ProductCode',
            'cloud_account_id',
            'lineItem/AvailabilityZone',
            'savingsPlan/SavingsPlanARN',
            'reservation/ReservationARN'
            'bill/BillingPeriodStartDate',
            'resource_id'
        ]
        if include_date:
            unique_list.extend([
                'lineItem/UsageStartDate',
                'start_date'
            ])
        return unique_list

    def get_update_fields(self):
        return [
            'lineItem/BlendedRate',
            'lineItem/BlendedCost',
            'lineItem/UnblendedRate',
            'lineItem/UnblendedCost',
            'lineItem/UsageEndDate',
            'end_date',
            'cost',
            'report_identity',
            '_rec_n'
        ]

    def get_raw_upsert_filters(self, expense):
        filters = super().get_raw_upsert_filters(expense)
        filters.update({
            '$or': [
                {'report_identity': {'$ne': self.report_identity}},
                {'_rec_n': expense['_rec_n']}
            ]
        })
        return filters

    def get_linked_account_map(self):
        org_id = self.cloud_acc['organization_id']
        _, linked_accs = self.rest_cl.cloud_account_list(
            org_id, only_linked=True, auto_import=True, type='aws_cnr')
        account_id_ca_id_map = {x['account_id']: x['id']
                                for x in linked_accs['cloud_accounts']}
        account_id_ca_id_map[self.cloud_acc['account_id']] = self.cloud_acc_id
        return account_id_ca_id_map

    def load_raw_data(self):
        account_id_ca_id_map = self.get_linked_account_map()
        report_files = []
        for r in self.report_files.values():
            report_files.extend(r)
        for report_path in report_files:
            self.load_report(report_path, account_id_ca_id_map)
        self.clear_rudiments()

    def load_report(self, report_path, account_id_ca_id_map):
        skipped_accounts = set()
        billing_period = None
        LOG.info('loading report %s', report_path)

        try:
            billing_period, skipped_accounts = self.load_parquet_report(
                report_path, account_id_ca_id_map, billing_period,
                skipped_accounts)
        except pyarrow.lib.ArrowInvalid:
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

    def update_raw_records(self, chunk):
        for row in chunk:
            # TODO: OS-5444
            # pymongo InsertOne fails on '.' in key, while UpdateOne splits
            # key by dot and saves as dict, ex.:
            #     {"resourceTags/user:test.dot": 1} ->
            #         {"resourceTags/user:test": {"dot": 1}}
            def split_dot_keys(key, value):
                result = {key: value}
                if '.' in key:
                    result.pop(key)
                    parts = key.split('.', 1)
                    result[parts[0]] = split_dot_keys(parts[1], value)
                    return result
                return result

            tags = {k: v for k, v in row.items() if
                    k.startswith('resourceTags')}
            for k, v in tags.items():
                row.pop(k)
                row.update(split_dot_keys(k, v))
            row['report_identity'] = self.report_identity
        super().update_raw_records(chunk)

    def load_csv_report(self, report_path, account_id_ca_id_map,
                        billing_period, skipped_accounts):
        with open(report_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            chunk = []
            record_number = 0
            for row in reader:
                if billing_period is None:
                    billing_period = row['bill/BillingPeriodStartDate']
                    LOG.info('detected billing period: %s', billing_period)
                    self.current_billing_period = billing_period

                if len(chunk) == CHUNK_SIZE:
                    self.update_raw_records(chunk)
                    chunk = []

                cloud_account_id = account_id_ca_id_map.get(
                    row['lineItem/UsageAccountId'])
                if cloud_account_id is None:
                    skipped_accounts.add(row['lineItem/UsageAccountId'])
                    continue

                self.detected_cloud_accounts.add(cloud_account_id)
                record_number += 1
                row['_rec_n'] = record_number
                row['cloud_account_id'] = cloud_account_id
                if 'lineItem/ResourceId' in row:
                    r_id = row['lineItem/ResourceId']
                    row['resource_id'] = r_id[r_id.find('/') + 1:]
                start_date = self._datetime_from_expense(
                    row, 'lineItem/UsageStartDate').replace(
                    hour=0, minute=0, second=0)
                row['start_date'] = start_date
                row['end_date'] = self._datetime_from_expense(
                    row, 'lineItem/UsageEndDate')
                row['cost'] = float(row['lineItem/BlendedCost']) if row[
                    'lineItem/BlendedCost'] else 0
                if 'BoxUsage' in row.get('lineItem/UsageType', ''):
                    row['box_usage'] = True
                for k, v in row.copy().items():
                    if v == '':
                        del row[k]
                if row.get('resource_id') is None:
                    res_id = self.compose_resource_id(row)
                    if res_id:
                        row['resource_id'] = res_id
                row['created_at'] = self.import_start_ts
                chunk.append(row)

            if chunk:
                self.update_raw_records(chunk)
        return billing_period, skipped_accounts

    def load_parquet_report(self, report_path, account_id_ca_id_map,
                            billing_period, skipped_accounts):
        dataframe = pq.read_pandas(report_path).to_pandas()
        dataframe.rename(columns=AWS_PARQUET_CSV_MAP, inplace=True)
        for i in range(0, dataframe.shape[0], CHUNK_SIZE):
            expense_chunk = dataframe.iloc[i:i + CHUNK_SIZE, :].to_dict()
            chunk = [{} for _ in range(0, CHUNK_SIZE)]
            skipped_rows = set()
            for field_name, values_dict in expense_chunk.items():
                for n, value in values_dict.items():
                    expense_num = n % CHUNK_SIZE
                    if expense_num in skipped_rows:
                        continue
                    chunk[expense_num]['_rec_n'] = n
                    if hasattr(value, 'timestamp'):
                        value = value.strftime('%Y-%m-%dT%H:%M:%SZ')
                    if (field_name == 'bill/BillingPeriodStartDate' and
                            billing_period is None):
                        billing_period = value
                        LOG.info('detected billing period: %s', billing_period)
                        self.current_billing_period = billing_period
                    elif field_name == 'lineItem/UsageAccountId':
                        cloud_account_id = account_id_ca_id_map.get(value)
                        if cloud_account_id is None:
                            skipped_accounts.add(value)
                            skipped_rows.add(expense_num)
                            continue
                        chunk[expense_num]['cloud_account_id'] = cloud_account_id
                        self.detected_cloud_accounts.add(cloud_account_id)
                    elif field_name == 'lineItem/ResourceId' and value != '':
                        chunk[expense_num]['resource_id'] = value[value.find('/') + 1:]
                    elif field_name == 'lineItem/UsageStartDate':
                        start_date = self._datetime_from_value(value).replace(
                            hour=0, minute=0, second=0)
                        chunk[expense_num]['start_date'] = start_date
                    elif field_name == 'lineItem/UsageEndDate':
                        chunk[expense_num]['end_date'] = self._datetime_from_value(
                            value)
                    elif field_name == 'lineItem/BlendedCost':
                        chunk[expense_num]['cost'] = float(value) if value else 0
                    elif field_name == 'lineItem/UsageType':
                        if 'BoxUsage' in value:
                            chunk[expense_num]['box_usage'] = True
                    if value != '':
                        chunk[expense_num][field_name] = value

            expenses = [x for x in chunk if x and
                        chunk.index(x) not in skipped_rows]
            for expense in expenses:
                expense['created_at'] = self.import_start_ts
                if expense.get('lineItem/ResourceId') is None:
                    expense['resource_id'] = self.compose_resource_id(expense)
            if expenses:
                self.update_raw_records(expenses)
        return billing_period, skipped_accounts

    def generate_clean_records(self, regeneration=False):
        # useless if there is nothing to import
        if not self.report_files and not regeneration:
            return
        billing_periods = {
            None} if not self.billing_periods else self.billing_periods
        for cc_id in self.detected_cloud_accounts:
            for billing_period in billing_periods:
                self.process_items_with_ids(cc_id, billing_period)

    def get_resource_ids(self, cloud_account_id, billing_period=None):
        filters = {
            'cloud_account_id': cloud_account_id,
            'resource_id': {'$exists': True, '$ne': None},
        }
        if billing_period:
            filters['bill/BillingPeriodStartDate'] = billing_period
        resource_ids = self.mongo_raw.aggregate([
            {'$match': filters},
            {'$group': {'_id': '$resource_id'}},
        ], allowDiskUse=True)
        return [x['_id'] for x in resource_ids]

    def collect_tags(self, expense):
        raw_tags = {}

        def _extract_tag_name(tag_key, prefix_symbol):
            prefix_len = tag_key.find(prefix_symbol) + 1
            return tag_key[prefix_len:]

        def _extract_parquet_tag_name(tag_key):
            prefix = 'resource_tags_'
            for prefix_ in tag_prefixes:
                if tag_key.startswith(prefix_):
                    prefix = prefix_
            return tag_key[len(prefix):]

        for k, v in expense.items():
            if (not k.startswith('resourceTags') and
                    not k.startswith('resource_tags')):
                continue
            if k != 'resourceTags/user:Name':
                if k.startswith('resourceTags/aws'):
                    name = _extract_tag_name(k, '/')
                elif k.startswith('resourceTags/'):
                    name = _extract_tag_name(k, ':')
                else:
                    name = _extract_parquet_tag_name(k)
                raw_tags[name] = v
        tags = self.extract_tags(raw_tags)
        return tags

    @staticmethod
    def _datetime_from_expense(expense, key):
        value = expense[key]
        if isinstance(value, str):
            return datetime.strptime(expense[key], '%Y-%m-%dT%H:%M:%SZ'
                                     ).replace(tzinfo=timezone.utc)
        return value.replace(tzinfo=timezone.utc)

    @staticmethod
    def _datetime_from_value(value):
        return datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ'
                                 ).replace(tzinfo=timezone.utc)

    def get_resource_info_from_expenses(self, expenses):
        name = None
        resource_type = None
        region = None
        last_region = None
        service_name = None
        first_seen = datetime.utcnow().replace(tzinfo=timezone.utc)
        tags = {}
        family_region_map = {}
        fake_cad_extras = {}
        last_seen = datetime.fromtimestamp(0).replace(tzinfo=timezone.utc)
        os_type = None
        preinstalled = None

        for e in expenses:
            start_date = self._datetime_from_expense(
                e, 'start_date')
            if start_date and start_date < first_seen:
                first_seen = start_date
            end_date = self._datetime_from_expense(
                e, 'lineItem/UsageEndDate')
            if end_date and end_date > last_seen:
                last_seen = end_date

            product = e.get('lineItem/ProductCode')
            if product and any(k in product.lower() for k in ['aws', 'amazon']):
                service_name = product
            elif service_name is None:
                service_name = e.get('bill/BillingEntity')

            name = e.get('resourceTags/user:Name') or name
            product_family = e.get('product/productFamily')
            tags.update(self.collect_tags(e))
            operation = e.get('lineItem/Operation')
            if operation == self.STORAGE_LENS_TYPE:
                resource_type = self.STORAGE_LENS_TYPE
            elif resource_type not in self.main_resources_product_family_map.keys():
                resource_type = self.get_resource_type(e, resource_type)
            last_region = e.get('product/region')
            fake_cad_extras.update(self._get_fake_cad_extras(e))

            family_value_list = self.main_resources_product_family_map.get(resource_type, [])
            if family_value_list and last_region and product_family:
                for family in family_value_list:
                    if family in product_family:
                        family_region_map[family] = last_region
                        break

            if resource_type == 'Instance' and not os_type and e.get('product/operatingSystem'):
                os_type = e.get('product/operatingSystem')
            if resource_type == 'Instance' and not preinstalled and e.get('product/preInstalledSw'):
                preinstalled = e.get('product/preInstalledSw')

        for product_family_value in self.main_resources_product_family_map.get(resource_type, []):
            family_region = family_region_map.get(product_family_value, None)
            if family_region:
                region = family_region
                break
        if region is None:
            region = last_region
        if last_seen < first_seen:
            last_seen = first_seen
        info = {
            'name': name,
            'type': resource_type,
            'region': region,
            'service_name': service_name,
            'tags': tags,
            'first_seen': int(first_seen.timestamp()),
            'last_seen': int(last_seen.timestamp()),
            **fake_cad_extras
        }
        if os_type:
            info['os'] = os_type
        if preinstalled:
            info['preinstalled'] = preinstalled
        LOG.debug('Detected resource info: %s', info)
        return info

    @staticmethod
    def get_resource_type(raw_expense, resource_type):
        item_type = raw_expense.get('lineItem/LineItemType')
        usage_type = raw_expense.get('lineItem/UsageType')
        operation = raw_expense.get('lineItem/Operation')
        tax_type = raw_expense.get('lineItem/TaxType')
        product = raw_expense.get('lineItem/ProductCode')
        product_family = raw_expense.get('product/productFamily')
        resource_id = raw_expense.get('lineItem/ResourceId')
        ip_address_type = 'IP Address'
        nat_gateway_type = 'NAT Gateway'
        instance_type = 'Instance'
        snapshot_type = 'Snapshot'
        volume_type = 'Volume'
        bucket_type = 'Bucket'

        def extract_type_by_product_type(res_type):
            return product_family and res_type in product_family

        resource_type_map = OrderedDict()
        if tax_type:
            resource_type_map[tax_type] = item_type == 'Tax'
        resource_type_map.update({
            nat_gateway_type: extract_type_by_product_type(nat_gateway_type),
            instance_type: (usage_type and operation and
                            extract_type_by_product_type(instance_type) and (
                                    'BoxUsage' in usage_type or instance_type in
                                    operation)),
            snapshot_type: usage_type and operation and (
                    snapshot_type in usage_type or snapshot_type in operation),
            volume_type: usage_type and volume_type in usage_type,
            'Bucket': product and 'AmazonS3' in product and (
                    bool(resource_id) and bucket_type in operation),
            ip_address_type: extract_type_by_product_type(ip_address_type),
            'Other': (tax_type or resource_type or product_family or
                      usage_type or item_type)
        })
        resource_type_keys = [k for k, v in resource_type_map.items()
                              if v is True]
        return (resource_type_keys[0] if resource_type_keys else
                resource_type_map.get('Other'))

    def clean_expenses_for_resource(self, resource_id, expenses):
        clean_expenses = {}
        for e in expenses:
            start_date = self._datetime_from_expense(
                e, 'start_date')
            end_date = self._datetime_from_expense(
                e, 'lineItem/UsageEndDate')
            # end date may point to the 00:00 on the next day,
            # so to avoid confusion removing one second
            end_date -= timedelta(seconds=1)
            days = (end_date - start_date).days + 1
            for d in range(days):
                date = start_date + timedelta(days=d)
                day = date.replace(hour=0, minute=0, second=0, microsecond=0)
                if day in clean_expenses:
                    clean_expenses[day]['cost'] += float(
                        e['lineItem/BlendedCost']) / days
                else:
                    clean_expenses[day] = {
                        'date': day,
                        'cost': float(e['lineItem/BlendedCost']) / days,
                        'resource_id': resource_id,
                        'cloud_account_id': e['cloud_account_id']
                    }
        return clean_expenses

    def _get_group_by_day_pipeline(self):
        unique_keys = AWSReportImporter.get_unique_field_list(
            include_date=False)
        day_group_id_pipeline = {k: '$%s' % k for k in unique_keys}
        day_group_id_pipeline.update({
            'start_date': {
                'month': {'$month': "$start_date"},
                'day': {'$dayOfMonth': "$start_date"},
                'year': {'$year': "$start_date"},
            },
            'end_date': {
                'month': {'$month': "$end_date"},
                'day': {'$dayOfMonth': "$end_date"},
                'year': {'$year': "$end_date"},
            },
            'resource_id': '$resource_id',
        })
        day_group_pipeline = {
            '_id': day_group_id_pipeline,
            "root": {"$first": "$$ROOT"},
            'raw_data_links': {'$push': '$_id'},
            'resource_id': {'$first': "$resource_id"},
            'lineItem/UsageStartDate': {"$min": "$start_date"},
            'lineItem/UsageEndDate': {"$max": "$end_date"},
            'lineItem/BlendedCost': {'$sum': '$cost'}
        }
        return day_group_pipeline

    def process_items_with_ids(self, cloud_account_id, billing_period):
        resource_ids = self.get_resource_ids(cloud_account_id, billing_period)
        total_count = len(resource_ids)
        LOG.info(
            'Generating clean expenses for %s resources in account %s for %s',
            total_count, cloud_account_id, billing_period)
        progress = 0
        for i in range(0, total_count, CHUNK_SIZE):
            new_progress = round(i / total_count * 100)
            if new_progress != progress:
                progress = new_progress
                LOG.info('Progress: %s', progress)

            filters = [
                {'cloud_account_id': cloud_account_id},
                {'resource_id': {
                    '$in': resource_ids[i:i + CHUNK_SIZE]
                }},
            ]
            if billing_period:
                filters.append(
                    {'bill/BillingPeriodStartDate': billing_period})
            expenses = list(self.mongo_raw.aggregate([
                {'$match': {
                    '$and': filters,
                }},
                {'$group': self._get_group_by_day_pipeline()},
                {'$replaceRoot': {'newRoot': {
                    '$mergeObjects': ["$root", "$$ROOT"]}
                }},
                {'$project': {"root": 0}}
            ], allowDiskUse=True))
            chunk = self.set_raw_chunk(expenses)
            self.save_clean_expenses(cloud_account_id, chunk)

        LOG.info('Finished generating clean expenses for %s resources',
                 total_count)

    @staticmethod
    def set_raw_chunk(expenses):
        chunk = {}
        for ex in expenses:
            resource_id = ex['resource_id']
            if not chunk.get(resource_id):
                chunk[resource_id] = list()
            chunk[resource_id].append(ex)
        return chunk

    def compose_resource_id(self, expense):
        item_type = expense['lineItem/LineItemType']
        if item_type in IGNORE_EXPENSE_TYPES:
            return
        parts = self.ITEM_TYPE_ID_FIELDS.get(item_type)
        if parts:
            resource_id = ' '.join([expense.get(k)
                                    for k in parts if k in expense])
            return resource_id
        else:
            return expense.get('lineItem/LineItemDescription')

    def data_import(self):
        if self.cloud_acc['last_import_at'] == 0 and self.import_file is None:
            # on first auto report import we will load raw data from reports and
            # generate expenses month by month from newest to oldest
            account_id_ca_id_map = self.get_linked_account_map()
            dates = [x for x in self.report_files]
            dates.sort(reverse=True)
            for date in dates:
                reports = self.report_files[date]
                for report in reports:
                    self.load_report(report, account_id_ca_id_map)
                LOG.info('Generating clean records')
                self.generate_clean_records()
                self.billing_periods = set()
        else:
            super().data_import()

    def update_cloud_import_time(self, ts):
        for cloud_acc_id in self.detected_cloud_accounts:
            self.rest_cl.cloud_account_update(
                cloud_acc_id,
                {'last_import_at': ts,
                 'last_import_modified_at': self.last_import_modified_at,
                 'last_import_attempt_at': ts})

    def detect_period_start(self):
        pass

    def update_cloud_import_attempt(self, ts, error=None):
        for cloud_acc_id in self.detected_cloud_accounts:
            self.rest_cl.cloud_account_update(
                cloud_acc_id,
                {'last_import_attempt_at': ts,
                 'last_import_attempt_error': error})

    def _get_cloud_extras(self, info):
        res = defaultdict(dict)
        for k in ['os', 'preinstalled']:
            val = info.get(k)
            if val:
                res['meta'][k] = val
        return res

    def create_traffic_processing_tasks(self):
        self._create_traffic_processing_tasks()
