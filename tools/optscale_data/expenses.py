import re
from calendar import monthrange
from datetime import datetime, timedelta, timezone

from tools.optscale_data.clickhouse import ExternalDataConverter
from tools.optscale_time import utcnow


class ExpenseQuery:
    def __init__(self, execute_clickhouse, resources_collection):
        self._execute_ch = execute_clickhouse
        self._resources = resources_collection

    def _execute(self, query, **kwargs):
        return self._execute_ch(query=query, **kwargs)

    def get_cloud_expenses_with_resource_info(self, cloud_acc_list, start_date, end_date):
        pipeline = [
            {
                '$match': {
                    '$and': [
                        {'cloud_account_id': {'$in': cloud_acc_list}},
                        {'_first_seen_date': {'$lt': end_date}},
                        {'_last_seen_date': {'$gte': start_date.replace(
                            hour=0, minute=0, second=0, microsecond=0)}},
                        {'first_seen': {'$lt': int(end_date.timestamp())}},
                        {'last_seen': {'$gte': int(start_date.timestamp())}},
                        {'deleted_at': 0}
                    ]
                }
            },
            {
                '$group': {
                    '_id': '$cloud_account_id',
                    'count': {'$sum': 1}
                }
            }
        ]
        resource_counts = list(self._resources.aggregate(pipeline))
        query = """
            SELECT cloud_account_id, SUM(cost * sign), count
            FROM expenses
            JOIN cloud_accounts
                ON expenses.cloud_account_id = cloud_accounts._id
            WHERE cloud_account_id IN %(cloud_acc_list)s
                AND date >= %(start_date)s AND date < %(end_date)s
            GROUP BY cloud_account_id, count
        """
        return self._execute(
            query=query,
            parameters={
                'start_date': start_date,
                'end_date': end_date,
                'cloud_acc_list': cloud_acc_list
            },
            external_data=ExternalDataConverter()([{
                'name': 'cloud_accounts',
                'structure': [
                    ('_id', 'String'),
                    ('count', 'Int32')
                ],
                'data': resource_counts
            }]),
        )

    @staticmethod
    def get_monthly_forecast(cost, month_cost, first_expense=None):
        today = datetime.today()
        month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month_start = (month_start - timedelta(days=1)).replace(day=1)
        start_date = max(last_month_start, first_expense) if (
            first_expense) else last_month_start
        worked_days = (today - month_start).days
        forecast_days = (today - start_date).days
        daily_forecast = cost / forecast_days if forecast_days > 0 else cost
        _, days_in_month = monthrange(today.year, today.month)
        forecast = month_cost + daily_forecast * (days_in_month - worked_days)
        return round(forecast, 2)

    def _get_first_cloud_account_expense(
            self, cloud_account_ids, date, field=None, values=None
    ):
        if (field and not values) or not cloud_account_ids:
            return []
        if field and re.search(r'[^_A-Za-z0-9]', field):
            raise ValueError('Suspected SQL injection ')
        query = f"""
            SELECT {field if field else 'cloud_account_id'}, min(date)
            FROM expenses
            WHERE cloud_account_id
                IN cloud_account_ids{' AND %s IN values' %
                                     field if field else ''}
                AND date >= %(date)s
            GROUP BY cloud_account_id{', %s' % field if field else ''}
        """
        external_tables = [
            {
                'name': 'cloud_account_ids',
                'structure': [('id', 'String')],
                'data': [{'id': r_id} for r_id in cloud_account_ids]
            }
        ]
        if values:
            external_tables.append({
                'name': 'values',
                'structure': [('id', 'String')],
                'data': [{'id': r_id} for r_id in values]
            })
        return self._execute(
            query=query,
            parameters={
                'date': date
            },
            external_data=ExternalDataConverter()(external_tables)
        )

    def get_first_expenses_for_forecast(self, field, values):
        prev_month_start = (utcnow().replace(day=1) - timedelta(
            days=1)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if field in ['cloud_account_id']:
            result = self._get_first_cloud_account_expense(values, prev_month_start)
        else:
            # TODO: Not the optimal solution to get expenses dates.
            #  We can get all the necessary dates at the time of receiving the
            #  expenses for the previous month
            resources = list(self._resources.find(
                {field: {'$in': values}, 'cloud_account_id': {'$ne': None}},
                ['cloud_account_id', field]))
            r_ids = list(map(lambda x: x['_id'], resources))
            cloud_account_ids = set(
                map(lambda x: x.get('cloud_account_id'), resources))
            expenses = self._get_first_cloud_account_expense(
                list(cloud_account_ids), prev_month_start, 'resource_id',
                r_ids)
            expenses_map = {e[0]: e[1] for e in expenses}
            result = {}
            for resource in resources:
                value = resource.get(field)
                date = expenses_map.get(resource['_id'])
                if not date:
                    continue
                if value not in result or result[value] > date:
                    result[value] = date
            result = [(k, v) for k, v in result.items()]
        return {r[0]: r[1] for r in result}
