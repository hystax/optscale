import logging
from datetime import datetime
from optscale_client.rest_api_client.client_v2 import Client as RestClient
from diworker.diworker.migrations.base import BaseMigration
"""
Replace Azure modern usage meterId -> meter_id
"""
LOG = logging.getLogger(__name__)


class Migration(BaseMigration):
    @property
    def mongo_expenses(self):
        return self.db.raw_expenses

    @property
    def rest_cl(self):
        if self._rest_cl is None:
            self._rest_cl = RestClient(
                url=self.config_cl.restapi_url(),
                secret=self.config_cl.cluster_secret())
        return self._rest_cl

    def _fix(self, cloud_account_id):
        LOG.info("Fix cloud account %s", cloud_account_id)
        start_dt = datetime.now()
        self.mongo_expenses.update_many(
            {
                'cloud_account_id': cloud_account_id,
            },
            {
                '$rename': {'meterId': 'meter_id'}
            }
        )
        seconds = (datetime.now() - start_dt).total_seconds()
        LOG.info("Fixed cloud account %s for %s sec.",
                 cloud_account_id, seconds)

    def upgrade(self):
        _, orgs = self.rest_cl.organization_list({
            'with_connected_accounts': True
        })
        organizations = orgs['organizations']
        broken_cloud_accounts = set()
        total_orgs = len(organizations)
        last_pct = -1
        for i, org in enumerate(organizations):
            _, ca_resp = self.rest_cl.cloud_account_list(
                org['id'], type='azure_cnr')
            for ca in ca_resp['cloud_accounts']:
                expense = self.mongo_expenses.find_one({
                    'cloud_account_id': ca['id']
                }, {'meterId': 1})
                if not expense:
                    continue
                meter_id = expense.get('meterId')
                if meter_id:
                    broken_cloud_accounts.add(ca['id'])
            pct = (i + 1) * 100 // total_orgs
            if pct != last_pct:
                LOG.info("Step 1/2: Collecting: %d%%", pct)
                last_pct = pct

        total = len(broken_cloud_accounts)
        LOG.info("Found %d broken cloud accounts", total)
        last_pct = -1
        for i, cloud_account_id in enumerate(broken_cloud_accounts):
            self._fix(cloud_account_id)
            pct = (i + 1) * 100 // total
            if pct != last_pct:
                LOG.info("Step 2/2: Fixing: %d%%", pct)
                last_pct = pct

    def downgrade(self):
        pass
