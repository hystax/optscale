import logging
import time
import os
import requests
import shutil
import uuid
from functools import cached_property

from collections import defaultdict
from pymongo import UpdateOne
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta
import boto3
from boto3.session import Config as BotoConfig
from tools.cloud_adapter.cloud import Cloud as CloudAdapter
from diworker.diworker.utils import retry_mongo_upsert, get_month_start

LOG = logging.getLogger(__name__)
CHUNK_SIZE = 200
CSV_REWRITE_DAYS = 5
REPORTS_PATH_PREFIX = 'reports'


class BaseReportImporter:
    def __init__(self, cloud_account_id, rest_cl, config_cl, mongo_raw,
                 mongo_resources, clickhouse_cl, import_file=None,
                 recalculate=False, detect_period_start=True):
        self.cloud_acc_id = cloud_account_id
        self.rest_cl = rest_cl
        self.config_cl = config_cl
        self.mongo_raw = mongo_raw
        self.mongo_resources = mongo_resources
        self.clickhouse_cl = clickhouse_cl
        self.import_file = import_file
        self._cloud_adapter = None
        self._mongo = None
        self._s3_client = None
        self.recalculate = recalculate
        self.period_start = None
        if detect_period_start:
            self.detect_period_start()
        self.imported_raw_dates_map = defaultdict(dict)
        self.report_identity = datetime.utcnow().timestamp()

    @property
    def cloud_acc(self):
        _, cloud = self.rest_cl.cloud_account_get(self.cloud_acc_id)
        return cloud

    @property
    def cloud_adapter(self):
        if self._cloud_adapter is None:
            cloud_acc = self.cloud_acc.copy()
            cloud_acc.update(self.cloud_acc['config'])
            self._cloud_adapter = CloudAdapter.get_adapter(cloud_acc)
            _, organization = self.rest_cl.organization_get(
                cloud_acc['organization_id'])
            self._cloud_adapter.set_currency(
                organization.get('currency', 'USD'))
        return self._cloud_adapter

    @property
    def s3_client(self):
        if self._s3_client is None:
            s3_params = self.config_cl.read_branch('/minio')
            self._s3_client = boto3.client(
                's3',
                endpoint_url='http://{}:{}'.format(
                    s3_params['host'], s3_params['port']),
                aws_access_key_id=s3_params['access'],
                aws_secret_access_key=s3_params['secret'],
                config=BotoConfig(s3={'addressing_style': 'path'})
            )
        return self._s3_client

    def prepare(self):
        pass

    def load_raw_data(self):
        raise NotImplementedError

    def get_update_fields(self):
        raise NotImplementedError

    @property
    def need_extend_report_interval(self):
        # decided not to consider the beginning of the month because we always
        # take a period of at least three months in the case of the first report
        if self.cloud_acc['last_import_at'] != 0:
            return False
        return True

    def get_raw_upsert_filters(self, expense):
        return {f: expense.get(f, {'$exists': False})
                for f in self.get_unique_field_list()}

    def update_raw_records(self, chunk):
        update_fields = self.get_update_fields()
        upsert_bulk = []
        for e in chunk:
            self._update_imported_raw_interval(e)
            upsert_bulk.append(UpdateOne(
                filter=self.get_raw_upsert_filters(e),
                update={
                    '$set': {k: e[k] for k in update_fields if k in e},
                    '$setOnInsert': {k: v for k, v in e.items()
                                     if k not in update_fields},
                },
                upsert=True,
            ))
        r = retry_mongo_upsert(self.mongo_raw.bulk_write, upsert_bulk)
        LOG.debug('updated: %s', r.bulk_api_result)

    @staticmethod
    def _get_fake_cad_extras(expense):
        res = {}
        for k in ['image_id']:
            val = expense.get(k)
            if val:
                res[k] = val
        return res

    def _get_cloud_extras(self, info):
        return {}

    def get_resource_data(self, r_id, info,
                          unique_id_field='cloud_resource_id'):
        return {
            unique_id_field: r_id,
            'resource_type': info['type'],
            'name': info['name'],
            'tags': info['tags'],
            'region': info['region'],
            'service_name': info.get('service_name'),
            'first_seen': info['first_seen'],
            'last_seen': info['last_seen'],
            **self._get_fake_cad_extras(info),
            **self._get_cloud_extras(info)
        }

    def create_resources_if_not_exist(self, cloud_account_id,
                                      resources_info_map,
                                      unique_id_field='cloud_resource_id'):
        resources_data = [
            self.get_resource_data(r_id, info, unique_id_field=unique_id_field)
            for r_id, info in resources_info_map.items()
        ]
        _, result = self.rest_cl.cloud_resource_create_bulk(
            cloud_account_id, {'resources': resources_data},
            behavior='skip_existing', return_resources=True,
            is_report_import=True)
        return result['resources']

    def get_resource_info_from_expenses(self, expenses):
        raise NotImplementedError

    def clean_expenses_for_resource(self, resource_id, expenses):
        clean_expenses = {}
        for e in expenses:
            usage_date = e['start_date'].replace(
                hour=0, minute=0, second=0, microsecond=0)
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

    @staticmethod
    def gen_clickhouse_expense(expense, new_cost=None):
        expense = {
            'cloud_account_id': expense['cloud_account_id'],
            'resource_id': expense['resource_id'],
            'date': expense['date'],
            'cost': expense['cost'],
            'sign': 1
        }
        if new_cost is not None:
            expense.update({
                'cost': new_cost,
                'sign': -1
            })
        return expense

    def get_clickhouse_expenses(self, from_dt, to_dt, resource_ids,
                                cloud_account_id):
        return self.clickhouse_cl.execute("""
            SELECT resource_id, date, cost, sign
            FROM expenses
            WHERE cloud_account_id = %(cloud_account_id)s
                AND date >= %(from_dt)s
                AND date <= %(to_dt)s
                AND resource_id in %(resource_ids)s
        """, params={
            'cloud_account_id': cloud_account_id,
            'from_dt': from_dt,
            'to_dt': to_dt,
            'resource_ids': list(resource_ids)
        })

    def save_clean_expenses(self, cloud_account_id, chunk,
                            unique_id_field='resource_id'):
        info_map = {
            r_id: self.get_resource_info_from_expenses(expenses)
            for r_id, expenses in chunk.items()
        }
        cloud_unique_id_field = 'cloud_%s' % unique_id_field

        resources_map = {
            r[cloud_unique_id_field]: r
            for r in self.create_resources_if_not_exist(
                cloud_account_id, info_map,
                unique_id_field=cloud_unique_id_field)
        }

        clean_expenses = []
        last_expense_info = {}
        max_date, min_date = None, None
        for r_id, expenses in chunk.items():
            resource_id = resources_map[r_id]['id']
            clean_expenses_map = self.clean_expenses_for_resource(
                resource_id, expenses)
            min_resource_date = min(clean_expenses_map.keys(), default=None)
            max_resource_date = max(clean_expenses_map.keys(), default=None)
            last_expense_cost = clean_expenses_map[max_resource_date]['cost']
            last_expense_info[resource_id] = (max_resource_date,
                                              last_expense_cost)
            if not min_date or min_resource_date < min_date:
                min_date = min_resource_date
            if not max_date or max_resource_date > max_date:
                max_date = max_resource_date
            clean_expenses.extend(clean_expenses_map.values())
        resource_ids = last_expense_info.keys()
        if resource_ids:
            existing_expenses = self.get_clickhouse_expenses(
                min_date, max_date, resource_ids, cloud_account_id)
            resource_id_date_cost_map = defaultdict(dict)
            for resource_id, date, clickhouse_cost, sign in existing_expenses:
                if not resource_id_date_cost_map[resource_id].get(date):
                    resource_id_date_cost_map[resource_id][date] = list()
                resource_id_date_cost_map[resource_id][date].append(
                    (clickhouse_cost, sign))
            clickhouse_expenses = []
            for expense in clean_expenses:
                expense_date = expense['date'].replace(tzinfo=None)
                clickhouse_expense = resource_id_date_cost_map[
                    expense['resource_id']].get(expense_date)
                if not clickhouse_expense:
                    clickhouse_expenses.append(
                        self.gen_clickhouse_expense(expense))
                    continue
                exists = sum([x for _, x in clickhouse_expense])
                if exists:
                    cost = sum([x * s for x, s in clickhouse_expense])
                    if cost != expense['cost']:
                        clickhouse_expenses.extend([
                            self.gen_clickhouse_expense(expense, cost),
                            self.gen_clickhouse_expense(expense)
                        ])
                else:
                    clickhouse_expenses.append(
                        self.gen_clickhouse_expense(expense))
            if clickhouse_expenses:
                self.update_clickhouse_expenses(clickhouse_expenses)
                self.update_resource_expense_info(cloud_account_id,
                                                  last_expense_info)

    def update_resource_expense_info(self, cloud_account_id,
                                     last_expense_info):
        resource_info = self.get_common_resource_expense_info(
            cloud_account_id, last_expense_info.keys())
        bulk = []
        for r_id, info in resource_info.items():
            max_date, total_cost = info
            last_expense_date, last_expense_cost = last_expense_info[r_id]
            updates = {
                'total_cost': total_cost
            }
            if last_expense_date.replace(tzinfo=None) >= max_date:
                updates['last_expense'] = {
                    'date': int(last_expense_date.timestamp()),
                    'cost': last_expense_cost
                }
            bulk.append(
                UpdateOne(
                    filter={
                        'cloud_account_id': cloud_account_id,
                        '_id': r_id
                    },
                    update={'$set': updates}
                )
            )
        if bulk:
            r = retry_mongo_upsert(self.mongo_resources.bulk_write, bulk)
            LOG.debug(
                'Updated resources with expense info: %s' % r.bulk_api_result)

    def get_common_resource_expense_info(self, cloud_account_id, resource_ids):
        info = self.clickhouse_cl.execute("""
            SELECT resource_id, max(date), sum(cost*sign)
            FROM expenses
            WHERE cloud_account_id = %(cloud_account_id)s
                AND resource_id IN resource_ids
            GROUP BY resource_id
        """, params={
            'cloud_account_id': cloud_account_id,
        }, external_tables=[
            {
                'name': 'resource_ids',
                'structure': [('id', 'String')],
                'data': [{'id': r_id} for r_id in resource_ids]
            }
        ])
        return {r[0]: (r[1], r[2]) for r in info}

    def get_resource_ids(self, cloud_account_id, period_start):
        base_filters = {'cloud_account_id': cloud_account_id}
        if period_start:
            base_filters['start_date'] = {'$gte': period_start}
        resource_ids = self.mongo_raw.aggregate([
            {'$match': base_filters},
            {'$group': {'_id': '$resource_id'}}
        ], allowDiskUse=True)
        return [x['_id'] for x in resource_ids]

    @staticmethod
    def set_raw_chunk(expenses):
        chunk = defaultdict(list)
        for ex in expenses:
            resource_id = ex['_id']['resource_id']
            chunk[resource_id].extend(ex['expenses'])
        return chunk

    @staticmethod
    def _get_additional_expenses_groupings():
        return

    def get_raw_expenses_by_filters(self, filters):
        grp_stage = {
            'resource_id': '$resource_id',
            'dt': '$start_date',
        }
        additional = self._get_additional_expenses_groupings()
        if additional:
            grp_stage.update(additional)
        return self.mongo_raw.aggregate([
                {'$match': {
                    '$and': filters,
                }},
                {'$group': {
                    '_id': grp_stage,
                    'expenses': {'$push': '$$ROOT'}
                }},
            ], allowDiskUse=True)

    def _get_billing_period_filters(self, period_start):
        return {'start_date': {'$gte': period_start}}

    def _generate_clean_records(self, resource_ids, cloud_account_id,
                                period_start):
        resource_count = len(resource_ids)
        LOG.info(
            'Generating clean expenses for %s resources in account %s for %s',
            resource_count, cloud_account_id, period_start)
        progress = 0
        for i in range(0, resource_count, CHUNK_SIZE):
            new_progress = round(i / resource_count * 100)
            if new_progress != progress:
                progress = new_progress
                LOG.info('Progress: %s', progress)

            filters = [
                {'cloud_account_id': cloud_account_id},
                self._get_billing_period_filters(period_start),
                {'resource_id': {
                    '$in': resource_ids[i:i + CHUNK_SIZE]}}]
            expenses = self.get_raw_expenses_by_filters(filters)
            chunk = self.set_raw_chunk(expenses)
            self.save_clean_expenses(cloud_account_id, chunk)

        LOG.info('Finished generating clean expenses for %s resources',
                 resource_count)

    def generate_clean_records(self, regeneration=False):
        resource_ids = self.get_resource_ids(self.cloud_acc_id,
                                             self.period_start)
        self._generate_clean_records(resource_ids, self.cloud_acc_id,
                                     self.period_start)

    def cleanup(self):
        pass

    def get_unique_field_list(self):
        raise NotImplementedError

    def recalculate_raw_expenses(self):
        raise NotImplementedError

    def process_alerts(self):
        self.rest_cl.alert_process(self.cloud_acc['organization_id'])

    def data_import(self):
        if self.recalculate:
            LOG.info('Recalculating raw expenses')
            self.recalculate_raw_expenses()
            # need to re-create clean expenses based on updated raw data
            regeneration = True
        else:
            LOG.info('Importing raw data')
            self.load_raw_data()
            regeneration = False
        LOG.info('Generating clean records')
        self.generate_clean_records(regeneration=regeneration)

    def import_report(self):
        LOG.info('Started import for %s', self.cloud_acc_id)
        self.prepare()
        try:
            self.data_import()
        finally:
            LOG.info('Cleanup')
            self.cleanup()

        LOG.info('Updating import time')
        self.update_cloud_import_time(int(time.time()))
        LOG.info('Import completed')

        LOG.info('Processing alerts')
        self.process_alerts()

        LOG.info('Creating traffic processing tasks')
        self.create_traffic_processing_tasks()

        LOG.info('Creating risp processing tasks')
        self.create_risp_processing_tasks()

        LOG.info('Processing completed')

    def update_clickhouse_expenses(self, expenses):
        self.clickhouse_cl.execute('INSERT INTO expenses VALUES', expenses)

    def update_cloud_import_time(self, ts):
        self.rest_cl.cloud_account_update(self.cloud_acc_id,
                                          {'last_import_at': ts,
                                           'last_import_attempt_at': ts})

    def update_cloud_import_attempt(self, ts, error=None):
        self.rest_cl.cloud_account_update(self.cloud_acc_id,
                                          {'last_import_attempt_at': ts,
                                           'last_import_attempt_error': error})

    @staticmethod
    def extract_tags(raw_tags):
        tags = {}

        def extract_tag(tag_name, value):
            if isinstance(value, dict):
                for key, val in value.items():
                    extract_tag("%s.%s" % (tag_name, key), val)
            elif isinstance(value, list):
                for index, val in enumerate(value):
                    extract_tag("%s.%s" % (tag_name, index), val)
            else:
                tags[tag_name] = value

        for k, v in raw_tags.items():
            extract_tag(k, v)
        return tags

    def detect_period_start(self):
        ca_last_import_at = self.cloud_acc.get('last_import_at')
        if (ca_last_import_at and
                datetime.utcfromtimestamp(
                    ca_last_import_at).month == datetime.utcnow().month):
            last_import_at = self.get_last_import_date(self.cloud_acc_id)
            # someone cleared expenses collection
            if not last_import_at:
                last_import_at = datetime.utcfromtimestamp(
                    self.cloud_acc['last_import_at'])
            if last_import_at.day == 1:
                self.period_start = get_month_start(
                    last_import_at - timedelta(days=1))
            else:
                self.period_start = last_import_at
        elif ca_last_import_at:
            self.period_start = datetime.utcfromtimestamp(
                self.cloud_acc['last_import_at'])
            self.remove_raw_expenses_from_period_start(self.cloud_acc_id)

        if self.period_start is None:
            self.set_period_start()

    def set_period_start(self):
        if self.need_extend_report_interval:
            this_month_start = datetime.utcnow().replace(
                day=1, hour=0, minute=0, second=0, microsecond=0)
            self.period_start = this_month_start - relativedelta(months=+3)
        else:
            self.period_start = get_month_start(datetime.utcnow())

    def get_last_import_date(self, cloud_account_id, tzinfo=None):
        max_dt = self.clickhouse_cl.execute(
            'SELECT max(date), count(date) from expenses '
            'WHERE cloud_account_id=%(ca_id)s',
            params={'ca_id': cloud_account_id})
        result, count = 0, 0
        for dt in max_dt:
            m_dt, count = dt
            result = m_dt if count else 0
        if result and tzinfo:
            result = result.replace(tzinfo=tzinfo)
        return result

    def remove_raw_expenses_from_period_start(self, cloud_account_id):
        query = {
            'start_date': {'$gte': self.period_start},
            'cloud_account_id': cloud_account_id
        }
        r = self.mongo_raw.delete_many(query)
        LOG.info('Raw expenses for cloud account %s since %s were '
                 'deleted: %s' % (
                    cloud_account_id, self.period_start, r.raw_result))

    def create_traffic_processing_tasks(self):
        return

    def _create_traffic_processing_tasks(self):
        for cloud_account_id, dates in self.imported_raw_dates_map.items():
            body = {
                'start_date': int(dates.get('start_date').timestamp()),
                'end_date': int(dates.get('end_date').timestamp())
            }
            try:
                self.rest_cl.traffic_processing_task_create(cloud_account_id,
                                                            body)
            except requests.exceptions.HTTPError as exc:
                if exc.response.status_code != 409:
                    raise
                LOG.info('Traffic processing task %s already exists '
                         'for cloud account %s' % (body, cloud_account_id))

    def create_risp_processing_tasks(self):
        return

    def _create_risp_processing_tasks(self):
        for cloud_account_id, dates in self.imported_raw_dates_map.items():
            body = {
                'start_date': int(dates.get('start_date').timestamp()),
                'end_date': int(dates.get('end_date').timestamp())
            }
            try:
                self.rest_cl.risp_processing_task_create(cloud_account_id,
                                                         body)
            except requests.exceptions.HTTPError as exc:
                if exc.response.status_code != 409:
                    raise
                LOG.info('Risp processing task %s already exists '
                         'for cloud account %s' % (body, cloud_account_id))

    def _update_imported_raw_interval(self, expense):
        cloud_account_id = expense['cloud_account_id']
        start_date = expense['start_date']
        cl_acc_dates = self.imported_raw_dates_map[cloud_account_id]
        raw_first_dt = cl_acc_dates.get('start_date')
        raw_last_date = cl_acc_dates.get('end_date')
        last_start_date = cl_acc_dates.get('last_start_date')
        if not raw_first_dt or raw_first_dt > start_date:
            cl_acc_dates['start_date'] = start_date
        if not raw_last_date or raw_last_date < start_date:
            cl_acc_dates['end_date'] = start_date
        if not last_start_date or last_start_date < start_date:
            cl_acc_dates['last_start_date'] = start_date

    def clear_rudiments(self):
        for cloud_account_id, dates in self.imported_raw_dates_map.items():
            result = self.mongo_raw.delete_many({
                'cloud_account_id': cloud_account_id,
                'start_date': {
                    '$gte': dates.get('start_date'),
                    '$lte': dates.get('last_start_date')
                },
                'report_identity': {'$ne': self.report_identity}
            })
            LOG.info('Cleared %s rudiments for cloud_account %s' %
                     (result.deleted_count, cloud_account_id))


