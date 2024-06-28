import logging
from collections import defaultdict
from optscale_client.rest_api_client.client_v2 import Client as RestClient
from risp.risp_worker.migrations.base import MigrationBase

BULK_SIZE = 1000
LOG = logging.getLogger(__name__)


class Migration(MigrationBase):

    def update_table(self):
        # default value is 0
        self.clickhouse_client.execute(
            """ALTER TABLE ri_sp_usage ADD COLUMN
            IF NOT EXISTS sp_rate FLOAT AFTER ri_norm_factor""")
        # default value is ''
        self.clickhouse_client.execute(
            """ALTER TABLE ri_sp_usage ADD COLUMN
            IF NOT EXISTS instance_type String AFTER date""")

    def insert_ch_expenses(self, expenses):
        self.clickhouse_client.execute(
            """INSERT INTO ri_sp_usage VALUES""", expenses)

    def query_raw_expenses(self, cloud_account_id, resource_id, offer_ids,
                           dates, offer_type):
        changes_map = defaultdict(lambda: defaultdict(
            lambda: defaultdict(dict)))
        if offer_type == 'ri':
            expenses = self.mongo_client.restapi.raw_expenses.find({
                'cloud_account_id': cloud_account_id,
                'resource_id': resource_id,
                'start_date': {'$in': dates},
                'box_usage': True,
                'lineItem/LineItemType': 'DiscountedUsage'},
                # todo: check fields
                {'start_date': 1, 'product/instanceType': 1,
                 'lineItem/LineItemDescription': 1,
                 'reservation/ReservationARN': 1,
                 'savingsPlan/SavingsPlanRate': 1})
            for expense in expenses:
                ri_id = expense['reservation/ReservationARN']
                ri_id = ri_id[ri_id.find('/') + 1:]
                if ri_id in offer_ids:
                    changes_map[resource_id][expense['start_date']][ri_id] = {
                        'instance_type': expense.get(
                            'product/instanceType') or expense.get(
                            'lineItem/LineItemDescription'),
                        'sp_rate': float(expense.get(
                             'savingsPlan/SavingsPlanRate') or 0)
                    }
        elif offer_type == 'sp':
            expenses = self.mongo_client.restapi.raw_expenses.find({
                'cloud_account_id': cloud_account_id,
                'resource_id': {'$in': offer_ids},
                'start_date': {'$in': dates},
                'box_usage': True,
                'lineItem/LineItemType': 'SavingsPlanCoveredUsage',
                'lineItem/ResourceId': resource_id},
                {'start_date': 1, 'product/instanceType': 1,
                 'lineItem/LineItemDescription': 1,
                 'lineItem/ResourceId': 1,
                 'savingsPlan/SavingsPlanARN': 1,
                 'savingsPlan/SavingsPlanRate': 1})
            for expense in expenses:
                sp_id = expense['savingsPlan/SavingsPlanARN']
                sp_id = sp_id[sp_id.find('/') + 1:]
                if sp_id in offer_ids:
                    resource_id = expense['lineItem/ResourceId']
                    changes_map[resource_id][expense['start_date']][sp_id] = {
                        'instance_type': expense.get(
                            'product/instanceType') or expense.get(
                            'lineItem/LineItemDescription'),
                        'sp_rate': float(expense.get(
                            'savingsPlan/SavingsPlanRate') or 0)
                    }
        return changes_map

    def fill_records(self, cloud_account_id, offer_type):
        ch_query = """SELECT resource_id, date, offer_id, instance_type,
                        sum(offer_cost * sign), sum(on_demand_cost * sign),
                        sum(usage * sign), any(ri_norm_factor), any(sp_rate),
                        sum(expected_cost * sign)
                      FROM ri_sp_usage
                      WHERE cloud_account_id=%(cloud_account_id)s
                          AND offer_type=%(offer_type)s
                      GROUP BY resource_id, date, offer_id, instance_type
                      HAVING sum(sign) > 0"""
        expenses = self.clickhouse_client.execute(
            ch_query, params={'cloud_account_id': cloud_account_id,
                              'offer_type': offer_type})
        ex_ch_exp_map = {}
        for expense in expenses:
            (resource_id, date, offer_id, instance_type, offer_cost,
             on_demand_cost, usage, ri_norm_factor, sp_rate,
             expected_cost) = expense
            exp_values = (instance_type, offer_cost, on_demand_cost, usage,
                          ri_norm_factor, sp_rate, expected_cost)
            ex_ch_exp_map.update({resource_id: {date: {offer_id: exp_values}}})

        changes_map = {}
        for res_id, data in ex_ch_exp_map.items():
            offer_ids = set(v for values in data.values() for v in values)
            dates = list(data.keys())
            changes_map.update(self.query_raw_expenses(
                cloud_account_id, res_id, list(offer_ids), dates, offer_type))

        ch_inserts = []
        for resource_id, resource_data in changes_map.items():
            for date, offer_data in resource_data.items():
                for offer_id, changes in offer_data.items():
                    ex_ch_expense = ex_ch_exp_map.get(resource_id, {}).get(
                        date, {}).get(offer_id)
                    if ex_ch_expense:
                        (ex_inst_type, offer_cost, on_demand_cost,
                         usage, ri_norm_factor, sp_rate,
                         expected_cost) = ex_ch_expense
                        # cancel record for current
                        ch_inserts.append({
                            'cloud_account_id': cloud_account_id,
                            'resource_id': resource_id,
                            'date': date,
                            'instance_type': ex_inst_type,
                            'offer_id': offer_id,
                            'offer_type': offer_type,
                            'on_demand_cost': on_demand_cost,
                            'offer_cost': offer_cost,
                            'usage': usage,
                            'ri_norm_factor': ri_norm_factor,
                            'sp_rate': sp_rate,
                            'expected_cost': expected_cost,
                            'sign': -1
                        })
                        instance_type = offer_data.get('instance_type', '')
                        sp_rate = offer_data.get('sp_rate', 0)
                        # new record
                        ch_inserts.append({
                            'cloud_account_id': cloud_account_id,
                            'resource_id': resource_id,
                            'date': date,
                            'instance_type': instance_type,
                            'offer_id': offer_id,
                            'offer_type': offer_type,
                            'on_demand_cost': on_demand_cost,
                            'offer_cost': offer_cost,
                            'usage': usage,
                            'ri_norm_factor': ri_norm_factor,
                            'sp_rate': sp_rate,
                            'expected_cost': expected_cost,
                            'sign': 1
                        })
                        if len(ch_inserts) >= BULK_SIZE:
                            self.insert_ch_expenses(ch_inserts)
                            ch_inserts.clear()
        if ch_inserts:
            self.insert_ch_expenses(ch_inserts)
            ch_inserts.clear()

    def upgrade(self):
        self.update_table()

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
                self.fill_records(cloud_account_id, 'ri')
                self.fill_records(cloud_account_id, 'sp')

        self.clickhouse_client.execute(
            """OPTIMIZE TABLE ri_sp_usage FINAL""")
