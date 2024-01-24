import logging
from diworker.diworker.migrations.base import BaseMigration
from optscale_client.rest_api_client.client_v2 import Client as RestClient

"""
Add organization_id to SearchCloudAccountDates index
"""

LOG = logging.getLogger(__name__)
OLD_INDEX = (
    'SearchCloudAccountDates',
    ['cloud_account_id', '_last_seen_date', '_first_seen_date']
)
NEW_INDEX = (
    'SearchCloudAccountDates2',
    ['cloud_account_id', '_last_seen_date', '_first_seen_date', 'organization_id']
)


class Migration(BaseMigration):
    @property
    def rest_cl(self):
        if self._rest_cl is None:
            self._rest_cl = RestClient(
                url=self.config_cl.restapi_url(), verify=False)
            self._rest_cl.secret = self.config_cl.cluster_secret()
        return self._rest_cl

    @property
    def resources(self):
        return self.db.resources

    def replace_index(self, old_index, new_index):
        existing_indexes = [x['name'] for x in self.resources.list_indexes()]
        old_index_name, _ = old_index
        new_index_name, new_index_keys = new_index
        if new_index_name not in existing_indexes:
            LOG.info('Add %s index', new_index_name)
            self.resources.create_index(
                [(f, 1) for f in new_index_keys],
                name=new_index_name,
                background=True
            )
        if old_index_name in existing_indexes:
            LOG.info('Drop %s index', old_index_name)
            self.resources.drop_index(old_index_name)

    def upgrade(self):
        self.replace_index(OLD_INDEX, NEW_INDEX)

    def downgrade(self):
        self.replace_index(NEW_INDEX, OLD_INDEX)
