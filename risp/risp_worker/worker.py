from collections import defaultdict
from datetime import datetime, timezone
from threading import Thread

import os
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

    def get_consumers(self, consumer, channel):
        return [consumer(queues=[TASK_QUEUE], accept=['json'],
                         callbacks=[self.process_task], prefetch_count=10)]

    def get_clickhouse_expenses(self, cloud_account_id, resource_ids, offer_type,
                                start_date, end_date):
        return self.clickhouse_client.execute("""
                SELECT resource_id, date, offer_id, sum(offer_cost * sign),
                    sum(on_demand_cost * sign), sum(usage * sign)
                FROM ri_sp_usage
                WHERE cloud_account_id = %(cloud_account_id)s
                    AND offer_type = %(offer_type)s
                    AND date >= %(start_date)s
                    AND date <= %(end_date)s
                    AND resource_id in %(resource_ids)s
                GROUP BY resource_id, date, offer_id
                HAVING sum(sign) > 0
            """, params={
                'cloud_account_id': cloud_account_id,
                'start_date': start_date,
                'end_date': end_date,
                'offer_type': offer_type,
                'resource_ids': resource_ids
            })

    def insert_clickhouse_expenses(self, expenses):
        self.clickhouse_client.execute(
            """INSERT INTO ri_sp_usage VALUES""", expenses)

    @staticmethod
    def inverse_dict(d):
        return {v: k for k, v in d.items()}

    @staticmethod
    def get_expenses_pipeline(offer_type, cloud_account_id, start_date, end_date):
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
            raise Exception('Unknown offer type: %s' % offer_type)

        return [
            {
                '$match': {
                    'cloud_account_id': cloud_account_id,
                    'start_date': {'$gte': start_date, '$lte': end_date},
                    'lineItem/LineItemType': offer_type_line_item_filter_map[offer_type],
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
                    },
                    'usage_hours': {'$push': {
                        '$cond': [{'$eq': ['$pricing/unit', 'Second']},
                                  0, '$lineItem/UsageAmount']}},
                    'usage_seconds': {'$push': {
                        '$cond': [{'$eq': ['$pricing/unit', 'Second']},
                                  '$lineItem/UsageAmount', 0]}},
                    'on_demand_cost': {'$push': '$pricing/publicOnDemandCost'},
                    'offer_cost': {'$push': offer_type_offer_cost_map[offer_type]},
                }
            }]

    def get_offers_expenses_by_type(self, offer_type, cloud_account_id,
                                    start_date, end_date):
        pipeline = self.get_expenses_pipeline(offer_type, cloud_account_id,
                                              start_date, end_date)
        return self.mongo_client.restapi.raw_expenses.aggregate(
            pipeline, allowDiskUse=True)

    def process_raw_expenses(self, offer_type, cloud_account_id, start_date,
                             end_date):
        cloud_resource_ids = set()
        cloud_offer_ids = set()
        new_expenses_map = defaultdict(lambda: defaultdict(dict))
        offer_expenses = self.get_offers_expenses_by_type(
            offer_type, cloud_account_id, start_date, end_date)
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
            cloud_offer_ids.add(cloud_offer_id)
            exp_start = datetime(**expense['_id']['start_date'],
                                 tzinfo=timezone.utc)
            offer_cost = sum(float(x) for x in expense['offer_cost'])
            on_demand_cost = sum(float(x) for x in expense['on_demand_cost'])
            usage = sum(float(x) for x in expense['usage_hours']) + sum(
                float(x) / SECONDS_IN_HOUR for x in expense['usage_seconds'])
            new_expenses_map[cloud_resource_id][exp_start][cloud_offer_id] = (
                offer_cost, on_demand_cost, usage)
        return new_expenses_map, cloud_resource_ids, cloud_offer_ids

    @staticmethod
    def clickhouse_expense(cloud_account_id, resource_id, date, offer_id,
                           offer_type, on_demand_cost, offer_cost, usage, sign=1):
        return {
            'cloud_account_id': cloud_account_id,
            'resource_id': resource_id,
            'date': date,
            'offer_id': offer_id,
            'offer_type': offer_type,
            'on_demand_cost': on_demand_cost,
            'offer_cost': offer_cost,
            'usage': usage,
            'sign': sign
        }

    def generate_expenses(self, offer_type, cloud_account_id, start_date,
                          end_date):
        LOG.info('Generating expenses for offer type: %s', offer_type)
        ch_expenses_list = []
        (new_expenses_map, cloud_resource_ids, _) = self.process_raw_expenses(
            offer_type, cloud_account_id, start_date, end_date)
        cloud_resource_ids = list(cloud_resource_ids)
        for i in range(0, len(cloud_resource_ids), CHUNK_SIZE):
            cloud_resource_ids_chunk = cloud_resource_ids[i:i + CHUNK_SIZE]
            existing_expenses = self.get_clickhouse_expenses(
                cloud_account_id, cloud_resource_ids_chunk, offer_type, start_date,
                end_date)
            for existing_expense in existing_expenses:
                (cloud_resource_id, date, offer_cloud_res_id, offer_cost, on_demand_cost,
                 usage) = existing_expense
                date = date.replace(tzinfo=timezone.utc)
                existing_expense_values = (offer_cost, on_demand_cost, usage)
                new_expense_values = new_expenses_map.get(
                    cloud_resource_id, {}).get(date, {}).get(offer_cloud_res_id)
                if not new_expense_values:
                    continue
                elif new_expense_values == existing_expense_values:
                    # not update already existing record
                    new_expenses_map[cloud_resource_id][date].pop(
                        offer_cloud_res_id)
                    continue
                # cancel record for existing record
                ch_expenses_list.append(
                    self.clickhouse_expense(cloud_account_id, cloud_resource_id, date,
                                            offer_cloud_res_id, offer_type,
                                            on_demand_cost, offer_cost, usage,
                                            sign=-1))

        for cloud_resource_id, data in new_expenses_map.items():
            for date, offer_data in data.items():
                for cloud_offer_id, (offer_cost, on_demand_cost, usage) in offer_data.items():
                    ch_expenses_list.append(
                        self.clickhouse_expense(
                            cloud_account_id, cloud_resource_id, date,
                            cloud_offer_id, offer_type, on_demand_cost,
                            offer_cost, usage, 1))
        LOG.info('Expenses list: %s', ch_expenses_list)
        if ch_expenses_list:
            self.insert_clickhouse_expenses(ch_expenses_list)

    def _process_task(self, body):
        cloud_account_id = body.get('cloud_account_id')
        code, response = self.rest_cl.risp_processing_task_list(cloud_account_id)
        LOG.info('Task list response: %s', response)
        if code != 200:
            raise ValueError('Task list response is invalid: %s' % response)
        for task in response['risp_processing_tasks']:
            start_date = datetime.fromtimestamp(task['start_date'])
            end_date = datetime.fromtimestamp(task['end_date'])
            for offer_type in ['ri', 'sp']:
                self.generate_expenses(offer_type, cloud_account_id,
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
    urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)
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
