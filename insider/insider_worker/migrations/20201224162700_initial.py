import logging

from insider.insider_worker.migrations.base import BaseMigration

"""
Creates an initial database structure with 'discoveries' and 'azure_prices'
collections and their indexes. The operations are idempotent to allow this
migration to pass on clusters that were created before migration support was
introduced.
"""

AZURE_PRICES_INDEX_NAME = 'ap_unique_index'
AZURE_PRICES_UNIQUE_FIELD_LIST = ['meterId', 'type', 'productName']

LOG = logging.getLogger(__name__)


class Migration(BaseMigration):

    def create_discoveries_indexes(self):
        self._create_search_index(self.discoveries, 'CloudType', 'cloud_type')

    def create_azure_prices_indexes(self):
        self._create_azure_prices_unique_index()
        self._create_search_index(self.azure_prices, 'CreatedAt', 'created_at')
        self._create_search_index(self.azure_prices, 'LastSeen', 'last_seen')

    def _create_azure_prices_unique_index(self):
        existing_indexes = [
            x['name'] for x in self.azure_prices.list_indexes()
        ]
        if AZURE_PRICES_INDEX_NAME not in existing_indexes:
            LOG.info('Creating unique index %s in azure_prices collection',
                     AZURE_PRICES_INDEX_NAME)
            self.azure_prices.create_index(
                [(f, 1) for f in AZURE_PRICES_UNIQUE_FIELD_LIST],
                name=AZURE_PRICES_INDEX_NAME,
                unique=True
            )

    @staticmethod
    def _create_search_index(collection, index_name, field_key):
        existing_indexes = [
            x['name'] for x in collection.list_indexes()
        ]
        if index_name not in existing_indexes:
            LOG.info('Creating search index %s in %s collection',
                     collection.name, index_name)
            collection.create_index([(field_key, 1)], name=index_name)

    def upgrade(self):
        self.create_discoveries_indexes()
        self.create_azure_prices_indexes()

    def downgrade(self):
        self.discoveries.drop()
        self.azure_prices.drop()
