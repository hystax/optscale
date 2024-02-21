import logging
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from optscale_client.rest_api_client.client_v2 import Client as RestClient
from risp.risp_worker.migrations.base import MigrationBase

HRS_IN_DAY = 24
SEC_IN_HR = 3600
LOG = logging.getLogger(__name__)


class Migration(MigrationBase):

    def update_table(self):
        # default value is 0
        self.clickhouse_client.execute(
            """ALTER TABLE ri_sp_usage ADD COLUMN
            IF NOT EXISTS expected_cost FLOAT AFTER ri_norm_factor""")

    def insert_ch_expenses(self, expenses):
        self.clickhouse_client.execute(
            """INSERT INTO ri_sp_usage VALUES""", expenses)

    @staticmethod
    def dates_range(start_date, end_date):
        dates = []
        date = start_date.replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
        while date <= end_date:
            dates.append(date)
            date += timedelta(days=1)
        return dates

    def ri_expected_cost_per_day(self, cloud_account_id, resource_ids):
        ri_date_expected_cost = defaultdict(lambda: defaultdict(float))
        expenses = self.mongo_client.restapi.raw_expenses.find(
            {
                'cloud_account_id': cloud_account_id,
                'lineItem/LineItemType': 'RIFee',
                'resource_id': {'$in': resource_ids},
                'lineItem/UsageStartDate': {'$exists': True}
            },
            {
                'start_date': 1,
                'end_date': 1,
                'reservation/TotalReservedNormalizedUnits': 1,
                'lineItem/NormalizationFactor': 1,
                'lineItem/UnblendedCost': 1,
                'lineItem/UsageStartDate': 1,
                'resource_id': 1
            })
        for expense in expenses:
            total_norm_hours = float(expense[
                'reservation/TotalReservedNormalizedUnits'])
            cost_per_n_hr = float(expense[
                                'lineItem/UnblendedCost']) / total_norm_hours
            norm_factor = float(expense['lineItem/NormalizationFactor'])
            exp_start_date = expense['start_date'].replace(tzinfo=timezone.utc)
            exp_end_date = expense['end_date'].replace(tzinfo=timezone.utc)
            dates = self.dates_range(exp_start_date, exp_end_date)
            for date in dates:
                ri_date_expected_cost[expense['resource_id']][
                    date] = HRS_IN_DAY * norm_factor * cost_per_n_hr
            # the first RIFee expense not includes hours from start of the
            # month to RI purchasing time
            period_start = datetime.strptime(
                expense['lineItem/UsageStartDate'], '%Y-%m-%dT%H:%M:%SZ'
            ).replace(tzinfo=timezone.utc)
            if period_start > exp_start_date:
                not_used_hrs = (period_start - exp_start_date
                                ).total_seconds() / SEC_IN_HR
                ri_date_expected_cost[expense['resource_id']][
                    exp_start_date] = (HRS_IN_DAY - not_used_hrs
                                       ) * norm_factor * cost_per_n_hr
        return ri_date_expected_cost

    def process_records(self, cloud_account_id, offer_cost_per_day,
                        offer_type):
        ch_query = """SELECT resource_id, sum(offer_cost * sign),
                        sum(on_demand_cost * sign), sum(usage * sign),
                        any(ri_norm_factor)
                      FROM ri_sp_usage
                      WHERE cloud_account_id=%(cloud_account_id)s AND
                        date=%(date)s AND offer_id=%(offer_id)s AND
                        expected_cost=0
                      GROUP BY resource_id
                      HAVING sum(sign) > 0"""
        for ri_id, data in offer_cost_per_day.items():
            new_ch_expenses = []
            for date, cost in data.items():
                expenses = self.clickhouse_client.execute(
                    ch_query, params={'cloud_account_id': cloud_account_id,
                                      'date': date,
                                      'offer_id': ri_id})
                if not expenses:
                    new_ch_expenses.append({
                        'cloud_account_id': cloud_account_id,
                        'resource_id': '',
                        'date': date,
                        'offer_id': ri_id,
                        'offer_type': offer_type,
                        'on_demand_cost': 0,
                        'offer_cost': 0,
                        'usage': 0,
                        'ri_norm_factor': 0,
                        'expected_cost': cost,
                        'sign': 1
                    })
                for expense in expenses:
                    (res_id, offer_cost, on_demand_cost, usage,
                     ri_factor) = expense
                    new_ch_expenses.append({
                        'cloud_account_id': cloud_account_id,
                        'resource_id': res_id,
                        'date': date,
                        'offer_id': ri_id,
                        'offer_type': offer_type,
                        'on_demand_cost': on_demand_cost,
                        'offer_cost': offer_cost,
                        'usage': usage,
                        'ri_norm_factor': ri_factor,
                        'expected_cost': 0,
                        'sign': -1
                    })
                    new_ch_expenses.append({
                        'cloud_account_id': cloud_account_id,
                        'resource_id': res_id,
                        'date': date,
                        'offer_id': ri_id,
                        'offer_type': offer_type,
                        'on_demand_cost': on_demand_cost,
                        'offer_cost': offer_cost,
                        'usage': usage,
                        'ri_norm_factor': ri_factor,
                        'expected_cost': cost,
                        'sign': 1
                    })
            self.insert_ch_expenses(new_ch_expenses)
            new_ch_expenses.clear()

    def update_ri_records(self, cloud_account_id):
        ri = self.mongo_client.restapi.resources.find({
            'cloud_account_id': cloud_account_id,
            'resource_type': 'Reserved Instances'
        }, {'cloud_resource_id': 1})
        ri_ids = [x['cloud_resource_id'] for x in ri]
        ri_cost_per_day = self.ri_expected_cost_per_day(cloud_account_id,
                                                        ri_ids)
        self.process_records(cloud_account_id, ri_cost_per_day, 'ri')

    def sp_expected_cost_per_day(self, cloud_account_id, sp_ids):
        sp_date_expected_cost = defaultdict(lambda: defaultdict(float))
        expenses = self.mongo_client.restapi.raw_expenses.find({
                    'cloud_account_id': cloud_account_id,
                    'resource_id': {'$in': sp_ids},
                    'lineItem/LineItemType': 'SavingsPlanRecurringFee',
                    'lineItem/UsageStartDate': {'$exists': True}
                }, {'start_date': 1, 'savingsPlan/TotalCommitmentToDate': 1,
                    'resource_id': 1})
        for expense in expenses:
            date = expense['start_date'].replace(tzinfo=timezone.utc)
            sp_date_expected_cost[expense['resource_id']][date] = float(
                expense['savingsPlan/TotalCommitmentToDate'])
        return sp_date_expected_cost

    def update_sp_records(self, cloud_account_id):
        sp = self.mongo_client.restapi.resources.find({
            'cloud_account_id': cloud_account_id,
            'resource_type': 'Savings Plan'
        }, {'cloud_resource_id': 1})
        sp_ids = [x['cloud_resource_id'] for x in sp]
        sp_cost_per_day = self.sp_expected_cost_per_day(cloud_account_id,
                                                        sp_ids)
        self.process_records(cloud_account_id, sp_cost_per_day, 'sp')

    def fill_expected_cost(self):
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
                self.update_ri_records(cloud_account_id)
                self.update_sp_records(cloud_account_id)

    def upgrade(self):
        self.update_table()
        self.fill_expected_cost()
        self.clickhouse_client.execute(
            """OPTIMIZE TABLE ri_sp_usage FINAL""")
