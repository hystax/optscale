import logging
from datetime import timedelta
from optscale_client.rest_api_client.client_v2 import Client as RestClient
from risp.risp_worker.migrations.base import MigrationBase


LOG = logging.getLogger(__name__)
SECONDS_IN_HOUR = 3600


class Migration(MigrationBase):
    def get_ch_expenses(self, cloud_account_id):
        dates = self.clickhouse_client.execute(
            """SELECT DISTINCT date FROM uncovered_usage
               WHERE cloud_account_id=%(cloud_account_id)s""",
            params={'cloud_account_id': cloud_account_id})
        return [x[0] for x in dates]

    @staticmethod
    def dates_ranges(start_date, end_date):
        dates = []
        while start_date <= end_date:
            dates.append(start_date)
            start_date += timedelta(days=1)
        return dates

    def fill_date(self, cloud_account_id, start_date):
        new_expenses = []
        expenses = self.mongo_client.restapi.raw_expenses.find({
            'cloud_account_id': cloud_account_id,
            'start_date': start_date,
            'box_usage': True,
            'lineItem/LineItemType': 'Usage'},
            {
                'start_date': 1,
                'resource_id': 1,
                'pricing/unit': 1,
                'lineItem/UsageAmount': 1,
                'pricing/publicOnDemandCost': 1,
                'product/operatingSystem': 1,
                'product/instanceType': 1,
                'product/region': 1,
                'lineItem/AvailabilityZone': 1
            }
        )
        for expense in expenses:
            cost = float(expense['pricing/publicOnDemandCost'])
            usage_hrs = float(expense['lineItem/UsageAmount'])
            if 'second' in expense['pricing/unit'].lower():
                usage_hrs = usage_hrs / SECONDS_IN_HOUR
            os = expense.get('product/operatingSystem', '')
            instance_type = expense.get('product/instanceType', '')
            location = expense.get('lineItem/AvailabilityZone') or expense.get(
                'product/region', '')
            new_expenses.append({
                'cloud_account_id': cloud_account_id,
                'date': expense['start_date'],
                'resource_id': expense['resource_id'],
                'instance_type': instance_type,
                'os': os,
                'location': location,
                'cost': cost,
                'usage': usage_hrs,
                'sign': 1
            })
        self.clickhouse_client.execute(
            'INSERT INTO uncovered_usage VALUES', new_expenses)

    def fill_table(self):
        rest_cl = RestClient(
            url=self.config_client.restapi_url(),
            secret=self.config_client.cluster_secret())
        _, orgs = rest_cl.organization_list({'is_demo': False})
        organizations = orgs['organizations']
        for i, org in enumerate(organizations):
            org_id = org['id']
            LOG.info('Start processing for organization %s (%s/%s)',
                     org_id, i + 1, len(organizations))
            _, cloud_accs = rest_cl.cloud_account_list(org_id, type='aws_cnr')
            cloud_accounts = cloud_accs['cloud_accounts']
            for j, cloud_account in enumerate(cloud_accounts):
                cloud_account_id = cloud_account['id']
                LOG.info('Start processing for cloud account %s (%s/%s)',
                         cloud_account_id, j + 1, len(cloud_accounts))
                min_max_date = list(
                    self.mongo_client.restapi.raw_expenses.aggregate([
                        {'$match': {'cloud_account_id': cloud_account_id,
                                    'box_usage': True}},
                        {'$group': {
                            '_id': None,
                            'min': {'$min': '$start_date'},
                            'max': {'$max': '$start_date'}
                        }}
                    ]))
                if min_max_date:
                    min_date = min_max_date[0]['min']
                    max_date = min_max_date[0]['max']
                    dates = self.dates_ranges(min_date, max_date)
                    exist_dates = self.get_ch_expenses(cloud_account_id)
                    for date in exist_dates:
                        dates.remove(date)
                    for date in dates:
                        self.fill_date(cloud_account_id, date)

    def upgrade(self):
        query = """CREATE TABLE IF NOT EXISTS uncovered_usage (
                             cloud_account_id String,
                             resource_id String,
                             date DateTime,
                             instance_type String,
                             os String,
                             location String,
                             usage Float64,
                             cost Float64,
                             sign Int8)
                           ENGINE = CollapsingMergeTree(sign)
                           PARTITION BY toYYYYMM(date)
                           ORDER BY (cloud_account_id, resource_id, date)"""
        self.clickhouse_client.execute(query)
        self.fill_table()
