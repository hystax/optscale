import logging
from diworker.diworker.migrations.base import BaseMigration

"""
Remove AWSRawUnique index for raw_expenses collection
"""
LOG = logging.getLogger(__name__)
INDEX_NAME = 'AWSRawUnique'
INDEX_FIELDS = [
    'lineItem/LineItemDescription',
    'lineItem/LineItemType',
    'lineItem/UsageStartDate',
    'lineItem/UsageType',
    'lineItem/Operation',
    'lineItem/ProductCode',
    'lineItem/ResourceId',
    'cloud_account_id',
    'lineItem/AvailabilityZone',
    'identity/LineItemId'
]
PARTIAL_FILTER_EXPRESSION = {
    "lineItem/LineItemDescription": {"$exists": True},
    "lineItem/LineItemType": {"$exists": True},
    "lineItem/UsageType": {"$exists": True},
    "lineItem/UsageStartDate": {"$exists": True},
    "lineItem/Operation": {"$exists": True},
    "lineItem/ProductCode": {"$exists": True},
    "start_date": {"$exists": True}
}


class Migration(BaseMigration):
    @property
    def mongo_raw(self):
        return self.db.raw_expenses

    def upgrade(self):
        indexes_info = self.mongo_raw.index_information()
        db_index = indexes_info.get(INDEX_NAME)
        if db_index:
            self.mongo_raw.drop_index(INDEX_NAME)

    def downgrade(self):
        indexes_info = self.mongo_raw.index_information()
        db_index = indexes_info.get(INDEX_NAME)
        if not db_index:
            LOG.info('Creating index %s' % INDEX_NAME)
            self.mongo_raw.create_index(
                [(f, 1) for f in INDEX_FIELDS],
                name=INDEX_NAME,
                background=True,
                partialFilterExpression=PARTIAL_FILTER_EXPRESSION,
                unique=True
            )
