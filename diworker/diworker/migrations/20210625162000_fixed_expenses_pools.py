from diworker.migrations.base import BaseMigration
from rest_api_client.client_v2 import Client as RestClient
from pymongo import UpdateMany

"""
Fixed expense inconsistency after reapply rules
"""
CHUNK_SIZE = 200


class Migration(BaseMigration):
    @property
    def rest_cl(self):
        if self._rest_cl is None:
            self._rest_cl = RestClient(
                url=self.config_cl.restapi_url(), verify=False)
            self._rest_cl.secret = self.config_cl.cluster_secret()
        return self._rest_cl

    @property
    def mongo_resource(self):
        return self.db.resources

    @property
    def mongo_clean(self):
        return self.db.expenses

    @property
    def mongo_group_month_resource(self):
        return self.db.expenses_group_month_resource

    def upgrade(self):
        _, orgs = self.rest_cl.organization_list()
        org_ids = list(map(lambda x: x['id'], orgs['organizations']))
        for org in org_ids:
            invalid_resources = []
            _, accs = self.rest_cl.cloud_account_list(org)
            for acc in accs['cloud_accounts']:
                rr = self.mongo_clean.aggregate([
                    {
                        '$match': {
                            'cloud_account_id': acc['id']
                        }
                    },
                    {
                        '$group': {
                            '_id': '$resource_id',
                            'pools': {'$addToSet': "$pool_id"},
                            'owners': {'$addToSet': "$owner_id"},
                        }
                    }
                ], allowDiskUse=True)
                for r in rr:
                    if len(r['pools']) != 1 or len(r['owners']) != 1:
                        invalid_resources.append(r['_id'])
            for i in range(0, len(invalid_resources), CHUNK_SIZE):
                resource_ids = invalid_resources[i:i + CHUNK_SIZE]
                resources = self.mongo_resource.find(
                    {'_id': {'$in': resource_ids}}, ['pool_id', 'employee_id'])
                update_bulk = [UpdateMany(
                    filter={'resource_id': r['_id']},
                    update={'$set': {
                        'pool_id': r.get('pool_id'),
                        'owner_id': r.get('employee_id')}
                    },
                ) for r in resources]
                for collection in [
                    self.mongo_clean, self.mongo_group_month_resource
                ]:
                    collection.bulk_write(update_bulk)

    def downgrade(self):
        pass
