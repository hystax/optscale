import logging
from datetime import datetime
from clickhouse_driver import Client as ClickHouseClient
from diworker.diworker.migrations.base import BaseMigration
from optscale_client.rest_api_client.client_v2 import Client as RestClient

"""
Migrate expenses to clickhouse
"""
LOG = logging.getLogger(__name__)
BULK_SIZE = 10000


class Migration(BaseMigration):
    def get_clickhouse_client(self):
        user, password, host, db_name = self.config_cl.clickhouse_params()
        return ClickHouseClient(
            host=host, password=password, database=db_name, user=user)

    def get_rest_client(self):
        rest_client = RestClient(
            url=self.config_cl.restapi_url(), verify=False)
        rest_client.secret = self.config_cl.cluster_secret()
        return rest_client

    def get_mongo_expenses_collection(self):
        return self.db.expenses

    def _write_to_clickhouse(self, clickhouse_cl, bulk):
        clickhouse_cl.execute('INSERT INTO expenses VALUES', bulk)

    def clear_clickhouse_db(self, clickhouse_cl):
        LOG.info('Clearing clickhouse db...')
        clickhouse_cl.execute('ALTER TABLE expenses DELETE WHERE 1')
        clickhouse_cl.execute('OPTIMIZE TABLE expenses FINAL')

    def upgrade(self):
        rest_client = self.get_rest_client()
        expenses_collection = self.get_mongo_expenses_collection()
        clickhouse_client = self.get_clickhouse_client()
        org_ids = []
        for is_demo in [False, True]:
            _, orgs = rest_client.organization_list(dict(is_demo=is_demo))
            org_ids.extend(list(map(lambda x: x['id'], orgs['organizations'])))
        self.clear_clickhouse_db(clickhouse_client)
        for i, organization_id in enumerate(org_ids):
            start_dt = datetime.utcnow()
            _, resp = rest_client.cloud_account_list(organization_id)
            cloud_account_ids = list(map(
                lambda x: x['id'], resp['cloud_accounts']))
            expenses = expenses_collection.find(
                {'cloud_account_id': {'$in': cloud_account_ids}}
            )
            total_expenses = expenses.count_documents()
            bulk = []
            total_migrated = 0
            LOG.info('Migrating expenses for org %s (%s/%s)...' % (
                organization_id, i+1, len(org_ids)))
            for expense in expenses:
                bulk.append({
                    'cloud_account_id': expense['cloud_account_id'],
                    'resource_id': expense['resource_id'],
                    'date': expense['date'],
                    'cost': expense['cost'],
                    'sign': 1,
                })
                if len(bulk) >= BULK_SIZE:
                    total_migrated += len(bulk)
                    self._write_to_clickhouse(clickhouse_client, bulk)
                    org_progress = int(total_migrated * 100 / total_expenses)
                    LOG.info('Expenses for org %s: %s%% migrated' % (
                        organization_id, org_progress))
                    bulk.clear()
            if bulk:
                total_migrated += len(bulk)
                self._write_to_clickhouse(clickhouse_client, bulk)
            execution_time = (datetime.utcnow() - start_dt).total_seconds()
            LOG.info('Expenses for org %s: completed at %s seconds' % (
                organization_id, execution_time))

    def downgrade(self):
        pass
