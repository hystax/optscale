import logging
from datetime import datetime, timezone

from pymongo import UpdateOne

from diworker.diworker.migrations.base import BaseMigration

"""
Migration removes raw records from current month. it is necessary because
otherwise existing records  won't match update statements (we added new field in
search criteria and this field is not present in existing data) and data will be
duplicated on import.
Clean expenses also updated to set cloud_resource_id in lowercase.
Migration also adds start_date and end_date fields in date format to be able to
use date-related queries.
"resource_id" field added and contains "instance_id" field in lowercase.
It resolves issues with Azure returning ids in different forms from consumption
APIs and APIs used by discovery.
Also added index to increase search of raw records to update. We already have an
index for resource_id and cloud_credentials_id on raw collection, but for azure
we also need start_date and meter_id fields. I didn't include
additional_properties, because this field is empty often, so it may not be
present in records as we remove empty fields.
"""

LOG = logging.getLogger(__name__)
INDEX_NAME = 'AzureRawFields'
CHUNK_SIZE = 200


class Migration(BaseMigration):
    @property
    def mongo_raw(self):
        return self.db.raw_expenses

    def create_index(self):
        existing_indexes = [x['name'] for x in self.mongo_raw.list_indexes()]
        if INDEX_NAME not in existing_indexes:
            LOG.info('Creating search index %s in raw collection', INDEX_NAME)
            self.mongo_raw.create_index(
                [('start_date', 1), ('meter_id', 1), ('resource_id', 1),
                 ('cloud_credentials_id', 1)],
                name=INDEX_NAME,
                partialFilterExpression={
                    'start_date': {'$exists': True},
                    'meter_id': {'$exists': True},
                    'resource_id': {'$exists': True},
                })

    def add_new_fields(self):
        update_requests = []
        filters = {
            'start_date': {'$exists': False},
            'end_date': {'$exists': False},
            'resource_id': {'$exists': False},
            'usage_start': {'$exists': True},
            'usage_end': {'$exists': True},
            'instance_id': {'$exists': True},
        }

        for item in self.db.raw_expenses.find(filters):
            update_request = UpdateOne(
                filter={'_id': item['_id']},
                update={'$set': {
                    'start_date': datetime.strptime(
                        item['usage_start'], '%Y-%m-%dT%H:%M:%S.%fZ'
                    ).replace(tzinfo=timezone.utc),
                    'end_date': datetime.strptime(
                        item['usage_end'], '%Y-%m-%dT%H:%M:%S.%fZ'
                    ).replace(tzinfo=timezone.utc),
                    'resource_id': item['instance_id'].lower(),
                }},
            )
            update_requests.append(update_request)
            if len(update_requests) == CHUNK_SIZE:
                self.db.raw_expenses.bulk_write(update_requests)
                update_requests = []

        if update_requests:
            self.db.raw_expenses.bulk_write(update_requests)

    def remove_azure_data_from_current_month(self):
        month_regex = datetime.utcnow().strftime('%Y-%m')
        self.db.raw_expenses.delete_many({'usage_start': {'$regex': month_regex}})

    def update_resource_id_in_clean_expenses(self):
        update_requests = []
        filters = {'cloud_resource_id': {
            '$regex': 'microsoft', '$options': 'i'}}

        for item in self.db.expenses.find(filters):
            update_request = UpdateOne(
                filter={'_id': item['_id']},
                update={'$set': {
                    'cloud_resource_id': item['cloud_resource_id'].lower(),
                }},
            )
            update_requests.append(update_request)
            if len(update_requests) == CHUNK_SIZE:
                self.db.expenses.bulk_write(update_requests)
                update_requests = []

        if update_requests:
            self.db.expenses.bulk_write(update_requests)

    def upgrade(self):
        self.update_resource_id_in_clean_expenses()
        self.remove_azure_data_from_current_month()
        self.add_new_fields()
        existing_indexes = [
            x['name'] for x in self.db.raw_expenses.list_indexes()
        ]
        if 'instance_id' in existing_indexes:
            self.db.raw_expenses.drop_index('instance_id')
        self.create_index()

    def create_instance_id_index(self):
        existing_indexes = [x['name'] for x in self.mongo_raw.list_indexes()]
        if 'instance_id' not in existing_indexes:
            LOG.info('Creating search index instance_id in raw collection')
            self.mongo_raw.create_index([('instance_id', 1)],
                                        name='instance_id')

    def downgrade(self):
        self.mongo_raw.drop_index(INDEX_NAME)
        self.create_instance_id_index()
        self.db.raw_expenses.update_many(
            filter={
                'start_date': {'$exists': True},
                'end_date': {'$exists': True},
                'usage_start': {'$exists': True},
                'instance_id': {'$exists': True},
                'resource_id': {'$exists': True},
            },
            update={'$unset': {
                'end_date': '', 'start_date': '', 'resource_id': ''
            }})
