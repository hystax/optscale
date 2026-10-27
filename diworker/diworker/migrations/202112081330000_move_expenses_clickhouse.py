import logging
from datetime import datetime
import clickhouse_connect

from diworker.diworker.migrations.base import BaseMigration
from optscale_client.rest_api_client.client_v2 import Client as RestClient

"""
Migrate expenses to clickhouse
"""
LOG = logging.getLogger(__name__)
BULK_SIZE = 10000


class Migration(BaseMigration):
    def get_clickhouse_client(self):
        user, password, host, db_name, port, secure = (
            self.config_cl.clickhouse_params())
        return clickhouse_connect.get_client(
                host=host, password=password, database=db_name, user=user,
                port=port, secure=secure)

    def get_rest_client(self):
        rest_client = RestClient(
            url=self.config_cl.restapi_url(), verify=False)
        rest_client.secret = self.config_cl.cluster_secret()
        return rest_client

    def get_mongo_expenses_collection(self):
        return self.db.expenses

    def _write_to_clickhouse(self, clickhouse_cl, bulk, column_names):
        clickhouse_cl.insert('expenses', bulk, column_names)

    def clear_clickhouse_db(self, clickhouse_cl):
        LOG.info('Clearing clickhouse db...')
        clickhouse_cl.query('ALTER TABLE expenses DELETE WHERE 1')
        clickhouse_cl.query('OPTIMIZE TABLE expenses FINAL')

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
            start_dt = datetime.now()
            _, resp = rest_client.cloud_account_list(organization_id)
            cloud_account_ids = list(map(
                lambda x: x['id'], resp['cloud_accounts']))
            expenses_filter = {'cloud_account_id': {'$in': cloud_account_ids}}
            total_expenses = expenses_collection.count_documents(
                expenses_filter)
            expenses = expenses_collection.find(expenses_filter)
            bulk = []
            total_migrated = 0
            LOG.info('Migrating expenses for org %s (%s/%s)...' % (
                organization_id, i+1, len(org_ids)))
            column_names = [
                'cloud_account_id', 'resource_id', 'date', 'cost', 'sign'
            ]
            for expense in expenses:
                bulk.append([
                    expense['cloud_account_id'],
                    expense['resource_id'],
                    expense['date'],
                    expense['cost'],
                    1,
                ])
                if len(bulk) >= BULK_SIZE:
                    total_migrated += len(bulk)
                    self._write_to_clickhouse(
                        clickhouse_client, bulk, column_names)
                    org_progress = int(total_migrated * 100 / total_expenses)
                    LOG.info('Expenses for org %s: %s%% migrated' % (
                        organization_id, org_progress))
                    bulk.clear()
            if bulk:
                total_migrated += len(bulk)
                self._write_to_clickhouse(clickhouse_client, bulk,
                                          column_names)
            execution_time = (datetime.now() - start_dt).total_seconds()
            LOG.info('Expenses for org %s: completed at %s seconds' % (
                organization_id, execution_time))

    def downgrade(self):
        pass
