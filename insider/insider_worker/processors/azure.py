from datetime import datetime
from kombu.log import get_logger
from requests.exceptions import SSLError
from kombu import Connection as QConnection
from kombu import Exchange, Queue
from kombu.pools import producers
from rest_api_client.client_v2 import Client as RestClient
from insider_worker.processors.base import BasePriceProcessor
from insider_worker.http_client.client import Client


ACTIVITIES_EXCHANGE_NAME = 'activities-tasks'
ACTIVITIES_EXCHANGE = Exchange(ACTIVITIES_EXCHANGE_NAME, type='topic')
LOG = get_logger(__name__)
PRICES_PER_REQUEST = 100
PRICES_COUNT_TO_LOG = 1000


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

    def get_last_discovery(self):
        discoveries = self.discoveries.find(
            {'cloud_type': self.CLOUD_TYPE, 'completed_at': {'$ne': 0}}
        ).sort(
            [('completed_at', -1)]).limit(1)
        try:
            return next(discoveries)
        except StopIteration:
            return {}

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

    def process_prices(self):
        last_discovery = self.get_last_discovery()
        old_prices = self.prices.find(
            {'last_seen': {'$gte': last_discovery.get('started_at', 0)}},
            {k: 1 for k in self.UNIQUE_FIELDS + self.CHANGE_FIELDS + ['last_seen']}
        )
        old_prices_map = {self.unique_values(p): p for p in old_prices}

        http_client = Client()
        processed_keys = {}
        prices_counter = 0
        for currency in self._get_currencies_list():
            next_page = 'https://prices.azure.com/api/retail/prices'
            next_page += '?currencyCode=%s' % currency
            while True:
                if prices_counter % PRICES_COUNT_TO_LOG == 0:
                    LOG.info('Total number of prices got from '
                             'cloud: %s' % prices_counter)
                try:
                    code, response = http_client.get(next_page)
                except SSLError:
                    LOG.error('Getting Azure prices failed with SSL verification '
                              'error. Will try to get prices without SSL '
                              'verification')
                    self.send_sslerror_service_email()
                    http_client = Client(verify=False)
                    code, response = http_client.get(next_page)
                items = response.get('Items', [])
                new_prices_map = {self.unique_values(p): p for p in items}
                self.update_price_records(new_prices_map, old_prices_map,
                                          processed_keys)
                new_url = response.get('NextPageLink')
                if not new_url or new_url == next_page:
                    LOG.info('Total number of prices got from '
                             'cloud: %s' % prices_counter)
                    break
                next_page = new_url
                prices_counter += PRICES_PER_REQUEST

    def update_price_records(self, new_prices_map, old_prices_map,
                             processed_keys):
        if not new_prices_map:
            return
        now_ts = int(datetime.utcnow().timestamp())
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
