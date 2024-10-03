import logging
from pymongo import DeleteOne, UpdateOne
from optscale_client.rest_api_client.client_v2 import Client as RestClient
from diworker.diworker.migrations.base import BaseMigration
"""
Remove duplicated resources created by SP covered resources and change long
cloud_resource_id like 'arn:aws:service:account_id:type/short_id' to short_id
"""
CHUNK_SIZE = 1000
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

    @staticmethod
    def short_resource_id(resource_id):
        return resource_id[resource_id.find('/') + 1:]

    def upgrade(self):
        cloud_accs = self.get_cloud_accs()
        for i, cloud_acc_id in enumerate(list(cloud_accs)):
            LOG.info('Starting processing for cloud account %s (%s/%s)' % (
                cloud_acc_id, i + 1, len(cloud_accs)))
            sps = self.mongo_resources.find({
                'cloud_account_id': cloud_acc_id,
                'resource_type': 'Savings Plan',
                'active': {'$exists': False}}, {'cloud_resource_id': 1})
            sps_ids = [x['cloud_resource_id'] for x in sps]
            if not sps_ids:
                continue
            LOG.info('Found %s Savings Plan resources', len(sps_ids))
            long_res_ids = list(
                set(x['lineItem/ResourceId'] for x in self.mongo_raw.find({
                    'cloud_account_id': cloud_acc_id,
                    'resource_id': {'$in': sps_ids},
                    'box_usage': True,
                    'lineItem/LineItemType': 'SavingsPlanCoveredUsage',
                    'lineItem/ResourceId': {'$regex': 'arn:aws(.*)'}
                }, {'lineItem/ResourceId': 1})))
            long_short_map = {}
            if long_res_ids:
                # collect ids map and filter out resource ids that have
                # correct ids
                for long_res_id in long_res_ids:
                    short_res_id = self.short_resource_id(long_res_id)
                    if short_res_id != long_res_id:
                        long_short_map[long_res_id] = short_res_id
                long_res_ids = list(long_short_map)
                if not long_res_ids:
                    continue

                actions = []
                updated = 0
                deleted = 0
                for j in range(0, len(long_res_ids), CHUNK_SIZE):
                    if len(actions) >= CHUNK_SIZE:
                        self.mongo_resources.bulk_write(actions)
                        actions = []
                    long_chunk = long_res_ids[j:j + CHUNK_SIZE]
                    short_chunk = [long_short_map[x] for x in long_chunk]
                    db_short_resources = self.mongo_resources.find(
                        {'cloud_account_id': cloud_acc_id,
                         'cloud_resource_id': {'$in': short_chunk}},
                        {'cloud_resource_id': 1}
                    )
                    db_short_res_ids = [x['cloud_resource_id']
                                        for x in db_short_resources]
                    # resources created by SP without expenses
                    db_long_resources = self.mongo_resources.find({
                        'cloud_account_id': cloud_acc_id,
                        'cloud_resource_id': {'$in': long_chunk},
                        'resource_type': 'Instance',
                        'total_cost': {'$exists': False}
                    })
                    for resource in db_long_resources:
                        long_id = resource['cloud_resource_id']
                        short_id = long_short_map[long_id]
                        if short_id in db_short_res_ids:
                            # delete resource duplicate
                            actions.append(DeleteOne({'_id': resource['_id']}))
                            deleted = deleted + 1
                        else:
                            # update resource id to short id
                            actions.append(UpdateOne(
                                filter={'_id': resource['_id']},
                                update={
                                    '$set': {'cloud_resource_id': short_id}}))
                            updated = updated + 1
                if actions:
                    self.mongo_resources.bulk_write(actions)
                LOG.info('Deleted %s resources, updated %s resources', deleted,
                         updated)

    def downgrade(self):
        pass
