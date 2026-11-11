import csv
import hashlib
import io
import logging
import math
import time
import zipfile
from collections import defaultdict
from datetime import date, datetime, time as dt_time, timedelta, timezone
from decimal import Decimal

import pyarrow as pa
import pyarrow.csv as pa_csv
import pyarrow.parquet as pq
from diworker.diworker.importers.base import CSVBaseReportImporter
import tools.optscale_time as opttime
from tools.cloud_adapter.clouds.focus import (
    CURRENCY_COLUMN, RowNormalizer, RowParseError, detect_format,
    effective_mapping)

LOG = logging.getLogger(__name__)

PARQUET_BATCH_SIZE = 5000
CSV_BLOCK_SIZE = 8 * 1024 * 1024
INSERT_CHUNK_SIZE = 1000
RESOURCE_CHUNK_SIZE = 200
# rows starting this long before a window may still overlap its days
# (monthly charges); they are read when clean expenses are regenerated
MAX_ROW_LENGTH = timedelta(days=32)
MIN_ROW_LENGTH = timedelta(seconds=1)
GZIP_MAGIC = b'\x1f\x8b'
PARQUET_MAGIC = b'PAR1'
# a local file header, or the end of central directory of an empty archive
ZIP_MAGICS = (b'PK\x03\x04', b'PK\x05\x06')
# identities of the groups of one import differ by this step
IDENTITY_STEP = 0.001
DOT_REPLACEMENT = '．'
DOLLAR_REPLACEMENT = '＄'
RAW_PROJECTION = {
    'resource_id': 1, 'cloud_account_id': 1, 'start_date': 1,
    'end_date': 1, 'cost': 1, 'resource_type': 1, 'name': 1, 'region': 1,
    'service_name': 1, 'tags': 1,
}


class FocusImportError(Exception):
    pass


def escape_key(key):
    key = str(key)
    if key.startswith('$'):
        key = DOLLAR_REPLACEMENT + key[1:]
    return key.replace('.', DOT_REPLACEMENT)


def unescape_key(key):
    if key.startswith(DOLLAR_REPLACEMENT):
        key = '$' + key[1:]
    return key.replace(DOT_REPLACEMENT, '.')


def to_bson(value):
    """Convert a value read by pyarrow to something MongoDB can store."""
    if isinstance(value, dict):
        return {escape_key(k): to_bson(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_bson(v) for v in value]
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, dt_time())
    if isinstance(value, (dt_time, timedelta)):
        return str(value)
    if isinstance(value, bytes):
        return value.decode('utf-8', errors='replace')
    return value


def day_end(dt):
    """First midnight at or after dt."""
    start = opttime.startday(dt)
    return start if start == dt else start + timedelta(days=1)


def split_by_days(start, end, cost):
    """Split cost over the days of [start, end) in proportion to time."""
    if end <= start:
        return {opttime.startday(start): cost}
    total = (end - start).total_seconds()
    result = {}
    day = opttime.startday(start)
    while day < end:
        next_day = day + timedelta(days=1)
        overlap = (min(end, next_day) - max(start, day)).total_seconds()
        if overlap > 0:
            result[day] = cost * overlap / total
        day = next_day
    return result


