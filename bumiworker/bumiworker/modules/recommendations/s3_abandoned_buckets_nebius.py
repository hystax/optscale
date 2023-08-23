import logging
from collections import OrderedDict, defaultdict

from bumiworker.bumiworker.modules.abandoned_base import S3AbandonedBucketsBase


LOG = logging.getLogger(__name__)
SUPPORTED_CLOUD_TYPES = [
    'nebius'
]

DEFAULT_DAYS_THRESHOLD = 7
DATA_SIZE_THRESHOLD = 1024
DATA_SIZE_KEY = 'data_size'
GET_REQUESTS_THRESHOLD = 100
PUT_REQUESTS_THRESHOLD = 100
POST_REQUESTS_THRESHOLD = 100
HEAD_REQUESTS_THRESHOLD = 100
OPTIONS_REQUESTS_THRESHOLD = 100
DELETE_REQUESTS_THRESHOLD = 100
MBS_IN_GB = 1024
AVG_DATA_SIZE_KEY = 'avg_data_size'
GET_REQUEST_KEY = 'get_request_quantity'
PUT_REQUEST_KEY = 'put_request_quantity'
POST_REQUEST_KEY = 'post_request_quantity'
HEAD_REQUEST_KEY = 'head_request_quantity'
OPTIONS_REQUEST_KEY = 'options_request_quantity'
DELETE_REQUEST_KEY = 'delete_request_quantity'


class S3AbandonedNebiusBuckets(S3AbandonedBucketsBase):
    SUPPORTED_CLOUD_TYPES = [
        'nebius'
    ]

    def __init__(self, organization_id, config_client, created_at):
        super().__init__(organization_id, config_client, created_at)
        self.option_ordered_map = OrderedDict({
            'days_threshold': {
                'default': DEFAULT_DAYS_THRESHOLD},
            'data_size_threshold': {
                'default': DATA_SIZE_THRESHOLD},
            'get_request_quantity_threshold': {
                'default': GET_REQUESTS_THRESHOLD},
            'post_request_quantity_threshold': {
                'default': POST_REQUESTS_THRESHOLD},
            'put_request_quantity_threshold': {
                'default': PUT_REQUESTS_THRESHOLD},
            'head_request_quantity_threshold': {
                'default': HEAD_REQUESTS_THRESHOLD},
            'options_request_quantity_threshold': {
                'default': OPTIONS_REQUESTS_THRESHOLD},
            'delete_request_quantity_threshold': {
                'default': DELETE_REQUESTS_THRESHOLD},
            'excluded_pools': {
                'default': {},
                'clean_func': self.clean_excluded_pools,
            },
            'skip_cloud_accounts': {'default': []}
        })

    def _get_data_size_request_metrics(
            self, cloud_account_id, cloud_resource_ids, start_date,
            days_threshold):
        resource_meter_value = defaultdict(dict)
        operations_types = {
            'GET': GET_REQUEST_KEY,
            'POST': POST_REQUEST_KEY,
            'HEAD': HEAD_REQUEST_KEY,
            'OPTIONS': OPTIONS_REQUEST_KEY,
            'PUT': PUT_REQUEST_KEY,
            'DELETE': DELETE_REQUEST_KEY
        }
        request_regex = '^(.*)storage — (.*) operations$'
        traffic_regex = '^(.*) traffic (.*)Object Storage(.*)$'
        expenses = self.mongo_client.restapi.raw_expenses.aggregate([
            {
                '$match': {
                    '$and': [
                        {'resource_id': {'$in': cloud_resource_ids}},
                        {'cloud_account_id': cloud_account_id},
                        {'start_date': {'$gte': start_date}},
                        {'$or': [{'sku_name': {'$regex': request_regex}},
                                 {'sku_name': {'$regex': traffic_regex}}]},
                    ]
                }
            },
            {
                '$group': {
                    '_id': {
                        '_id': '$resource_id',
                        'sku_name': '$sku_name',
                        'pricing_unit': '$pricing_unit',
                    },
                    'pricing_quantity': {'$push': '$pricing_quantity'}
                }
            }
        ])
        for expense in expenses:
            cloud_resource_id = expense['_id']['_id']
            value = sum(float(x) for x in expense['pricing_quantity'])
            pricing_unit = expense['_id']['pricing_unit']
            operation_type = list(filter(lambda x: x in expense['_id']['sku_name'],
                                         operations_types.keys()))
            if operation_type:
                operation_key = operations_types[operation_type[0]]
                if pricing_unit == '1k*request':
                    value = round(value * 1000)
                elif pricing_unit == '10k*request':
                    value = round(value * 10000)
                else:
                    LOG.warning('Unknown pricing unit %s', pricing_unit)
                resource_meter_value[cloud_resource_id][operation_key] = value
            elif pricing_unit == 'gbyte':
                avg_size = (value / days_threshold) * MBS_IN_GB
                resource_meter_value[cloud_resource_id][
                    AVG_DATA_SIZE_KEY] = avg_size
        return resource_meter_value

    def get_metric_threshold_map(self):
        options = self.get_options()
        return {
            GET_REQUEST_KEY: options.get('get_request_quantity_threshold'),
            POST_REQUEST_KEY: options.get('post_request_quantity_threshold'),
            PUT_REQUEST_KEY: options.get('put_request_quantity_threshold'),
            HEAD_REQUEST_KEY: options.get('head_request_quantity_threshold'),
            OPTIONS_REQUEST_KEY: options.get(
                'options_request_quantity_threshold'),
            DELETE_REQUEST_KEY: options.get(
                'delete_request_quantity_threshold'),
            AVG_DATA_SIZE_KEY: options.get('data_size_threshold')
        }

    @staticmethod
    def metrics_result(data_req_map):
        return {
            'get_request_quantity': data_req_map.get(
                GET_REQUEST_KEY, 0),
            'post_request_quantity': data_req_map.get(
                POST_REQUEST_KEY, 0),
            'put_request_quantity': data_req_map.get(
                PUT_REQUEST_KEY, 0),
            'options_request_quantity': data_req_map.get(
                OPTIONS_REQUEST_KEY, 0),
            'head_request_quantity': data_req_map.get(
                HEAD_REQUEST_KEY, 0),
            'delete_request_quantity': data_req_map.get(
                DELETE_REQUEST_KEY, 0),
            'avg_data_size': data_req_map.get(AVG_DATA_SIZE_KEY),
        }


def main(organization_id, config_client, created_at, **kwargs):
    return S3AbandonedNebiusBuckets(
        organization_id, config_client, created_at).get()


def get_module_email_name():
    return 'Abandoned Nebius buckets'
