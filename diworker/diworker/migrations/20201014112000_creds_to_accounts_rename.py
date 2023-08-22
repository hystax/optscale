import logging

from pymongo import UpdateOne, UpdateMany

from diworker.diworker.migrations.base import BaseMigration

"""
Migration adds cloud_account_id field for all expenses in both clean and raw
collections and also recreates all indexes relevant to cloud_credentials_id to
make use of cloud_account_id instead.
"""

LOG = logging.getLogger(__name__)
CHUNK_SIZE = 200
OLD_RAW_INDEX_NAME = 'CredentialsID'
NEW_RAW_INDEX_NAME = 'CloudAccountId'
OLD_AWS_RAW_INDEX_NAME = 'AWSReportImporter'
OLD_AWS_RAW_FIELD_LIST = [
    'lineItem/LineItemType',
    'lineItem/UsageStartDate',
    'lineItem/UsageType',
    'lineItem/Operation',
    'lineItem/ResourceId',
    'cloud_credentials_id',
    'start_date'
]
NEW_AWS_RAW_INDEX_NAME = 'AWSRawUnique'
NEW_AWS_RAW_FIELD_LIST = [
    'lineItem/LineItemType',
    'lineItem/UsageStartDate',
    'lineItem/UsageType',
    'lineItem/Operation',
    'lineItem/ResourceId',
    'cloud_account_id',
    'start_date'
]
AWS_PARTIAL_FILTER_EXPRESSION = {
    'lineItem/LineItemType': {'$exists': True},
    'lineItem/UsageStartDate': {'$exists': True},
    'lineItem/UsageType': {'$exists': True},
    'lineItem/Operation': {'$exists': True},
    'start_date': {'$exists': True},
}

AZURE_RAW_INDEX_NAME = 'AzureRawFields'
OLD_AZURE_RAW_FIELD_LIST = [
    'start_date',
    'meter_id',
    'resource_id',
    'cloud_credentials_id',
]
NEW_AZURE_RAW_FIELD_LIST = [
    'start_date',
    'meter_id',
    'resource_id',
    'cloud_account_id',
]
AZURE_PARTIAL_FILTER_EXPRESSION = {
    'start_date': {'$exists': True},
    'meter_id': {'$exists': True},
    'resource_id': {'$exists': True},
}
CLEAN_INDEX_NAME = 'unique_index'
OLD_CLEAN_INDEX_FIELDS = [
    'resource_id',
    'date',
    'cloud_credentials_id',
]
NEW_CLEAN_INDEX_FIELDS = [
    'resource_id',
    'date',
    'cloud_account_id',
]