class FocusReportImporter(CSVBaseReportImporter):
    """Imports FOCUS files uploaded manually or found in S3-compatible
    storage.
    A unit of import is a group of files: one uploaded file, or the files of
    one parent directory in the bucket.
    """

    def __init__(self, *args, **kwargs):
        self._cloud_acc_cache = None
        self._org_currency = None
        self._clean_days = None
        super().__init__(*args, **kwargs)
        self._file_keys = {}

    @property
    def cloud_acc(self):
        if self._cloud_acc_cache is None:
            self._cloud_acc_cache = super().cloud_acc
        return self._cloud_acc_cache

    @property
    def config(self):
        return self.cloud_acc.get('config') or {}

    @property
    def org_currency(self):
        if self._org_currency is None:
            _, organization = self.rest_cl.organization_get(
                self.cloud_acc['organization_id'])
            self._org_currency = organization.get('currency') or 'USD'
        return self._org_currency

    @property
    def _is_upload_only(self):
        return not self.config.get('bucket_name')

    @property
    def _is_targeted_import(self):
        if self._is_upload_only:
            return self.import_file is None
        if self.import_file is not None:
            return True
        return super()._is_targeted_import

    # ---- file selection ----

    @staticmethod
    def _group_etag(files):
        """Combined ETag of a group: changes when a file of the group is
        changed, added or removed."""
        files_etags = sorted('%s:%s' % (
            f['Key'], CSVBaseReportImporter._get_file_etag(f)) for f in files)
        return hashlib.sha1('\n'.join(files_etags).encode()).hexdigest()

    @staticmethod
    def _last_modified(files):
        return max((f['LastModified'].timestamp() for f in files
                    if f.get('LastModified')), default=None)

    def _min_group_modified_ts(self):
        if self.import_from is not None:
            return self.import_from
        return opttime.utctimestamp(self._reimport_period_start)

    def get_files_to_process(self):
        """Return the files of changed groups, oldest group first, so the
        rows of a newer export replace the rows of an older one. The state of
        a group is saved in report_import_files under the group key."""
        if self._is_upload_only:
            LOG.info('Cloud account %s has no bucket, nothing to import',
                     self.cloud_acc_id)
            return []
        groups = self.cloud_adapter.get_report_files()
        previous_states = self.get_previous_file_states()
        import_all = (self.reimport or self.import_from is not None or
                      self.import_to is not None)
        min_modified = self._min_group_modified_ts()
        result = []
        selected = 0
        for group_key, files in sorted(
                groups.items(), key=lambda g: self._last_modified(g[1]) or 0):
            last_modified = self._last_modified(files)
            if last_modified is not None and last_modified < min_modified:
                LOG.info('Group %s skipped: changed before %s', group_key,
                         opttime.utcfromtimestamp(min_modified))
                continue
            etag = self._group_etag(files)
            stored_etag = previous_states.get(group_key, {}).get('etag', '')
            if not import_all and etag == stored_etag:
                LOG.info('Group %s skipped: no file changes', group_key)
                continue
            identity = self.report_identity + selected * IDENTITY_STEP
            selected += 1
            files = sorted(files, key=lambda f: f['Key'])
            for i, f in enumerate(files):
                result.append({
                    'date': group_key,
                    'report': {
                        'Key': f['Key'],
                        'ETag': self._get_file_etag(f),
                        'group': group_key,
                        'group_etag': etag,
                        'identity': identity,
                        'last_in_group': i == len(files) - 1,
                    },
                    'stored_etag': stored_etag,
                })
        LOG.info('Selected %s of %s groups for import', selected,
                 len(groups))
        return result

    def prepare_one_file(self, date, report):
        # all files of a group share the identity set by the orchestrator
        self.report_identity = report['identity']
        path = self.get_new_report_path()
        with open(path, 'wb') as f_report:
            self.cloud_adapter.download_report_file(report['Key'], f_report)
        self._file_keys[path] = report['Key']
        if report['last_in_group']:
            # the raw worker calls _clear_file_rudiments with this key and
            # passes its state to the clean task
            self.report_file_keys[path] = report['group']
            self.report_cloud_etags[report['group']] = report['group_etag']
        return path

    # ---- import ----

    def load_report(self, report_path, account_id_ca_id_map,
                    report_key=None):
        file_key = self._file_keys.get(report_path, self.import_file)
        LOG.info('Importing %s, report identity %s', file_key,
                 self.report_identity)
        if self.import_file is None:
            # a redelivered task loads the file again
            self.delete_raw_expenses({
                'cloud_account_id': self.cloud_acc_id,
                'report_identity': self.report_identity,
                'report_key': file_key,
            })
        try:
            self._load_file(report_path, file_key)
        except Exception:
            self._rollback()
            raise

    def _iter_batches(self, path):
        """Yield (columns, rows) batches of a CSV, CSV.gz, zipped CSV or
        Parquet file."""
        with open(path, 'rb') as f:
            magic = f.read(4)
        if magic.startswith(PARQUET_MAGIC):
            parquet_file = pq.ParquetFile(path)
            columns = parquet_file.schema_arrow.names
            for batch in parquet_file.iter_batches(
                    batch_size=PARQUET_BATCH_SIZE):
                yield columns, batch.to_pylist()
            return
        if magic.startswith(ZIP_MAGICS):
            with zipfile.ZipFile(path) as archive:
                member = self._zip_csv_member(archive)
                yield from self._iter_csv_batches(
                    lambda: archive.open(member))
            return
        compression = 'gzip' if magic.startswith(GZIP_MAGIC) else None
        yield from self._iter_csv_batches(
            lambda: pa.input_stream(path, compression=compression))

    @staticmethod
    def _zip_csv_member(archive):
        """The only file of a zip archive, which must be a plain CSV like
        in AWS exports."""
        members = [m for m in archive.infolist() if not m.is_dir() and
                   not m.filename.startswith('__MACOSX/')]
        if len(members) != 1:
            raise FocusImportError(
                'zip archive must contain one report file, found %s' %
                len(members))
        with archive.open(members[0]) as f:
            magic = f.read(4)
        if magic.startswith((PARQUET_MAGIC, GZIP_MAGIC) + ZIP_MAGICS):
            raise FocusImportError(
                'zip archive must contain a CSV file, found %s' %
                members[0].filename)
        return members[0]

    @staticmethod
    def _iter_csv_batches(open_stream):
        """open_stream returns a new binary stream of the CSV on each call:
        the header is read first, then the whole file by pyarrow."""
        with io.TextIOWrapper(open_stream(), encoding='utf-8-sig',
                              newline='') as f:
            columns = next(csv.reader(f), None)
        if not columns:
            return
        convert_options = pa_csv.ConvertOptions(
            column_types={c: pa.string() for c in columns},
            strings_can_be_null=False)
        read_options = pa_csv.ReadOptions(block_size=CSV_BLOCK_SIZE)
        # quoted values may contain line breaks (descriptions, JSON tags)
        parse_options = pa_csv.ParseOptions(newlines_in_values=True)
        with open_stream() as stream:
            reader = pa_csv.open_csv(stream, read_options=read_options,
                                     parse_options=parse_options,
                                     convert_options=convert_options)
            for batch in reader:
                yield columns, batch.to_pylist()

    def _in_import_range(self, start_date):
        if self.import_file is not None:
            return True
        if (self.import_from is not None and
                start_date < opttime.utcfromtimestamp(self.import_from)):
            return False
        if (self.import_to is not None and
                start_date >= opttime.utcfromtimestamp(self.import_to)):
            return False
        return True

    def _load_file(self, path, report_key):
        LOG.info('Loading %s', report_key)
        normalizer = None
        fmt = None
        has_currency = False
        currency_unchecked = 0
        rec_n = 0
        loaded = 0
        now_ts = int(time.time())
        for columns, rows in self._iter_batches(path):
            if normalizer is None:
                fmt = detect_format(columns)
                mapping = effective_mapping(fmt, self.config.get('mapping'))
                try:
                    normalizer = RowNormalizer(mapping, columns)
                except Exception as exc:
                    raise FocusImportError(
                        '%s: %s' % (report_key, exc)) from exc
                has_currency = CURRENCY_COLUMN in columns
                if not has_currency:
                    LOG.warning('%s: no %s column, currency is not checked',
                                report_key, CURRENCY_COLUMN)
                LOG.info('%s: detected format %s', report_key, fmt)
            docs = []
            for row in rows:
                rec_n += 1
                try:
                    normalized = normalizer.normalize(row)
                except RowParseError as exc:
                    raise FocusImportError('%s: row %s: %s' % (
                        report_key, rec_n, exc)) from exc
                if has_currency and normalizer.cost_in_billing_currency:
                    self._check_currency(row, report_key, rec_n)
                elif has_currency:
                    # the currency of other cost columns is unknown
                    currency_unchecked += 1
                if not self._in_import_range(normalized['start_date']):
                    continue
                normalized['tags'] = {escape_key(k): v for k, v in
                                      normalized['tags'].items()}
                normalized.update({
                    'cloud_account_id': self.cloud_acc_id,
                    'report_identity': self.report_identity,
                    'report_key': report_key,
                    '_rec_n': rec_n,
                    'focus_format': fmt,
                    'created_at': now_ts,
                    'source': to_bson(row),
                })
                docs.append(normalized)
                self._extend_window(normalized)
            self._insert(docs)
            loaded += len(docs)
        if normalizer is not None:
            for warning in normalizer.collect_warnings():
                LOG.warning('%s: %s', report_key, warning)
        if currency_unchecked:
            LOG.warning('%s: currency of %s rows is not checked: their cost '
                        'is taken from a column of unknown currency',
                        report_key, currency_unchecked)
        LOG.info('%s: %s of %s rows loaded', report_key, loaded, rec_n)

    def _check_currency(self, row, report_key, rec_n):
        currency = row.get(CURRENCY_COLUMN)
        if currency is None or not str(currency).strip():
            return
        if str(currency).strip().upper() != self.org_currency.upper():
            raise FocusImportError(
                '%s: row %s: %s %s does not match organization currency %s'
                % (report_key, rec_n, CURRENCY_COLUMN, currency,
                   self.org_currency))

    def _extend_window(self, row):
        # unlike other importers, end_date is the max ChargePeriodEnd: the
        # window must cover the last day of the imported rows
        window = self.imported_raw_dates_map[self.cloud_acc_id]
        end_date = max(row['end_date'], row['start_date'] + MIN_ROW_LENGTH)
        if not window:
            window.update(start_date=row['start_date'], end_date=end_date)
            return
        window['start_date'] = min(window['start_date'], row['start_date'])
        window['end_date'] = max(window['end_date'], end_date)

    def _insert(self, docs):
        for i in range(0, len(docs), INSERT_CHUNK_SIZE):
            self.mongo_raw.insert_many(docs[i:i + INSERT_CHUNK_SIZE])

    def clear_rudiments(self):
        # an upload replaces its window here
        if self.import_file is not None:
            self._replace_window()

    def _clear_file_rudiments(self, report_key):
        # called with the group key after the last file of a group: rows of
        # the group replace older raw expenses in its window, not only the
        # rows of its files
        self._replace_window()

    def _raw_window(self, **filters):
        """[min start_date, max end_date] of the account's raw expenses
        matching filters, or None if there are none."""
        windows = list(self.mongo_raw.aggregate([
            {'$match': dict(filters, cloud_account_id=self.cloud_acc_id)},
            {'$group': {'_id': None, 'start': {'$min': '$start_date'},
                        'max_start_date': {'$max': '$start_date'},
                        'end': {'$max': '$end_date'}}},
        ]))
        if not windows or windows[0]['start'] is None:
            return None
        window = windows[0]
        return window['start'], max(window['end'],
                                    window['max_start_date'] + MIN_ROW_LENGTH)

    def _replace_window(self):
        window = self._raw_window(report_identity=self.report_identity)
        if not window:
            LOG.info('No rows imported, raw expenses are not replaced')
            return
        start, end = window
        deleted = self.delete_raw_expenses({
            'cloud_account_id': self.cloud_acc_id,
            'start_date': {'$gte': start, '$lt': end},
            'report_identity': {'$lt': self.report_identity},
        })
        LOG.info('Replaced window [%s, %s): %s old raw expenses deleted',
                 start, end, deleted)

    def _rollback(self):
        # the rows of the whole group go: it is imported again next time
        self.imported_raw_dates_map.pop(self.cloud_acc_id, None)
        deleted = self.delete_raw_expenses({
            'cloud_account_id': self.cloud_acc_id,
            'report_identity': self.report_identity,
        })
        LOG.info('Rolled back %s raw expenses of report identity %s',
                 deleted, self.report_identity)

    # ---- clean expenses ----

    def generate_clean_records(self, regeneration=False):
        window = self.imported_raw_dates_map.get(self.cloud_acc_id)
        if window:
            start, end = window['start_date'], window['end_date']
        elif regeneration:
            # the regenerator drops all clean expenses of the account and
            # has no imported window: rebuild them from all raw expenses
            window = self._raw_window()
            if not window:
                LOG.info('No raw expenses, nothing to regenerate')
                return
            start, end = window
        else:
            LOG.info('No rows imported, nothing to generate')
            return
        self._generate_clean_for_window(start, end)

    def _generate_clean_for_window(self, start, end):
        first_day, last_day = opttime.startday(start), day_end(end)
        if last_day <= first_day:
            last_day = first_day + timedelta(days=1)
        self._clean_days = (first_day, last_day)
        overlap_filter = {
            'cloud_account_id': self.cloud_acc_id,
            'start_date': {'$gte': first_day - MAX_ROW_LENGTH,
                           '$lt': last_day},
            '$or': [{'end_date': {'$gt': first_day}},
                    {'start_date': {'$gte': first_day}}],
        }
        resource_ids = [r['_id'] for r in self.mongo_raw.aggregate([
            {'$match': overlap_filter},
            {'$group': {'_id': '$resource_id'}},
        ], allowDiskUse=True)]
        LOG.info('Generating clean expenses for %s resources, days [%s, %s)',
                 len(resource_ids), first_day, last_day)
        for i in range(0, len(resource_ids), RESOURCE_CHUNK_SIZE):
            chunk_ids = resource_ids[i:i + RESOURCE_CHUNK_SIZE]
            chunk = defaultdict(list)
            for expense in self.mongo_raw.find(
                    dict(overlap_filter, resource_id={'$in': chunk_ids}),
                    RAW_PROJECTION):
                chunk[expense['resource_id']].append(expense)
            if chunk:
                self.save_clean_expenses(self.cloud_acc_id, chunk)

    def clean_expenses_for_resource(self, resource_id, expenses):
        first_day, last_day = self._clean_days
        clean_expenses = {}
        for e in expenses:
            for day, cost in split_by_days(e['start_date'], e['end_date'],
                                           e['cost']).items():
                if not first_day <= day < last_day:
                    continue
                day = day.replace(tzinfo=timezone.utc)
                if day in clean_expenses:
                    clean_expenses[day]['cost'] += cost
                else:
                    clean_expenses[day] = {
                        'date': day,
                        'cost': cost,
                        'resource_id': resource_id,
                        'cloud_account_id': e['cloud_account_id'],
                    }
        return clean_expenses

    def get_resource_info_from_expenses(self, expenses):
        expenses = sorted(expenses, key=lambda e: e['start_date'])
        info = {'name': None, 'type': None, 'region': None,
                'service_name': None, 'tags': {}}
        for e in expenses:
            for key, field in (('name', 'name'), ('type', 'resource_type'),
                               ('region', 'region'),
                               ('service_name', 'service_name')):
                if e.get(field):
                    info[key] = e[field]
            info['tags'].update({unescape_key(k): v
                                 for k, v in (e.get('tags') or {}).items()})
        info['first_seen'] = opttime.utctimestamp(min(
            e['start_date'] for e in expenses))
        info['last_seen'] = opttime.utctimestamp(max(
            e['end_date'] for e in expenses))
        return info
