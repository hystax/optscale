import logging
from optscale_client.rest_api_client.client_v2 import Client as RestClient
from diworker.diworker.migrations.base import BaseMigration
"""
Fixed names for discount fields in AWS expenses
"""
LOG = logging.getLogger(__name__)


class Migration(BaseMigration):
    @property
    def rest_cl(self):
        if self._rest_cl is None:
            self._rest_cl = RestClient(
                url=self.config_cl.restapi_url(),
                secret=self.config_cl.cluster_secret())
        return self._rest_cl

    @property
    def mongo_raw(self):
        return self.db.raw_expenses

    def get_cloud_accs(self):
        cloud_accounts_ids = set()
        _, organizations = self.rest_cl.organization_list({
            'with_connected_accounts': True, 'is_demo': False})
        for org in organizations['organizations']:
            _, accounts = self.rest_cl.cloud_account_list(
                org['id'], type='aws_cnr')
            for cloud_account in accounts['cloud_accounts']:
                if cloud_account['auto_import']:
                    cloud_accounts_ids.add(cloud_account['id'])
        return cloud_accounts_ids

    def upgrade(self):
        cloud_accs = self.get_cloud_accs()
        for i, cloud_acc_id in enumerate(cloud_accs):
            LOG.info('Starting processing for cloud account %s (%s/%s)' % (
                cloud_acc_id, i+1, len(cloud_accs)))
            self.db.raw_expenses.update_many(
                {'bill/BillingPeriodStartDate': {'$exists': True},
                 'cloud_account_id': cloud_acc_id},
                {'$rename': {
                    'discount_total_discount': 'discount/TotalDiscount',
                    'discount_bundled_discount': 'discount/BundledDiscount'}})

    def downgrade(self):
        pass
