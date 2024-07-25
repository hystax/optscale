import logging
from diworker.diworker.migrations.base import BaseMigration
from optscale_client.rest_api_client.client_v2 import Client as RestClient

"""
Fixed eu region for gcp resources
"""

LOG = logging.getLogger(__name__)


class Migration(BaseMigration):
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
            'with_connected_accounts': True})
        org_len = len(organizations['organizations'])
        counter = 0
        for org in organizations['organizations']:
            org_id = org['id']
            counter = counter + 1
            LOG.info('Start processing for organization %s (%s/%s)',
                     org_id, counter, org_len)
            _, accounts = self.rest_cl.cloud_account_list(
                org_id, type='gcp_cnr')
            cloud_accounts = [x['id'] for x in accounts['cloud_accounts']]
            if cloud_accounts:
                LOG.info('Updating resources for cloud accounts: %s',
                         cloud_accounts)
                self.mongo_resources.update_many({
                    'cloud_account_id': {'$in': cloud_accounts},
                    'region': 'eu',
                }, {'$set': {'region': 'europe'}})

    def downgrade(self):
        pass
