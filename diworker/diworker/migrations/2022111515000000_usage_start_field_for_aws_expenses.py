import logging
from datetime import datetime, timezone
from diworker.diworker.migrations.base import BaseMigration
from pymongo import UpdateOne
from optscale_client.rest_api_client.client_v2 import Client as RestClient

"""
Add usage_start field with datetime value of 'lineItem/UsageStartDate'
for AWS expenses
"""
CHUNK_SIZE = 200
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

    @staticmethod
    def datetime_from_str(str_date):
        return datetime.strptime(
            str_date, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)

    def get_cloud_account_ids(self):
        cloud_account_ids = []
        _, orgs = self.rest_cl.organization_list()
        org_ids = [x['id'] for x in orgs['organizations']]
        for org_id in org_ids:
            _, response = self.rest_cl.cloud_account_list(org_id, type='aws_cnr')
            cloud_account_ids.extend([x['id'] for x in response['cloud_accounts']])
        return cloud_account_ids

    def upgrade(self):
        cloud_account_ids = self.get_cloud_account_ids()
        for i, cloud_account_id in enumerate(cloud_account_ids):
            LOG.info('Started updating raw expenses for '
                     'cloud account {0} ({1}/{2})'.format(
                        cloud_account_id, i + 1, len(cloud_account_ids)))
            expenses = self.mongo_raw.aggregate([
                {'$match': {
                    'cloud_account_id': cloud_account_id,
                    'lineItem/UsageStartDate': {'$exists': True}}}])
            chunk = []
            for expense in expenses:
                chunk.append(UpdateOne(
                    filter={'_id': expense['_id']},
                    update={'$set': {
                        'usage_start': self.datetime_from_str(
                            expense['lineItem/UsageStartDate'])}}))
                if len(chunk) >= CHUNK_SIZE:
                    self.mongo_raw.bulk_write(chunk)
                    chunk = []
            if chunk:
                self.mongo_raw.bulk_write(chunk)

    def downgrade(self):
        cloud_account_ids = self.get_cloud_account_ids()
        self.mongo_raw.update_many(
            filter={'cloud_account_id': {'$in': cloud_account_ids}},
            update={'$unset': {'usage_start': ''}})
