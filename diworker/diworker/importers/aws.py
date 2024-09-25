#!/usr/bin/env python
import csv
import gzip
import logging
import math
import os
import re
import pyarrow
import shutil
import uuid
import zipfile
import json
from collections import defaultdict, OrderedDict
from datetime import datetime, timedelta, timezone
from functools import cached_property

from diworker.diworker.importers.base import CSVBaseReportImporter

import pyarrow.parquet as pq

LOG = logging.getLogger(__name__)
CHUNK_SIZE = 200
GZIP_ENDING = '.gz'
IGNORE_EXPENSE_TYPES = ['Credit']
RI_PLATFORMS = [
    'Linux/UNIX',
    'Linux with SQL Server Standard',
    'Linux with SQL Server Web',
    'Linux with SQL Server Enterprise',
    'SUSE Linux',
    'Red Hat Enterprise Linux',
    'Red Hat Enterprise Linux with HA',
    'Windows',
    'Windows with SQL Server Standard',
    'Windows with SQL Server Web',
    'Windows with SQL Server Enterprise',
]
SERVICE_TAGS_MAP = {
    'user_name': 'user:Name',
    'aws_cloudformation_stack_id': 'aws:cloudformation:stack-id',
    'aws_cloudformation_logical_id': 'aws:cloudformation:logical-id',
    'aws_cloudformation_stack_name': 'aws:cloudformation:stack-name',
    'aws_created_by': 'aws:createdBy',
}
SERVICE_TAG_PREFIXES = ['aws', 'user', 'cloudformation']
# This map is needed for proper extraction of nested objects
# format: {field_name_prefix: (is_lowercase, [case exceptions])}
AWS_CUR_PREFIX_MAP = {
    'identity': (False, []),
    'bill': (False, []),
    'discount': (False, []),
    'line_item': (False, []),
    'product': (True, ['product_name', 'purchase_option', 'size_flex']),
    'pricing': (True, ['rate_code', 'rate_id', 'purchase_option',
                       'offering_class', 'lease_contract_length']),
    'reservation': (False, []),
    'savings_plan': (False, []),
    'resource_tags': (False, []),
    'cost_category': (False, []),
}


