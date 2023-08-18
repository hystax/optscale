import logging
from diworker.diworker.migrations.base import BaseMigration
from optscale_client.rest_api_client.client_v2 import Client as RestClient
from diworker.diworker.importers.aws import AWSReportImporter
from itertools import islice

CHUNK_SIZE = 100
LOG = logging.getLogger(__name__)

"""
Update aws system tags for inactive resources
"""


class AWSUpdateSystemTagsImporter(AWSReportImporter):
    @staticmethod
    def chunks(data, chunk_size):
        it = iter(data)
        for i in range(0, len(data), chunk_size):
            yield {key: data[key] for key in islice(it, chunk_size)}

    def save_clean_expenses(self, cloud_account_id, chunk, groupings_map):
        info_map = {
            r_id: self.get_resource_info_from_expenses(expenses)
            for r_id, expenses in chunk.items()
        }
        LOG.info('Saving tags for cloud account %s with resource count %d', cloud_account_id, len(info_map))
        for chunk_dict in self.chunks(info_map, CHUNK_SIZE):
            self.create_resources_if_not_exist(cloud_account_id, chunk_dict)


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

    @property
    def mongo_clean(self):
        return self.db.expenses

    @property
    def mongo_group_month_resource(self):
        return self.db.expenses_group_month_resource

    @property
    def mongo_group_month_ca(self):
        return self.db.expenses_group_month_ca

    def upgrade(self):
        _, organization_list = self.rest_cl.organization_list()
        organizations = organization_list['organizations']
        for org in organizations:
            if org['is_demo']:
                continue
            _, cloud_acc_list = self.rest_cl.cloud_account_list(org['id'], type='aws_cnr')
            cloud_accounts = cloud_acc_list['cloud_accounts']
            for cloud_account in cloud_accounts:
                cloud_account_id = cloud_account['id']
                last_import_at = cloud_account['last_import_at']
                if not last_import_at:
                    continue
                parameters = dict(
                    cloud_account_id=cloud_account_id,
                    rest_cl=self.rest_cl,
                    config_cl=self.config_cl,
                    mongo_raw=self.mongo_raw,
                    mongo_clean=self.mongo_clean,
                    mongo_groupings={
                        'expenses_group_month_resource':
                            self.mongo_group_month_resource,
                        'expenses_group_month_ca':
                            self.mongo_group_month_ca
                    }
                )
                importer = AWSUpdateSystemTagsImporter(**parameters)
                LOG.info('Started updating tags for %s', cloud_account_id)
                groupings_map = {'month_resource': {}, 'month_ca': {}}
                importer.generate_clean_records(groupings_map, regeneration=True)
                LOG.info('Update tags completed')

    def downgrade(self):
        pass
