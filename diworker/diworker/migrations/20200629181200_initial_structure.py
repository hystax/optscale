import logging

from diworker.diworker.migrations.base import BaseMigration

"""
Creates an initial database structure with 'raw_expenses' and 'expenses'
collections and their indexes. The operations are idempotent to allow this
migration to pass on clusters that were created before migration support was
introduced.
"""

CLEAN_COLLECTION_INDEX_NAME = 'unique_index'
UNIQUE_FIELD_LIST = [
    'lineItem/LineItemType',
    'lineItem/UsageStartDate',
    'lineItem/UsageType',
    'lineItem/Operation',
    'lineItem/ResourceId',
    'cloud_credentials_id',
]

LOG = logging.getLogger(__name__)


class Migration(BaseMigration):

    @property
    def mongo_raw(self):
        return self.db.raw_expenses

    @property
    def mongo_clean(self):
        return self.db.expenses

    def create_clean_indexes(self):
        existing_indexes = [x['name'] for x in self.mongo_clean.list_indexes()]
        if CLEAN_COLLECTION_INDEX_NAME not in existing_indexes:
            LOG.info('Creating unique index %s in clean collection',
                     CLEAN_COLLECTION_INDEX_NAME)
            self.mongo_clean.create_index(
                [('resource_id', 1), ('date', 1), ('cloud_credentials_id', 1)],
                name=CLEAN_COLLECTION_INDEX_NAME,
                unique=True,
            )
        self.create_raw_indexes()

    def create_raw_indexes(self):
        self._create_raw_unique_index()
        self._create_raw_search_index(
            'CredentialsID', 'cloud_credentials_id')
        self._create_raw_search_index(
            'ResourceID', 'resource_id')
        self._create_raw_search_index(
            'AWSBillingPeriodStartDate', 'bill/BillingPeriodStartDate')

    def _create_raw_unique_index(self):
        index_name = 'AWSReportImporter'
        existing_indexes = [x['name'] for x in self.mongo_raw.list_indexes()]
        if index_name not in existing_indexes:
            LOG.info('Creating unique index %s in raw collection', index_name)
            self.mongo_raw.create_index(
                [(f, 1) for f in UNIQUE_FIELD_LIST],
                name=index_name,
                unique=True,
                partialFilterExpression={
                    'lineItem/LineItemType': {'$exists': True},
                    'lineItem/UsageStartDate': {'$exists': True},
                    'lineItem/UsageType': {'$exists': True},
                    'lineItem/Operation': {'$exists': True},
                },
            )

    def _create_raw_search_index(self, index_name, field_key):
        existing_indexes = [x['name'] for x in self.mongo_raw.list_indexes()]
        if index_name not in existing_indexes:
            LOG.info('Creating search index %s in raw collection', index_name)
            self.mongo_raw.create_index([(field_key, 1)], name=index_name)

    def upgrade(self):
        self.create_clean_indexes()
        self.create_raw_indexes()

    def downgrade(self):
        self.mongo_clean.drop()
        self.mongo_raw.drop()
