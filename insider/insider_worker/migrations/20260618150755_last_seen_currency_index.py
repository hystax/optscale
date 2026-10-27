import logging
from insider.insider_worker.migrations.base import BaseMigration

NEW_INDEXES = {
    'CurrencyLastSeen': ['currencyCode', 'last_seen']
}
OLD_INDEXES = {
    'LastSeen': ['last_seen']
}
LOG = logging.getLogger(__name__)


class Migration(BaseMigration):
    def get_indexes(self):
        return [x['name'] for x in self.azure_prices.list_indexes()]

    def upgrade(self):
        existing_indexes = self.get_indexes()
        for index_name, index_fields in NEW_INDEXES.items():
            if index_name in existing_indexes:
                LOG.info(f'Index {index_name} already exists')
                continue
            LOG.info(f'Creating index {index_name}')
            self.azure_prices.create_index(
                [(f, 1) for f in index_fields],
                name=index_name,
                background=True
            )
        for index_name, index_fields in OLD_INDEXES.items():
            if index_name in existing_indexes:
                LOG.info(f'Dropping index {index_name}')
                self.azure_prices.drop_index(index_name)
            else:
                LOG.info(f'Index {index_name} doesn\'t exist')

    def downgrade(self):
        existing_indexes = self.get_indexes()
        for index_name, index_fields in OLD_INDEXES.items():
            if index_name in existing_indexes:
                LOG.info(f'Index {index_name} already exists')
                continue
            LOG.info(f'Creating index {index_name}')
            self.azure_prices.create_index(
                [(f, 1) for f in index_fields],
                name=index_name,
                background=True
            )
        for index_name, index_fields in NEW_INDEXES.items():
            if index_name in existing_indexes:
                LOG.info(f'Dropping index {index_name}')
                self.azure_prices.drop_index(index_name)
            else:
                LOG.info(f'Index {index_name} doesn\'t exist')