class Migration(BaseMigration):
    @property
    def mongo_raw(self):
        return self.db.raw_expenses

    @property
    def mongo_clean(self):
        return self.db.expenses

    def update_collection(self, collection, upgrade=True):
        old_field_name = 'cloud_credentials_id' if upgrade else 'cloud_account_id'
        new_field_name = 'cloud_account_id' if upgrade else 'cloud_credentials_id'

        cred_ids = collection.distinct(old_field_name)
        update_requests = []
        for id_ in cred_ids:
            update_requests.append(UpdateMany(
                filter={old_field_name: id_},
                update={'$set': {new_field_name: id_}},
            ))
            if len(update_requests) == CHUNK_SIZE:
                collection.bulk_write(update_requests)
                update_requests = []

        if update_requests:
            collection.bulk_write(update_requests)

    def upgrade(self):
        LOG.info('adding account id to raw collection')
        self.update_collection(self.mongo_raw)
        LOG.info('adding account id to clean collection')
        self.update_collection(self.mongo_clean)

        raw_indexes = [x['name'] for x in self.mongo_raw.list_indexes()]
        if OLD_RAW_INDEX_NAME in raw_indexes:
            LOG.info('dropping index %s', OLD_RAW_INDEX_NAME)
            self.mongo_raw.drop_index(OLD_RAW_INDEX_NAME)
            LOG.info('creating index %s', NEW_RAW_INDEX_NAME)
            self.mongo_raw.create_index([('cloud_account_id', 1)],
                                        name=NEW_RAW_INDEX_NAME)

        if OLD_AWS_RAW_INDEX_NAME in raw_indexes:
            LOG.info('dropping index %s', OLD_AWS_RAW_INDEX_NAME)
            self.mongo_raw.drop_index(OLD_AWS_RAW_INDEX_NAME)
            LOG.info('creating index %s', NEW_AWS_RAW_INDEX_NAME)
            self.mongo_raw.create_index(
                [(f, 1) for f in NEW_AWS_RAW_FIELD_LIST],
                name=NEW_AWS_RAW_INDEX_NAME,
                unique=True,
                partialFilterExpression=AWS_PARTIAL_FILTER_EXPRESSION
            )

        if AZURE_RAW_INDEX_NAME in raw_indexes:
            LOG.info('dropping index %s', AZURE_RAW_INDEX_NAME)
            self.mongo_raw.drop_index(AZURE_RAW_INDEX_NAME)
            LOG.info('creating index %s', AZURE_RAW_INDEX_NAME)
            self.mongo_raw.create_index(
                [(f, 1) for f in NEW_AZURE_RAW_FIELD_LIST],
                name=AZURE_RAW_INDEX_NAME,
                partialFilterExpression=AZURE_PARTIAL_FILTER_EXPRESSION
            )

        clean_indexes = [x['name'] for x in self.mongo_clean.list_indexes()]
        if CLEAN_INDEX_NAME in clean_indexes:
            LOG.info('dropping index %s', CLEAN_INDEX_NAME)
            self.mongo_clean.drop_index(CLEAN_INDEX_NAME)
            LOG.info('creating index %s', CLEAN_INDEX_NAME)
            self.mongo_clean.create_index(
                [(f, 1) for f in NEW_CLEAN_INDEX_FIELDS],
                name=CLEAN_INDEX_NAME,
                unique=True,
            )

    def downgrade(self):
        self.update_collection(self.mongo_raw, upgrade=False)
        self.update_collection(self.mongo_clean, upgrade=False)

        raw_indexes = [x['name'] for x in self.mongo_raw.list_indexes()]
        if NEW_RAW_INDEX_NAME in raw_indexes:
            self.mongo_raw.drop_index(NEW_RAW_INDEX_NAME)
            self.mongo_raw.create_index([('cloud_credentials_id', 1)],
                                        name=OLD_RAW_INDEX_NAME)

        if NEW_AWS_RAW_INDEX_NAME in raw_indexes:
            self.mongo_raw.drop_index(NEW_AWS_RAW_INDEX_NAME)
            self.mongo_raw.create_index(
                [(f, 1) for f in OLD_AWS_RAW_FIELD_LIST],
                name=OLD_AWS_RAW_INDEX_NAME,
                unique=True,
                partialFilterExpression=AWS_PARTIAL_FILTER_EXPRESSION
            )

        if AZURE_RAW_INDEX_NAME in raw_indexes:
            self.mongo_raw.drop_index(AZURE_RAW_INDEX_NAME)
            self.mongo_raw.create_index(
                [(f, 1) for f in OLD_AZURE_RAW_FIELD_LIST],
                name=AZURE_RAW_INDEX_NAME,
                partialFilterExpression=AZURE_PARTIAL_FILTER_EXPRESSION
            )

        clean_indexes = [x['name'] for x in self.mongo_clean.list_indexes()]
        if CLEAN_INDEX_NAME in clean_indexes:
            self.mongo_clean.drop_index(CLEAN_INDEX_NAME)
            self.mongo_clean.create_index(
                [(f, 1) for f in OLD_CLEAN_INDEX_FIELDS],
                name=CLEAN_INDEX_NAME,
                unique=True,
            )
