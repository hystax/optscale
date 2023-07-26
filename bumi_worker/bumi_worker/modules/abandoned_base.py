from datetime import datetime, timedelta
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
                        AND date != %(today)s
                        AND cost != 0
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


class S3AbandonedBucketsBase(AbandonedBase):
    SUPPORTED_CLOUD_TYPES = []

    def _get_data_size_request_metrics(self, cloud_account_id,
                                       cloud_resource_ids, start_date,
                                       days_threshold):
        raise NotImplementedError

    @staticmethod
    def _are_below_thresholds(res_data_request_map, metric_threshold_map):
        resource_ids = []
        for res_id, data_request_map in res_data_request_map.items():
            if all(data_request_map.get(key, 0) <= threshold_value
                   for key, threshold_value in metric_threshold_map.items()):
                resource_ids.append(res_id)
        return resource_ids

    @staticmethod
    def metrics_result(data_req_map):
        raise NotImplementedError

    def get_metric_threshold_map(self):
        raise NotImplementedError

    @property
    def days_threshold(self):
        return self.get_options().get('days_threshold')

    @property
    def skip_cloud_accounts(self):
        return self.get_options().get('skip_cloud_accounts')

    @property
    def excluded_pools(self):
        return self.get_options().get('excluded_pools')

    def _get(self):
        now = datetime.utcnow()
        start_date = now - timedelta(days=self.days_threshold)

        cloud_accounts = self.get_cloud_accounts(self.SUPPORTED_CLOUD_TYPES,
                                                 self.skip_cloud_accounts)
        buckets_by_account = self.get_active_resources(
            list(cloud_accounts.keys()), start_date, 'Bucket')
        employees = self.get_employees()
        pools = self.get_pools()

        metric_threshold_map = self.get_metric_threshold_map()

        result = []
        for account in cloud_accounts.values():
            cloud_account_id = account['id']
            cloud_type = account['type']
            account_buckets = buckets_by_account[cloud_account_id]
            if account_buckets:
                bucket_cloud_resource_map = {
                    account_bucket['cloud_resource_id']: account_bucket
                    for account_bucket in account_buckets}
                res_data_request_map = self._get_data_size_request_metrics(
                    cloud_account_id, list(bucket_cloud_resource_map.keys()),
                    start_date, self.days_threshold)
                matched_res_ids = self._are_below_thresholds(
                    res_data_request_map, metric_threshold_map)
                matched_bucket_res_ids = [
                    bucket_cloud_resource_map[res_id]['_id']
                    for res_id in matched_res_ids]
                expenses = self.get_month_saving_by_daily_avg_expenses(
                    matched_bucket_res_ids, start_date)
                for cloud_res_id in matched_res_ids:
                    bucket = bucket_cloud_resource_map[cloud_res_id]
                    bucket_id = bucket['_id']
                    data_req_map = res_data_request_map[cloud_res_id]
                    saving = expenses.get(bucket_id, 0)
                    if saving > 0:
                        base_result_dict = {
                            'cloud_resource_id': bucket['cloud_resource_id'],
                            'resource_name': bucket.get('name'),
                            'resource_id': bucket_id,
                            'cloud_account_id': bucket['cloud_account_id'],
                            'cloud_type': cloud_type,
                            'region': bucket.get('region'),
                            'owner': self._extract_owner(
                                bucket.get('employee_id'), employees),
                            'pool': self._extract_pool(
                                bucket.get('pool_id'), pools),
                            'is_excluded': bucket.get(
                                'pool_id') in self.excluded_pools,
                            'saving': saving
                        }
                        base_result_dict.update(self.metrics_result(data_req_map))
                        result.append(base_result_dict)
        return result
