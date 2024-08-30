import logging
from diworker.diworker.migrations.base import BaseMigration
from optscale_client.rest_api_client.client_v2 import Client as RestClient

"""
Fix resource type for RDD resources detected as volumes
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
                url=self.config_cl.restapi_url(),
                secret=self.config_cl.cluster_secret())
        return self._rest_cl

    def upgrade(self):
        _, organizations = self.rest_cl.organization_list({
            'with_connected_accounts': True, 'is_demo': False})
        counter = 0
        org_len = len(organizations['organizations'])
        for org in organizations['organizations']:
            org_id = org['id']
            counter = counter + 1
            LOG.info('Start processing for organization %s (%s/%s)',
                     org_id, counter, org_len)
            _, accounts = self.rest_cl.cloud_account_list(
                org_id, type='alibaba_cnr')
            cloud_accounts = [x['id'] for x in accounts['cloud_accounts']]
            if cloud_accounts:
                LOG.info('Updating resources for cloud accounts: %s',
                         cloud_accounts)
                # every cloud account has a maximum of one needed resource,
                # as it is not included into expenses in base and is created by
                # OptScale to account round down discount
                self.mongo_resources.update_many({
                    'cloud_account_id': {'$in': cloud_accounts},
                    'resource_type': 'Volume',
                    'active': {'$exists': False},
                    'cloud_resource_id': 'Elastic Block Storage RDD'
                }, {'$set': {'resource_type': 'Round Down Discount'}})

    def downgrade(self):
        pass
