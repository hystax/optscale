import re
import os
import csv
import logging
import pyarrow
import pyarrow.parquet as pq
from decimal import Decimal
from collections import defaultdict
from datetime import datetime, timezone
from gzip import BadGzipFile
from diworker.diworker.importers.base import CSVBaseReportImporter
from diworker.diworker.importers.azure import AzureImporterBase

LOG = logging.getLogger(__name__)
CHUNK_SIZE = 200


class AzureExportImporter(CSVBaseReportImporter, AzureImporterBase):

    def unpack_report(self, report_file, date):
        dest_dir = self.get_new_report_path(date)
        os.makedirs(dest_dir, exist_ok=True)
        try:
            new_report_path = self.gunzip_report(report_file, dest_dir)
        except BadGzipFile:
            return report_file
        if new_report_path:
            os.remove(report_file)
            return new_report_path
        else:
            return report_file

    def get_current_reports(self, reports_groups, previous_states):
        current_reports = defaultdict(list)
        for date, reports in reports_groups.items():
            if any(self._etag_changed(r, previous_states) for r in reports):
                LOG.info('Group selected (etag changed): %s', date)
                current_reports[date].extend(reports)
            else:
                LOG.info('Group skipped (etag unchanged): %s', date)
        total = sum(len(r) for r in current_reports.values())
        total_checked = sum(len(r) for r in reports_groups.values())
        LOG.info('Selected %d/%d files for import', total, total_checked)
        return current_reports

    def unpack_report_files(self):
        for date, reports in self.report_files.items():
            new_reports = []
            for old_path in reports:
                new_path = self.unpack_report(old_path, date)
                if new_path != old_path and old_path in self.report_file_keys:
                    self.report_file_keys[new_path] = self.report_file_keys.pop(
                        old_path)
                new_reports.append(new_path)
            self.report_files[date] = new_reports

    def load_report(self, report_path, *_args, report_key=None):
        LOG.info('loading report %s', report_path)

        try:
            skipped_accounts = self.load_parquet_report(
                report_path, report_key=report_key)
        except pyarrow.lib.ArrowInvalid as exc:
            LOG.warning(
                f"Could not open source file as Parquet {report_path}: "
                f"{str(exc)}. Will try to open it as CSV")
            skipped_accounts = self.load_csv_report(
                report_path, report_key=report_key)

        if len(skipped_accounts) > 0:
            LOG.warning('Import skipped for the following subscriptions: %s',
                        skipped_accounts)

    def _get_legacy_key(self, key):
        return re.sub("(.)([A-Z]+)", r"\1_\2", key).lower()

    @staticmethod
    def _detect_billing_period(report_path):
        billing_period = report_path.split('/')[-2]
        LOG.info('detected billing period: %s', billing_period)

    def _convert_to_legacy_csv_columns(self, columns, dict_format=False):
        if not dict_format:
            return [self._get_legacy_key(col) for col in columns]
        return {col: self._get_legacy_key(col) for col in columns}

    def load_csv_report(self, report_path, report_key=None):
        date_start = datetime.now(tz=timezone.utc)
        subscription_id = self.cloud_acc['account_id']
        skipped_accounts = set()
        self._detect_billing_period(report_path)
        with open(report_path, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            reader.fieldnames = self._convert_to_legacy_csv_columns(
                reader.fieldnames)
            chunk = []
            record_number = 0
            for row in reader:
                row_subscription_id = row.get('subscription_id') or row.get(
                    'subscription_guid')
                if (row_subscription_id and
                        row_subscription_id != subscription_id):
                    skipped_accounts.add(subscription_id)
                    continue
                exp_date = row.get('usage_date_time')
                if exp_date:
                    usage_datetime = datetime.strptime(exp_date, '%Y-%m-%d')
                else:
                    usage_datetime = datetime.strptime(row['date'], '%m/%d/%Y')
                usage_datetime_utc = usage_datetime.replace(tzinfo=timezone.utc)
                if usage_datetime_utc < self.min_date_import_threshold:
                    continue
                record_number += 1
                row['_rec_n'] = record_number
                row['kind'] = 'export'
                self._fill_custom_fields(row)
                self._clean_tree(row)
                if report_key is not None:
                    row['report_key'] = report_key
                chunk.append(row)

                if len(chunk) == CHUNK_SIZE:
                    self.update_raw_records(chunk)
                    chunk = []
                    now = datetime.now(tz=timezone.utc)
                    if (now - date_start).total_seconds() > 60:
                        LOG.info('report %s: processed %s rows',
                                 report_path, record_number)
                        date_start = now
            if chunk:
                self.update_raw_records(chunk)
        return skipped_accounts

    def load_parquet_report(self, report_path, report_key=None):
        date_start = datetime.now(tz=timezone.utc)
        skipped_accounts = set()
        subscription_id = self.cloud_acc['account_id']
        dataframe = pq.read_pandas(report_path).to_pandas()
        new_columns = self._convert_to_legacy_csv_columns(
            dataframe.columns, dict_format=True)
        dataframe.rename(columns=new_columns, inplace=True)
        self._detect_billing_period(report_path)
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
                    if (field_name == 'subscription_id' or
                            field_name == 'subscription_guid'):
                        if value != subscription_id:
                            skipped_accounts.add(value)
                            skipped_rows.add(expense_num)
                            continue
                    elif field_name == 'usage_date_time':
                        if value.to_pydatetime().replace(
                                tzinfo=timezone.utc) < self.min_date_import_threshold:
                            skipped_rows.add(expense_num)
                            continue
                        # to suit to csv usage_date_time format
                        value = value.strftime('%Y-%m-%d')
                    elif field_name == 'date':
                        if value.to_pydatetime().replace(
                                tzinfo=timezone.utc) < self.min_date_import_threshold:
                            skipped_rows.add(expense_num)
                            continue
                        # to suit to csv usage_date_time format
                        value = value.strftime('%m/%d/%Y')
                    if value is not None:
                        if isinstance(value, Decimal):
                            value = float(value)
                        chunk[expense_num][field_name] = value
            expenses = [x for x in chunk if x and
                        chunk.index(x) not in skipped_rows]
            for expense in expenses:
                expense['kind'] = 'export'
                self._fill_custom_fields(expense)
                if report_key is not None:
                    expense['report_key'] = report_key
            if expenses:
                self.update_raw_records(expenses)
                now = datetime.now(tz=timezone.utc)
                if (now - date_start).total_seconds() > 60:
                    LOG.info('report %s: processed %s rows', report_path, i)
                    date_start = now
        return skipped_accounts

    def get_resource_ids(self, cloud_account_id, period_start):
        return super(AzureImporterBase, self).get_resource_ids(
            cloud_account_id, period_start)

    def finalize_raw_import(self, report_key=None, is_last=True):
        super().finalize_raw_import(report_key, is_last)
        if is_last:
            try:
                self.generate_reservations_expenses(
                    self.min_date_import_threshold)
            except Exception as exc:
                LOG.exception("Failed getting reservations info: %s", str(exc))

    def generate_clean_records(self, regeneration=False):
        resource_ids = self.get_resource_ids(self.cloud_acc_id,
                                             self.min_date_import_threshold)
        self._generate_clean_records(resource_ids, self.cloud_acc_id,
                                     self.min_date_import_threshold)
