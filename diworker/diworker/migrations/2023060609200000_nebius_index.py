import logging
from diworker.migrations.base import BaseMigration
from pymongo import IndexModel
"""
Added index for Nebius raw expenses
"""
INDEXES = {
    'NebiusSku': {
        'keys': [
            "cloud_account_id",
            "start_date",
            "sku_name"
        ],
        'partial': ['sku_name']
    },
    'NebiusRawSearch': {
        'keys': [
            "cloud_account_id",
            "start_date",
            "date"
        ],
        'partial': ['date']
    }
}

LOG = logging.getLogger(__name__)


class Migration(BaseMigration):
    @property
    def mongo_raw(self):
        return self.db.raw_expenses

    def create_index(self, index_name, index_info):
        body = {
            'name': index_name,
            'background': True
        }
        partial = {
            f: {"$exists": True} for f in index_info.get('partial', [])
        }
        body['partialFilterExpression'] = partial
        LOG.info('Create index %s - %s' % (index_name, index_info))
        return IndexModel([(f, 1) for f in index_info['keys']], **body)

    def delete_index(self, index_name):
        index_names = [x['name'] for x in self.mongo_raw.list_indexes()]
        if index_name in index_names:
            LOG.info('Delete index %s' % index_name)
            self.mongo_raw.drop_index(index_name)

    def upgrade(self):
        indexes_to_create = []
        index_names = [x['name'] for x in self.mongo_raw.list_indexes()]
        for index_name, index_info in INDEXES.items():
            if index_name not in index_names:
                indexes_to_create.append(
                    self.create_index(index_name, index_info))
        if indexes_to_create:
            self.mongo_raw.create_indexes(indexes_to_create)

    def downgrade(self):
        index_names = [x['name'] for x in self.mongo_raw.list_indexes()]
        for index_name in INDEXES:
            if index_name not in index_names:
                LOG.info('Dropping index: %s' % index_name)
                self.mongo_raw.drop_index(index_name)
