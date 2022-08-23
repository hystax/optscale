from datetime import datetime
from bumi_worker.modules.base import ModuleBase, DAYS_IN_MONTH


class AbandonedBase(ModuleBase):
    def get_active_resources(self, cloud_account_ids, start_date,
                             resource_type):
        resources = self.mongo_client.restapi.resources.find({
            'cloud_account_id': {
                '$in': cloud_account_ids
            },
            'active': True,
            'resource_type': resource_type,
            'first_seen': {'$lt': int(start_date.timestamp())}
        })
        resources_by_account_map = {x: [] for x in cloud_account_ids}
        for res in resources:
            account_id = res['cloud_account_id']
            resources_by_account_map[account_id].append(res)
        return resources_by_account_map

    def get_avg_daily_expenses(self, resource_ids, start_date):
        today = datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0)
        start_date = start_date.replace(
            hour=0, minute=0, second=0, microsecond=0)
        external_table = [{'id': r_id} for r_id in resource_ids]
        query = """
                    SELECT resource_id, sum(cost * sign), min(date)
                    FROM expenses
                    JOIN resources ON resource_id = resources.id
                        AND date >= %(start_date)s
                        AND or(date != %(today)s, cost != 0)
                    GROUP BY resource_id
                """
        expenses = self.clickhouse_client.execute(
            query=query,
            external_tables=[{
                'name': 'resources',
                'structure': [('id', 'String')],
                'data': external_table
            }],
            params={
                'today': today,
                'start_date': start_date
            }
        )
        result = {}
        for expense in expenses:
            days = (today - expense[2]).days
            result[expense[0]] = (expense[1] / days)
        return result

    def get_month_saving_by_daily_avg_expenses(self, resource_ids, start_date):
        result = {}
        daily_expenses = self.get_avg_daily_expenses(resource_ids, start_date)
        for resource_id, expenses in daily_expenses.items():
            result[resource_id] = expenses * DAYS_IN_MONTH
        return result
