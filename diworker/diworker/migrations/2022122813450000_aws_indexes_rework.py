import logging
from diworker.migrations.base import BaseMigration
from pymongo import IndexModel
from rest_api_client.client_v2 import Client as RestClient

"""
Reworked indexes for performance reasons
"""
REMOVED_INDEXES = {
    'AWSRawExpenses': {
        'keys': [
            'cloud_account_id', 'lineItem/LineItemDescription',
            'resource_id', 'identity/LineItemId'
        ]
    },
    'AWSRawWithoutIdsFields': {
        'keys': [
            'resource_id', 'cloud_account_id', 'lineItem/LineItemType',
            'bill/BillingPeriodStartDate'
        ]
    },
    'SearchBoxUsage': {
        'keys': [
            'cloud_account_id', 'resource_id', 'box_usage', 'start_date'
        ]
    },
    'AWSRawWithIdsFields': {
        'keys': [
            'resource_id', 'cloud_account_id', 'bill/BillingPeriodStartDate'
        ]
    }
}
NEW_INDEXES = {
    'AWSResourceUpsert': {
        'keys': ['cloud_account_id', 'resource_id', 'start_date'],
        'partial': ['lineItem/UsageStartDate']
    },
    'AWSBillingPeriodSearch': {
        'keys': ['cloud_account_id', 'bill/BillingPeriodStartDate'],
        'partial': ['bill/BillingPeriodStartDate']
    },
    'BoxUsageSearch': {
        'keys': [
            'cloud_account_id', 'resource_id', 'box_usage', 'start_date'
        ],
        'partial': ['box_usage']
    },
    'AWSRawSearch': {
        'keys': [
            'cloud_account_id', 'resource_id', 'bill/BillingPeriodStartDate'
        ],
        'partial': ['bill/BillingPeriodStartDate']
    }
}
LOG = logging.getLogger(__name__)


class Migration(BaseMigration):
    @property
    def mongo_raw(self):
        return self.db.raw_expenses

    @property
    def rest_cl(self):
        if self._rest_cl is None:
            self._rest_cl = RestClient(
                url=self.config_cl.restapi_url(), verify=False)
            self._rest_cl.secret = self.config_cl.cluster_secret()
        return self._rest_cl

    def create_index(self, index_name, index_info):
        body = {
            'name': index_name,
            'background': True
        }
        partial = {
            f: {"$exists": True} for f in index_info.get('partial', [])
        }
        if partial:
            body['partialFilterExpression'] = partial
        LOG.info('Create index %s - %s' % (index_name, index_info))
        return IndexModel([(f, 1) for f in index_info['keys']], **body)

    def delete_index(self, index_name):
        index_names = [x['name'] for x in self.mongo_raw.list_indexes()]
        if index_name in index_names:
            LOG.info('Delete index %s' % index_name)
            self.mongo_raw.drop_index(index_name)

    def recreate_indexes(self, new_indexes, removed_indexes):
        for index_name in removed_indexes.keys():
            self.delete_index(index_name)
        indexes = []
        index_names = [x['name'] for x in self.mongo_raw.list_indexes()]
        for index_name, index in new_indexes.items():
            if index_name not in index_names:
                indexes.append(self.create_index(index_name, index))
        if indexes:
            self.mongo_raw.create_indexes(indexes)
        LOG.info('Recreation indexes complete')

    def upgrade(self):
        self.recreate_indexes(
            new_indexes=NEW_INDEXES, removed_indexes=REMOVED_INDEXES)

    def downgrade(self):
        self.recreate_indexes(
            new_indexes=REMOVED_INDEXES, removed_indexes=NEW_INDEXES)
