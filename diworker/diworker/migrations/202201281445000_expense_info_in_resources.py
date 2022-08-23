import logging
from pymongo import UpdateOne
from diworker.migrations.base import BaseMigration
from clickhouse_driver import Client as ClickHouseClient
from rest_api_client.client_v2 import Client as RestClient
from diworker.utils import retry_mongo_upsert

"""
Add total cost and last expense info in mongo resources
"""

LOG = logging.getLogger(__name__)
BULK_SIZE = 10000


class Migration(BaseMigration):
    def get_clickhouse_client(self):
        user, password, host, db_name = self.config_cl.clickhouse_params()
        return ClickHouseClient(
            host=host, password=password, database=db_name, user=user)

    @property
    def rest_cl(self):
        if self._rest_cl is None:
            self._rest_cl = RestClient(
                url=self.config_cl.restapi_url(), verify=False)
            self._rest_cl.secret = self.config_cl.cluster_secret()
        return self._rest_cl

    @property
    def mongo_resources(self):
        return self.db.resources

    def upgrade(self):
        cloud_account_ids = []
        clickhouse_cl = self.get_clickhouse_client()
        for is_demo in [False, True]:
            _, orgs = self.rest_cl.organization_list(dict(is_demo=is_demo))
            org_ids = list(map(lambda x: x['id'], orgs['organizations']))
            for org in org_ids:
                _, accs = self.rest_cl.cloud_account_list(org)
                cloud_account_ids.extend(list(map(
                    lambda x: x['id'], accs['cloud_accounts'])))
        for i, cloud_account_id in enumerate(cloud_account_ids):
            LOG.info('Processing cloud account %s (%s/%s)' % (
                cloud_account_id, i, len(cloud_account_ids)))
            resources = self.mongo_resources.find(
                {'cloud_account_id': cloud_account_id}, [])
            bulk_ids = []
            for r in resources:
                bulk_ids.append(r['_id'])
                if len(bulk_ids) == BULK_SIZE:
                    self.process_bulk_ids(
                        clickhouse_cl, cloud_account_id, bulk_ids)
                    bulk_ids.clear()
            if bulk_ids:
                self.process_bulk_ids(
                    clickhouse_cl, cloud_account_id, bulk_ids)

    def get_totals(self, clickhouse_cl, cloud_account_id, bulk):
        total_expenses = clickhouse_cl.execute(
            query="""
                SELECT resource_id, max(date), sum(cost*sign)
                FROM expenses
                JOIN resources ON expenses.cloud_account_id = %(cloud_account_id)s
                    AND expenses.resource_id = resources.id
                GROUP BY resource_id
            """,
            params={
                'cloud_account_id': cloud_account_id
            },
            external_tables=[{
                'name': 'resources',
                'structure': [
                    ('id', 'String'),
                ],
                'data': [{'id': k} for k in bulk]
            }]
        )
        return {r[0]: (r[1], r[2]) for r in total_expenses}

    @staticmethod
    def get_last_expenses(clickhouse_cl, cloud_account_id,
                          resource_totals_map):
        last_expenses = clickhouse_cl.execute(
            query="""
                SELECT resource_id, sum(cost*sign)
                FROM expenses
                JOIN resources
                    ON expenses.cloud_account_id = %(cloud_account_id)s
                    AND expenses.resource_id = resources.id
                    AND expenses.date = resources.date
                GROUP BY resource_id
            """,
            params={
                'cloud_account_id': cloud_account_id
            },
            external_tables=[{
                'name': 'resources',
                'structure': [
                    ('id', 'String'),
                    ('date', 'DateTime')
                ],
                'data': [
                    {
                        'id': k,
                        'date': v[0]
                    } for k, v in resource_totals_map.items()
                ]
            }]
        )
        return {r[0]: r[1] for r in last_expenses}

    def process_bulk_ids(self, clickhouse_cl, cloud_account_id, bulk):
        resource_totals_map = self.get_totals(
            clickhouse_cl, cloud_account_id, bulk)
        resource_last_expense = self.get_last_expenses(
            clickhouse_cl, cloud_account_id, resource_totals_map)
        op_bulk = []
        for r_id in bulk:
            total_cost = 0
            last_date = None
            resource_total = resource_totals_map.get(r_id)
            if resource_total:
                last_date, total_cost = resource_total
            updates = {
                'total_cost': total_cost
            }
            last_expense = resource_last_expense.get(r_id)
            if last_expense:
                updates['last_expense'] = {
                    'date': int(last_date.timestamp()),
                    'cost': last_expense
                }
            op_bulk.append(
                UpdateOne(
                    filter={
                        'cloud_account_id': cloud_account_id,
                        '_id': r_id
                    },
                    update={'$set': updates}
                )
            )
        if op_bulk:
            retry_mongo_upsert(self.mongo_resources.bulk_write, op_bulk)

    def downgrade(self):
        cloud_account_ids = []
        for is_demo in [False, True]:
            _, orgs = self.rest_cl.organization_list(dict(is_demo=is_demo))
            org_ids = list(map(lambda x: x['id'], orgs['organizations']))
            for org in org_ids:
                _, accs = self.rest_cl.cloud_account_list(org)
                cloud_account_ids.extend(list(map(
                    lambda x: x['id'], accs['cloud_accounts'])))
        for cloud_account_id in cloud_account_ids:
            retry_mongo_upsert(self.mongo_resources.update_many(
                filter={
                    'cloud_account_id': cloud_account_id
                },
                update={
                    '$unset': {
                        'total_cost': 1,
                        'last_expense': 1
                    }
                }
            ))
