import logging
from diworker.migrations.base import BaseMigration

"""
Updates AWSRawUnique with new unique fields
"""
INDEX_NAME = "AWSRawUnique"
OLD_FIELDS = [
    'lineItem/LineItemDescription',
    'lineItem/LineItemType',
    'lineItem/UsageStartDate',
    'lineItem/UsageType',
    'lineItem/Operation',
    'lineItem/ProductCode',
    'lineItem/ResourceId',
    'cloud_account_id',
    'start_date'
]
NEW_FIELDS = [
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
LOG = logging.getLogger(__name__)


class Migration(BaseMigration):
    @property
    def mongo_raw(self):
        return self.db.raw_expenses

    def dicts_equal(self, dict1, dict2):
        if set(dict1.keys()) != set(dict2.keys()):
            return False
        for k, v in dict1.items():
            if k not in dict2 or dict2[k] != v:
                return False
        return True

    def recreate_index(self, index_fields_list):
        indexes_info = self.mongo_raw.index_information()
        db_index = indexes_info.get(INDEX_NAME)
        if not db_index:
            LOG.info('Creating index %s' % INDEX_NAME)
            self.mongo_raw.create_index(
                [(f, 1) for f in index_fields_list],
                name=INDEX_NAME,
                background=True,
                partialFilterExpression=PARTIAL_FILTER_EXPRESSION,
                unique=True
            )
        else:
            db_key = set(db_index['key'])
            key = set((f, 1) for f in index_fields_list)
            db_filter_expr = {}
            if 'partialFilterExpression' in db_index:
                db_filter_expr = db_index['partialFilterExpression'].to_dict()

            if (db_index.get('unique') is not True or db_key != key or
                    not self.dicts_equal(
                        db_filter_expr, PARTIAL_FILTER_EXPRESSION)):
                LOG.info('Index %s exists. Will drop and recreate '
                         'it' % INDEX_NAME)
                self.mongo_raw.drop_index(INDEX_NAME)
                self.mongo_raw.create_index(
                    [(f, 1) for f in index_fields_list],
                    name=INDEX_NAME,
                    background=True,
                    partialFilterExpression=PARTIAL_FILTER_EXPRESSION,
                    unique=True
                )
            else:
                LOG.info('Index %s already exists' % INDEX_NAME)

    def upgrade(self):
        self.recreate_index(OLD_FIELDS + NEW_FIELDS)

    def downgrade(self):
        self.recreate_index(OLD_FIELDS)
