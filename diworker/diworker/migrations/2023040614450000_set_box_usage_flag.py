import logging
from diworker.diworker.migrations.base import BaseMigration
from pymongo import UpdateOne
from optscale_client.rest_api_client.client_v2 import Client as RestClient

"""
Set 'box_usage' flag to Fargate, Lambda and SageMaker raw expenses
"""

LOG = logging.getLogger(__name__)

CHUNK_SIZE = 200


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

    @property
    def mongo_temp_table(self):
        # temporary table for storing handled cloud accounts
        return self.db.migration_2023040614450000

    def get_cloud_accounts_ids(self):
        cloud_accounts_ids = set()
        _, organizations = self.rest_cl.organization_list()
        for org in organizations['organizations']:
            _, accounts = self.rest_cl.cloud_account_list(
                org['id'], type='aws_cnr')
            cloud_accounts_ids.update(
                account['id'] for account in accounts['cloud_accounts'])
        return cloud_accounts_ids

    @staticmethod
    def _is_flavor_usage(expense):
        usage_type = expense.get('lineItem/UsageType', '')
        service_code = expense.get('product/servicecode', '')
        description = expense.get('lineItem/LineItemDescription', '')
        return ((service_code == 'AmazonECS' and 'Fargate' in usage_type) or
                (service_code == 'AmazonSageMaker' and 'ml.' in description) or
                (service_code == 'AWSLambda' and'Lambda-GB-Second' in usage_type) or
                ('BoxUsage' in usage_type))

    def upgrade(self):
        cloud_accounts_ids = self.get_cloud_accounts_ids()
        for i, cloud_account_id in enumerate(cloud_accounts_ids):
            LOG.info('Started processing for cloud account: %s (%s/%s)' % (
                cloud_account_id, i+1, len(cloud_accounts_ids)))
            is_processed = self.mongo_temp_table.find({
                'cloud_account_id': cloud_account_id})
            if is_processed:
                LOG.info('Cloud account %s already processed' % cloud_account_id)
                continue
            update_bulk = []
            raw_expenses = self.mongo_raw.find({
                'cloud_account_id': cloud_account_id,
                'box_usage': {'$exists': False},
                'product/servicecode': {
                    '$in': ['AmazonECS', 'AmazonSageMaker', 'AWSLambda']}
            })
            for expense in raw_expenses:
                if self._is_flavor_usage(expense):
                    expense['box_usage'] = True
                    update_bulk.append(UpdateOne({'_id': expense['_id']},
                                                 {'$set': expense}))
                if len(update_bulk) >= CHUNK_SIZE:
                    self.mongo_raw.bulk_write(update_bulk)
                    update_bulk = []
            if update_bulk:
                self.mongo_raw.bulk_write(update_bulk)
            self.mongo_temp_table.insert_one(
                {'cloud_account_id': cloud_account_id})
        try:
            self.mongo_temp_table.drop()
        except Exception as exc:
            LOG.warning('Failed to drop temp table: %s' % str(exc))

    def downgrade(self):
        cloud_accounts_ids = self.get_cloud_accounts_ids()
        for i, cloud_account_id in enumerate(cloud_accounts_ids):
            LOG.info('Started processing for cloud account: %s (%s/%s)' % (
                cloud_account_id, i+1, len(cloud_accounts_ids)))
            is_processed = self.mongo_temp_table.find({
                'cloud_account_id': cloud_account_id})
            if is_processed:
                LOG.info('Cloud account %s already processed' % cloud_account_id)
                continue
            update_bulk = []
            raw_expenses = self.mongo_raw.find({
                'cloud_account_id': cloud_account_id,
                'box_usage': True,
                'product/servicecode': {
                    '$in': ['AmazonECS', 'AmazonSageMaker', 'AWSLambda']}
            })
            for expense in raw_expenses:
                expense.pop('box_usage', None)
                update_bulk.append(UpdateOne({'_id': expense['_id']},
                                             {'$set': expense}))
                if len(update_bulk) >= CHUNK_SIZE:
                    self.mongo_raw.bulk_write(update_bulk)
                    update_bulk = []
            if update_bulk:
                self.mongo_raw.bulk_write(update_bulk)
            self.mongo_temp_table.insert_one(
                {'cloud_account_id': cloud_account_id})
        try:
            self.mongo_temp_table.drop()
        except Exception as exc:
            LOG.warning('Failed to drop temp table: %s' % str(exc))
