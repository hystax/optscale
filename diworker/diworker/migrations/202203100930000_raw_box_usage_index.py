import logging
from diworker.diworker.migrations.base import BaseMigration
from optscale_client.rest_api_client.client_v2 import Client as RestClient

"""
Add box_usage field into raw expenses and search index
"""

LOG = logging.getLogger(__name__)
INDEX_NAME = 'SearchBoxUsage'
FIELD_LIST = [
    'cloud_account_id', 'resource_id', 'box_usage', 'start_date'
]


class Migration(BaseMigration):
    @property
    def rest_cl(self):
        if self._rest_cl is None:
            self._rest_cl = RestClient(
                url=self.config_cl.restapi_url(), verify=False)
            self._rest_cl.secret = self.config_cl.cluster_secret()
        return self._rest_cl

    @property
    def raw_expenses(self):
        return self.db.raw_expenses

    def upgrade(self):
        _, orgs = self.rest_cl.organization_list()
        cloud_filter_map = {
            'aws_cnr': {'lineItem/UsageType': {'$regex': 'BoxUsage'}},
            'azure_cnr': {
                'meter_details.meter_category': 'Virtual Machines'},
            'alibaba_cnr': {'BillingItem': {
                '$in': ['Cloud server configuration', 'instance_type',
                        'Class Code', 'Instance Type']
            }}
        }
        for i, org in enumerate(orgs['organizations']):
            LOG.info('Migrating raw expenses for org %s (%s/%s)...' % (
                org['id'], i + 1, len(orgs['organizations'])))
            _, accs = self.rest_cl.cloud_account_list(org['id'])
            for ca in accs['cloud_accounts']:
                if ca['type'] not in cloud_filter_map.keys():
                    continue
                filters = {
                    'cloud_account_id': ca['id'],
                    **cloud_filter_map[ca['type']]
                }
                res = self.raw_expenses.update_many(
                    filter=filters,
                    update={'$set': {'box_usage': True}}
                )
                LOG.info('Updated %s records for cloud_account %s' % (
                    res.modified_count, ca['id']))
        LOG.info('creating index %s', INDEX_NAME)
        self.raw_expenses.create_index(
            [(f, 1) for f in FIELD_LIST], name=INDEX_NAME, background=True
        )

    def downgrade(self):
        _, orgs = self.rest_cl.organization_list()
        for i, org in enumerate(orgs['organizations']):
            _, accs = self.rest_cl.cloud_account_list(org['id'])
            for ca in accs['cloud_accounts']:
                if ca['type'] not in ['aws_cnr', 'azure_cnr', 'alibaba_cnr']:
                    continue
                self.raw_expenses.update_many(
                    filter={'cloud_account_id': ca['id'], 'box_usage': True},
                    update={'$unset': {'box_usage': 1}}
                )
        self.raw_expenses.drop_index(INDEX_NAME)
