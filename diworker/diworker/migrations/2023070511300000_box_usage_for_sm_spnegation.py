import logging
from diworker.diworker.migrations.base import BaseMigration
from optscale_client.rest_api_client.client_v2 import Client as RestClient
"""
Set box_usage=True for SavingsPlanNegation expenses of AmazonSageMaker service
"""

LOG = logging.getLogger(__name__)


class Migration(BaseMigration):
    @property
    def mongo_raw(self):
        return self.db.raw_expenses

    @property
    def mongo_resources(self):
        return self.db.resources

    @property
    def rest_cl(self):
        if self._rest_cl is None:
            self._rest_cl = RestClient(
                url=self.config_cl.restapi_url(), verify=False)
            self._rest_cl.secret = self.config_cl.cluster_secret()
        return self._rest_cl

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

    def execute(self, update_condition):
        cloud_accs = self.get_cloud_accs()
        for i, cloud_acc_id in enumerate(cloud_accs):
            LOG.info('Starting processing for cloud account %s (%s/%s)' % (
                cloud_acc_id, i+1, len(cloud_accs)))
            sp_resources = list(
                x['cloud_resource_id'] for x in self.mongo_resources.find(
                    {'cloud_account_id': cloud_acc_id,
                     'resource_type': 'Savings Plan'},
                    {'cloud_resource_id': 1}))
            for cloud_resource_id in sp_resources:
                self.mongo_raw.update_many(
                    {'cloud_account_id': cloud_acc_id,
                     'resource_id': cloud_resource_id,
                     'product/servicecode': 'AmazonSageMaker',
                     'lineItem/LineItemType': 'SavingsPlanNegation'},
                    update_condition
                )

    def upgrade(self):
        update_condition = {'$set': {'box_usage': True}}
        self.execute(update_condition)

    def downgrade(self):
        update_condition = {'$unset': {'box_usage': ''}}
        self.execute(update_condition)
