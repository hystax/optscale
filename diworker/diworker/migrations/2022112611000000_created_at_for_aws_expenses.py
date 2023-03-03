import logging
from datetime import datetime, timezone
from diworker.migrations.base import BaseMigration
from pymongo import UpdateOne
from rest_api_client.client_v2 import Client as RestClient

"""
Set created_at for AWS expenses and create index AWSRawExpenses

"""
CHUNK_SIZE = 200
LOG = logging.getLogger(__name__)
INDEX_NAME = 'AWSRawExpenses'
INDEX_FIELDS = ['cloud_account_id', 'lineItem/LineItemDescription',
                'resource_id', 'identity/LineItemId']


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

    def create_index(self, index_fields_list):
        indexes_info = self.mongo_raw.index_information()
        db_index = indexes_info.get(INDEX_NAME)
        if not db_index:
            LOG.info('Creating index %s' % INDEX_NAME)
            self.mongo_raw.create_index(
                [(f, 1) for f in index_fields_list],
                name=INDEX_NAME,
                background=True,
            )
        else:
            db_key = set(db_index['key'])
            key = set((f, 1) for f in index_fields_list)
            if db_index.get('unique') is True or db_key != key:
                LOG.info('Index %s exists. Will drop and recreate '
                         'it' % INDEX_NAME)
                self.mongo_raw.drop_index(INDEX_NAME)
                self.mongo_raw.create_index(
                    [(f, 1) for f in index_fields_list],
                    name=INDEX_NAME,
                    background=True,
                )
            else:
                LOG.info('Index %s already exists' % INDEX_NAME)

    def upgrade(self):
        now = int(datetime.utcnow().timestamp())
        cloud_account_ids = self.get_cloud_account_ids()
        for i, cloud_account_id in enumerate(cloud_account_ids):
            LOG.info('Started updating raw expenses for '
                     'cloud account {0} ({1}/{2})'.format(
                        cloud_account_id, i + 1, len(cloud_account_ids)))
            self.mongo_raw.update_many(
                filter={'cloud_account_id': cloud_account_id},
                update={'$set': {'created_at': now}})
        self.create_index(INDEX_FIELDS)

    def downgrade(self):
        cloud_account_ids = self.get_cloud_account_ids()
        indexes_info = self.mongo_raw.index_information()
        self.mongo_raw.update_many(
            filter={'cloud_account_id': {'$in': cloud_account_ids}},
            update={'$unset': {'created_at': ''}})
        db_index = indexes_info.get(INDEX_NAME)
        if db_index:
            self.mongo_raw.drop_index(INDEX_NAME)
