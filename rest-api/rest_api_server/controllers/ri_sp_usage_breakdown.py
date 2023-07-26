import logging
from clickhouse_driver import Client as ClickHouseClient
from collections import defaultdict
from datetime import datetime, timedelta
from rest_api_server.controllers.expense import CleanExpenseController
from rest_api_server.controllers.base_async import BaseAsyncControllerWrapper

CH_DB_NAME = 'risp'
LOG = logging.getLogger(__name__)
SEC_IN_HR = 3600
SUPPORTED_CLOUD_TYPES = ['aws_cnr']


class RiSpUsageController(CleanExpenseController):
    @property
    def clickhouse_client(self):
        if not self._clickhouse_client:
            user, password, host, _ = self._config.clickhouse_params()
            self._clickhouse_client = ClickHouseClient(
                host=host, password=password, database=CH_DB_NAME, user=user)
        return self._clickhouse_client

    def get_usage_breakdown(self, start_date, end_date, cloud_account_ids):
        return self.execute_clickhouse(
            """SELECT
                 cloud_account_id, offer_type, date, sum(usage * sign)
               FROM ri_sp_usage
               WHERE cloud_account_id IN %(cloud_account_ids)s AND
                 date >= %(start_date)s AND date <= %(end_date)s
               GROUP BY cloud_account_id, offer_type, date
               HAVING sum(sign) > 0
               """,
            params={
                'cloud_account_ids': cloud_account_ids,
                'start_date': datetime.fromtimestamp(start_date),
                'end_date': datetime.fromtimestamp(end_date)
            })

    def get_total_usage(self, start_date, end_date, cloud_account_ids):
        pipeline = [
            {'$match': {
                'cloud_account_id': {'$in': cloud_account_ids},
                'start_date': {
                    '$gte': datetime.fromtimestamp(start_date),
                    '$lte': datetime.fromtimestamp(end_date)},
                'box_usage': True,
                'lineItem/LineItemType': {'$ne': 'Credit'}
            }},
            {
                '$project': {
                    'start_date': 1,
                    'cloud_account_id': 1,
                    'pricing/unit': 1,
                    'lineItem/UsageAmount': 1
                }
            },
            {'$group': {
                '_id': {
                    'start_date': '$start_date',
                    'cloud_account_id': '$cloud_account_id',
                },
                'total_hours_usage': {
                    '$push': {'$cond': [{'$eq': ['$pricing/unit', 'Second']},
                                        0, '$lineItem/UsageAmount']}},
                'total_seconds_usage': {
                    '$push': {'$cond': [{'$eq': ['$pricing/unit', 'Second']},
                                        '$lineItem/UsageAmount', 0]}},
            }}]
        return self.raw_expenses_collection.aggregate(pipeline)

    def breakdown_dates(self):
        dates = []
        date = datetime.fromtimestamp(self.start_date).replace(
            hour=0, minute=0, second=0, microsecond=0)
        while date < datetime.fromtimestamp(self.end_date):
            dates.append(int(date.timestamp()))
            date += timedelta(days=1)
        return dates

    def get_total_cloud_account_stats(self, cloud_account_ids):

        cloud_account_total_usage = defaultdict(lambda: defaultdict(lambda: 0))
        accounts_total_usages = self.get_total_usage(
            self.start_date, self.end_date, cloud_account_ids)
        for mongo_usage in accounts_total_usages:
            cloud_account_id = mongo_usage['_id']['cloud_account_id']
            date = mongo_usage['_id']['start_date']
            total_hours = sum(float(x) for x in mongo_usage['total_hours_usage'])
            total_seconds = sum(
                float(x) for x in mongo_usage['total_seconds_usage'])
            cloud_account_total_usage[
                cloud_account_id][date] += total_hours + total_seconds / SEC_IN_HR
        return cloud_account_total_usage

    def get_cloud_account_ri_sp_stats(self, cloud_account_ids):
        cloud_account_usage = defaultdict(
            lambda: defaultdict(lambda: defaultdict(lambda: 0)))
        usage_breakdown = self.get_usage_breakdown(
            self.start_date, self.end_date, cloud_account_ids)
        for ch_usage in usage_breakdown:
            cloud_account_id, offer_type, date, usage = ch_usage
            cloud_account_usage[cloud_account_id][date][offer_type] += usage
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
                      ri_sp_stats, cloud_accs_map):
        ri_stats = ri_sp_stats.get('ri', 0)
        sp_stats = ri_sp_stats.get('sp', 0)
        result_dict = {
            'cloud_account_id': cloud_account_id,
            'total_usage_hrs': total_stats,
            'ri_usage_hrs': ri_stats,
            'sp_usage_hrs': sp_stats,
        }
        result_dict.update(self.format_cloud_account(
            cloud_account_id, cloud_accs_map))
        result[date_ts].append(result_dict)
        return result

    def _empty_stats(self, cloud_account_id, cloud_accs_map):
        result_dict = {
            'cloud_account_id': cloud_account_id,
            'total_usage_hrs': 0,
            'ri_usage_hrs': 0,
            'sp_usage_hrs': 0,
        }
        result_dict.update(self.format_cloud_account(
            cloud_account_id, cloud_accs_map))
        return result_dict

    def fill_empty_dates(self, result, dates, cloud_account_ids, aws_cloud_accs):
        if not cloud_account_ids:
            return result
        for date_ts, date_result in result.items():
            date_cloud_accs_ids = set(
                x['cloud_account_id'] for x in date_result)
            cloud_accs_to_fill = set(cloud_account_ids) - date_cloud_accs_ids
            for cloud_acc_id in cloud_accs_to_fill:
                date_result.append(self._empty_stats(
                    cloud_acc_id, aws_cloud_accs))
        dates_to_fill = [x for x in dates if x not in result]
        for date in dates_to_fill:
            result[date] = [self._empty_stats(x, aws_cloud_accs)
                            for x in cloud_account_ids]
        return result

    def get(self, organization_id, **params):
        filters = params.copy()
        _, cloud_accounts = self.get_organization_and_cloud_accs(organization_id)
        self.handle_filters(params, filters, organization_id)
        aws_cloud_accs_map = {
            x.id: {
                'type': x.type.value,
                'name': x.name
            }
            for x in cloud_accounts if x.type.value in SUPPORTED_CLOUD_TYPES
        }
        cloud_account_ids = params.get('cloud_account_id')
        if not cloud_account_ids:
            cloud_account_ids = list(aws_cloud_accs_map.keys())
        else:
            for cloud_account_id in cloud_account_ids:
                if cloud_account_id not in aws_cloud_accs_map.keys():
                    cloud_account_ids.remove(cloud_account_id)
        cloud_account_total_usage = self.get_total_cloud_account_stats(
            cloud_account_ids)
        cloud_account_usage = self.get_cloud_account_ri_sp_stats(
            cloud_account_ids)

        result = defaultdict(list)
        for cloud_account_id in cloud_account_ids:
            date_total_usage_map = cloud_account_total_usage.get(
                cloud_account_id, {})
            date_ri_sp_usage = cloud_account_usage.get(cloud_account_id, {})
            for date, total_stats in date_total_usage_map.items():
                date_ts = int(date.timestamp())
                ri_sp_stats = date_ri_sp_usage.get(date, {})
                result = self.format_result(
                    result, cloud_account_id, date_ts, total_stats, ri_sp_stats,
                    aws_cloud_accs_map)
        breakdown_dates = self.breakdown_dates()
        result = self.fill_empty_dates(
            result, breakdown_dates, cloud_account_ids, aws_cloud_accs_map)
        return result


class RiSpUsageAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return RiSpUsageController
