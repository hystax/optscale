from collections import OrderedDict
from datetime import datetime, timedelta

from bumi_worker.modules.abandoned_base import AbandonedBase

SUPPORTED_CLOUD_TYPES = [
    'aws_cnr'
]

DEFAULT_DAYS_THRESHOLD = 7
DATA_SIZE_THRESHOLD = 1024
TIER_1_REQUESTS_THRESHOLD = 100
TIER_2_REQUESTS_THRESHOLD = 2000
MBS_IN_GB = 1024
AVG_DATA_SIZE_KEY = 'avg_data_size'
TIER_1_REQUESTS_QUANTITY_KEY = 'tier_1_request_quantity'
TIER_2_REQUESTS_QUANTITY_KEY = 'tier_2_request_quantity'


class S3AbandonedBuckets(AbandonedBase):
    def __init__(self, organization_id, config_client, created_at):
        super().__init__(organization_id, config_client, created_at)
        self.option_ordered_map = OrderedDict({
            'days_threshold': {
                'default': DEFAULT_DAYS_THRESHOLD},
            'data_size_threshold': {
                'default': DATA_SIZE_THRESHOLD},
            'tier_1_request_quantity_threshold': {
                'default': TIER_1_REQUESTS_THRESHOLD},
            'tier_2_request_quantity_threshold': {
                'default': TIER_2_REQUESTS_THRESHOLD},
            'excluded_pools': {
                'default': {},
                'clean_func': self.clean_excluded_pools,
            },
            'skip_cloud_accounts': {'default': []}
        })

    def _get_data_size_tier_request_metrics(self, cloud_account_id,
                                            cloud_resource_ids, start_date,
                                            days_threshold):
        product_families = ['Data Transfer', 'API Request']
        data_size_key = 'data_size'
        tier_1_request_type = 'Requests-Tier1'
        tier_2_request_type = 'Requests-Tier2'
        data_api_requests = self.mongo_client.restapi.raw_expenses.aggregate([
            {
                '$match': {
                    '$and': [
                        {'resource_id': {'$in': cloud_resource_ids}},
                        {'cloud_account_id': cloud_account_id},
                        {'start_date': {'$gte': start_date}},
                        {'product/productFamily': {'$in': product_families}}
                    ]
                }
            },
            {
                '$group': {
                    '_id': {
                        '_id': '$resource_id',
                        'productFamily': '$product/productFamily',
                        'tier_type': '$lineItem/UsageType',
                        'operation': '$lineItem/Operation'
                    },
                    'usage_amount': {'$push': '$lineItem/UsageAmount'}
                }
            }
        ])
        resource_data_request_map = {}
        for data_api_request in data_api_requests:
            cloud_resource_id = data_api_request['_id']['_id']
            if not resource_data_request_map.get(cloud_resource_id):
                resource_data_request_map[cloud_resource_id] = {}
                resource_data_request_map[cloud_resource_id][
                    data_size_key] = 0.0
                resource_data_request_map[cloud_resource_id][
                    TIER_1_REQUESTS_QUANTITY_KEY] = 0
                resource_data_request_map[cloud_resource_id][
                    TIER_2_REQUESTS_QUANTITY_KEY] = 0
            total_sum = sum(
                [float(x) for x in data_api_request['usage_amount']])
            if data_api_request['_id']['productFamily'] == 'Data Transfer':
                resource_data_request_map[cloud_resource_id][
                    data_size_key] += total_sum
            else:
                res_tier_type = data_api_request['_id']['tier_type']
                res_operation = data_api_request['_id']['operation']
                if tier_1_request_type in res_tier_type:
                    resource_data_request_map[cloud_resource_id][
                        TIER_1_REQUESTS_QUANTITY_KEY] += int(total_sum)
                elif (tier_2_request_type in res_tier_type and
                      res_operation == 'GetObject'):
                    resource_data_request_map[cloud_resource_id][
                        TIER_2_REQUESTS_QUANTITY_KEY] += int(total_sum)
        resource_meter_value = {}
        for res_id, meter_map in resource_data_request_map.items():
            if not resource_meter_value.get(res_id):
                resource_meter_value[res_id] = {}
            for meter_key, total in meter_map.items():
                if meter_key == data_size_key:
                    avg_size = (total / days_threshold) * MBS_IN_GB
                    resource_meter_value[res_id][AVG_DATA_SIZE_KEY] = avg_size
                else:
                    resource_meter_value[res_id][meter_key] = total
        return resource_meter_value

    def _are_below_thresholds(self, res_data_request_map, data_size_threshold,
                              tier_1_threshold, tier_2_threshold):
        resource_ids = []
        for res_id, data_request_map in res_data_request_map.items():
            if (data_request_map[AVG_DATA_SIZE_KEY] <= data_size_threshold and
                    data_request_map[TIER_1_REQUESTS_QUANTITY_KEY] <=
                    tier_1_threshold and
                    data_request_map[TIER_2_REQUESTS_QUANTITY_KEY] <=
                    tier_2_threshold):
                resource_ids.append(res_id)
        return resource_ids

    def _get(self):
        (days_threshold, data_size_threshold, tier_1_request_quantity_threshold,
         tier_2_request_quantity_threshold, excluded_pools,
         skip_cloud_accounts) = self.get_options_values()

        now = datetime.utcnow()
        start_date = now - timedelta(days=days_threshold)

        cloud_accounts = self.get_cloud_accounts(SUPPORTED_CLOUD_TYPES,
                                                 skip_cloud_accounts)
        buckets_by_account = self.get_active_resources(
            list(cloud_accounts.keys()), start_date, 'Bucket')
        employees = self.get_employees()
        pools = self.get_pools()

        result = []
        for account in cloud_accounts.values():
            cloud_account_id = account['id']
            account_buckets = buckets_by_account[cloud_account_id]
            if account_buckets:
                bucket_cloud_resource_map = {
                    account_bucket['cloud_resource_id']: account_bucket
                    for account_bucket in account_buckets}
                res_data_request_map = self._get_data_size_tier_request_metrics(
                    cloud_account_id, list(bucket_cloud_resource_map.keys()),
                    start_date, days_threshold)
                matched_res_ids = self._are_below_thresholds(
                    res_data_request_map, data_size_threshold,
                    tier_1_request_quantity_threshold,
                    tier_2_request_quantity_threshold)
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
                        result.append(
                            {
                                'cloud_resource_id': bucket[
                                    'cloud_resource_id'],
                                'resource_name': bucket.get('name'),
                                'resource_id': bucket_id,
                                'cloud_account_id': bucket['cloud_account_id'],
                                'cloud_type': account['type'],
                                'region': bucket['region'],
                                'owner': self._extract_owner(
                                    bucket.get('employee_id'), employees),
                                'pool': self._extract_pool(
                                    bucket.get('pool_id'), pools),
                                'is_excluded': bucket.get(
                                    'pool_id') in excluded_pools,
                                'avg_data_size': data_req_map[
                                    AVG_DATA_SIZE_KEY],
                                'tier_1_request_quantity': data_req_map[
                                    TIER_1_REQUESTS_QUANTITY_KEY],
                                'tier_2_request_quantity': data_req_map[
                                    TIER_2_REQUESTS_QUANTITY_KEY],
                                'saving': saving
                            })
        return result


def main(organization_id, config_client, created_at, **kwargs):
    return S3AbandonedBuckets(
        organization_id, config_client, created_at).get()


def get_module_email_name():
    return 'Abandoned Amazon S3 buckets'
