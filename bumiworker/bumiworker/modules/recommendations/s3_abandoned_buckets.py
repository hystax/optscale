import logging
from collections import OrderedDict
from bumiworker.bumiworker.modules.abandoned_base import S3AbandonedBucketsBase


LOG = logging.getLogger(__name__)

DEFAULT_DAYS_THRESHOLD = 7
DATA_SIZE_THRESHOLD = 1024
DATA_SIZE_KEY = 'data_size'
TIER_1_REQUESTS_THRESHOLD = 100
TIER_2_REQUESTS_THRESHOLD = 2000
MBS_IN_GB = 1024
AVG_DATA_SIZE_KEY = 'avg_data_size'
TIER_1_REQUESTS_QUANTITY_KEY = 'tier_1_request_quantity'
TIER_2_REQUESTS_QUANTITY_KEY = 'tier_2_request_quantity'


class S3AbandonedBuckets(S3AbandonedBucketsBase):
    SUPPORTED_CLOUD_TYPES = [
        'aws_cnr'
    ]

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

    def get_metric_threshold_map(self):
        options = self.get_options()
        return {
            TIER_1_REQUESTS_QUANTITY_KEY: options.get(
                'tier_1_request_quantity_threshold'),
            TIER_2_REQUESTS_QUANTITY_KEY: options.get(
                'tier_2_request_quantity_threshold'),
            AVG_DATA_SIZE_KEY: options.get('data_size_threshold')
        }

    def _get_data_size_request_metrics(self, cloud_account_id,
                                       cloud_resource_ids, start_date,
                                       days_threshold):
        product_families = ['Data Transfer', 'API Request']
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
                    DATA_SIZE_KEY] = 0.0
                resource_data_request_map[cloud_resource_id][
                    TIER_1_REQUESTS_QUANTITY_KEY] = 0
                resource_data_request_map[cloud_resource_id][
                    TIER_2_REQUESTS_QUANTITY_KEY] = 0
            total_sum = sum(
                [float(x) for x in data_api_request['usage_amount']])
            if data_api_request['_id']['productFamily'] == 'Data Transfer':
                resource_data_request_map[cloud_resource_id][
                    DATA_SIZE_KEY] += total_sum
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
                if meter_key == DATA_SIZE_KEY:
                    avg_size = (total / days_threshold) * MBS_IN_GB
                    resource_meter_value[res_id][AVG_DATA_SIZE_KEY] = avg_size
                else:
                    resource_meter_value[res_id][meter_key] = total
        return resource_meter_value

    @staticmethod
    def metrics_result(data_req_map):
        return {
            'tier_1_request_quantity': data_req_map.get(
                TIER_1_REQUESTS_QUANTITY_KEY),
            'tier_2_request_quantity': data_req_map.get(
                TIER_2_REQUESTS_QUANTITY_KEY),
            'avg_data_size': data_req_map.get(AVG_DATA_SIZE_KEY),
        }


def main(organization_id, config_client, created_at, **kwargs):
    return S3AbandonedBuckets(
        organization_id, config_client, created_at).get()


def get_module_email_name():
    return 'Abandoned Amazon S3 buckets'
