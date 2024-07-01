import logging
from collections import defaultdict
from datetime import datetime
from rest_api.rest_api_server.controllers.ri_breakdown import (
    RiBreakdownController)
from rest_api.rest_api_server.controllers.base_async import (
    BaseAsyncControllerWrapper)

CH_DB_NAME = 'risp'
LOG = logging.getLogger(__name__)
SEC_IN_HR = 3600
SUPPORTED_CLOUD_TYPES = ['aws_cnr']


class SpBreakdownController(RiBreakdownController):
    RESOURCE_PREFIX = 'sp'

    def get_usage_breakdown(self, start_date, end_date, cloud_account_ids):
        return self.execute_clickhouse(
            """SELECT cloud_account_id, date, sum(usage * sign),
                 sum(on_demand_cost * sign), sum(offer_cost * sign)
               FROM ri_sp_usage
               WHERE cloud_account_id IN cloud_account_ids AND
                 date >= %(start_date)s AND date <= %(end_date)s AND
                 offer_type='sp'
               GROUP BY cloud_account_id, date
               HAVING sum(sign) > 0
               """,
            params={
                'start_date': datetime.fromtimestamp(start_date),
                'end_date': datetime.fromtimestamp(end_date)
            },
            external_tables=[{'name': 'cloud_account_ids',
                              'structure': [('id', 'String')],
                              'data': [{'id': r_id} for r_id in
                                       cloud_account_ids]}]
        )

    def get_flavors(self, cloud_account_ids):
        flavor_rate_map = defaultdict(float)
        flavors = self.execute_clickhouse(
            """SELECT DISTINCT instance_type, sp_rate
               FROM ri_sp_usage
               WHERE cloud_account_id IN cloud_account_ids AND
                 date >= %(start_date)s AND date <= %(end_date)s AND
                 offer_type='sp' and sp_rate!=0
               """,
            params={
                'start_date': datetime.fromtimestamp(self.start_date),
                'end_date': datetime.fromtimestamp(self.end_date)
            },
            external_tables=[{'name': 'cloud_account_ids',
                              'structure': [('id', 'String')],
                              'data': [{'id': r_id} for r_id in
                                       cloud_account_ids]}])
        # todo: it could be two different rates for flavor
        for flavor in flavors:
            flavor_name, sp_rate = flavor
            if sp_rate:
                flavor_rate_map[flavor_name] = sp_rate
        return flavor_rate_map

    def get_cloud_account_usage_stats(self, cloud_account_ids):
        cloud_account_usage = defaultdict(
            lambda: defaultdict(lambda: defaultdict(float)))
        usage_breakdown = self.get_usage_breakdown(
            self.start_date, self.end_date, cloud_account_ids)
        for ch_usage in usage_breakdown:
            (cloud_account_id, date, usage, cost_without_offer,
             cost_with_offer) = ch_usage
            cloud_account_usage[cloud_account_id][date]['usage'] += usage
            cloud_account_usage[cloud_account_id][date][
                'cost_without_offer'] += cost_without_offer
            cloud_account_usage[cloud_account_id][date][
                'cost_with_offer'] += cost_with_offer
        return cloud_account_usage

    def get_overprovision_ch_expenses(
            self, cloud_account_ids, start_date, end_date):
        # SP may be used on several cloud accounts at the same time.
        # Rows from other cloud account have expected_cost=0, so find main
        # cloud account for offers to add offer_cost to main account cost
        query = """SELECT cloud_account_id, date, sum(offer_cost), sum(expected_cost)
                   FROM (
                     SELECT offer_id, date, any(cloud_account_id) as cloud_account_id,
                       sum(offer_cost * sign) AS offer_cost,
                       any(n_expected_cost) AS expected_cost
                     FROM (
                       SELECT offer_id, date, offer_cost, sign,
                         if(expected_cost=0, null, cloud_account_id) as cloud_account_id,
                         if(expected_cost=0, null, expected_cost) as n_expected_cost
                       FROM ri_sp_usage
                       WHERE cloud_account_id IN cloud_account_ids AND
                         date >= %(start_date)s AND date <= %(end_date)s AND
                         offer_type = 'sp')
                     GROUP BY offer_id, date
                     HAVING sum(sign) > 0)
                   GROUP BY cloud_account_id, date"""
        return self.execute_clickhouse(
            query,
            params={'start_date': start_date, 'end_date': end_date},
            external_tables=[{'name': 'cloud_account_ids',
                              'structure': [('id', 'String')],
                              'data': [{'id': r_id} for r_id in
                                       cloud_account_ids]}])

    def fill_overprovisioning(self, flavor_rate_map, cloud_account_usage,
                              start_date, end_date, offer_type='sp'):
        cloud_acc_ids = list(cloud_account_usage.keys())
        sp_acc_date_exp = defaultdict(lambda: defaultdict(float))
        expenses = self.get_overprovision_ch_expenses(
            cloud_acc_ids, start_date, end_date)
        for data in expenses:
            cloud_account_id, date, used, expected = data
            if expected:
                overprov_exp = expected - used
            else:
                overprov_exp = 0
            sp_acc_date_exp[cloud_account_id][date] += overprov_exp
        for cloud_acc_id, date_exp in cloud_account_usage.items():
            for date, data in date_exp.items():
                sp_overprov_exp = sp_acc_date_exp[cloud_acc_id].get(date, 0)
                data['overprovision'] = sp_overprov_exp
                if 'overprovision_hrs' not in data:
                    data.update({'overprovision_hrs': {}})
                for flavor_name, sp_rate in flavor_rate_map.items():
                    sp_usage = sp_overprov_exp / sp_rate
                    data['overprovision_hrs'][flavor_name] = sp_usage
        return cloud_account_usage


class SpBreakdownAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return SpBreakdownController
