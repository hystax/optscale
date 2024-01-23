import logging
from diworker.diworker.migrations.base import BaseMigration
from optscale_client.rest_api_client.client_v2 import Client as RestClient
from datetime import datetime
from pymongo import UpdateOne

"""
Add first_seen_date and last_seen_date fields into resources with search index
"""

LOG = logging.getLogger(__name__)
CHUNK_SIZE = 200
INDEXES = {
    'SearchCloudAccountDates': (
        ['cloud_account_id', '_last_seen_date', '_first_seen_date'],
        None
    ),
    'SearchPoolDates': (
        ['pool_id', '_last_seen_date', '_first_seen_date'],
        None
    ),
    'PoolRecommendationsRunTime': (
        ['pool_id', 'recommendations.run_timestamp'],
        {'recommendations.run_timestamp': {'$exists': True}}
    )
}


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

    @staticmethod
    def to_start_date(timestamp):
        return datetime.utcfromtimestamp(timestamp).replace(
            hour=0, minute=0, second=0, microsecond=0)

    def add_date_fields(self):
        for is_demo in [False, True]:
            _, orgs = self.rest_cl.organization_list(dict(is_demo=is_demo))
            for i, org in enumerate(orgs['organizations']):
                LOG.info('Migrating resources for org %s (%s/%s)...' % (
                    org['id'], i + 1, len(orgs['organizations'])))
                _, accs = self.rest_cl.cloud_account_list(org['id'])
                chunk = []

                iter_filter = [{'organization_id': org['id']}]
                iter_filter.extend([
                    {'cloud_account_id': ca['id']} for ca in accs['cloud_accounts']
                ])
                for filt in iter_filter:
                    res = self.resources.find({
                        '$and': [
                            filt,
                            {
                                '$or': [
                                    {'_first_seen_date': {'$exists': False}},
                                    {'_last_seen_date': {'$exists': False}},
                                ]
                            }
                        ]

                    },
                        ['first_seen', 'last_seen']
                    )
                    for r in res:
                        chunk.append(UpdateOne(
                            filter={'_id': r['_id']},
                            update={'$set': {
                                '_first_seen_date': self.to_start_date(
                                    r.get('first_seen', 0)),
                                '_last_seen_date': self.to_start_date(
                                    r.get('last_seen', 0)),
                            }}
                        ))
                        if len(chunk) >= CHUNK_SIZE:
                            self.resources.bulk_write(chunk)
                            chunk.clear()
                if chunk:
                    self.resources.bulk_write(chunk)
                    chunk.clear()

    def add_indexes(self):
        existing_indexes = [x['name'] for x in self.resources.list_indexes()]
        for index_name, (field_list, partial_exp) in INDEXES.items():
            if index_name not in existing_indexes:
                LOG.info('Creating search index %s in resource collection',
                         index_name)
                body = dict(
                    name=index_name,
                    background=True
                )
                if partial_exp:
                    body['partialFilterExpression'] = partial_exp
                self.resources.create_index(
                    [(f, 1) for f in field_list], **body)

    def remove_indexes(self):
        existing_indexes = [x['name'] for x in self.resources.list_indexes()]
        for index_name in INDEXES.keys():
            if index_name in existing_indexes:
                self.resources.drop_index(index_name)

    def upgrade(self):
        self.add_indexes()
        self.add_date_fields()

    def downgrade(self):
        self.remove_indexes()
