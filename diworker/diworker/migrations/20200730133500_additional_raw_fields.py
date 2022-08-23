import logging
from pymongo import UpdateOne
from datetime import datetime, timezone
from diworker.migrations.base import BaseMigration

"""
Adds a 'start_date', 'start_date', 'cost' fields to all raw expenses'.
Needed for calculating costs per day'.
"""

LOG = logging.getLogger(__name__)
CHUNK_SIZE = 200
UNIQUE_INDEX_NAME = 'AWSReportImporter'
OLD_UNIQUE_FIELD_LIST = [
    'lineItem/LineItemType',
    'lineItem/UsageStartDate',
    'lineItem/UsageType',
    'lineItem/Operation',
    'lineItem/ResourceId',
    'cloud_credentials_id',
]
OLD_PARTIAL_FILTER_EXPRESSION = {
    'lineItem/LineItemType': {'$exists': True},
    'lineItem/UsageStartDate': {'$exists': True},
    'lineItem/UsageType': {'$exists': True},
    'lineItem/Operation': {'$exists': True},
}
NEW_PARTIAL_FILTER_EXPRESSION = {
    'lineItem/LineItemType': {'$exists': True},
    'lineItem/UsageStartDate': {'$exists': True},
    'lineItem/UsageType': {'$exists': True},
    'lineItem/Operation': {'$exists': True},
    'start_date': {'$exists': True},
}
NEW_UNIQUE_FIELD_LIST = [
    'lineItem/LineItemType',
    'lineItem/UsageStartDate',
    'lineItem/UsageType',
    'lineItem/Operation',
    'lineItem/ResourceId',
    'cloud_credentials_id',
    'start_date'
]


class Migration(BaseMigration):
    def _create_raw_unique_index(self, field_list, partial_filter_expression):
        existing_indexes = [
            x['name'] for x in self.db.raw_expenses.list_indexes()
        ]
        if UNIQUE_INDEX_NAME not in existing_indexes:
            LOG.info('Creating unique index %s in raw collection',
                     UNIQUE_INDEX_NAME)
            self.db.raw_expenses.create_index(
                [(f, 1) for f in field_list],
                name=UNIQUE_INDEX_NAME,
                unique=True,
                partialFilterExpression=partial_filter_expression
            )

    def fix_resource_ids(self):
        update_requests = []
        filters = {
            'resource_id': {'$exists': True},
            'lineItem/ResourceId': {'$exists': True},
        }

        for item in self.db.raw_expenses.find(filters):
            r_id = item['lineItem/ResourceId']
            update_request = UpdateOne(
                filter={'_id': item['_id']},
                update={'$set': {
                    'resource_id': r_id[r_id.find('/') + 1:]
                }}
            )
            update_requests.append(update_request)
            if len(update_requests) == CHUNK_SIZE:
                self.db.raw_expenses.bulk_write(update_requests)
                update_requests = []

        if len(update_requests) > 0:
            self.db.raw_expenses.bulk_write(update_requests)

    def add_new_fields(self):
        update_requests = []
        filters = {
            'cost': {'$exists': False},
            'lineItem/UsageStartDate': {'$exists': True}
        }

        for item in self.db.raw_expenses.find(filters):
            update_request = UpdateOne(
                filter={'_id': item['_id']},
                update={'$set': {
                    'cost': float(item.get('lineItem/BlendedCost', 0)),
                    'end_date': datetime.strptime(
                        item['lineItem/UsageEndDate'], '%Y-%m-%dT%H:%M:%SZ'
                    ).replace(tzinfo=timezone.utc),
                    'start_date': datetime.strptime(
                        item['lineItem/UsageStartDate'], '%Y-%m-%dT%H:%M:%SZ'
                    ).replace(tzinfo=timezone.utc),
                }},
            )
            update_requests.append(update_request)
            if len(update_requests) == CHUNK_SIZE:
                self.db.raw_expenses.bulk_write(update_requests)
                update_requests = []

        if len(update_requests) > 0:
            self.db.raw_expenses.bulk_write(update_requests)

    def upgrade(self):
        self.fix_resource_ids()
        self.add_new_fields()
        existing_indexes = [
            x['name'] for x in self.db.raw_expenses.list_indexes()
        ]
        if UNIQUE_INDEX_NAME in existing_indexes:
            self.db.raw_expenses.drop_index(UNIQUE_INDEX_NAME)
        self._create_raw_unique_index(
            NEW_UNIQUE_FIELD_LIST, NEW_PARTIAL_FILTER_EXPRESSION)

    def downgrade(self):
        update_requests = []
        filters = {
            'resource_id': {'$exists': True},
            'lineItem/ResourceId': {'$exists': True},
        }

        for item in self.db.raw_expenses.find(filters):
            update_request = UpdateOne(
                filter={'_id': item['_id']},
                update={'$set': {
                    'resource_id': item['lineItem/ResourceId'].split('/')[-1]}
                },
            )
            update_requests.append(update_request)
            if len(update_requests) == CHUNK_SIZE:
                self.db.raw_expenses.bulk_write(update_requests)
                update_requests = []

        if len(update_requests) > 0:
            self.db.raw_expenses.bulk_write(update_requests)

        self.db.raw_expenses.update_many(
            {}, {'$unset': {'cost': '', 'end_date': '', 'start_date': ''}})
        existing_indexes = [
            x['name'] for x in self.db.raw_expenses.list_indexes()
        ]
        if UNIQUE_INDEX_NAME in existing_indexes:
            self.db.raw_expenses.drop_index(UNIQUE_INDEX_NAME)
        self._create_raw_unique_index(
            OLD_UNIQUE_FIELD_LIST, OLD_PARTIAL_FILTER_EXPRESSION)
