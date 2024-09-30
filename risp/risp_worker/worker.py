from collections import defaultdict
from datetime import datetime, timezone, timedelta
from threading import Thread

import os
import re
import time
import logging
import urllib3

from etcd import Lock as EtcdLock
from clickhouse_driver import Client as ClickHouseClient
from pymongo import MongoClient
from kombu import Connection, Exchange, Queue
from kombu.mixins import ConsumerMixin
from kombu.utils.debug import setup_logging
from optscale_client.config_client.client import Client as ConfigClient
from optscale_client.rest_api_client.client_v2 import Client as RestClient
from risp.risp_worker.migrator import Migrator


LOG = logging.getLogger(__name__)
CH_DB_NAME = 'risp'
CHUNK_SIZE = 200
HRS_IN_DAY = 24
SECONDS_IN_HOUR = 3600
SECONDS_IN_DAY = 86400
QUEUE_NAME = 'risp-task'
EXCHANGE_NAME = 'risp-tasks'
TASK_EXCHANGE = Exchange(EXCHANGE_NAME, type='direct')
TASK_QUEUE = Queue(QUEUE_NAME, TASK_EXCHANGE, routing_key=QUEUE_NAME)


class RISPWorker(ConsumerMixin):
    def __init__(self, connection, config_client):
        self.connection = connection
        self.running = True
        self.config_client = config_client
        self._mongo_client = None
        self._clickhouse_client = None
        self._rest_cl = None
        self.thread = Thread(target=self.heartbeat)
        self.thread.start()

    @property
    def rest_cl(self):
        if self._rest_cl is None:
            self._rest_cl = RestClient(
                url=self.config_client.restapi_url(),
                secret=self.config_client.cluster_secret(),
                verify=False)
        return self._rest_cl

    @property
    def mongo_client(self):
        if self._mongo_client is None:
            mongo_params = self.config_client.mongo_params()
            mongo_conn_string = "mongodb://%s:%s@%s:%s" % mongo_params[:-1]
            self._mongo_client = MongoClient(mongo_conn_string)
        return self._mongo_client

    @property
    def clickhouse_client(self):
        if self._clickhouse_client is None:
            user, password, host, _ = self.config_client.clickhouse_params()
            self._clickhouse_client = ClickHouseClient(
                host=host, password=password, database=CH_DB_NAME, user=user)
        return self._clickhouse_client

    @staticmethod
    def _datetime_from_value(value):
        dt_format = '%Y-%m-%dT%H:%M:%SZ'
        if re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z", value):
            dt_format = '%Y-%m-%dT%H:%M:%S.%fZ'
        return datetime.strptime(value, dt_format).replace(tzinfo=timezone.utc)

    def get_consumers(self, consumer, channel):
        return [consumer(queues=[TASK_QUEUE], accept=['json'],
                         callbacks=[self.process_task], prefetch_count=10)]

    def get_ri_sp_usage_expenses(self, cloud_account_id, resource_ids,
                                 offer_type, start_date, end_date):
        return self.clickhouse_client.execute(
            """SELECT resource_id, date, instance_type, offer_id,
                    any(ri_norm_factor), any(sp_rate),
                    any(expected_cost), sum(offer_cost * sign),
                    sum(on_demand_cost * sign), sum(usage * sign)
                FROM ri_sp_usage
                WHERE cloud_account_id = %(cloud_account_id)s
                    AND offer_type = %(offer_type)s
                    AND date >= %(start_date)s
                    AND date <= %(end_date)s
                    AND resource_id in %(resource_ids)s
                GROUP BY resource_id, date, instance_type, offer_id
                HAVING sum(sign) > 0""",
            params={
                'cloud_account_id': cloud_account_id,
                'start_date': start_date,
                'end_date': end_date,
                'offer_type': offer_type,
                'resource_ids': resource_ids
            })

    def insert_clickhouse_expenses(self, expenses, table='ri_sp_usage'):
        self.clickhouse_client.execute(
            f'INSERT INTO {table} VALUES', expenses)

    @staticmethod
    def inverse_dict(d):
        return {v: k for k, v in d.items()}

    @staticmethod
    def get_expenses_pipeline(offer_type, cloud_account_id, start_date,
                              end_date):
        offer_type_line_item_filter_map = {
            'ri': 'DiscountedUsage',
            'sp': 'SavingsPlanCoveredUsage'
        }
        offer_type_id_field_map = {
            'ri': '$reservation/ReservationARN',
            'sp': '$savingsPlan/SavingsPlanARN'
        }
        offer_type_offer_cost_map = {
            'ri': '$reservation/EffectiveCost',
            'sp': '$savingsPlan/SavingsPlanEffectiveCost'
        }
        if offer_type not in offer_type_id_field_map:
            raise Exception(f'Unknown offer type: {offer_type}')

        return [
            {
                '$match': {
                    'cloud_account_id': cloud_account_id,
                    'start_date': {'$gte': start_date, '$lte': end_date},
                    'box_usage': True,
                    'lineItem/LineItemType': offer_type_line_item_filter_map[
                        offer_type],
                }
            },
            {
                '$group': {
                    '_id': {
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
                        'cloud_resource_id': '$lineItem/ResourceId',
                        'cloud_offer_id': offer_type_id_field_map[offer_type],
                        'instance_type': '$product/instanceType',
                        'description': '$lineItem/LineItemDescription'
                    },
                    'usage_hours': {'$push': {
                        '$cond': [{'$eq': ['$pricing/unit', 'Second']},
                                  0, '$lineItem/UsageAmount']}},
                    'usage_seconds': {'$push': {
                        '$cond': [{'$eq': ['$pricing/unit', 'Second']},
                                  '$lineItem/UsageAmount', 0]}},
                    'on_demand_cost': {'$push': '$pricing/publicOnDemandCost'},
                    'offer_cost': {
                        '$push': offer_type_offer_cost_map[offer_type]
                    },
                    'ri_norm_factor': {
                        '$first': '$lineItem/NormalizationFactor'
                    },
                    'sp_rate': {
                        '$first': '$savingsPlan/SavingsPlanRate'
                    }
                }
            }]

    def get_offers_expenses_by_type(self, offer_type, cloud_account_id,
                                    start_date, end_date):
        pipeline = self.get_expenses_pipeline(offer_type, cloud_account_id,
                                              start_date, end_date)
        return self.mongo_client.restapi.raw_expenses.aggregate(
            pipeline, allowDiskUse=True)

    def process_ri_sp_expenses(self, offer_type, cloud_account_id, start_date,
                               end_date):
        cloud_resource_ids = set()
        new_expenses_map = defaultdict(lambda: defaultdict(
            lambda: defaultdict(dict)))
        offer_expenses = self.get_offers_expenses_by_type(
            offer_type, cloud_account_id, start_date, end_date)
        if offer_type == 'ri':
            # lineItem/NormalizationFactor is missing for RDS instances,
            # use 1 as default value
            default_ri_norm_factor = 1
        else:
            # SP not use lineItem/NormalizationFactor
            default_ri_norm_factor = 0
        for expense in offer_expenses:
            LOG.info('Processing expense: %s', expense)
            expense['offer_type'] = offer_type
            expense['cloud_account_id'] = cloud_account_id
            cloud_resource_id = expense['_id']['cloud_resource_id']
            cloud_offer_id = expense['_id']['cloud_offer_id']
            # remove prefixes if exists
            cloud_resource_id = cloud_resource_id[
                                    cloud_resource_id.find('/') + 1:]
            cloud_offer_id = cloud_offer_id[cloud_offer_id.find('/') + 1:]
            cloud_resource_ids.add(cloud_resource_id)
            exp_start = datetime(**expense['_id']['start_date'],
                                 tzinfo=timezone.utc)
            offer_cost = sum(float(x) for x in expense['offer_cost'])
            on_demand_cost = sum(float(x) for x in expense['on_demand_cost'])
            usage = sum(float(x) for x in expense['usage_hours']) + sum(
                float(x) / SECONDS_IN_HOUR for x in expense['usage_seconds'])
            ri_norm_factor = float(
                expense.get('ri_norm_factor') or default_ri_norm_factor)
            sp_rate = float(expense.get('sp_rate') or 0)
            instance_type = expense['_id'].get(
                'instance_type') or expense['_id'].get('description')
            new_expenses_map[cloud_resource_id][exp_start][cloud_offer_id][
                instance_type] = (offer_cost, on_demand_cost, usage,
                                  ri_norm_factor, sp_rate)
        return new_expenses_map, cloud_resource_ids

    @staticmethod
    def ri_sp_usage_expense(cloud_account_id, resource_id, date, instance_type,
                            offer_id, offer_type, on_demand_cost, offer_cost,
                            usage, ri_norm_factor, sp_rate, expected_cost,
                            sign=1):
        return {
            'cloud_account_id': cloud_account_id,
            'resource_id': resource_id,
            'date': date,
            'instance_type': instance_type,
            'offer_id': offer_id,
            'offer_type': offer_type,
            'on_demand_cost': on_demand_cost,
            'offer_cost': offer_cost,
            'usage': usage,
            'ri_norm_factor': ri_norm_factor,
            'sp_rate': sp_rate,
            'expected_cost': expected_cost,
            'sign': sign
        }

    @staticmethod
    def dates_range(start_date, end_date):
        dates = []
        date = start_date.replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
        while date <= end_date:
            dates.append(date)
            date += timedelta(days=1)
        return dates

    def _sp_expected_cost_per_day(
            self, cloud_account_id, start_date, end_date):
        return self.mongo_client.restapi.raw_expenses.find({
                    'cloud_account_id': cloud_account_id,
                    'start_date': {'$gte': start_date, '$lte': end_date},
                    'lineItem/LineItemType': 'SavingsPlanRecurringFee',
                    'lineItem/UsageStartDate': {'$exists': True}
                }, {'start_date': 1, 'savingsPlan/TotalCommitmentToDate': 1,
                    'resource_id': 1})

    def sp_expected_cost_per_day(self, cloud_account_id, start_date, end_date):
        sp_date_expected_cost = defaultdict(lambda: defaultdict(float))
        expenses = self._sp_expected_cost_per_day(cloud_account_id, start_date,
                                                  end_date)
        for expense in expenses:
            date = expense['start_date'].replace(tzinfo=timezone.utc)
            sp_date_expected_cost[expense['resource_id']][date] = float(
                expense['savingsPlan/TotalCommitmentToDate'])
        return sp_date_expected_cost

    def _ri_expected_cost_per_day(
            self, cloud_account_id, start_date, end_date):
        # RIFee may be created at start of the month
        start_of_month = start_date.replace(day=1, hour=0, minute=0, second=0,
                                            microsecond=0)
        return self.mongo_client.restapi.raw_expenses.find(
            {
                'cloud_account_id': cloud_account_id,
                'start_date': {'$gte': start_of_month, '$lte': end_date},
                'lineItem/LineItemType': 'RIFee',
                'lineItem/UsageStartDate': {'$exists': True}
            },
            {
                'start_date': 1,
                'end_date': 1,
                'reservation/TotalReservedNormalizedUnits': 1,
                'reservation/TotalReservedUnits': 1,
                'reservation/AmortizedUpfrontFeeForBillingPeriod': 1,
                'lineItem/NormalizationFactor': 1,
                'lineItem/UnblendedCost': 1,
                'lineItem/UsageStartDate': 1,
                'resource_id': 1
            })

    def ri_expected_cost_per_day(self, cloud_account_id, start_date, end_date):
        ri_date_expected_cost = defaultdict(lambda: defaultdict(float))
        expenses = self._ri_expected_cost_per_day(
            cloud_account_id, start_date, end_date)
        for expense in expenses:
            # lineItem/TotalReservedNormalizedUnits is missing for RDS instances
            total_norm_hours = float(expense.get(
                'reservation/TotalReservedNormalizedUnits') or expense.get(
                'reservation/TotalReservedUnits'))
            total_cost_per_month = float(
                expense.get('lineItem/UnblendedCost', 0)) + float(expense.get(
                    'reservation/AmortizedUpfrontFeeForBillingPeriod', 0))
            cost_per_n_hr = total_cost_per_month / total_norm_hours
            norm_factor = float(expense.get('lineItem/NormalizationFactor', 1))
            exp_start_date = expense['start_date'].replace(tzinfo=timezone.utc)
            exp_end_date = expense['end_date'].replace(tzinfo=timezone.utc)
            dates = self.dates_range(exp_start_date, exp_end_date)
            for date in dates:
                ri_date_expected_cost[expense['resource_id']][
                    date] = HRS_IN_DAY * norm_factor * cost_per_n_hr
            # the first RIFee expense not includes hours from start of the
            # month to RI purchasing time
            period_start = self._datetime_from_value(
                expense['lineItem/UsageStartDate'])
            if period_start > exp_start_date:
                not_used_hrs = (period_start - exp_start_date
                                ).total_seconds() / SECONDS_IN_HOUR
                ri_date_expected_cost[expense['resource_id']][
                    exp_start_date] = (HRS_IN_DAY - not_used_hrs
                                       ) * norm_factor * cost_per_n_hr
        return ri_date_expected_cost

    def _get_offer_date_map(self, offer_ids, cloud_account_id,
                            start_date, end_date):
        result = defaultdict(list)
        offer_dates = self.clickhouse_client.execute(
            """SELECT DISTINCT offer_id, date
               FROM ri_sp_usage
               WHERE cloud_account_id = %(cloud_account_id)s AND
                 date >= %(start_date)s AND date <= %(end_date)s AND
                 offer_id in %(offer_ids)s
            """, params={
                'cloud_account_id': cloud_account_id,
                'start_date': start_date,
                'end_date': end_date,
                'offer_ids': offer_ids
            })
        for data in offer_dates:
            result[data[0]].append(data[1])
        return result

    def fill_ri_sp_usage_empty(self, offer_exp_cost_per_day, cloud_account_id,
                               start_date, end_date, offer_type):
        offer_dates_map = self._get_offer_date_map(
            list(offer_exp_cost_per_day), cloud_account_id, start_date,
            end_date)
        ch_expenses = []
        for offer_id, data in offer_exp_cost_per_day.items():
            exist_dates = offer_dates_map.get(offer_id, [])
            for date, cost in data.items():
                if date not in exist_dates:
                    LOG.info('Will add empty expense for offer %s, date: %s',
                             offer_id, date)
                    ch_expenses.append(self.ri_sp_usage_expense(
                        cloud_account_id, '', date, '', offer_id, offer_type,
                        0, 0, 0, 0, 0, cost, sign=1))
        LOG.info('Will add %s empty expense', len(ch_expenses))
        if ch_expenses:
            self.insert_clickhouse_expenses(ch_expenses)

    def generate_ri_sp_usage(self, offer_type, cloud_account_id, start_date,
                             end_date):
        LOG.info('Generating expenses for offer type: %s', offer_type)
        expected_values = {
            'ri': self.ri_expected_cost_per_day,
            'sp': self.sp_expected_cost_per_day,
        }
        func = expected_values[offer_type]
        offer_exp_cost_per_day = func(cloud_account_id, start_date, end_date)
        ch_expenses_list = []
        (new_expenses_map, cloud_resource_ids) = self.process_ri_sp_expenses(
            offer_type, cloud_account_id, start_date, end_date)
        cloud_resource_ids = list(cloud_resource_ids)
        for i in range(0, len(cloud_resource_ids), CHUNK_SIZE):
            cloud_resource_ids_chunk = cloud_resource_ids[i:i + CHUNK_SIZE]
            existing_expenses = self.get_ri_sp_usage_expenses(
                cloud_account_id, cloud_resource_ids_chunk, offer_type,
                start_date, end_date)
            for existing_expense in existing_expenses:
                (cloud_resource_id, date, instance_type, offer_cloud_res_id,
                 ri_norm_factor, sp_rate, expected_cost, offer_cost,
                 on_demand_cost, usage) = existing_expense
                date = date.replace(tzinfo=timezone.utc)
                existing_expense_values = (offer_cost, on_demand_cost, usage,
                                           ri_norm_factor, sp_rate)
                new_expense_values = new_expenses_map.get(
                    cloud_resource_id, {}).get(date, {}).get(
                    offer_cloud_res_id, {}).get(instance_type)
                if not new_expense_values:
                    continue
                elif new_expense_values == existing_expense_values:
                    # not update already existing record
                    new_expenses_map[cloud_resource_id][date].pop(
                        offer_cloud_res_id)
                    continue
                # cancel record for existing record
                ch_expenses_list.append(
                    self.ri_sp_usage_expense(
                        cloud_account_id, cloud_resource_id, date,
                        instance_type, offer_cloud_res_id, offer_type,
                        on_demand_cost, offer_cost, usage, ri_norm_factor,
                        sp_rate, expected_cost, sign=-1))

        for cloud_resource_id, data in new_expenses_map.items():
            for date, offer_data in data.items():
                for cloud_offer_id, instance_type_data in offer_data.items():
                    for instance_type, (offer_cost, on_demand_cost, usage,
                                        ri_norm_factor, sp_rate
                                        ) in instance_type_data.items():
                        expected_cost = offer_exp_cost_per_day.get(
                            cloud_offer_id, {}).get(date, 0)
                        ch_expenses_list.append(
                            self.ri_sp_usage_expense(
                                cloud_account_id, cloud_resource_id, date,
                                instance_type, cloud_offer_id, offer_type,
                                on_demand_cost, offer_cost, usage,
                                ri_norm_factor, sp_rate, expected_cost, 1))
        LOG.info('Will add %s expenses to ri_sp_usage', len(ch_expenses_list))
        if ch_expenses_list:
            self.insert_clickhouse_expenses(ch_expenses_list)
        self.fill_ri_sp_usage_empty(
            offer_exp_cost_per_day, cloud_account_id, start_date, end_date,
            offer_type)

    def get_uncovered_usage_expenses(self, cloud_account_id, resource_ids,
                                     start_date, end_date):
        return self.clickhouse_client.execute(
            """SELECT instance_type, os, location, resource_id, date,
                    sum(cost * sign), sum(usage * sign)
                FROM uncovered_usage
                WHERE cloud_account_id = %(cloud_account_id)s
                    AND date >= %(start_date)s
                    AND date <= %(end_date)s
                    AND resource_id in %(resource_ids)s
                GROUP BY resource_id, date, location, os,
                    instance_type
                HAVING sum(sign) > 0
            """, params={
                'cloud_account_id': cloud_account_id,
                'start_date': start_date,
                'end_date': end_date,
                'resource_ids': resource_ids
            })

    @staticmethod
    def uncovered_usage_expense(
            instance_type, os_type, location, cloud_account_id, date,
            resource_id, usage, cost, sign=1):
        return {
            'cloud_account_id': cloud_account_id,
            'date': date,
            'resource_id': resource_id,
            'instance_type': instance_type,
            'os': os_type,
            'location': location,
            'cost': cost,
            'usage': usage,
            'sign': sign
        }

    def get_uncovered_raw_expenses(self, cloud_account_id, start_date,
                                   end_date):
        return self.mongo_client.restapi.raw_expenses.find({
            'cloud_account_id': cloud_account_id,
            'start_date': {'$gte': start_date, '$lte': end_date},
            'box_usage': True,
            'lineItem/LineItemType': 'Usage'},
            {
                'start_date': 1,
                'resource_id': 1,
                'pricing/unit': 1,
                'lineItem/UsageAmount': 1,
                'lineItem/UnblendedCost': 1,
                'pricing/publicOnDemandCost': 1,
                'product/operatingSystem': 1,
                'product/instanceType': 1,
                'product/usagetype': 1,
                'product/region': 1,
                'lineItem/AvailabilityZone': 1
            }
        )

    def generate_uncovered_usage(self, cloud_account_id, start_date, end_date):
        LOG.info('Start generating uncovered usage for cloud account %s',
                 cloud_account_id)
        new_expenses_map = defaultdict(lambda: defaultdict(
            lambda: defaultdict(lambda: (0, 0))))
        raw_expenses = self.get_uncovered_raw_expenses(
            cloud_account_id, start_date, end_date)
        for expense in raw_expenses:
            # pricing/publicOnDemandCost may be missing for Fargate expenses and
            # lineItem/UnblendedCost may be missing for Lambda
            cost = expense.get('pricing/publicOnDemandCost') or expense.get(
                'lineItem/UnblendedCost')
            if 'SpotUsage-Fargate' in expense.get('product/usagetype', ''):
                # spot Fargate tasks can't be covered by RI/SP
                continue
            if cost is None:
                raise Exception('Unsupported expense for resource %s, '
                                'cloud account: %s, date: %s' % (
                                    expense['resource_id'],
                                    cloud_account_id,
                                    expense['start_date']))
            cost = float(cost)
            usage_hrs = float(expense['lineItem/UsageAmount'])
            if 'second' in expense['pricing/unit'].lower():
                usage_hrs = usage_hrs / SECONDS_IN_HOUR
            os_type = expense.get('product/operatingSystem', '')
            instance_type = expense.get('product/instanceType', '')
            location = expense.get('lineItem/AvailabilityZone') or expense.get(
                'product/region', '')
            res_data = (os_type, instance_type, location)
            total_cost = new_expenses_map[expense['resource_id']][
                expense['start_date']][res_data][0]
            total_usage = new_expenses_map[expense['resource_id']][
                expense['start_date']][res_data][1]
            new_expenses_map[expense['resource_id']][expense['start_date']][
                res_data] = (total_cost + cost, total_usage + usage_hrs)
        cloud_resource_ids = list(new_expenses_map)
        ch_expenses_list = []
        for i in range(0, len(cloud_resource_ids), CHUNK_SIZE):
            cloud_resource_ids_chunk = cloud_resource_ids[i:i + CHUNK_SIZE]
            existing_expenses = self.get_uncovered_usage_expenses(
                cloud_account_id, cloud_resource_ids_chunk, start_date,
                end_date)
            for existing_expense in existing_expenses:
                (instance_type, os_type, location, cloud_resource_id, date,
                 cost, usage) = existing_expense
                res_data = (os_type, instance_type, location)
                date = date.replace(tzinfo=timezone.utc)
                existing_expense_values = (cost, usage)
                new_expense_values = new_expenses_map.get(
                    cloud_resource_id, {}).get(date, {}).get(res_data)
                if not new_expense_values:
                    continue
                elif new_expense_values == existing_expense_values:
                    # not update already existing record
                    new_expenses_map[cloud_resource_id].pop(date)
                    continue
                # cancel record for existing record
                ch_expenses_list.append(
                    self.uncovered_usage_expense(
                        instance_type, os_type, location, cloud_account_id,
                        date, cloud_resource_id, usage, cost, sign=-1))

        for cloud_resource_id, data in new_expenses_map.items():
            for date, usage_data in data.items():
                for res_data, cost_data in usage_data.items():
                    (os_type, instance_type, location) = res_data
                    cost, usage = cost_data
                    ch_expenses_list.append(
                        self.uncovered_usage_expense(
                            instance_type, os_type, location, cloud_account_id,
                            date, cloud_resource_id, usage, cost, sign=1))
        LOG.info('Expenses list: %s', ch_expenses_list)
        if ch_expenses_list:
            self.insert_clickhouse_expenses(ch_expenses_list,
                                            table='uncovered_usage')

    def _process_task(self, body):
        cloud_account_id = body.get('cloud_account_id')
        code, response = self.rest_cl.risp_processing_task_list(
            cloud_account_id)
        LOG.info('Task list response: %s', response)
        if code != 200:
            raise ValueError(f'Task list response is invalid: {response}')
        for task in response['risp_processing_tasks']:
            start_date = datetime.fromtimestamp(task['start_date']).replace(
                tzinfo=timezone.utc)
            end_date = datetime.fromtimestamp(task['end_date']).replace(
                tzinfo=timezone.utc)
            for offer_type in ['ri', 'sp']:
                self.generate_ri_sp_usage(offer_type, cloud_account_id,
                                          start_date, end_date)
            self.generate_uncovered_usage(cloud_account_id,
                                          start_date, end_date)
            self.rest_cl.risp_processing_task_delete(task['id'])

    def process_task(self, body, message):
        try:
            LOG.info('Processing task: %s', body)
            self._process_task(body)
        except Exception as exc:
            LOG.exception('Task processing failed for cloud account %s '
                          'with exception: %s',
                          body.get('cloud_account_id'), str(exc))
        LOG.info('Task is finished')
        message.ack()

    def heartbeat(self):
        while self.running:
            self.connection.heartbeat_check()
            time.sleep(1)


if __name__ == '__main__':
    urllib3.disable_warnings(
        category=urllib3.exceptions.InsecureRequestWarning)
    debug = os.environ.get('DEBUG', False)
    log_level = 'DEBUG' if debug else 'INFO'
    setup_logging(loglevel=log_level, loggers=[''])

    config_cl = ConfigClient(
        host=os.environ.get('HX_ETCD_HOST'),
        port=int(os.environ.get('HX_ETCD_PORT')),
    )
    config_cl.wait_configured()
    conn_str = 'amqp://{user}:{pass}@{host}:{port}'.format(
        **config_cl.read_branch('/rabbit'))
    with Connection(conn_str) as conn:
        try:
            migrator = Migrator(config_cl)
            with EtcdLock(config_cl, 'risp_migrations'):
                migrator.migrate()
            worker = RISPWorker(conn, config_cl)
            worker.run()
        except KeyboardInterrupt:
            worker.running = False
            worker.thread.join()
            LOG.info('Shutdown received')
