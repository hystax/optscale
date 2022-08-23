from datetime import datetime
from kombu.log import get_logger

from insider_worker.processors.base import BasePriceProcessor
from insider_worker.http_client.client import Client


LOG = get_logger(__name__)


class AzurePriceProcessor(BasePriceProcessor):
    # common unique params + 2 additional keys for reservations
    UNIQUE_FIELDS = ['meterId', 'type', 'productName', 'reservationTerm', 'tierMinimumUnits']
    CHANGE_FIELDS = ['retailPrice', 'unitPrice', 'meterName', 'effectiveStartDate']
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

    def process_prices(self):
        last_discovery = self.get_last_discovery()
        old_prices = self.prices.find(
            {'last_seen': {'$gte': last_discovery.get('started_at', 0)}},
            {k: 1 for k in self.UNIQUE_FIELDS + self.CHANGE_FIELDS + ['last_seen']}
        )
        old_prices_map = {self.unique_values(p): p for p in old_prices}

        next_page = 'https://prices.azure.com/api/retail/prices'
        http_client = Client()
        processed_keys = {}
        while True:
            code, response = http_client.get(next_page)
            items = response.get('Items', [])
            new_prices_map = {self.unique_values(p): p for p in items}
            self.update_price_records(new_prices_map, old_prices_map,
                                      processed_keys)
            new_url = response.get('NextPageLink')
            if not new_url or new_url == next_page:
                break
            next_page = new_url

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