class CSVBaseReportImporter(BaseReportImporter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.billing_periods = set()
        self.detected_cloud_accounts = set()
        self.detected_cloud_accounts.add(self.cloud_acc_id)
        self.reports_dir = f'{REPORTS_PATH_PREFIX}/{uuid.uuid4()}'
        os.makedirs(self.reports_dir)
        self.report_files = defaultdict(list)
        self.last_import_modified_at = self.cloud_acc.get(
            'last_import_modified_at', 0)

    @cached_property
    def min_date_import_threshold(self) -> datetime:
        last_import_dt = datetime.fromtimestamp(
            self.cloud_acc.get('last_import_modified_at', 0), tz=timezone.utc)
        return last_import_dt.replace(
            hour=0, minute=0, second=0, microsecond=0
        ) - timedelta(days=CSV_REWRITE_DAYS)

    def detect_period_start(self):
        pass

    def get_new_report_path(self, date=''):
        return os.path.join(self.reports_dir, date, str(uuid.uuid4()))

    def download_from_object_store(self):
        bucket, filename = self.import_file.split('/')
        self.report_files['reports'] = [self.get_new_report_path()]
        with open(self.report_files['reports'][0], 'wb') as f_report:
            self.s3_client.download_fileobj(bucket, filename, f_report)

    def get_current_reports(self, reports_groups, last_import_modified_at):
        raise NotImplementedError

    def download_from_cloud(self):
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
            current_reports = self.get_current_reports(
                reports_groups, last_import_modified_at)

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

    def unpack_report_files(self):
        pass

    def load_report(self, report_path, account_id_ca_id_ma):
        raise NotImplementedError

    def prepare(self):
        if self.import_file is not None:
            self.download_from_object_store()
        else:
            self.download_from_cloud()
        self.unpack_report_files()

    def get_linked_account_map(self):
        return {self.cloud_acc['account_id']: self.cloud_acc_id}

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

    def load_raw_data(self):
        account_id_ca_id_map = {self.cloud_acc['account_id']: self.cloud_acc_id}
        report_files = []
        for r in self.report_files.values():
            report_files.extend(r)
        for report_path in report_files:
            self.load_report(report_path, account_id_ca_id_map)
        self.clear_rudiments()

    def get_resource_ids(self, cloud_account_id, billing_period):
        raise NotImplementedError

    def generate_clean_records(self, regeneration=False):
        # useless if there is nothing to import
        if not self.report_files and not regeneration:
            return
        billing_periods = {
            None} if not self.billing_periods else self.billing_periods
        for cc_id in self.detected_cloud_accounts:
            for billing_period in sorted(billing_periods, reverse=True):
                resource_ids = self.get_resource_ids(cc_id, billing_period)
                self._generate_clean_records(resource_ids, cc_id, billing_period)

    def cleanup(self):
        shutil.rmtree(self.reports_dir, ignore_errors=True)
        if self.import_file:
            bucket, filename = self.import_file.split('/')
            self.s3_client.delete_object(Bucket=bucket, Key=filename)

    def update_cloud_import_attempt(self, ts, error=None):
        for cloud_acc_id in self.detected_cloud_accounts:
            self.rest_cl.cloud_account_update(
                cloud_acc_id,
                {'last_import_attempt_at': ts,
                 'last_import_attempt_error': error})

    def update_cloud_import_time(self, ts):
        for cloud_acc_id in self.detected_cloud_accounts:
            self.rest_cl.cloud_account_update(
                cloud_acc_id,
                {'last_import_at': ts,
                 'last_import_modified_at': self.last_import_modified_at,
                 'last_import_attempt_at': ts})
