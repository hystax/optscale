import logging
from diworker.migrations.base import BaseMigration

"""
Add new index AwsServiceName to filter resources efficiently based on which
service they belong to (e.g. ec2, s3, kinesis).
"""

LOG = logging.getLogger(__name__)
INDEX_NAME = 'AwsServiceName'
FIELD_LIST = [
    'cloud_account_id', 'product/servicecode', 'pricing/term'
]
PARTIAL_FILTER_EXPRESSION = {
    'product/servicecode': {'$exists': True},
    'pricing/term': {'$exists': True},
}


class Migration(BaseMigration):
    @property
    def raw_expenses(self):
        return self.db.raw_expenses

    def upgrade(self):
        LOG.info('creating index %s', INDEX_NAME)
        self.raw_expenses.create_index(
            [(f, 1) for f in FIELD_LIST], name=INDEX_NAME, background=True,
            partialFilterExpression=PARTIAL_FILTER_EXPRESSION,
        )

    def downgrade(self):
        LOG.info('removing index %s', INDEX_NAME)
        self.raw_expenses.drop_index(INDEX_NAME)
