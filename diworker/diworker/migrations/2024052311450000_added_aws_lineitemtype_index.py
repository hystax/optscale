import logging
from diworker.diworker.migrations.base import BaseMigration

"""
Added aws LineItemType index
"""

LOG = logging.getLogger(__name__)
NEW_INDEXES = {
    'AWSLineItemType': (
        ['cloud_account_id', 'lineItem/LineItemType', 'start_date'],
        {'lineItem/LineItemType': {'$exists': True}}
    )
}


class Migration(BaseMigration):
    @property
    def raw_collection(self):
        return self.db.raw_expenses

    def _get_existing_index_names(self):
        return [i['name'] for i in self.raw_collection.list_indexes()]

    def upgrade(self):
        existing_indexes = self._get_existing_index_names()
        for index_name, (index_keys, partial_exp) in NEW_INDEXES.items():
            if index_name in existing_indexes:
                continue
            self.raw_collection.create_index(
                [(f, 1) for f in index_keys],
                name=index_name,
                background=True,
                partialFilterExpression=partial_exp)

    def downgrade(self):
        existing_indexes = self._get_existing_index_names()
        for index_name in NEW_INDEXES.keys():
            if index_name in existing_indexes:
                self.raw_collection.drop_index(index_name)
