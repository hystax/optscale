import logging

from diworker.diworker.migrations.base import BaseMigration

"""
1. Removed AWSBillingPeriodStartDate index.
2. Added compound index (resource_id, cloud_account_id,
   bill/BillingPeriodStartDate) for "get_resource_ids" and
   "process_items_with_ids" (AWS).
2. Added compound index (resource_id, cloud_account_id, lineItem/LineItemType,
   bill/BillingPeriodStartDate) for "get_unique_pseudo_ids" and
   "process_items_without_ids" (AWS).
"""

LOG = logging.getLogger(__name__)
BILLING_PERIOD_INDEX = 'AWSBillingPeriodStartDate'
AWS_SEARCH_WITH_IDS_INDEX = 'AWSRawWithIdsFields'
AWS_SEARCH_WITHOUT_IDS_INDEX = 'AWSRawWithoutIdsFields'


class Migration(BaseMigration):
    @property
    def mongo_raw(self):
        return self.db.raw_expenses

    def upgrade(self):
        self.mongo_raw.drop_index(BILLING_PERIOD_INDEX)
        self.mongo_raw.create_index(
            [('resource_id', 1), ('cloud_account_id', 1),
             ('bill/BillingPeriodStartDate', 1)],
            name=AWS_SEARCH_WITH_IDS_INDEX)
        self.mongo_raw.create_index(
            [('resource_id', 1), ('cloud_account_id', 1),
             ('lineItem/LineItemType', 1), ('bill/BillingPeriodStartDate', 1)],
            name=AWS_SEARCH_WITHOUT_IDS_INDEX)

    def downgrade(self):
        for index_name in [AWS_SEARCH_WITHOUT_IDS_INDEX,
                           AWS_SEARCH_WITH_IDS_INDEX]:
            self.mongo_raw.drop_index(index_name)
        self.mongo_raw.create_index(
            [('bill/BillingPeriodStartDate', 1)],
            name=BILLING_PERIOD_INDEX)