class AWSReportImporter(CSVBaseReportImporter):
    ITEM_TYPE_ID_FIELDS = {
        'Tax': ['lineItem/TaxType', 'product/ProductName'],
        'Usage': ['lineItem/ProductCode', 'lineItem/Operation',
                  'product/region'],
    }
    STORAGE_LENS_TYPE = 'StorageLens'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_resources_product_family_map = {
            'Bucket': ['Storage', 'Data Transfer', 'Fee'],
            'Instance': ['Compute Instance', 'Stopped Instance'],
            'Snapshot': ['Storage Snapshot'],
            'Volume': ['Storage'],
            'Savings Plan': [],
            'Reserved Instances': []
        }
        self.import_start_ts = int(datetime.utcnow().timestamp())
        self.current_billing_period = None

    @cached_property
    def use_edp_discount(self):
        return self.cloud_acc['config'].get('use_edp_discount', False)

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

    @staticmethod
    def to_camel_case(snake_str):
        return "".join(x.capitalize() for x in snake_str.split("_"))

    @staticmethod
    def to_lower_case(snake_str):
        return snake_str[0].lower() + snake_str[1:]

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
            'discount/EdpDiscount',
            'lineItem/BlendedRate',
            'lineItem/BlendedCost',
            'lineItem/UnblendedRate',
            'lineItem/UnblendedCost',
            'lineItem/UsageEndDate',
            'lineItem/UsageAmount',
            'savingsPlan/SavingsPlanEffectiveCost',
            'reservation/EffectiveCost',
            'pricing/publicOnDemandCost',
            'savingPlan/UsedCommitment',
            'savingsPlan/SavingsPlanRate',
            'reservation/UnusedQuantity',
            'reservation/UnusedRecurringFee',
            'reservation/UnusedAmortizedUpfrontFeeForBillingPeriod',
            'reservation/AmortizedUpfrontFeeForBillingPeriod',
            'end_date',
            'cost',
            'report_identity',
            '_rec_n'
        ]

    def get_current_reports(self, reports_groups, last_import_modified_at):
        current_reports = defaultdict(list)
        reports_count = 0
        for date, reports in reports_groups.items():
            for report in reports:
                if report.get('LastModified', -1) > last_import_modified_at:
                    # use all reports for month
                    current_reports[date].extend(reports)
                    reports_count += len(reports)
                    break
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

    @staticmethod
    def _is_flavor_usage(expense):
        usage_type = expense.get('lineItem/UsageType', '')
        service_code = expense.get('product/servicecode', '')
        description = expense.get('lineItem/LineItemDescription', '')
        item_type = expense.get('lineItem/LineItemType', '')
        return (
            (service_code == 'AmazonECS' and 'Fargate' in usage_type) or
            (service_code == 'AmazonSageMaker' and (
                'ml.' in description or item_type == 'SavingsPlanNegation')) or
            (service_code == 'AWSLambda' and 'Lambda-GB-Second' in usage_type) or
            ('BoxUsage' in usage_type)
        )

    def _set_resource_id(self, expense):
        if (expense.get('resource_id') is None or (
                # move SavingsPlanCoveredUsage expenses from applied
                # resource to 'Savings Plan' resource
                expense.get(
                    'lineItem/LineItemType') == 'SavingsPlanCoveredUsage' and
                expense.get('savingsPlan/SavingsPlanARN'))):
            res_id = self.compose_resource_id(expense)
            if res_id:
                expense['resource_id'] = res_id

    def _to_csv_tag(self, prefix, tag, root=True):
        if root and tag in SERVICE_TAGS_MAP:
            return f'{prefix}{SERVICE_TAGS_MAP[tag]}'
        subprefix = next((
            s for s in SERVICE_TAG_PREFIXES if tag.startswith(s)
        ), None)
        if not subprefix:
            return f'{prefix}{tag}'
        subkey = f'{tag[len(subprefix) + 1:]}'
        return self._to_csv_tag(f'{prefix}{subprefix}:', subkey, False)

    def _get_legacy_csv_key(self, old_key):
        key = next((
            s for s in AWS_CUR_PREFIX_MAP.keys() if old_key.startswith(f'{s}_')
        ), None)
        if not key:
            return old_key
        prefix = self.to_lower_case(self.to_camel_case(key))
        subkey = old_key[len(key) + 1:]
        if not subkey:
            return prefix
        if key == 'resource_tags':
            return self._to_csv_tag(f'{prefix}/', subkey)
        else:
            to_lower, exceptions = AWS_CUR_PREFIX_MAP[key]
            new_key = self.to_camel_case(subkey)
            if subkey in exceptions:
                to_lower = not to_lower
            if to_lower:
                new_key = self.to_lower_case(new_key)
        return f'{prefix}/{new_key}'

    def _extract_nested_objects(self, obj, parquet=False):
        updates = defaultdict(dict)
        removed_keys = set()
        # extract nested objects
        for k in AWS_CUR_PREFIX_MAP.keys():
            values = obj.get(k)
            if not values:
                continue
            if parquet:
                for n, vals in values.items():
                    if isinstance(vals, list):
                        for postfix, value in vals:
                            snake_key = f'{k}_{postfix}'
                            csv_key = self._get_legacy_csv_key(snake_key)
                            updates[csv_key][n] = value
                        removed_keys.add(k)
            else:
                try:
                    nested_objects = json.loads(values)
                except Exception:
                    continue
                for new_key, new_value in nested_objects.items():
                    snake_key = f'{k}_{new_key}'
                    csv_key = self._get_legacy_csv_key(snake_key)
                    updates[csv_key] = new_value
                removed_keys.add(k)
        for k in removed_keys:
            obj.pop(k)
        obj.update(updates)
        return obj

    def _convert_to_legacy_csv_columns(self, columns, dict_format=False):
        if not dict_format:
            return [self._get_legacy_csv_key(col) for col in columns]
        return {col: self._get_legacy_csv_key(col) for col in columns}

    def load_csv_report(self, report_path, account_id_ca_id_map,
                        billing_period, skipped_accounts):
        date_start = datetime.utcnow()
        with open(report_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            reader.fieldnames = self._convert_to_legacy_csv_columns(
                reader.fieldnames)
            chunk = []
            record_number = 0
            for row in reader:
                row = self._extract_nested_objects(row)
                if billing_period is None:
                    billing_period = row['bill/BillingPeriodStartDate']
                    LOG.info('detected billing period: %s', billing_period)
                    self.current_billing_period = billing_period

                if len(chunk) == CHUNK_SIZE:
                    self.update_raw_records(chunk)
                    chunk = []
                    now = datetime.utcnow()
                    if (now - date_start).total_seconds() > 60:
                        LOG.info('report %s: processed %s rows',
                                 report_path, record_number)
                        date_start = now

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
                # RIFee is created once a month and is updated every day
                if (start_date < self.min_date_import_threshold and
                        row['lineItem/LineItemType'] != 'RIFee'):
                    continue
                row['start_date'] = start_date
                row['end_date'] = self._datetime_from_expense(
                    row, 'lineItem/UsageEndDate')
                row['cost'] = float(row['lineItem/BlendedCost']) if row[
                    'lineItem/BlendedCost'] else 0
                if self.use_edp_discount:
                    row['cost'] += float(row.get('discount/EdpDiscount') or 0)
                if self._is_flavor_usage(row):
                    row['box_usage'] = True
                for k, v in row.copy().items():
                    if v == '':
                        del row[k]
                self._set_resource_id(row)
                row['created_at'] = self.import_start_ts
                chunk.append(row)

            if chunk:
                self.update_raw_records(chunk)
        return billing_period, skipped_accounts

    def load_parquet_report(self, report_path, account_id_ca_id_map,
                            billing_period, skipped_accounts):
        date_start = datetime.utcnow()
        dataframe = pq.read_pandas(report_path).to_pandas()
        new_columns = self._convert_to_legacy_csv_columns(
            dataframe.columns, dict_format=True)
        dataframe.rename(columns=new_columns, inplace=True)
        for i in range(0, dataframe.shape[0], CHUNK_SIZE):
            expense_chunk = self._extract_nested_objects(
                dataframe.iloc[i:i + CHUNK_SIZE, :].to_dict(), parquet=True)
            chunk = [{'cost': 0} for _ in range(0, CHUNK_SIZE)]
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
                    elif field_name == 'lineItem/ResourceId' and value:
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
                    elif (self.use_edp_discount and
                          field_name == 'discount/EdpDiscount' and value):
                        chunk[expense_num]['cost'] += float(value)
                    elif field_name == 'lineItem/UsageType':
                        if 'BoxUsage' in value:
                            chunk[expense_num]['box_usage'] = True
                    if isinstance(value, float) and math.isnan(value):
                        value = 0
                    if value:
                        chunk[expense_num][field_name] = value

            expenses = [x for x in chunk if x and
                        chunk.index(x) not in skipped_rows and
                        x['cloud_account_id'] is not None and
                        # RIFee is created once a month and is updated every day
                        (x['start_date'] >= self.min_date_import_threshold or
                         x['lineItem/LineItemType'] == 'RIFee')]
            for expense in expenses:
                expense['created_at'] = self.import_start_ts
                if self._is_flavor_usage(expense):
                    expense['box_usage'] = True
                self._set_resource_id(expense)
            if expenses:
                self.update_raw_records(expenses)
                now = datetime.utcnow()
                if (now - date_start).total_seconds() > 60:
                    LOG.info('report %s: processed %s rows', report_path, i)
                    date_start = now
        return billing_period, skipped_accounts

    def collect_tags(self, expense):
        raw_tags = {}

        def _extract_tag_name(tag_key, prefix_symbol):
            prefix_len = tag_key.find(prefix_symbol) + 1
            return tag_key[prefix_len:]

        for k, v in expense.items():
            if (not k.startswith('resourceTags') and
                    not k.startswith('resource_tags')):
                continue
            if k != 'resourceTags/user:Name':
                if k.startswith('resourceTags/aws'):
                    name = _extract_tag_name(k, '/')
                else:
                    name = _extract_tag_name(k, ':')
                raw_tags[name] = v
        tags = self.extract_tags(raw_tags)
        return tags

    @staticmethod
    def _datetime_from_expense(expense, key):
        value = expense[key]
        if isinstance(value, str):
            return AWSReportImporter._datetime_from_value(expense[key])
        return value.replace(tzinfo=timezone.utc)

    @staticmethod
    def _datetime_from_value(value):
        dt_format = '%Y-%m-%dT%H:%M:%SZ'
        if re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z", value):
            dt_format = '%Y-%m-%dT%H:%M:%S.%fZ'
        return datetime.strptime(value, dt_format).replace(tzinfo=timezone.utc)

    def get_resource_info_from_expenses(self, expenses, resource_type=None):
        name = None
        resource_type = resource_type
        region = None
        last_region = None
        service_name = None
        first_seen = datetime.now(tz=timezone.utc)
        tags = {}
        family_region_map = {}
        fake_cad_extras = {}
        meta_dict = {}
        last_seen = datetime.fromtimestamp(0).replace(tzinfo=timezone.utc)
        os_type = None
        preinstalled = None
        payment_option = None
        offering_type = None
        purchase_term = None
        applied_region = None
        start = None
        end = None
        instance_type = None
        platform = None
        zone = None

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

            family_value_list = self.main_resources_product_family_map.get(
                resource_type, [])
            if family_value_list and last_region and product_family:
                for family in family_value_list:
                    if family in product_family:
                        family_region_map[family] = last_region
                        break

            if resource_type == 'Instance':
                if not os_type and 'product/operatingSystem' in e:
                    os_type = e['product/operatingSystem']
                    meta_dict['os'] = os_type
                if not preinstalled and 'product/preInstalledSw' in e:
                    preinstalled = e['product/preInstalledSw']
                    meta_dict['preinstalled'] = preinstalled
            elif resource_type == 'Savings Plan':
                if not payment_option and 'savingsPlan/PaymentOption' in e:
                    payment_option = e['savingsPlan/PaymentOption']
                    meta_dict['payment_option'] = payment_option
                if not offering_type and 'savingsPlan/OfferingType' in e:
                    offering_type = e['savingsPlan/OfferingType']
                    meta_dict['offering_type'] = offering_type
                if not purchase_term and 'savingsPlan/PurchaseTerm' in e:
                    purchase_term = e['savingsPlan/PurchaseTerm']
                    meta_dict['purchase_term'] = purchase_term
                if not applied_region and 'savingsPlan/Region' in e:
                    applied_region = e['savingsPlan/Region']
                    meta_dict['applied_region'] = applied_region
                if not start and 'savingsPlan/StartTime' in e:
                    try:
                        start = int(self._datetime_from_value(
                            e['savingsPlan/StartTime']).timestamp())
                        meta_dict['start'] = start
                    except (TypeError, ValueError):
                        pass
                if not end and 'savingsPlan/EndTime' in e:
                    try:
                        end = int(self._datetime_from_value(
                            e['savingsPlan/EndTime']).timestamp())
                        meta_dict['end'] = end
                    except (TypeError, ValueError):
                        pass
            elif resource_type == 'Reserved Instances':
                if not payment_option and 'pricing/PurchaseOption' in e:
                    payment_option = e['pricing/PurchaseOption']
                    meta_dict['payment_option'] = payment_option
                if not offering_type and 'pricing/OfferingClass' in e:
                    offering_type = e['pricing/OfferingClass']
                    meta_dict['offering_type'] = offering_type
                if not purchase_term and 'pricing/LeaseContractLength' in e:
                    purchase_term = e['pricing/LeaseContractLength']
                    meta_dict['purchase_term'] = purchase_term
                if not start and 'reservation/StartTime' in e:
                    try:
                        start = int(self._datetime_from_value(
                            e['reservation/StartTime']).timestamp())
                        meta_dict['start'] = start
                    except (TypeError, ValueError):
                        pass
                if not end and 'reservation/EndTime' in e:
                    try:
                        end = int(self._datetime_from_value(
                            e['reservation/EndTime']).timestamp())
                        meta_dict['end'] = end
                    except (TypeError, ValueError):
                        pass
                if not instance_type and 'lineItem/UsageType' in e:
                    instance_type = e['lineItem/UsageType'].split(
                        ':')[-1]
                    meta_dict['instance_type'] = instance_type
                if not platform and 'lineItem/LineItemDescription' in e:
                    platform = e['lineItem/LineItemDescription']
                    for ri_platform in RI_PLATFORMS:
                        if ri_platform in platform:
                            meta_dict['platform'] = ri_platform
                            break
                if not zone and 'reservation/AvailabilityZone' in e:
                    zone = e['reservation/AvailabilityZone']
                    meta_dict['instance_type'] = zone
        for product_family_value in self.main_resources_product_family_map.get(
                resource_type, []):
            family_region = family_region_map.get(product_family_value, None)
            if family_region:
                region = family_region
                break
        if region is None:
            region = last_region
        if last_seen < first_seen:
            last_seen = first_seen

        if resource_type in ['Reserved Instances', 'Savings Plan']:
            name = None
            tags = {}

        info = {
            'name': name,
            'type': resource_type,
            'region': region,
            'service_name': service_name,
            'tags': tags,
            'first_seen': int(first_seen.timestamp()),
            'last_seen': int(last_seen.timestamp()),
            **fake_cad_extras,
            **meta_dict
        }
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
        ri_id = raw_expense.get('reservation/ReservationARN')
        sp_id = raw_expense.get('savingsPlan/SavingsPlanARN')
        ip_address_type = 'IP Address'
        nat_gateway_type = 'NAT Gateway'
        instance_type = 'Instance'
        snapshot_type = 'Snapshot'
        volume_type = 'Volume'
        bucket_type = 'Bucket'
        sp_type = 'Savings Plan'
        ri_type = 'Reserved Instances'

        def extract_type_by_product_type(res_type):
            return product_family and res_type in product_family

        def extract_data_transfer():
            return (resource_id and 'natgateway' not in resource_id and
                    product_family and 'Data Transfer' in product_family)

        resource_type_map = OrderedDict()
        if tax_type:
            resource_type_map[tax_type] = item_type == 'Tax'
        resource_type_map.update({
            nat_gateway_type: extract_type_by_product_type(nat_gateway_type),
            instance_type: (usage_type and operation and
                            'SavingsPlan' not in item_type and
                            (extract_type_by_product_type(instance_type) or
                             extract_data_transfer()) and
                            ('BoxUsage' in usage_type or instance_type in
                             operation)),
            snapshot_type: usage_type and operation and (
                    snapshot_type in usage_type or snapshot_type in operation),
            volume_type: usage_type and volume_type in usage_type,
            'Bucket': product and 'AmazonS3' in product and (
                    bool(resource_id) and bucket_type in operation),
            ip_address_type: extract_type_by_product_type(ip_address_type),
            sp_type: bool(sp_id) and 'SavingsPlan' in item_type,
            ri_type: bool(ri_id),
            'Other': (tax_type or resource_type or product_family or
                      usage_type or item_type)
        })
        resource_type_keys = [k for k, v in resource_type_map.items()
                              if v is True]
        return (resource_type_keys[0] if resource_type_keys else
                resource_type_map.get('Other'))

    def get_resource_info_map(self, chunk):
        regular_res_info_map = {}
        sp_covered_chunk = defaultdict(list)
        for r_id, expenses in chunk.items():
            # collect regular resources infos
            regular_res_info_map[r_id] = self.get_resource_info_from_expenses(
                expenses)

            # collect instances covered by SP info map to create them due to
            # these instances may not have own raw expenses as their expenses
            # are related to SP resource
            for exp in expenses:
                if exp['lineItem/LineItemType'] == 'SavingsPlanCoveredUsage':
                    sp_covered_chunk[exp['lineItem/ResourceId']].append(exp)

        # use predefined resource type to avoid detecting SP fields
        info_map = {
            r_id: self.get_resource_info_from_expenses(
                expenses, resource_type='Instance')
            for r_id, expenses in sp_covered_chunk.items()
        }
        info_map.update(regular_res_info_map)
        return info_map

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

    @staticmethod
    def _get_group_by_day_pipeline():
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
            'resource_id': {'$first': "$resource_id"},
            'lineItem/UsageStartDate': {"$min": "$start_date"},
            'lineItem/UsageEndDate': {"$max": "$end_date"},
            'lineItem/BlendedCost': {'$sum': '$cost'}
        }
        return day_group_pipeline

    def get_resource_ids(self, cloud_account_id, billing_period):
        filters = {
            'cloud_account_id': cloud_account_id,
            'resource_id': {'$exists': True, '$ne': None},
            'start_date': {'$gte': self.min_date_import_threshold}
        }
        if billing_period:
            filters['bill/BillingPeriodStartDate'] = billing_period
        resource_ids = self.mongo_raw.aggregate([
            {'$match': filters},
            {'$group': {'_id': '$resource_id'}},
        ], allowDiskUse=True)
        return [x['_id'] for x in resource_ids]

    def get_raw_expenses_by_filters(self, filters):
        return self.mongo_raw.aggregate([
                {'$match': {
                    '$and': filters,
                }},
                {'$group': self._get_group_by_day_pipeline()},
                {'$replaceRoot': {'newRoot': {
                    '$mergeObjects': ["$root", "$$ROOT"]}
                }},
                {'$project': {"root": 0}}
            ], allowDiskUse=True)

    def _get_billing_period_filters(self, billing_period):
        return {
            'bill/BillingPeriodStartDate': billing_period,
            'start_date': {'$gte': self.min_date_import_threshold}
        }

    @staticmethod
    def set_raw_chunk(expenses):
        chunk = defaultdict(list)
        for ex in expenses:
            resource_id = ex['resource_id']
            chunk[resource_id].append(ex)
        return chunk

    def compose_resource_id(self, expense):
        item_type = expense['lineItem/LineItemType']
        sp_id = expense.get('savingsPlan/SavingsPlanARN')
        ri_id = expense.get('reservation/ReservationARN')
        if item_type in IGNORE_EXPENSE_TYPES:
            return
        elif 'SavingsPlan' in item_type and sp_id:
            return sp_id[sp_id.find('/') + 1:]
        elif ri_id:
            return ri_id[ri_id.find('/') + 1:]
        parts = self.ITEM_TYPE_ID_FIELDS.get(item_type)
        if parts:
            resource_id = ' '.join([expense.get(k)
                                    for k in parts if k in expense])
            return resource_id
        else:
            return expense.get('lineItem/LineItemDescription')

    def _get_cloud_extras(self, info):
        res = defaultdict(dict)
        for k in ['os', 'preinstalled', 'payment_option', 'offering_type',
                  'purchase_term', 'applied_region', 'start', 'end', 'platform',
                  'instance_type', 'zone']:
            val = info.get(k)
            if val:
                res['meta'][k] = val
        return res

    def create_traffic_processing_tasks(self):
        self._create_traffic_processing_tasks()

    def create_risp_processing_tasks(self):
        self._create_risp_processing_tasks()
