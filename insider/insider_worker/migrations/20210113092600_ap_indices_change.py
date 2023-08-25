import logging

from insider.insider_worker.migrations.base import BaseMigration

"""
Because of necessity to keep azure prices historical changes unique index
need to keep last_seen. In addition it must include extra fields because of
Azure reservation prices uniqueness. Current index will stay non-unique in
search purposes.
"""

AZURE_PRICES_INDEX_NAME = 'ap_unique_index'
AZURE_PRICES_UNIQUE_FIELD_LIST_OLD = ['meterId', 'type', 'productName']
AZURE_PRICES_UNIQUE_FIELD_LIST_NEW = ['meterId', 'type', 'productName',
                                      'reservationTerm', 'tierMinimumUnits',
                                      'last_seen']

LOG = logging.getLogger(__name__)


class Migration(BaseMigration):

    def recreate_ap_unique_index(self, new=True):
        self._drop_index(self.azure_prices, AZURE_PRICES_INDEX_NAME)
        self._create_ap_unique_index(new)

    def _create_ap_unique_index(self, new):
        existing_indexes = [
            x['name'] for x in self.azure_prices.list_indexes()
        ]
        if AZURE_PRICES_INDEX_NAME not in existing_indexes:
            LOG.info('Creating unique index %s in azure_prices collection',
                     AZURE_PRICES_INDEX_NAME)
            field_list = (AZURE_PRICES_UNIQUE_FIELD_LIST_NEW
                          if new else AZURE_PRICES_UNIQUE_FIELD_LIST_OLD)
            self.azure_prices.create_index(
                [(f, 1) for f in field_list],
                name=AZURE_PRICES_INDEX_NAME,
                unique=True
            )

    @staticmethod
    def _drop_index(collection, index_name):
        existing_indexes = [
            x['name'] for x in collection.list_indexes()
        ]
        if index_name in existing_indexes:
            LOG.info('Dropping %s in %s collection',
                     index_name, collection)
            collection.drop_index(index_name)

    def upgrade(self):
        self.recreate_ap_unique_index(True)

    def downgrade(self):
        self.recreate_ap_unique_index(False)
