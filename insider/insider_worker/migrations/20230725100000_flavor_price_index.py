import logging

from insider.insider_worker.migrations.base import BaseMigration

FLAVOR_PRICE_INDEX_NAME = 'FlavorPrice'
FLAVOR_PRICE_INDEX_FIELDS = ['armSkuName', 'type', 'serviceName',
                             'armRegionName', 'currencyCode', 'last_seen']
LOG = logging.getLogger(__name__)


class Migration(BaseMigration):

    def get_indexes(self):
        return [x['name'] for x in self.azure_prices.list_indexes()]

    def upgrade(self):
        indexes = self.get_indexes()
        if FLAVOR_PRICE_INDEX_NAME not in indexes:
            LOG.info(f'Creating index {FLAVOR_PRICE_INDEX_NAME}')
            self.azure_prices.create_index(
                [(f, 1) for f in FLAVOR_PRICE_INDEX_FIELDS],
                name=FLAVOR_PRICE_INDEX_NAME,
                background=True
            )
        else:
            LOG.info(f'Index {FLAVOR_PRICE_INDEX_NAME} already exists')

    def downgrade(self):
        indexes = self.get_indexes()
        if FLAVOR_PRICE_INDEX_NAME in indexes:
            LOG.info(f'Dropping index {FLAVOR_PRICE_INDEX_NAME}')
            self.azure_prices.drop_index(FLAVOR_PRICE_INDEX_NAME)
        else:
            LOG.info(f'Index {FLAVOR_PRICE_INDEX_NAME} doesn\'t exist')
