import logging
from pymongo.errors import OperationFailure
from diworker.migrations.base import BaseMigration

"""
Migration recreates AWSRawUnique index with adding 'lineItem/LineItemDescription' field
"""

LOG = logging.getLogger(__name__)
AWS_RAW_INDEX_NAME = 'AWSRawUnique'
OLD_AWS_RAW_FIELD_LIST = [
    'lineItem/LineItemType',
    'lineItem/UsageStartDate',
    'lineItem/UsageType',
    'lineItem/Operation',
    'lineItem/ProductCode',
    'lineItem/ResourceId',
    'cloud_account_id',
    'start_date'
]
NEW_AWS_RAW_FIELD_LIST = [
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
OLD_AWS_PARTIAL_FILTER_EXPRESSION = {
    'lineItem/LineItemType': {'$exists': True},
    'lineItem/UsageStartDate': {'$exists': True},
    'lineItem/UsageType': {'$exists': True},
    'lineItem/Operation': {'$exists': True},
    'lineItem/ProductCode': {'$exists': True},
    'start_date': {'$exists': True},
}
NEW_AWS_PARTIAL_FILTER_EXPRESSION = {
    'lineItem/LineItemDescription': {'$exists': True},
    'lineItem/LineItemType': {'$exists': True},
    'lineItem/UsageStartDate': {'$exists': True},
    'lineItem/UsageType': {'$exists': True},
    'lineItem/Operation': {'$exists': True},
    'lineItem/ProductCode': {'$exists': True},
    'start_date': {'$exists': True},
}


class Migration(BaseMigration):
    @property
    def mongo_raw(self):
        return self.db.raw_expenses

    def upgrade(self):
        LOG.info('dropping index %s', AWS_RAW_INDEX_NAME)
        try:
            self.mongo_raw.drop_index(AWS_RAW_INDEX_NAME)
        except OperationFailure:
            LOG.info('index %s is missing', AWS_RAW_INDEX_NAME)
        LOG.info('creating index %s', AWS_RAW_INDEX_NAME)
        self.mongo_raw.create_index(
            [(f, 1) for f in NEW_AWS_RAW_FIELD_LIST],
            name=AWS_RAW_INDEX_NAME,
            unique=True,
            partialFilterExpression=NEW_AWS_PARTIAL_FILTER_EXPRESSION,
            background=True
        )
        LOG.info('creating of an index %s is completed', AWS_RAW_INDEX_NAME)

    def downgrade(self):
        LOG.info('dropping index %s', AWS_RAW_INDEX_NAME)
        try:
            self.mongo_raw.drop_index(AWS_RAW_INDEX_NAME)
        except OperationFailure:
            LOG.info('index %s is missing', AWS_RAW_INDEX_NAME)
        LOG.info('creating index %s', AWS_RAW_INDEX_NAME)
        self.mongo_raw.create_index(
            [(f, 1) for f in OLD_AWS_RAW_FIELD_LIST],
            name=AWS_RAW_INDEX_NAME,
            unique=True,
            partialFilterExpression=OLD_AWS_PARTIAL_FILTER_EXPRESSION,
            background=True
        )
        LOG.info('creating of an index %s is completed', AWS_RAW_INDEX_NAME)
