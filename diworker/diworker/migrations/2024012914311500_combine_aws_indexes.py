import logging
from diworker.diworker.migrations.base import BaseMigration

"""
Replaced AWSBillingPeriodSearch and AWSRawSearch with one changed index
"""

LOG = logging.getLogger(__name__)
NEW_INDEXES = {
    'AWSRawSearch': (
        ['cloud_account_id', 'bill/BillingPeriodStartDate', 'resource_id'],
        {'bill/BillingPeriodStartDate': {'$exists': True}}
    )
}
OLD_INDEXES = {
    'AWSBillingPeriodSearch': (
        ['cloud_account_id', 'bill/BillingPeriodStartDate'],
        {'bill/BillingPeriodStartDate': {'$exists': True}}
    ),
    'AWSRawSearch': (
        ['cloud_account_id', 'resource_id', 'bill/BillingPeriodStartDate'],
        {'bill/BillingPeriodStartDate': {'$exists': True}}
    )
}


class Migration(BaseMigration):
    @property
    def raw_collection(self):
        return self.db.raw_expenses

    def rebuild_indexes(self, old_indexes_map, new_indexes_map):
        index_list = self.raw_collection.list_indexes()
        existing_index_map = {i['name']: i['key'] for i in index_list}
        for new_index_name, (new_index_keys, partial_exp) in new_indexes_map.items():
            if new_index_name in existing_index_map:
                existing_index_keys = list(existing_index_map[new_index_name])
                if existing_index_keys == new_index_keys:
                    LOG.info('Skip index %s - already exists', new_index_name)
                    continue
                self.raw_collection.drop_index(new_index_name)
                LOG.info('Dropped index %s', new_index_name)
            self.raw_collection.create_index(
                [(f, 1) for f in new_index_keys],
                name=new_index_name,
                background=True,
                partialFilterExpression=partial_exp)
            LOG.info('Added index %s', new_index_name)
        for index_name in old_indexes_map.keys():
            if index_name not in new_indexes_map:
                self.raw_collection.drop_index(index_name)
                LOG.info('Dropped index %s', index_name)

    def upgrade(self):
        self.rebuild_indexes(OLD_INDEXES, NEW_INDEXES)

    def downgrade(self):
        self.rebuild_indexes(NEW_INDEXES, OLD_INDEXES)
