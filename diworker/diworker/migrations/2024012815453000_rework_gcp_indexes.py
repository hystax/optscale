import logging
from diworker.diworker.migrations.base import BaseMigration

"""
Added indexes for GCP and rework old indexes
"""

LOG = logging.getLogger(__name__)
NEW_INDEXES = {
    'GcpSku': (
        ['cloud_account_id', 'sku', 'start_date', 'resource_id', 'resource_hash'],
        {'sku': {'$exists': True}}
    ),
    'SearchResourceIdDates': (
        ['cloud_account_id', 'resource_id', 'start_date'],
        {'resource_id': {'$exists': True}}
    ),
    'SearchResourceHashDates': (
        ['cloud_account_id', 'resource_hash', 'start_date'],
        {'resource_hash': {'$exists': True}}
    )
}
OLD_INDEXES = {
    'GcpSku': (
        ['cloud_account_id', 'start_date', 'sku'],
        {'sku': {'$exists': True}}
    ),
    'AWSResourceUpsert': (
        ['cloud_account_id', 'resource_id', 'start_date'],
        {'lineItem/UsageStartDate': {'$exists': True}}
    )
}


class Migration(BaseMigration):
    @property
    def raw_collection(self):
        return self.db.raw_expenses

    def _get_existing_indexes(self):
        return {
            i['name']: list(i['key'])
            for i in self.raw_collection.list_indexes()
        }

    def rebuild_indexes(self, old_indexes_map, new_indexes_map):
        existing_index_map = self._get_existing_indexes()
        for new_index_name, (new_index_keys, partial_exp) in new_indexes_map.items():
            if new_index_name in existing_index_map:
                existing_index_keys = existing_index_map[new_index_name]
                if existing_index_keys == new_index_keys:
                    LOG.info('Skip index %s - already exists', new_index_name)
                    continue
                self.raw_collection.drop_index(new_index_name)
                LOG.info('Dropped index %s (duplicate name)', new_index_name)
            else:
                for index_name, (index_keys, _) in old_indexes_map.items():
                    if index_keys == new_index_keys:
                        self.raw_collection.drop_index(index_name)
                        LOG.info('Dropped index %s (duplicate keys)', index_name)
            self.raw_collection.create_index(
                [(f, 1) for f in new_index_keys],
                name=new_index_name,
                background=True,
                partialFilterExpression=partial_exp)
            LOG.info('Added index %s', new_index_name)
        existing_index_map = self._get_existing_indexes()
        for index_name in old_indexes_map.keys():
            if index_name not in new_indexes_map and index_name in existing_index_map:
                self.raw_collection.drop_index(index_name)
                LOG.info('Dropped index %s', index_name)

    def upgrade(self):
        self.rebuild_indexes(OLD_INDEXES, NEW_INDEXES)

    def downgrade(self):
        self.rebuild_indexes(NEW_INDEXES, OLD_INDEXES)
