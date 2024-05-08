from bumiworker.bumiworker.modules.abandoned_base import (
    S3AbandonedBucketsArchiveBase
)
from bumiworker.bumiworker.modules.recommendations.s3_abandoned_buckets_nebius import (
    S3AbandonedNebiusBuckets as S3AbandonedNebiusBucketsRecommendation,
    AVG_DATA_SIZE_KEY, GET_REQUEST_KEY, POST_REQUEST_KEY, PUT_REQUEST_KEY,
    HEAD_REQUEST_KEY, OPTIONS_REQUEST_KEY, DELETE_REQUEST_KEY
)


class S3AbandonedNebiusBuckets(S3AbandonedBucketsArchiveBase,
                               S3AbandonedNebiusBucketsRecommendation):
    SUPPORTED_CLOUD_TYPES = [
        'nebius'
    ]

    def get_previous_metric_threshold_map(self, previous_options):
        return {
            GET_REQUEST_KEY: previous_options.get(
                'get_request_quantity_threshold'),
            POST_REQUEST_KEY: previous_options.get(
                'post_request_quantity_threshold'),
            PUT_REQUEST_KEY: previous_options.get(
                'put_request_quantity_threshold'),
            HEAD_REQUEST_KEY: previous_options.get(
                'head_request_quantity_threshold'),
            OPTIONS_REQUEST_KEY: previous_options.get(
                'options_request_quantity_threshold'),
            DELETE_REQUEST_KEY: previous_options.get(
                'delete_request_quantity_threshold'),
            AVG_DATA_SIZE_KEY: previous_options.get('data_size_threshold')
        }


def main(organization_id, config_client, created_at, **kwargs):
    return S3AbandonedNebiusBuckets(
        organization_id, config_client, created_at).get()
