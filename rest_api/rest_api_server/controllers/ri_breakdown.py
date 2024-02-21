import logging
import json
from clickhouse_driver import Client as ClickHouseClient
from collections import defaultdict
from datetime import datetime, timedelta
from rest_api.rest_api_server.controllers.expense import CleanExpenseController
from rest_api.rest_api_server.controllers.base_async import (
    BaseAsyncControllerWrapper)

CH_DB_NAME = 'risp'
LOG = logging.getLogger(__name__)
SEC_IN_HR = 3600
SUPPORTED_CLOUD_TYPES = ['aws_cnr']
RI_FACTOR_MAP = {
    'nano': 0.25,
    'micro': 0.5,
    'small': 1,
    'medium': 2,
    'large': 4,
    'xlarge': 8,
    '2xlarge': 16,
    '4xlarge': 32,
    '8xlarge': 64,
    '10xlarge': 80,
    '16xlarge': 128,
    '32xlarge': 256
}


class RiBreakdownController(CleanExpenseController):
    RESOURCE_PREFIX = 'ri'

    @property
    def clickhouse_client(self):
        if not self._clickhouse_client:
            user, password, host, _ = self._config.clickhouse_params()
            self._clickhouse_client = ClickHouseClient(
                host=host, password=password, database=CH_DB_NAME, user=user)
        return self._clickhouse_client

    def get_usage_breakdown(self, cloud_account_ids):
        return self.execute_clickhouse(
            """SELECT cloud_account_id, date, sum(usage * sign),
                   sum(usage * ri_norm_factor * sign),
                   sum(on_demand_cost * sign), sum(offer_cost * sign)
               FROM ri_sp_usage
               WHERE cloud_account_id IN cloud_account_ids AND
                 date >= %(start_date)s AND date <= %(end_date)s AND
                 offer_type='ri'
               GROUP BY cloud_account_id, date
               HAVING sum(sign) > 0
               """,
            params={
                'start_date': datetime.fromtimestamp(self.start_date),
                'end_date': datetime.fromtimestamp(self.end_date)
            },
            external_tables=[{'name': 'cloud_account_ids',
                              'structure': [('id', 'String')],
                              'data': [{'id': r_id} for r_id in
                                       cloud_account_ids]}])

    def get_total_stats(self, cloud_account_ids):
        cloud_account_total = defaultdict(lambda: defaultdict(
            lambda: defaultdict(float)))
        uncovered = self.execute_clickhouse(
            """SELECT cloud_account_id, date, sum(cost * sign),
                 sum(usage * sign)
               FROM uncovered_usage
               WHERE cloud_account_id IN cloud_account_ids AND
                 date >= %(start_date)s AND date <= %(end_date)s
               GROUP BY cloud_account_id, date
               HAVING sum(sign) > 0
               """,
            params={
                'start_date': datetime.fromtimestamp(self.start_date),
                'end_date': datetime.fromtimestamp(self.end_date)
            },
            external_tables=[{'name': 'cloud_account_ids',
                              'structure': [('id', 'String')],
                              'data': [{'id': r_id} for r_id in
                                       cloud_account_ids]}])
        for row in uncovered:
            (cloud_account_id, date, cost, usage) = row
            cloud_account_total[cloud_account_id][date]['usage'] = usage
            cloud_account_total[cloud_account_id][date][
                'cost_with_offer'] = cost
            cloud_account_total[cloud_account_id][date][
                'cost_without_offer'] = cost
        covered = self.execute_clickhouse(
            """SELECT cloud_account_id, date, sum(on_demand_cost * sign),
                 sum(offer_cost * sign), sum(usage * sign)
               FROM ri_sp_usage
               WHERE cloud_account_id IN cloud_account_ids AND
                 date >= %(start_date)s AND date <= %(end_date)s
               GROUP BY cloud_account_id, date
               HAVING sum(sign) > 0
               """,
            params={
                'start_date': datetime.fromtimestamp(self.start_date),
                'end_date': datetime.fromtimestamp(self.end_date)
            },
            external_tables=[{'name': 'cloud_account_ids',
                              'structure': [('id', 'String')],
                              'data': [{'id': r_id} for r_id in
                                       cloud_account_ids]}])
        for row in covered:
            (cloud_account_id, date, on_demand_cost, offer_cost, usage) = row
            cloud_account_total[cloud_account_id][date]['usage'] += usage
            cloud_account_total[cloud_account_id][date][
                'cost_with_offer'] += offer_cost
            cloud_account_total[cloud_account_id][date][
                'cost_without_offer'] += on_demand_cost
        return cloud_account_total

    def get_flavors(self, cloud_account_ids):
        flavor_factor_map = defaultdict(float)
        expenses = self.raw_expenses_collection.distinct(
            'product/instanceType', {
                'cloud_account_id': {'$in': cloud_account_ids},
                'start_date': {
                    '$gte': datetime.fromtimestamp(self.start_date),
                    '$lt': datetime.fromtimestamp(self.end_date)},
                'box_usage': True,
                'lineItem/LineItemType': 'DiscountedUsage'
            }
        )
        for flavor_name in expenses:
            for key, value in RI_FACTOR_MAP.items():
                if key in flavor_name:
                    flavor_factor_map[flavor_name] = value
                    break
        return flavor_factor_map

    @staticmethod
    def breakdown_dates(start_date, end_date):
        dates = []
        date = datetime.fromtimestamp(start_date).replace(
            hour=0, minute=0, second=0, microsecond=0)
        while date < datetime.fromtimestamp(end_date):
            dates.append(int(date.timestamp()))
            date += timedelta(days=1)
        return dates

    def get_cloud_account_usage_stats(self, cloud_account_ids):
        cloud_account_usage = defaultdict(
            lambda: defaultdict(lambda: defaultdict(float)))
        usage_breakdown = self.get_usage_breakdown(cloud_account_ids)
        for ch_usage in usage_breakdown:
            (cloud_account_id, date, usage, ri_norm_usage, cost_without_offer,
             cost_with_offer) = ch_usage
            cloud_account_usage[cloud_account_id][date]['usage'] += usage
            cloud_account_usage[cloud_account_id][date][
                'ri_norm_usage'] += ri_norm_usage
            cloud_account_usage[cloud_account_id][date][
                'cost_without_offer'] += cost_without_offer
            cloud_account_usage[cloud_account_id][date][
                'cost_with_offer'] += cost_with_offer
        return cloud_account_usage

    @staticmethod
    def format_cloud_account(cloud_account_id, cloud_accs_map):
        cloud_account = cloud_accs_map.get(cloud_account_id, {})
        cloud_account_type = cloud_account.get('type')
        cloud_account_name = cloud_account.get('name')
        return {
            'cloud_account_type': cloud_account_type,
            'cloud_account_name': cloud_account_name,
        }

    def format_result(self, result, cloud_account_id, date_ts, total_stats,
                      ri_sp_stats, cloud_accs_map, flavors_map):
        usage = ri_sp_stats.get('usage', 0)
        overprovision_hrs = ri_sp_stats.get('overprovision_hrs', {})
        cost_with_offer = ri_sp_stats.get('cost_with_offer', 0)
        cost_without_offer = ri_sp_stats.get('cost_without_offer', 0)
        for flavor in flavors_map:
            if flavor not in overprovision_hrs:
                overprovision_hrs[flavor] = 0
        overprovision = ri_sp_stats.get('overprovision', 0)
        total_usage_hrs = total_stats.get('usage', 0)
        total_cost_without_offer = total_stats.get('cost_without_offer', 0)
        total_cost_with_offer = total_stats.get('cost_with_offer', 0)
        result_dict = {
            'cloud_account_id': cloud_account_id,
            'total_usage_hrs': total_usage_hrs,
            'cost_without_offer': total_cost_without_offer,
            'cost_with_offer': total_cost_with_offer,
            f'{self.RESOURCE_PREFIX}_usage_hrs': usage,
            f'{self.RESOURCE_PREFIX}_overprovision_hrs': overprovision_hrs,
            f'{self.RESOURCE_PREFIX}_overprovision': overprovision,
            f'{self.RESOURCE_PREFIX}_cost_without_offer': cost_without_offer,
            f'{self.RESOURCE_PREFIX}_cost_with_offer': cost_with_offer
        }
        result_dict.update(self.format_cloud_account(
            cloud_account_id, cloud_accs_map))
        result[date_ts].append(result_dict)
        return result

    def _empty_stats(self, cloud_account_id, cloud_accs_map, flavors_map):
        result_dict = {
            'cloud_account_id': cloud_account_id,
            'total_usage_hrs': 0,
            'cost_without_offer': 0,
            'cost_with_offer': 0,
            f'{self.RESOURCE_PREFIX}_usage_hrs': 0,
            f'{self.RESOURCE_PREFIX}_overprovision_hrs': {
                x: 0 for x in flavors_map
            },
            f'{self.RESOURCE_PREFIX}_overprovision': 0,
            f'{self.RESOURCE_PREFIX}_cost_with_offer': 0,
            f'{self.RESOURCE_PREFIX}_cost_without_offer': 0
        }
        result_dict.update(self.format_cloud_account(
            cloud_account_id, cloud_accs_map))
        return result_dict

    def fill_empty_dates(self, result, dates, cloud_account_ids, aws_cloud_accs,
                         flavors_map):
        if not cloud_account_ids:
            return result
        for date_ts, date_result in result.items():
            date_cloud_accs_ids = set(
                x['cloud_account_id'] for x in date_result)
            cloud_accs_to_fill = set(cloud_account_ids) - date_cloud_accs_ids
            for cloud_acc_id in cloud_accs_to_fill:
                date_result.append(self._empty_stats(
                    cloud_acc_id, aws_cloud_accs, flavors_map))
        dates_to_fill = [x for x in dates if x not in result]
        for date in dates_to_fill:
            result[date] = [self._empty_stats(x, aws_cloud_accs, flavors_map)
                            for x in cloud_account_ids]
        return result

    def get_overprovision_ch_expenses(
            self, cloud_account_ids, start_date, end_date):
        # RI may be used on several cloud accounts at the same time.
        # Rows from other cloud account have expected_cost=0, so find main
        # cloud account for offers to add offer_cost to main account cost
        query = """SELECT cloud_account_id, date, sum(offer_cost),
                     sum(expected_cost), sum(n_usage)
                   FROM (
                     SELECT offer_id, date,
                       any(cloud_account_id) as cloud_account_id,
                       sum(offer_cost * sign) AS offer_cost,
                       sum(n_usage * sign) AS n_usage,
                       any(n_expected_cost) AS expected_cost
                     FROM (
                       SELECT offer_id, date, offer_cost, sign,
                         if(expected_cost=0, null, cloud_account_id) as cloud_account_id,
                         if(expected_cost=0, null, expected_cost) as n_expected_cost,
                         usage * ri_norm_factor AS n_usage
                       FROM ri_sp_usage
                       WHERE cloud_account_id IN cloud_account_ids AND
                         date >= %(start_date)s AND date <= %(end_date)s AND
                         offer_type = 'ri')
                     GROUP BY offer_id, date
                     HAVING sum(sign) > 0)
                   GROUP BY cloud_account_id, date"""
        return self.execute_clickhouse(
            query, params={
                'start_date': start_date,
                'end_date': end_date},
            external_tables=[{'name': 'cloud_account_ids',
                              'structure': [('id', 'String')],
                              'data': [{'id': r_id} for r_id in
                                       cloud_account_ids]}])

    def fill_overprovisioning(self, flavor_factor_map, cloud_account_usage,
                              start_date, end_date):
        cloud_acc_ids = list(cloud_account_usage.keys())
        expenses = self.get_overprovision_ch_expenses(
            cloud_acc_ids, start_date, end_date)
        cloud_acc_overprov = defaultdict(lambda: defaultdict(float))
        cloud_acc_overprov_n_hrs = defaultdict(lambda: defaultdict(float))
        for data in expenses:
            cloud_acc_id, date, offer_cost, expected_cost, n_usage = data
            if expected_cost:
                overprov_exp = expected_cost - offer_cost
            else:
                overprov_exp = 0
            cloud_acc_overprov[cloud_acc_id][date] += overprov_exp
            if n_usage and offer_cost:
                cost_per_norm_hr = offer_cost / n_usage
                overprov_n_hrs = overprov_exp / cost_per_norm_hr
            else:
                overprov_n_hrs = 0
            cloud_acc_overprov_n_hrs[cloud_acc_id][date] += overprov_n_hrs
        for cloud_acc_id, date_exp in cloud_account_usage.items():
            for date, data in date_exp.items():
                data['overprovision'] = cloud_acc_overprov.get(
                    cloud_acc_id, {}).get(date, 0)
                if 'overprovision_hrs' not in data:
                    data.update({'overprovision_hrs': {}})
                ri_overprov_norm_hrs = cloud_acc_overprov_n_hrs.get(
                    cloud_acc_id, {}).get(date, 0)
                for flavor_name, ri_norm_factor in flavor_factor_map.items():
                    if ri_norm_factor is not None:
                        ri_usage = ri_overprov_norm_hrs / ri_norm_factor
                        data['overprovision_hrs'][flavor_name] = ri_usage
        return cloud_account_usage

    def get_aws_accounts_map(self, organization_id):
        _, cloud_accounts = self.get_organization_and_cloud_accs(
            organization_id)
        return {
            x.id: {
                'type': x.type.value,
                'name': x.name
            }
            for x in cloud_accounts if x.type.value in SUPPORTED_CLOUD_TYPES
        }

    @staticmethod
    def filter_cloud_accounts(params, aws_cloud_accs_map):
        cloud_account_ids = params.get('cloud_account_id')
        if not cloud_account_ids:
            cloud_account_ids = list(aws_cloud_accs_map.keys())
        else:
            for cloud_account_id in cloud_account_ids:
                if cloud_account_id not in aws_cloud_accs_map.keys():
                    cloud_account_ids.remove(cloud_account_id)
        return cloud_account_ids

    def get(self, organization_id, **params):
        filters = params.copy()
        aws_cloud_accs_map = self.get_aws_accounts_map(organization_id)
        self.handle_filters(params, filters, organization_id)
        cloud_account_ids = self.filter_cloud_accounts(
            params, aws_cloud_accs_map)
        flavor_rate_map = self.get_flavors(cloud_account_ids)
        cloud_account_total = self.get_total_stats(cloud_account_ids)
        cloud_account_usage = self.get_cloud_account_usage_stats(
            cloud_account_ids)
        cloud_account_usage = self.fill_overprovisioning(
            flavor_rate_map, cloud_account_usage,
            datetime.fromtimestamp(self.start_date),
            datetime.fromtimestamp(self.end_date))
        result = defaultdict(list)
        for cloud_account_id in cloud_account_ids:
            date_total_usage_map = cloud_account_total.get(
                cloud_account_id, {})
            date_ri_usage = cloud_account_usage.get(cloud_account_id, {})
            for date, total_stats in date_total_usage_map.items():
                date_ts = int(date.timestamp())
                ri_stats = date_ri_usage.get(date, {})
                result = self.format_result(
                    result, cloud_account_id, date_ts, total_stats, ri_stats,
                    aws_cloud_accs_map, flavor_rate_map)
        breakdown_dates = self.breakdown_dates(self.start_date, self.end_date)
        result = self.fill_empty_dates(
            result, breakdown_dates, cloud_account_ids, aws_cloud_accs_map,
            flavor_rate_map)
        return result


class RiBreakdownAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return RiBreakdownController
