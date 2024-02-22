import logging
from datetime import datetime, timezone
from pymongo import UpdateOne
from diworker.diworker.migrations.base import BaseMigration
from optscale_client.rest_api_client.client_v2 import Client as RestClient

"""
Set 'start' and 'end' to Savings Plan and Reserved Instances resources meta
"""

CHUNK_SIZE = 200
LOG = logging.getLogger(__name__)
RI_PLATFORMS = [
    'Linux/UNIX',
    'Linux with SQL Server Standard',
    'Linux with SQL Server Web',
    'Linux with SQL Server Enterprise',
    'SUSE Linux',
    'Red Hat Enterprise Linux',
    'Red Hat Enterprise Linux with HA',
    'Windows',
    'Windows with SQL Server Standard',
    'Windows with SQL Server Web',
    'Windows with SQL Server Enterprise',
]


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
        result = []
        _, organizations = self.rest_cl.organization_list({
            'with_connected_accounts': True, 'is_demo': False})
        for org in organizations['organizations']:
            _, accounts = self.rest_cl.cloud_account_list(
                org['id'], type='aws_cnr')
            result.extend(x['id'] for x in accounts['cloud_accounts'])
        return result

    def upgrade(self):
        cloud_accs = self.get_cloud_accs()
        for i, cloud_acc_id in enumerate(cloud_accs):
            LOG.info('Starting processing for cloud account %s (%s/%s)' % (
                cloud_acc_id, i+1, len(cloud_accs)))
            resource_ids_map = {}
            resource_start_end = {}
            resources = self.mongo_resources.find(
                    {'cloud_account_id': cloud_acc_id,
                     'resource_type': {
                         '$in': ['Savings Plan', 'Reserved Instances']}},
                    {'_id': 1, 'cloud_resource_id': 1, 'first_seen': 1,
                     'last_seen': 1})
            for resource in resources:
                cloud_res_id = resource['cloud_resource_id']
                resource_ids_map[cloud_res_id] = resource['_id']
                resource_start_end[cloud_res_id] = (resource['first_seen'],
                                                    resource['last_seen'])
            cloud_resources_ids = list(resource_ids_map)
            updates_chunk = []
            for j in range(0, len(cloud_resources_ids), CHUNK_SIZE):
                resource_ids = cloud_resources_ids[j:j + CHUNK_SIZE]
                fist_seen = datetime.fromtimestamp(min(
                    resource_start_end[resource_id][0]
                    for resource_id in resource_ids))
                last_seen = datetime.fromtimestamp(max(
                    resource_start_end[resource_id][1]
                    for resource_id in resource_ids))
                pipeline = [
                    {'$match': {'cloud_account_id': cloud_acc_id,
                                'resource_id': {'$in': resource_ids},
                                'start_date': {'$gte': fist_seen,
                                               '$lt': last_seen},
                                'lineItem/LineItemType': {
                                    '$in': ['SavingsPlanRecurringFee',
                                            'RIFee']}}},
                    {'$group': {'_id': '$resource_id',
                                'start': {'$first': {'$cond': [
                                    {'$eq': ['$lineItem/LineItemType',
                                             'RIFee']},
                                    '$reservation/StartTime',
                                    '$savingsPlan/StartTime']}},
                                'end': {'$first': {'$cond': [
                                    {'$eq': ['$lineItem/LineItemType',
                                             'RIFee']},
                                    '$reservation/EndTime',
                                    '$savingsPlan/EndTime']}},
                                'instance_type': {
                                    '$first': '$lineItem/UsageType'},
                                'platform': {
                                    '$first': '$lineItem/LineItemDescription'},
                                'zone': {
                                    '$first': '$reservation/AvailabilityZone'}}
                     }
                ]
                expenses = self.mongo_raw.aggregate(pipeline)
                for expense in expenses:
                    start = None
                    end = None
                    updates = {}
                    try:
                        start = int(datetime.strptime(
                            expense.get('start'),
                            '%Y-%m-%dT%H:%M:%S.%fZ').replace(
                                tzinfo=timezone.utc).timestamp())
                        end = int(datetime.strptime(
                            expense.get('end'),
                            '%Y-%m-%dT%H:%M:%S.%fZ').replace(
                                tzinfo=timezone.utc).timestamp())
                    except (ValueError, TypeError):
                        pass
                    if start:
                        updates['meta.start'] = start
                    if end:
                        updates['meta.end'] = end
                    instance_type = expense.get('instance_type')
                    if instance_type:
                        instance_type = instance_type.split(':')[-1]
                        updates['meta.instance_type'] = instance_type
                    platform = expense['platform']
                    for ri_platform in RI_PLATFORMS:
                        if ri_platform in platform:
                            updates['meta.platform'] = ri_platform
                            break
                    zone = expense.get('zone')
                    if zone:
                        updates['meta.zone'] = zone
                    if updates:
                        updates_chunk.append(UpdateOne(
                            filter={'_id': resource_ids_map[expense['_id']]},
                            update={'$set': updates}))
                    if len(updates_chunk) >= CHUNK_SIZE:
                        self.mongo_resources.bulk_write(updates_chunk)
                        updates_chunk.clear()
            if updates_chunk:
                self.mongo_resources.bulk_write(updates_chunk)

    def downgrade(self):
        cloud_accs = self.get_cloud_accs()
        for i, cloud_acc_id in enumerate(cloud_accs):
            LOG.info('Starting processing for cloud account %s (%s/%s)' % (
                cloud_acc_id, i+1, len(cloud_accs)))
            resources = self.mongo_resources.find(
                    {'cloud_account_id': cloud_acc_id,
                     'resource_type': {
                         '$in': ['Savings Plan', 'Reserved Instances']}},
                    {'_id': 1})
            resource_ids = [x['_id'] for x in resources]
            if resource_ids:
                self.mongo_resources.update_many(
                    filter={'_id': {'$in': resource_ids}},
                    update={'$unset': {'meta.start': 1, 'meta.end': 1}}
                )
