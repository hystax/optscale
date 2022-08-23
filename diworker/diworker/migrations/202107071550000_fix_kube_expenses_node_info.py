import logging
from diworker.migrations.base import BaseMigration
from rest_api_client.client_v2 import Client as RestClient
from pymongo import UpdateOne

UPDATE_CHUNK_SIZE = 200
LOG = logging.getLogger(__name__)

"""
Update k8s raw expenses node info
"""


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
        _, organization_list = self.rest_cl.organization_list()
        organizations = organization_list['organizations']
        for org in organizations:
            if org['is_demo']:
                continue
            _, cloud_acc_list = self.rest_cl.cloud_account_list(org['id'], type='kubernetes_cnr')
            cloud_accounts = cloud_acc_list['cloud_accounts']
            for cloud_account in cloud_accounts:
                cloud_account_id = cloud_account['id']
                filters = {
                    'cloud_account_id': cloud_account_id,
                    'node_info': {'$exists': True},
                    'total_pods_value': {'$exists': True}
                }
                raw_expenses = self.mongo_raw.find(filters)
                chunk = []
                for raw_expense in raw_expenses:
                    node_name = raw_expense['instance']
                    node_info = raw_expense['node_info']
                    total_pods_value = raw_expense['total_pods_value']
                    chunk.append(UpdateOne(
                        filter={'_id': raw_expense['_id']},
                        update={'$set': {
                            'node_info': node_info[node_name] if
                            node_info.get(node_name) else node_info,
                            'total_pods_value': total_pods_value[node_name]
                            if isinstance(total_pods_value, dict) and
                            total_pods_value.get(node_name) else total_pods_value}}))
                    if len(chunk) == UPDATE_CHUNK_SIZE:
                        self.mongo_raw.bulk_write(chunk)
                        chunk = []
                if chunk:
                    self.mongo_raw.bulk_write(chunk)

    def downgrade(self):
        pass
