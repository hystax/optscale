import csv
from io import StringIO
from datetime import datetime, timezone
from urllib.parse import quote
from kombu.log import get_logger
from kombu import Connection as QConnection
from kombu import Exchange
from kombu.log import get_logger
from kombu.pools import producers
from requests.exceptions import SSLError
from optscale_client.rest_api_client.client_v2 import Client as RestClient
from insider.insider_worker.processors.base import BasePriceProcessor
from insider.insider_worker.http_client.client import Client


ACTIVITIES_EXCHANGE_NAME = 'activities-tasks'
ACTIVITIES_EXCHANGE = Exchange(ACTIVITIES_EXCHANGE_NAME, type='topic')
LOG = get_logger(__name__)
PRICES_COUNT_TO_LOG = 10000
CHINA_CURRENCY_CODE = 'CNY'
BASE_PRICES_URL = 'https://prices.azure.com/api/retail/prices'


class AzurePriceProcessor(BasePriceProcessor):
    # common unique params + 2 additional keys for reservations
    UNIQUE_FIELDS = ['meterId', 'type', 'productName', 'reservationTerm',
                     'tierMinimumUnits', 'currencyCode']
    CHANGE_FIELDS = ['retailPrice', 'unitPrice', 'meterName',
                     'effectiveStartDate']
    CLOUD_TYPE = 'azure_cnr'

    @property
    def discoveries(self):
        return self.mongo_client.insider.discoveries

    @property
    def prices(self):
        return self.mongo_client.insider.azure_prices

    @staticmethod
    def unique_values(price):
        return tuple(price.get(p) for p in AzurePriceProcessor.UNIQUE_FIELDS)

    @staticmethod
    def change_values(price):
        return tuple(price.get(p) for p in AzurePriceProcessor.CHANGE_FIELDS)

    def publish_activities_tasks(self, task):
        queue_conn = QConnection('amqp://{user}:{pass}@{host}:{port}'.format(
            **self.config_client.read_branch('/rabbit')))
        with producers[queue_conn].acquire(block=True) as producer:
            producer.publish(
                task,
                serializer='json',
                exchange=ACTIVITIES_EXCHANGE,
                declare=[ACTIVITIES_EXCHANGE],
                routing_key='insider.error.sslerror',
                retry=True
            )

    def send_sslerror_service_email(self):
        task = {
            'action': 'insider_prices_sslerror',
            'object_id': None
        }
        self.publish_activities_tasks(task)

    def _get_currencies_list(self):
        rest_cl = RestClient(
            url=self.config_client.restapi_url(),
            secret=self.config_client.cluster_secret(),
            verify=False)
        _, orgs = rest_cl.organization_list()
        currencies = set(map(lambda x: x['currency'], orgs['organizations']))
        return list(currencies)

    def _process_global_prices(self, http_client, old_prices_map, currency):
        price_types = self._get_all_price_types(http_client, currency)
        # break down by type to avoid 1000000 record limit
        for price_type in price_types:
            LOG.info('Processing Azure prices for currency: %s, type: %s',
                     currency, price_type)
            processed_keys = {}
            prices_counter = 0
            next_page = BASE_PRICES_URL + '?currencyCode=%s&$filter=%s' % (
                currency, quote("type eq '%s'" % price_type))
            while True:
                if prices_counter % PRICES_COUNT_TO_LOG == 0:
                    LOG.info('Total number of prices got from '
                             'cloud: %s', prices_counter)
                code, response = self._make_ratail_price_request(
                    http_client, next_page)
                items = response.get('Items', [])
                new_prices_map = {self.unique_values(p): p for p in items}
                self.update_price_records(new_prices_map, old_prices_map,
                                          processed_keys)
                new_url = response.get('NextPageLink')
                if not new_url or new_url == next_page:
                    LOG.info('Total number of prices got from '
                             'cloud: %s', prices_counter)
                    break
                next_page = new_url
                prices_counter += response.get('Count', 0)

    def _process_china_prices(self, http_client, old_prices_map, currency):
        LOG.info('Start processing Azure China prices (%s)', currency)
        url = 'https://prices.azure.cn/api/retail/pricesheet/download?' \
              'api-version=2023-06-01-preview'
        _, response = http_client.get(url)
        download_url = response['DownloadUrl']
        _, response = http_client.get(download_url)
        stream = StringIO(response.decode('utf-8'))
        csv_reader = csv.DictReader(stream)
        new_prices_map = {self.unique_values(p): p for p in csv_reader}
        self.update_price_records(new_prices_map, old_prices_map, {})
        LOG.info('Total number of prices got from cloud: %s',
                 len(new_prices_map))

    def _make_ratail_price_request(self, http_client, url):
        try:
            code, response = http_client.get(url)
        except SSLError:
            LOG.error('Getting Azure prices failed with SSL '
                      'verification error. Will try to get prices'
                      'without SSL verification')
            self.send_sslerror_service_email()
            http_client = Client(verify=False)
            code, response = http_client.get(url)
        return code, response

    def _get_all_price_types(self, http_client, currency):
        def _get_next_price_types(http_client, currency, excluded_types=None):
            next_page = BASE_PRICES_URL + '?currencyCode=%s' % currency
            if excluded_types:
                conditions = ["type ne '%s'" % f for f in excluded_types]
                filter_str = ' and '.join(conditions)
                next_page += '&$filter=%s' % quote(filter_str)
            code, response = self._make_ratail_price_request(
                http_client, next_page)
            items = response.get('Items', [])
            return set(item['type'] for item in items)

        all_types = set()
        while True:
            new_types = _get_next_price_types(
                http_client, currency, list(all_types))
            if not new_types:
                return all_types
            all_types |= new_types

    def process_prices(self, last_discovery_ts):
        http_client = Client()
        process_func_map = {
            CHINA_CURRENCY_CODE: self._process_china_prices
        }
        for currency in self._get_currencies_list():
            old_prices = self.prices.find(
                {
                    'last_seen': {
                        '$gte': last_discovery_ts
                    },
                    'currencyCode': currency
                },
                {
                    k: 1 for k in
                    self.UNIQUE_FIELDS + self.CHANGE_FIELDS + ['last_seen']
                }
            )
            old_prices_map = {self.unique_values(p): p for p in old_prices}
            process_func = process_func_map.get(
                currency, self._process_global_prices)
            process_func(http_client, old_prices_map, currency)

    def update_price_records(self, new_prices_map, old_prices_map,
                             processed_keys):
        if not new_prices_map:
            return
        now_ts = int(datetime.now(tz=timezone.utc).timestamp())
        update_ids = []
        for key, new_price in new_prices_map.copy().items():
            processed_key = processed_keys.get(key)
            if processed_key:
                new_prices_map.pop(key)
                continue
            processed_keys[key] = True
            if self.change_values(new_price) == self.change_values(
                    old_prices_map.get(key, {})):
                update_ids.append(old_prices_map.get(key)['_id'])
                new_prices_map.pop(key)
                continue

            new_prices_map[key].update(
                {'created_at': now_ts, 'last_seen': now_ts})
        if update_ids:
            self.prices.update_many(
                filter={
                    '_id': {'$in': update_ids},
                },
                update={'$set': {'last_seen': now_ts}}
            )
        if new_prices_map:
            self.prices.insert_many(new_prices_map.values())
