import logging
from diworker.diworker.migrations.base import BaseMigration
from optscale_client.rest_api_client.client_v2 import Client as RestClient
from pymongo import UpdateOne

"""
Generating 'resource_id' field for AWS raw expenses without 'resource_id' field
"""
CHUNK_SIZE = 200
ITEM_TYPE_ID_FIELDS = {
    'Tax': ['lineItem/TaxType', 'product/ProductName'],
    'Usage': ['lineItem/ProductCode', 'lineItem/Operation',
              'product/region'],
}
LOG = logging.getLogger(__name__)


def compose_resource_id(expense):
    parts = ITEM_TYPE_ID_FIELDS.get(expense['lineItem/LineItemType'])
    if parts:
        resource_id = ' '.join([expense.get(k) for k in parts if k in expense])
        return resource_id


class Migration(BaseMigration):
    @property
    def rest_cl(self):
        if self._rest_cl is None:
            self._rest_cl = RestClient(
                url=self.config_cl.restapi_url(), verify=False)
            self._rest_cl.secret = self.config_cl.cluster_secret()
        return self._rest_cl

    @property
    def mongo_raw(self):
        return self.db.raw_expenses

    def upgrade(self):
        _, orgs = self.rest_cl.organization_list()
        org_ids = list(map(lambda x: x['id'], orgs['organizations']))
        for org_id in org_ids:
            _, accs = self.rest_cl.cloud_account_list(org_id, type='aws_cnr')
            for acc in accs['cloud_accounts']:
                expenses = self.mongo_raw.aggregate([
                    {
                        '$match': {
                            'cloud_account_id': acc['id'],
                            'resource_id': {'$exists': False},
                            'lineItem/LineItemType': {
                                '$in': list(ITEM_TYPE_ID_FIELDS.keys())}
                        }
                    }])
                chunk = []
                for exp in expenses:
                    resource_id = compose_resource_id(exp)
                    chunk.append(UpdateOne(
                        filter={'_id': exp['_id']},
                        update={'$set': {'resource_id': resource_id}}))
                    if len(chunk) >= CHUNK_SIZE:
                        self.mongo_raw.bulk_write(chunk)
                        chunk = []
                if chunk:
                    self.mongo_raw.bulk_write(chunk)
            LOG.info('Resource ids were generated for raw expenses '
                     'of org: %s' % org_id)

    def downgrade(self):
        pass
